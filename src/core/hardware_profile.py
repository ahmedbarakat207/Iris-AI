import os
import re
import sys
import platform
import subprocess
import threading
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from enum import Enum

try:
    import psutil

    _PSUTIL = True
except ImportError:
    _PSUTIL = False


class AccelBackend(str, Enum):
    METAL = "metal"
    CUDA = "cuda"
    ROCM = "rocm"
    VULKAN = "vulkan"
    CPU = "cpu"


class ChipFamily(str, Enum):
    APPLE_M1 = "apple_m1"
    APPLE_M2 = "apple_m2"
    APPLE_M3 = "apple_m3"
    APPLE_M4 = "apple_m4"
    APPLE_UNKNOWN = "apple_unknown"
    NVIDIA = "nvidia"
    AMD = "amd"
    INTEL_CPU = "intel_cpu"
    AMD_CPU = "amd_cpu"
    ARM_CPU = "arm_cpu"
    UNKNOWN = "unknown"


@dataclass
class HardwareProfile:

    chip_family: ChipFamily = ChipFamily.UNKNOWN
    backend: AccelBackend = AccelBackend.CPU
    device_label: str = "Unknown device"

    total_ram_gb: float = 8.0
    free_ram_gb: float = 4.0
    total_vram_gb: float = 0.0
    num_gpus: int = 0

    physical_cores: int = 4
    perf_cores: int = 4
    logical_cores: int = 4

    n_gpu_layers: int = -1
    n_threads: int = 4
    n_threads_batch: int = 4
    n_batch: int = 512
    n_ubatch: int = 256
    flash_attn: bool = True
    use_mmap: bool = True
    use_mlock: bool = False

    ctx_triage: int = 8192
    ctx_control: int = 8192
    ctx_math: int = 4096
    ctx_code: int = 8192
    ctx_reasoning: int = 8192
    ctx_general: int = 8192
    ctx_vision: int = 4096
    ctx_default: int = 4096

    kv_quant: str = "q8_0"

    recommended_size: str = "small"

    notes: list = field(default_factory=list)


def _ram_gb() -> tuple[float, float]:

    if _PSUTIL:
        vm = psutil.virtual_memory()
        return vm.total / 1e9, vm.available / 1e9
    try:
        if platform.system() == "Darwin":
            out = subprocess.check_output(["sysctl", "-n", "hw.memsize"], text=True)
            total = int(out.strip()) / 1e9

            vm = subprocess.check_output(["vm_stat"], text=True)
            pages_free = int(re.search(r"Pages free:\s+(\d+)", vm).group(1))
            pages_inactive = int(re.search(r"Pages inactive:\s+(\d+)", vm).group(1))
            page_size = 16384
            free = (pages_free + pages_inactive) * page_size / 1e9
            return total, free
        elif platform.system() == "Linux":
            with open("/proc/meminfo") as f:
                mi = f.read()
            total = int(re.search(r"MemTotal:\s+(\d+)", mi).group(1)) * 1024 / 1e9
            avail = int(re.search(r"MemAvailable:\s+(\d+)", mi).group(1)) * 1024 / 1e9
            return total, avail
        elif platform.system() == "Windows":
            import ctypes

            class MEMORYSTATUSEX(ctypes.Structure):
                _fields_ = [
                    ("dwLength", ctypes.c_ulong),
                    ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong),
                    ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong),
                    ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong),
                    ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("sullAvailExtendedVirtual", ctypes.c_ulonglong),
                ]

            stat = MEMORYSTATUSEX()
            stat.dwLength = ctypes.sizeof(stat)
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
            return stat.ullTotalPhys / 1e9, stat.ullAvailPhys / 1e9
    except Exception:
        pass

    try:
        total = os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES") / 1e9
        return total, total * 0.4
    except Exception:
        return 8.0, 3.0


def _cpu_cores() -> tuple[int, int, int]:

    logical = os.cpu_count() or 4

    if _PSUTIL:
        try:
            physical = psutil.cpu_count(logical=False) or logical // 2
        except Exception:
            physical = logical // 2
    else:
        physical = logical // 2

    perf = physical
    if platform.system() == "Darwin":
        try:
            p = subprocess.check_output(
                ["sysctl", "-n", "hw.perflevel0.physicalcpu"], text=True
            ).strip()
            perf = int(p)
        except Exception:

            perf = max(4, physical // 2)

    return physical, perf, logical


def _detect_apple_chip() -> tuple[ChipFamily, str]:

    try:
        brand = subprocess.check_output(
            ["sysctl", "-n", "machdep.cpu.brand_string"], text=True
        ).strip()
    except Exception:
        brand = ""

    if not brand:
        try:
            brand = subprocess.check_output(
                ["sysctl", "-n", "hw.model"], text=True
            ).strip()
        except Exception:
            brand = ""

    label = brand or "Apple Silicon"
    low = brand.lower()

    if "m4" in low:
        return ChipFamily.APPLE_M4, label
    if "m3" in low:
        return ChipFamily.APPLE_M3, label
    if "m2" in low:
        return ChipFamily.APPLE_M2, label
    if "m1" in low:
        return ChipFamily.APPLE_M1, label
    return ChipFamily.APPLE_UNKNOWN, label


def _detect_nvidia() -> tuple[bool, float, str, int]:

    try:
        out = subprocess.check_output(
            [
                "nvidia-smi",
                "--query-gpu=name,memory.total",
                "--format=csv,noheader,nounits",
            ],
            text=True,
            timeout=5,
        )
        lines = [l.strip() for l in out.strip().splitlines() if l.strip()]
        if not lines:
            return False, 0.0, "", 0
        name = lines[0].rsplit(",", 1)[0].strip()
        vram_gbs = [float(l.rsplit(",", 1)[1].strip()) / 1024 for l in lines]
        total_vram_gb = sum(vram_gbs)
        return True, total_vram_gb, name, len(lines)
    except Exception:
        return False, 0.0, "", 0


def _detect_amd_gpu() -> tuple[bool, str]:

    try:
        out = subprocess.check_output(
            ["rocm-smi", "--showproductname"], text=True, timeout=5
        )
        if "GPU" in out or "Radeon" in out:
            return True, out.splitlines()[0].strip()
    except Exception:
        pass
    return False, ""


def _ctx_for_ram(
    total_ram_gb: float,
    model_size_gb: float = 4.0,
    backend: AccelBackend = AccelBackend.CPU,
    vram_gb: float = 0.0,
) -> dict:

    if backend == AccelBackend.METAL:
        budget_gb = total_ram_gb - model_size_gb - 2.5
    elif backend in (AccelBackend.CUDA, AccelBackend.ROCM):
        budget_gb = total_ram_gb - 2.0
    else:
        budget_gb = total_ram_gb - model_size_gb - 2.0

    budget_gb = max(budget_gb, 0.5)

    if budget_gb < 1.5:
        base = 2048
    elif budget_gb < 3.0:
        base = 4096
    elif budget_gb < 6.0:
        base = 8192
    elif budget_gb < 12.0:
        base = 16384
    else:
        base = 32768

    if backend in (AccelBackend.CUDA, AccelBackend.ROCM):
        if vram_gb > 0 and vram_gb < 8.0:
            base = min(base, 8192)
        elif vram_gb > 0 and vram_gb < 12.0:
            base = min(base, 16384)

    return {
        "ctx_triage": max(base, 8192),
        "ctx_control": min(base, 8192),
        "ctx_math": min(base, 8192),
        "ctx_code": base,
        "ctx_reasoning": base,
        "ctx_general": base,
        "ctx_vision": min(base, 8192),
        "ctx_default": min(base, 8192),
    }


def _apple_silicon_params(
    chip: ChipFamily, total_ram_gb: float, perf_cores: int
) -> dict:

    is_pro_max_ultra = total_ram_gb >= 32

    threads = max(4, min(perf_cores, 8))

    if is_pro_max_ultra:

        n_batch = 1024
        n_ubatch = 512
        kv_quant = "f16"
    elif total_ram_gb >= 16:
        n_batch = 512
        n_ubatch = 256
        kv_quant = "f16"
    else:

        n_batch = 512
        n_ubatch = 256
        kv_quant = "q8_0"

    if chip == ChipFamily.APPLE_M4:
        n_batch = min(n_batch * 2, 2048)
        n_ubatch = min(n_ubatch * 2, 512)

    return dict(
        n_gpu_layers=-1,
        n_threads=1,
        n_threads_batch=threads,
        n_batch=n_batch,
        n_ubatch=n_ubatch,
        flash_attn=True,
        use_mmap=True,
        use_mlock=False,
        kv_quant=kv_quant,
    )


def _nvidia_params(vram_gb: float, system_ram_gb: float, logical_cores: int) -> dict:

    cpu_threads = min(logical_cores, 8)
    kv_quant = "f16" if vram_gb >= 10 else "q8_0"

    return dict(
        n_gpu_layers=-1,
        n_threads=cpu_threads,
        n_threads_batch=cpu_threads,
        n_batch=2048,
        n_ubatch=512,
        flash_attn=True,
        use_mmap=True,
        use_mlock=False,
        kv_quant=kv_quant,
    )


def _amd_gpu_params(system_ram_gb: float, logical_cores: int) -> dict:

    cpu_threads = min(logical_cores, 8)
    return dict(
        n_gpu_layers=-1,
        n_threads=cpu_threads,
        n_threads_batch=cpu_threads,
        n_batch=1024,
        n_ubatch=512,
        flash_attn=False,
        use_mmap=True,
        use_mlock=False,
        kv_quant="q8_0",
    )


def _cpu_only_params(
    total_ram_gb: float, physical_cores: int, logical_cores: int
) -> dict:

    threads = min(physical_cores, 16)
    mlock = total_ram_gb >= 16

    if total_ram_gb >= 32:
        n_batch = 512
        n_ubatch = 256
    elif total_ram_gb >= 16:
        n_batch = 256
        n_ubatch = 128
    else:
        n_batch = 128
        n_ubatch = 64

    return dict(
        n_gpu_layers=0,
        n_threads=threads,
        n_threads_batch=threads,
        n_batch=n_batch,
        n_ubatch=n_ubatch,
        flash_attn=False,
        use_mmap=True,
        use_mlock=mlock,
        kv_quant="q4_0",
    )


def _recommend_size(total_ram_gb: float, vram_gb: float, backend: AccelBackend) -> str:

    if backend == AccelBackend.CUDA and vram_gb > 0:
        memory = vram_gb
    else:
        memory = total_ram_gb

    if memory < 4:
        return "nano"
    elif memory < 8:
        return "tiny"
    elif memory < 16:
        return "small"
    elif memory < 24:
        return "medium"
    elif memory < 48:
        return "large"
    else:
        return "max"


_cached_profile: Optional[HardwareProfile] = None
_profile_lock = threading.Lock()


def get_hardware_profile(force_refresh: bool = False) -> HardwareProfile:

    global _cached_profile
    with _profile_lock:
        if _cached_profile is not None and not force_refresh:
            return _cached_profile
        _cached_profile = _build_profile()
        return _cached_profile


def _build_profile() -> HardwareProfile:
    p = HardwareProfile()
    system = platform.system()

    p.total_ram_gb, p.free_ram_gb = _ram_gb()

    p.physical_cores, p.perf_cores, p.logical_cores = _cpu_cores()

    if system == "Darwin" and platform.machine() in ("arm64", "aarch64"):

        chip, label = _detect_apple_chip()
        p.chip_family = chip
        p.backend = AccelBackend.METAL
        p.device_label = label
        p.total_vram_gb = 0.0

        params = _apple_silicon_params(chip, p.total_ram_gb, p.perf_cores)
        p.notes.append(f"Apple Silicon Metal backend — perf_cores={p.perf_cores}")

    else:

        nvidia_found, nvidia_vram, nvidia_label, num_gpus = _detect_nvidia()
        if nvidia_found:
            p.chip_family = ChipFamily.NVIDIA
            p.backend = AccelBackend.CUDA
            p.device_label = (
                f"{num_gpus}x {nvidia_label}" if num_gpus > 1 else nvidia_label
            )
            p.total_vram_gb = nvidia_vram
            p.num_gpus = num_gpus
            params = _nvidia_params(nvidia_vram, p.total_ram_gb, p.logical_cores)
            p.notes.append(
                f"NVIDIA CUDA — {num_gpus} GPUs, Total VRAM={nvidia_vram:.1f} GB"
            )
        else:

            amd_found, amd_label = _detect_amd_gpu()
            if amd_found:
                p.chip_family = ChipFamily.AMD
                p.backend = AccelBackend.ROCM
                p.device_label = amd_label
                params = _amd_gpu_params(p.total_ram_gb, p.logical_cores)
                p.notes.append("AMD ROCm GPU detected")
            else:

                machine = platform.machine().lower()
                cpu_brand = ""
                try:
                    if system == "Linux":
                        with open("/proc/cpuinfo") as f:
                            for line in f:
                                if "model name" in line:
                                    cpu_brand = line.split(":", 1)[1].strip()
                                    break
                    elif system == "Windows":
                        import winreg

                        key = winreg.OpenKey(
                            winreg.HKEY_LOCAL_MACHINE,
                            r"HARDWARE\DESCRIPTION\System\CentralProcessor\0",
                        )
                        cpu_brand = winreg.QueryValueEx(key, "ProcessorNameString")[0]
                except Exception:
                    pass

                low = cpu_brand.lower()
                if "intel" in low:
                    p.chip_family = ChipFamily.INTEL_CPU
                elif "amd" in low or "ryzen" in low:
                    p.chip_family = ChipFamily.AMD_CPU
                elif "arm" in machine or "aarch" in machine:
                    p.chip_family = ChipFamily.ARM_CPU

                p.backend = AccelBackend.CPU
                p.device_label = cpu_brand or f"{p.physical_cores}-core CPU"
                params = _cpu_only_params(
                    p.total_ram_gb, p.physical_cores, p.logical_cores
                )
                p.notes.append(
                    f"CPU-only — {p.physical_cores} cores, {p.total_ram_gb:.1f} GB RAM"
                )

    p.n_gpu_layers = params["n_gpu_layers"]
    p.n_threads = params["n_threads"]
    p.n_threads_batch = params["n_threads_batch"]
    p.n_batch = params["n_batch"]
    p.n_ubatch = params["n_ubatch"]
    p.flash_attn = params["flash_attn"]
    p.use_mmap = params["use_mmap"]
    p.use_mlock = params["use_mlock"]
    p.kv_quant = params["kv_quant"]

    ctx_vals = _ctx_for_ram(
        p.total_ram_gb, model_size_gb=4.0, backend=p.backend, vram_gb=p.total_vram_gb
    )
    for key, val in ctx_vals.items():
        setattr(p, key, val)

    p.recommended_size = _recommend_size(p.total_ram_gb, p.total_vram_gb, p.backend)

    p.notes.append(
        f"RAM={p.total_ram_gb:.1f} GB  size={p.recommended_size}  "
        f"ctx_default={p.ctx_default}  kv={p.kv_quant}  "
        f"threads={p.n_threads}  batch={p.n_batch}/{p.n_ubatch}  "
        f"flash_attn={p.flash_attn}"
    )
    return p


def apply_to_config(cfg: dict, hw: Optional[HardwareProfile] = None) -> dict:

    if hw is None:
        hw = get_hardware_profile()

    profile = cfg.get("performance_profile", "balanced").lower()

    n_threads = hw.n_threads
    n_threads_batch = hw.n_threads_batch
    n_batch = hw.n_batch
    kv_quant = hw.kv_quant
    flash_attn = hw.flash_attn

    if profile == "low":
        n_threads = min(4, hw.physical_cores)
        n_threads_batch = n_threads
        kv_quant = "q8_0"
        flash_attn = True
    elif profile == "high":

        kv_quant = "f16"

    def _auto_or_missing(key, fallback):
        v = cfg.get(key)
        if v is None or str(v).lower() == "auto":
            cfg[key] = fallback

    _auto_or_missing("n_gpu_layers", hw.n_gpu_layers)
    _auto_or_missing("n_threads", n_threads)
    _auto_or_missing("n_threads_batch", n_threads_batch)
    _auto_or_missing("n_batch", n_batch)
    _auto_or_missing("n_ubatch", hw.n_ubatch)
    _auto_or_missing("flash_attn", flash_attn)
    _auto_or_missing("use_mlock", hw.use_mlock)

    if hw.num_gpus >= 2:
        _auto_or_missing("tensor_split", [1.0] * hw.num_gpus)

    if cfg.get("size", "auto") in ("auto", "", None):
        cfg["size"] = hw.recommended_size

    ca = cfg.setdefault("compressed_attention", {})
    if ca.get("kv_quant", "auto").lower() == "auto":
        ca["kv_quant"] = kv_quant

    return cfg


def ctx_for_role(role_name: str, hw: Optional[HardwareProfile] = None) -> int:

    if hw is None:
        hw = get_hardware_profile()
    mapping = {
        "triage": hw.ctx_triage,
        "router": hw.ctx_triage,
        "control": hw.ctx_control,
        "math": hw.ctx_math,
        "code": hw.ctx_code,
        "reasoning": hw.ctx_reasoning,
        "reviewer": hw.ctx_reasoning,
        "general": hw.ctx_general,
        "vision": hw.ctx_vision,
    }
    return mapping.get(role_name, hw.ctx_default)


def summary() -> str:

    hw = get_hardware_profile()
    return (
        f"[HW] {hw.device_label} | {hw.backend.value.upper()} | "
        f"RAM={hw.total_ram_gb:.1f}GB | size={hw.recommended_size} | "
        f"ctx={hw.ctx_default} | kv={hw.kv_quant} | "
        f"threads={hw.n_threads} | batch={hw.n_batch}/{hw.n_ubatch} | "
        f"flash={hw.flash_attn}"
    )


if __name__ == "__main__":
    import json

    hw = get_hardware_profile()
    print(summary())
    print()
    print(
        json.dumps(
            {
                "device": hw.device_label,
                "backend": hw.backend.value,
                "chip_family": hw.chip_family.value,
                "total_ram_gb": round(hw.total_ram_gb, 1),
                "total_vram_gb": round(hw.total_vram_gb, 1),
                "physical_cores": hw.physical_cores,
                "perf_cores": hw.perf_cores,
                "recommended_size": hw.recommended_size,
                "n_gpu_layers": hw.n_gpu_layers,
                "n_threads": hw.n_threads,
                "n_threads_batch": hw.n_threads_batch,
                "n_batch": hw.n_batch,
                "n_ubatch": hw.n_ubatch,
                "flash_attn": hw.flash_attn,
                "use_mlock": hw.use_mlock,
                "kv_quant": hw.kv_quant,
                "ctx_triage": hw.ctx_triage,
                "ctx_code": hw.ctx_code,
                "ctx_reasoning": hw.ctx_reasoning,
                "ctx_default": hw.ctx_default,
                "notes": hw.notes,
            },
            indent=2,
        )
    )
