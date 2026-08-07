import os
import concurrent.futures
import gc
import glob
import hashlib
import json
import pickle
import platform
import re
import threading
import time
import warnings
import math
from contextlib import asynccontextmanager
from enum import Enum
from typing import Any, Dict, Generator, List, Optional, Tuple, Union

os.environ["HF_XET_HIGH_PERFORMANCE"] = "1"
os.environ["GGML_CUDA_NO_VMM"] = "1"
warnings.filterwarnings("ignore")

from .logger import get_logger

logger = get_logger("iris")


def _load_skill_prompt(skill_path: str) -> str:
    path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "skills",
        skill_path,
    )
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        logger.warning(f"Skill prompt not found: {path}")
        return ""


from typing import Any, Dict, Generator, List, Optional, Tuple, Union

warnings.filterwarnings("ignore")

import math
from contextlib import asynccontextmanager

from src.core.hardware_profile import get_hardware_profile

try:
    from llama_cpp.llama_speculative import LlamaDraftModel
except ImportError:

    class LlamaDraftModel:
        pass


class DualLlamaDraftModel(LlamaDraftModel):
    def __init__(self, draft_llm, num_pred_tokens: int = 4):
        import numpy as np

        self.draft_llm = draft_llm
        self.num_pred_tokens = num_pred_tokens
        self.np = np

    def __call__(self, input_ids, /, **kwargs):
        input_list = input_ids.tolist()

        if self.draft_llm.n_tokens > len(input_list):
            self.draft_llm.n_tokens = len(input_list)

        new_tokens = input_list[self.draft_llm.n_tokens :]
        if new_tokens:
            self.draft_llm.eval(new_tokens)

        drafts = []
        for _ in range(self.num_pred_tokens):
            next_token = self.draft_llm.sample()
            drafts.append(next_token)
            self.draft_llm.eval([next_token])

        return self.np.array(drafts, dtype=self.np.intc)


from src.hca.compressed_attention import (
    KVQuantLevel,
    _get_ftype,
    estimate_kv_cache_ram,
    select_kv_quant,
    smart_compress,
)
from src.hca.context_compactor import auto_compact_for_role

from .hardware_profile import apply_to_config, ctx_for_role, get_hardware_profile
from .hardware_profile import summary as hw_summary

try:
    import torch
    import torch.nn.functional as F
    from torch.utils.data import DataLoader, Dataset

    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer, util

    RAG_AVAILABLE = True
except Exception as e:
    logger.warning(f"[WARNING] RAG disabled due to library error: {e}")
    RAG_AVAILABLE = False

try:
    import mlx.core as mx

    MLX_AVAILABLE = True
except ImportError:
    MLX_AVAILABLE = False

try:
    from transformers import AutoModelForCausalLM, AutoTokenizer

    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

try:
    from datasets import load_dataset

    DATASETS_AVAILABLE = True
except ImportError:
    DATASETS_AVAILABLE = False


if os.name == "nt":
    cuda_path = os.environ.get("CUDA_PATH")
    if cuda_path and os.path.exists(os.path.join(cuda_path, "bin")):
        cuda_bin = os.path.join(cuda_path, "bin")
        try:
            os.add_dll_directory(cuda_bin)
            logger.info(
                f"[Windows CUDA] Added DLL directory from CUDA_PATH: {cuda_bin}"
            )
        except Exception as e:
            logger.warning(
                f"[Windows CUDA] Failed to add DLL directory {cuda_bin}: {e}"
            )

    common_cuda_root = r"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA"
    if os.path.exists(common_cuda_root):
        try:
            for item in os.listdir(common_cuda_root):
                bin_path = os.path.join(common_cuda_root, item, "bin")
                if os.path.exists(bin_path):
                    try:
                        os.add_dll_directory(bin_path)
                        logger.info(
                            f"[Windows CUDA] Added DLL directory from default path: {bin_path}"
                        )
                    except Exception:
                        pass
        except Exception:
            pass

import threading as _hw_thread

import llama_cpp
from llama_cpp import Llama

_hw_thread.Thread(
    target=lambda: __import__("src.core.hardware_profile", fromlist=["summary"]).summary(),
    daemon=True,
).start()

import ctypes


def _llama_log_callback(level, text, user_data):
    if text:
        try:
            msg = text.decode("utf-8", errors="ignore").strip()
            if msg:
                logger.debug(f"[llama.cpp] {msg}")
        except Exception:
            pass


_log_cb = ctypes.CFUNCTYPE(None, ctypes.c_int, ctypes.c_char_p, ctypes.c_void_p)(
    _llama_log_callback
)
llama_cpp.llama_log_set(_log_cb, ctypes.c_void_p(0))
from .harness import (
    HERMES_AGENT_SYSTEM_PROMPT,
    HermesAgentLoop,
    HermesResultAnalyzer,
    HermesToolRegistry,
    SandboxResult,
    apply_smart_harness_code,
    apply_smart_harness_math,
    build_code_refinement_prompt,
    build_hermes_text_prompt,
    build_math_refinement_prompt,
    parse_hermes_tool_call,
)
from .harness import (
    apply_code_specific as _apply_harness,
)
from .harness import (
    apply_math as _apply_math_harness,
)
from .syntax_checker import check_syntax, extract_code_blocks


class ModelRole(str, Enum):
    TRIAGE = "triage"
    ROUTER = "router"
    MATH = "math"
    CODE = "code"
    REASONING = "reasoning"
    GENERAL = "general"
    VISION = "vision"
    CONTROL = "control"
    REVIEWER = "reviewer"


class TaskType(str, Enum):
    CODING_SIMPLE = "coding_simple"
    CODING_COMPLEX = "coding_complex"
    MATH = "math"
    REASONING = "reasoning"
    GENERAL = "general"
    SEARCH = "search"
    CONTROL = "control"


_HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(os.path.dirname(_HERE), "config", "iris.conf")

DEFAULT_MODEL_FILES: Dict[str, str] = {
    "triage": "iris_001.gguf",
    "router": "iris_001.gguf",
    "control": "iris_004.gguf",
    "math": "iris_003.gguf",
    "code": "iris_004.gguf",
    "reasoning": "iris_005.gguf",
    "reviewer": "iris_005.gguf",
    "general": "iris_005.gguf",
    "vision": "iris_006.gguf",
    "clip": "iris_007.gguf",
}
_MODEL_SOURCES: Dict[str, list] = {
    "iris_001.gguf": [
        ("Qwen/Qwen2.5-3B-Instruct-GGUF", "qwen2.5-3b-instruct-q4_k_m.gguf"),
    ],
    "iris_004.gguf": [
        (
            "Qwen/Qwen2.5-Coder-14B-Instruct-GGUF",
            "qwen2.5-coder-14b-instruct-q4_k_m.gguf",
        ),
    ],
    "iris_003.gguf": [
        (
            "bartowski/Qwen2.5-Math-7B-Instruct-GGUF",
            "Qwen2.5-Math-7B-Instruct-Q4_K_M.gguf",
        ),
    ],
    "iris_005.gguf": [
        (
            "unsloth/DeepSeek-R1-Distill-Qwen-14B-GGUF",
            "DeepSeek-R1-Distill-Qwen-14B-Q4_K_M.gguf",
        ),
    ],
    "iris_006.gguf": [
        ("unsloth/Qwen2.5-VL-7B-Instruct-GGUF", "Qwen2.5-VL-7B-Instruct-Q4_K_M.gguf"),
    ],
    "iris_007.gguf": [
        ("unsloth/Qwen2.5-VL-7B-Instruct-GGUF", "mmproj-F16.gguf"),
    ],
}


ROLE_CTX: Dict[ModelRole, int] = {
    ModelRole.TRIAGE: 32768,
    ModelRole.ROUTER: 32768,
    ModelRole.CONTROL: 32768,
    ModelRole.MATH: 32768,
    ModelRole.CODE: 32768,
    ModelRole.REASONING: 32768,
    ModelRole.REVIEWER: 32768,
    ModelRole.GENERAL: 32768,
    ModelRole.VISION: 32768,
}

DEFAULT_CTX = 4096
DEFAULT_GPU_LAYERS = -1
DEFAULT_THREADS = 4
DEFAULT_BATCH = 2048
DEFAULT_UBATCH = 512
DEFAULT_THREADS_BATCH = 4


IRIS_IDENTITY = (
    "You are Iris, made by the Iris Team. You talk to the user like a sharp, easygoing friend having a "
    "conversation — not like a corporate 'AI assistant'. Be casual, warm, and direct. Avoid stiff, formal, "
    "customer-service phrasing (no 'I'd be happy to assist you', no sign-offs like 'let me know if there's "
    "anything else I can help with'). "
    "If asked who made you, who created you, or who you are, answer casually in a sentence or two — you're "
    "Iris, made by the Iris Team — and do NOT recite a list of your capabilities. "
    "Never open a message by introducing yourself ('I am Iris...') — just respond naturally, the way a person would. "
    "CRITICAL LANGUAGE RULE: You MUST always respond in English. All responses, explanations, code comments, and text MUST be written entirely in English, even if the user speaks or inputs in Arabic or any other language. Your internal reasoning process and final response must be fully in English."
)


from collections import OrderedDict

_model_pool: OrderedDict[str, "Llama"] = OrderedDict()
_model_paths: dict[str, str] = {}


def _get_max_pool_size() -> int:
    try:
        _gcfg = load_generation_config()
    except Exception:
        _gcfg = {}

    if "max_pool_size" in _gcfg:
        return _gcfg["max_pool_size"]

    try:
        _size = _gcfg.get("size", "tiny")
        _size_path = os.path.join(
            os.path.dirname(CONFIG_PATH), "sizes", f"{_size}.json"
        )
        if os.path.exists(_size_path):
            with open(_size_path, "r", encoding="utf-8") as f:
                _size_cfg = json.load(f)
            if "max_pool_size" in _size_cfg:
                return _size_cfg["max_pool_size"]
    except Exception:
        pass

    _n_gpu = _gcfg.get("n_gpu_layers", -1)

    if _n_gpu != 0:
        try:
            import subprocess

            _r = subprocess.run(
                [
                    "nvidia-smi",
                    "--query-gpu=memory.total",
                    "--format=csv,noheader,nounits",
                ],
                capture_output=True,
                text=True,
                timeout=3,
            )
            if _r.returncode == 0:
                _vram_mb = float(_r.stdout.strip().splitlines()[0])
                if _vram_mb >= 12000:
                    return 3
                elif _vram_mb >= 6000:
                    return 2
        except Exception:
            pass
    return 2


_keep_loaded: bool = False
_model_lock = threading.RLock()


_mlx_backend_cache: dict = {}
_mlx_cache_lock = threading.Lock()


class MLXTextModel:
    def __init__(self, model_path: str, temp: float = 0.7):
        import mlx.core as mx
        from mlx_lm import load as mlx_load

        self.model, self.tokenizer = mlx_load(model_path)
        self.temp = temp
        self._path = model_path

    def n_ctx(self) -> int:
        return 8192

    def n_embd(self) -> int:
        return getattr(self, "_n_embd", 0) or 2560

    def create_chat_completion(
        self,
        messages,
        stream=True,
        max_tokens=512,
        temperature=None,
        top_p=0.9,
        top_k=40,
        repeat_penalty=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        min_p=0.0,
        seed=42,
        **kwargs,
    ):
        import json
        import time

        import mlx.core as mx
        from mlx_lm import generate as mlx_gen

        temp = temperature if temperature is not None else self.temp

        if hasattr(self.tokenizer, "apply_chat_template"):
            prompt = self.tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )
        else:
            prompt = json.dumps(messages)

        try:
            tokens = mx.array(self.tokenizer.encode(prompt))
        except Exception:
            from mlx_lm.utils import generate_step

            prompt = "\n".join(f"{m['role']}: {m['content']}" for m in messages)
            tokens = mx.array(self.tokenizer.encode(prompt))

        max_new = min(max_tokens, 8192)

        if not stream:
            response = mlx_gen(
                self.model,
                self.tokenizer,
                prompt=prompt,
                max_tokens=max_new,
                temp=temp,
                top_p=top_p,
                verbose=False,
            )
            return {
                "choices": [
                    {
                        "message": {"content": response},
                        "finish_reason": "stop",
                    }
                ]
            }

        class _MLXStream:
            def __init__(slf):
                slf._gen = mlx_gen(
                    self.model,
                    self.tokenizer,
                    prompt=prompt,
                    max_tokens=max_new,
                    temp=temp,
                    top_p=top_p,
                    verbose=False,
                )
                slf._done = False
                slf._buf = ""

            def __iter__(slf):
                return slf

            def __next__(slf):
                if slf._done:
                    raise StopIteration
                try:
                    text = next(slf._gen)
                    if isinstance(text, str) and text:
                        slf._buf += text
                        return {"choices": [{"delta": {"content": text}}]}
                    return {"choices": [{"delta": {"content": ""}}]}
                except StopIteration:
                    slf._done = True
                    return {
                        "choices": [{"delta": {"content": ""}, "finish_reason": "stop"}]
                    }

        return _MLXStream()

    def reset(self):
        pass

    def close(self):
        import mlx.core as mx

        mx.clear_cache()


def _get_mlx_model(model_path: str, temp: float = 0.7) -> Optional[MLXTextModel]:
    global _mlx_backend_cache
    with _mlx_cache_lock:
        key = f"{model_path}:{temp:.2f}"
        if key in _mlx_backend_cache:
            return _mlx_backend_cache[key]
        try:
            model = MLXTextModel(model_path, temp)
            _mlx_backend_cache[key] = model
            logger.info(
                f"[MLX] Loaded text model via Metal GPU: {os.path.basename(model_path)}"
            )
            return model
        except Exception as e:
            logger.warning(f"[MLX] Failed to load model via MLX: {e}")
            return None


def _get_model_filename(role: ModelRole) -> str:
    cfg = load_generation_config()
    models_dict = cfg.get("models", {})
    return models_dict.get(role.value) or DEFAULT_MODEL_FILES.get(
        role.value, f"iris-{role.value}.gguf"
    )


def _model_path(filename: str) -> str:
    return os.path.join(os.path.dirname(_HERE), "models", filename)


def _parse_hf_url(url: str) -> Optional[Tuple[str, str]]:
    if "huggingface.co" in url and "/resolve/" in url:
        try:
            parts = url.split("huggingface.co/")[-1].split("/resolve/")
            repo_id = parts[0]
            subparts = parts[1].split("/")
            remote_name = "/".join(subparts[1:])
            return repo_id, remote_name
        except Exception:
            pass
    return None


def get_size_config_download_info(filename: str) -> Optional[Tuple[str, str]]:
    try:
        cfg = load_generation_config()
        size = cfg.get("size", "tiny")
        size_path = os.path.join(os.path.dirname(CONFIG_PATH), "sizes", f"{size}.json")
        if os.path.exists(size_path):
            with open(size_path, "r", encoding="utf-8") as f:
                size_cfg = json.load(f)

            gguf_map = size_cfg.get("gguf", {})
            role = None
            for r, g_name in gguf_map.items():
                if g_name == filename:
                    role = r
                    break

            if not role and size_cfg.get("clip") == filename:
                url_map = size_cfg.get("download_urls", {})
                if filename in url_map:
                    return url_map[filename], filename

            if role:
                src_name = size_cfg.get("source_filenames", {}).get(role)
                url_map = size_cfg.get("download_urls", {})
                if src_name and src_name in url_map:
                    return url_map[src_name], src_name
    except Exception as e:
        logger.warning(
            f"[Iris] Failed to read size config for download URL lookup: {e}"
        )
    return None


def _is_gguf_valid(path: str) -> bool:
    if not os.path.exists(path):
        return False

    local_size = os.path.getsize(path)
    if local_size < 10 * 1024 * 1024:
        return False

    try:
        with open(path, "rb") as f:
            magic = f.read(4)
            if magic != b"GGUF":
                return False
    except Exception:
        return False

    return True


def download_gguf(filename: str, quiet: bool = False) -> bool:
    dest_path = os.path.join(os.path.dirname(_HERE), "models", filename)
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)

    if os.path.exists(dest_path) and _is_gguf_valid(dest_path):
        if not quiet:
            logger.info(
                f"[Iris] {filename} already present and valid, skipping download"
            )
        return True

    if not quiet:
        logger.info(f"[Iris] Downloading {filename} ...")

    sources = []
    if download_info:
        url, remote_name = download_info
        hf_parsed = _parse_hf_url(url)
        if hf_parsed:
            sources.append(hf_parsed)
        else:
            sources.append(("", url))

    if filename in _MODEL_SOURCES:
        for repo_id, remote_name in _MODEL_SOURCES[filename]:
            if (repo_id, remote_name) not in sources:
                sources.append((repo_id, remote_name))

    if not sources:
        if not quiet:
            logger.info(f"[Iris] No download sources known for {filename}")
        return False

    last_error = None

    try:
        import time as _time

        import os
        from huggingface_hub import hf_hub_download

        for repo_id, remote_name in sources:
            if not repo_id:
                continue
            try:
                if not quiet:
                    logger.info(f"  Trying {repo_id}/{remote_name} ...")
                start = _time.time()
                downloaded_path = hf_hub_download(
                    repo_id=repo_id,
                    filename=remote_name,
                    local_dir=os.path.join(os.path.dirname(_HERE), "models"),
                    local_dir_use_symlinks=False,
                )
                if (
                    downloaded_path
                    and os.path.exists(downloaded_path)
                    and os.path.abspath(downloaded_path) != os.path.abspath(dest_path)
                ):
                    os.rename(downloaded_path, dest_path)
                elapsed = _time.time() - start
                size_mb = os.path.getsize(dest_path) / (1024 * 1024)
                if not quiet:
                    logger.info(
                        f"  Done: {filename} — {size_mb:.0f} MB in {elapsed:.0f}s"
                    )
                return True
            except Exception as e:
                last_error = str(e)
                if "401" in last_error or "gated" in last_error.lower():
                    continue
                if "already exists" in last_error.lower():
                    return True
                if not quiet:
                    logger.warning(f"  Failed: {last_error[:60]}...")
    except ImportError:
        pass

    try:
        import time as _time
        import urllib.request

        for repo_id, remote_name in sources:
            if not repo_id:
                url = remote_name
            else:
                url = f"https://huggingface.co/{repo_id}/resolve/main/{remote_name}"
            try:
                if not quiet:
                    logger.info(f"  Trying direct: {url[:80]}...")
                start = _time.time()
                tmp = dest_path + ".part"
                urllib.request.urlretrieve(url, tmp)
                os.replace(tmp, dest_path)
                elapsed = _time.time() - start
                size_mb = os.path.getsize(dest_path) / (1024 * 1024)
                if not quiet:
                    logger.info(
                        f"  Done: {filename} — {size_mb:.0f} MB in {elapsed:.0f}s"
                    )
                return True
            except Exception as e:
                last_error = str(e)
                if not quiet:
                    logger.warning(f"  Failed: {last_error[:60]}...")
    except Exception:
        pass

    if not quiet:
        logger.warning(f"[Iris] Failed to download {filename}: {last_error}")
    return False


def _unload_locked(role_to_evict: str = None, force_all: bool = False) -> None:

    global _model_pool, _model_paths

    if role_to_evict:
        llm = _model_pool.pop(role_to_evict, None)
        _model_paths.pop(role_to_evict, None)
        if llm:
            try:
                if hasattr(llm, "close"):
                    llm.close()
                else:
                    llm.reset()
            except Exception:
                pass
            del llm
    else:
        try:
            cfg = load_generation_config()
            _keep_triage = cfg.get("keep_triage_loaded", True)
        except Exception:
            _keep_triage = True

        keys_to_remove = []
        for r, llm in list(_model_pool.items()):

            if (
                _keep_triage
                and not force_all
                and r in (ModelRole.TRIAGE.value, ModelRole.ROUTER.value)
            ):
                continue
            keys_to_remove.append(r)
            try:
                if hasattr(llm, "close"):
                    llm.close()
                else:
                    llm.reset()
            except Exception:
                pass
            del llm

        for r in keys_to_remove:
            _model_pool.pop(r, None)
            _model_paths.pop(r, None)

    gc.collect()
    if platform.system() == "Linux":
        try:
            import ctypes

            ctypes.CDLL(None).malloc_trim(0)
        except Exception:
            pass


def _evict_from_pool_locked(pool_size_limit: int) -> None:
    global _model_pool
    if len(_model_pool) >= pool_size_limit:
        try:
            cfg = load_generation_config()
            _keep_triage = cfg.get("keep_triage_loaded", True)
        except Exception:
            _keep_triage = True

        role_to_evict = None
        if _keep_triage:
            for r in _model_pool:
                if r not in (ModelRole.TRIAGE.value, ModelRole.ROUTER.value):
                    role_to_evict = r
                    break
        if role_to_evict is None:
            role_to_evict = next(iter(_model_pool))

        _unload_locked(role_to_evict)


_prefetched_files = set()


def prefetch_model_file(filename: str) -> None:
    global _prefetched_files
    if filename in _prefetched_files:
        return
    try:
        path = _model_path(filename)
        if os.path.exists(path):
            if hasattr(os, "posix_fadvise") and hasattr(os, "POSIX_FADV_WILLNEED"):
                logger.info(f"[Iris] Prefetching model pages into OS cache: {filename}")
                fd = os.open(path, os.O_RDONLY)
                os.posix_fadvise(fd, 0, 0, os.POSIX_FADV_WILLNEED)
                os.close(fd)
                _prefetched_files.add(filename)
    except Exception as e:
        logger.debug(f"[Iris] Prefetch failed for {filename}: {e}")


def load_model(role: ModelRole, override_n_ctx: Optional[int] = None) -> "Llama":

    global _model_pool, _model_paths

    with _model_lock:
        filename = _get_model_filename(role)
        prefetch_model_file(filename)
        path = _model_path(filename)

        if role.value in _model_pool and _model_paths.get(role.value) == path:
            cached_llm = _model_pool[role.value]
            cached_n_ctx = (
                cached_llm.n_ctx()
                if callable(getattr(cached_llm, "n_ctx", None))
                else getattr(cached_llm, "n_ctx", 1024)
            )
            if override_n_ctx is None or cached_n_ctx >= override_n_ctx:
                _model_pool.move_to_end(role.value)
                return cached_llm
            else:
                logger.info(
                    f"[Iris] Evicting cached {role.value} model because n_ctx {cached_n_ctx} < {override_n_ctx}"
                )
                _unload_locked(role.value)

        if not os.path.exists(path) or not _is_gguf_valid(path):
            raise FileNotFoundError(
                f"GGUF model not found or invalid for role '{role.value}'.\n"
                f"Expected: {path}\n"
                f"Please place the GGUF file in {os.path.join(os.path.dirname(_HERE), 'models')}/"
            )
        cfg = load_generation_config()

        size = cfg.get("size", "tiny")
        size_path = os.path.join(os.path.dirname(CONFIG_PATH), "sizes", f"{size}.json")
        size_cfg = {}
        if os.path.exists(size_path):
            try:
                with open(size_path, "r", encoding="utf-8") as f:
                    size_cfg = json.load(f)
            except Exception as e:
                logger.warning(f"[Iris] Failed to load size config {size_path}: {e}")

        hw = get_hardware_profile()

        if override_n_ctx is not None:
            n_ctx = override_n_ctx
        else:
            _ctx_raw = cfg.get("n_ctx_allocation", "auto")
            if str(_ctx_raw).lower() == "auto":
                n_ctx = ctx_for_role(role.value, hw)
            else:
                try:
                    n_ctx = int(_ctx_raw)
                except (ValueError, TypeError):
                    n_ctx = ctx_for_role(role.value, hw)

            n_ctx = min(n_ctx, ROLE_CTX.get(role, n_ctx))
            if "context_length" in size_cfg:
                n_ctx = min(n_ctx, size_cfg["context_length"])
            if not n_ctx:
                n_ctx = hw.ctx_default

        n_gpu_layers = cfg.get("n_gpu_layers", -1)
        if (str(n_gpu_layers).lower() == "auto") and "num_layers" in size_cfg:
            n_gpu_layers = size_cfg["num_layers"]
        if n_gpu_layers == -1:
            n_gpu_layers = hw.n_gpu_layers

        n_threads = cfg.get("n_threads", hw.n_threads)
        if str(n_threads).lower() == "auto":
            n_threads = hw.n_threads
        else:
            n_threads = int(n_threads)

        _ca_cfg = cfg.get("compressed_attention", {})
        _kv_pref = _ca_cfg.get("kv_quant", "auto")
        _profile = cfg.get("size", "tiny")
        _ram_gb = 16.0
        try:
            if os.name == "posix":
                _ram_gb = (os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES")) / (
                    1024**3
                )
        except Exception:
            pass
        try:
            _kv_pref_enum = KVQuantLevel(_kv_pref.lower())
        except ValueError:
            _kv_pref_enum = KVQuantLevel.AUTO

        _flash_attn = cfg.get("flash_attn", hw.flash_attn)
        _kv_quant = select_kv_quant(
            model_size_gb=os.path.getsize(path) / (1024**3),
            n_ctx=n_ctx,
            ram_gb=_ram_gb,
            preference=_kv_pref_enum,
            profile=_profile,
        )
        _selected_kv_type = _get_ftype(_kv_quant)
        if not _flash_attn:

            _selected_kv_type = 1
            _kv_quant = KVQuantLevel.F16
        _kv_ram_mb = estimate_kv_cache_ram(
            os.path.getsize(path) / (1024**3), n_ctx, _kv_quant
        )
        logger.debug(
            f"[Iris] KV cache: {_kv_quant.value.upper()} → ~{_kv_ram_mb:.0f} MB @ n_ctx={n_ctx}"
        )

        draft_model = None

        _sd_cfg = cfg.get("speculative_decoding", {})
        if _sd_cfg.get("enabled", False):
            try:
                _sd_type = _sd_cfg.get("type", "model")
                if _sd_type == "model":
                    _draft_role_str = _sd_cfg.get("draft_model_role", "triage")
                    try:
                        _draft_role = ModelRole(_draft_role_str)
                        if _draft_role != role:
                            logger.info(
                                f"[Iris] Speculative decoding: Loading draft model '{_draft_role.value}'..."
                            )
                            _draft_llm = load_model(_draft_role, override_n_ctx=n_ctx)

                            if (
                                _draft_llm.n_vocab() != True
                                if "_new_llm_vocab" in locals()
                                else 0
                            ):
                                pass

                            draft_model = DualLlamaDraftModel(
                                _draft_llm,
                                num_pred_tokens=_sd_cfg.get("num_pred_tokens", 4),
                            )
                            logger.info(
                                f"[Iris] Speculative decoding: Draft model '{_draft_role.value}' injected."
                            )
                    except ValueError:
                        logger.warning(
                            f"[Iris] Invalid draft_model_role: '{_draft_role_str}'"
                        )
                else:
                    from llama_cpp.llama_speculative import LlamaPromptLookupDecoding

                    draft_model = LlamaPromptLookupDecoding(
                        max_ngram_size=2, num_pred_tokens=10
                    )
                    logger.info(
                        f"[Iris] Speculative decoding: N-Gram Prompt Lookup enabled"
                    )
            except ImportError:
                logger.warning(
                    f"[Iris] Speculative decoding requested, but dependencies missing."
                )
            except Exception as _e:
                logger.warning(
                    f"[Iris] Speculative decoding failed to initialize: {_e}"
                )

        _backend_pref = (
            os.environ.get("IRIS_BACKEND") or cfg.get("backend", "auto")
        ).lower()
        _use_mlx = _backend_pref in ("mlx", "metal", "gpu")
        if _use_mlx and MLX_AVAILABLE:
            try:
                _mlx_dir = os.path.join(
                    os.path.dirname(_HERE), "mlx_data", os.path.splitext(filename)[0]
                )
                if os.path.isdir(_mlx_dir):
                    _mlx_temp = cfg.get("temperature", 0.7)
                    _pool_size_limit = _get_max_pool_size()
                    _evict_from_pool_locked(_pool_size_limit)
                    _mlx_llm = _get_mlx_model(_mlx_dir, _mlx_temp)
                    if _mlx_llm is not None:
                        _model_pool[role.value] = _mlx_llm
                        _model_paths[role.value] = path
                        logger.info(
                            f"[Iris] Using MLX Metal GPU backend for {role.value}"
                        )
                        return _mlx_llm
                else:
                    logger.warning(
                        f"[Iris] MLX model dir not found: {_mlx_dir}. Falling back to llama.cpp (GGUF)."
                    )
            except Exception as _mlx_e:
                logger.warning(
                    f"[Iris] MLX backend failed, falling back to llama.cpp: {_mlx_e}"
                )

        _n_threads_batch = cfg.get("n_threads_batch", hw.n_threads_batch)
        if str(_n_threads_batch).lower() == "auto":
            _n_threads_batch = hw.n_threads_batch
        else:
            _n_threads_batch = int(_n_threads_batch)

        _n_batch = cfg.get("n_batch", hw.n_batch)
        if str(_n_batch).lower() == "auto":
            _n_batch = hw.n_batch
        else:
            _n_batch = int(_n_batch)

        _n_ubatch = cfg.get("n_ubatch", hw.n_ubatch)
        if str(_n_ubatch).lower() == "auto":
            _n_ubatch = hw.n_ubatch

        _flash_attn = cfg.get("flash_attn", hw.flash_attn)

        _main_gpu = cfg.get("main_gpu", 0)
        _tensor_split = cfg.get("tensor_split", None)
        if _tensor_split and not isinstance(_tensor_split, list):
            _tensor_split = None

        _pool_size_limit = _get_max_pool_size()
        _evict_from_pool_locked(_pool_size_limit)

        logger.info(
            f"[Iris] Instantiating Llama: model={path}, n_gpu_layers={n_gpu_layers}, n_threads={n_threads}, main_gpu={_main_gpu}, tensor_split={_tensor_split}"
        )
        try:
            _new_llm = Llama(
                model_path=path,
                n_ctx=n_ctx,
                n_gpu_layers=n_gpu_layers,
                n_threads=n_threads,
                n_threads_batch=_n_threads_batch,
                use_mmap=hw.use_mmap,
                use_mlock=hw.use_mlock,
                flash_attn=cfg.get("flash_attn", _flash_attn),
                type_k=_selected_kv_type,
                type_v=_selected_kv_type,
                n_batch=_n_batch,
                n_ubatch=_n_ubatch,
                verbose=False,
                logits_all=(draft_model is not None),
                main_gpu=_main_gpu,
                tensor_split=_tensor_split,
            )
            if "tokenizer.chat_template" not in _new_llm.metadata:
                logger.info(
                    f"[Iris] No chat template found in {path} metadata; falling back to ChatML format."
                )
                _new_llm.chat_format = "chatml"
        except Exception as e:
            logger.error(
                f"[Iris] Failed to load model from file: {path}. Error: {e}",
                exc_info=True,
            )
            raise RuntimeError(
                f"Failed to load model from file: {path}. "
                f"This usually indicates that you ran out of memory (RAM/VRAM) to load this model, "
                f"or the downloaded file is incomplete. If you suspect the file is corrupted, "
                f"please delete {path} manually and try again."
            )

        if draft_model is not None:
            _new_llm.draft_model = draft_model

        _model_pool[role.value] = _new_llm
        _model_paths[role.value] = path

        if isinstance(draft_model, DualLlamaDraftModel):
            if draft_model.draft_llm.n_vocab() != _new_llm.n_vocab():
                logger.warning(
                    f"[Iris] Disabling draft model! Vocab mismatch: Draft({draft_model.draft_llm.n_vocab()}) != Target({_new_llm.n_vocab()})"
                )
                _new_llm.draft_model = None

        return _new_llm


def unload_model(role_to_evict: str = None, force_all: bool = False) -> None:

    with _model_lock:
        _unload_locked(role_to_evict, force_all=force_all)


def _force_unload_all_models() -> None:
    unload_model(force_all=True)
    try:
        from src.iris.iris.vision import unload_vision_model

        unload_vision_model()
    except Exception:
        pass


def _system_prompt_for(role: ModelRole) -> str:
    from src.iris.iris.coding import get_code_prompt, get_reviewer_prompt
    from src.iris.iris.control import get_control_prompt
    from src.iris.iris.general import get_general_prompt
    from src.iris.iris.math import get_math_prompt
    from src.iris.iris.reasoning import get_reasoning_prompt
    from src.iris.iris.triage import TRIAGE_SYSTEM_PROMPT

    GENERAL_SYSTEM_PROMPT = get_general_prompt(IRIS_IDENTITY)
    CODE_SYSTEM_PROMPT = get_code_prompt(IRIS_IDENTITY)
    MATH_SYSTEM_PROMPT = get_math_prompt(IRIS_IDENTITY)
    REASONING_SYSTEM_PROMPT = get_reasoning_prompt(IRIS_IDENTITY)
    REVIEWER_SYSTEM_PROMPT = get_reviewer_prompt(IRIS_IDENTITY)
    CONTROL_SYSTEM_PROMPT = get_control_prompt(IRIS_IDENTITY)

    prompts = {
        ModelRole.TRIAGE: TRIAGE_SYSTEM_PROMPT,
        ModelRole.ROUTER: "You are the Iris AI Router. Output JSON action matrices.",
        ModelRole.CONTROL: CONTROL_SYSTEM_PROMPT,
        ModelRole.MATH: MATH_SYSTEM_PROMPT,
        ModelRole.CODE: CODE_SYSTEM_PROMPT,
        ModelRole.REASONING: REASONING_SYSTEM_PROMPT,
        ModelRole.REVIEWER: REVIEWER_SYSTEM_PROMPT,
        ModelRole.GENERAL: GENERAL_SYSTEM_PROMPT,
        ModelRole.VISION: "You are the Iris AI Vision node. Analyze the visual context.",
    }
    return prompts.get(role, GENERAL_SYSTEM_PROMPT)


def _minimize_history(
    history: List[Dict[str, str]], max_entries: int = 4
) -> List[Dict[str, str]]:
    if not history:
        return []
    recent = history[-max_entries:]
    result = []
    for msg in recent:
        content = msg.get("content", "")
        content = re.sub(r"```[\s\S]*?```", "```\n[code omitted]\n```", content)
        if len(content) > 500:
            content = content[:500] + "\n...[truncated]"
        result.append({"role": msg["role"], "content": content})
    return result


def _is_continuation(query: str, history: List[Dict[str, str]]) -> bool:
    if not history:
        return False
    q = query.strip().lower().strip("?.!,;:\"'")
    continuation_words = {
        "continue",
        "keep going",
        "go on",
        "proceed",
        "finish",
        "finish the code",
        "finish code",
        "more",
        "complete",
        "next",
    }
    if q in continuation_words or re.match(
        r"^(continue|finish|complete)\s+(writing|code|the\s+code|generating|developing)$",
        q,
    ):
        for msg in reversed(history):
            role = msg.get("role", "")
            content = msg.get("content", "")
            if role == "assistant" and (
                "```" in content or "def " in content or "class " in content
            ):
                return True
        return False
    return False


def _quality_guard(text: str) -> str:

    text = re.sub(
        r"^\s*(?:think|thinking|reasoning|analysis)\s*[:\-]\s*",
        "",
        text,
        count=1,
        flags=re.IGNORECASE,
    )

    text = re.sub(r"```\w*\s*```", "", text)
    text = re.sub(r"```\w*\s*\n```", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    def _scrub_latex_in_code(m: re.Match) -> str:
        block = m.group(0)
        block = re.sub(r"\$([^$\n]*)\$", r"\1", block)
        block = re.sub(r"\$\$[\s\S]*?\$\$", "", block)
        block = re.sub(
            r"(def |class )([\w$\\{}_^]+)",
            lambda mm: (
                mm.group(1) + re.sub(r"[\\${}^]|_(?=\{)", "_", mm.group(2)).strip("_")
            ),
            block,
        )
        block = re.sub(
            r"\\(?:boxed|frac|sqrt|text|mathrm|left|right)\{[^}]*\}", "", block
        )
        return block

    text = re.sub(r"```[\s\S]*?```", _scrub_latex_in_code, text)

    text = text.replace("\\[", "$$").replace("\\]", "$$")

    text = re.sub(
        r"(?i)(I('m| am) (DeepSeek|Qwen|Intern|Hermes|Llama|Meta|Mistral|"
        r"a large language model|an AI language model|an artificial intelligence)"
        r"[^.]*\.?\s*)",
        "",
        text,
    ).strip()

    text = re.sub(
        r"(?i)(?:<\|im_end\b(?:>)?|<\|im_start\b(?:>)?|<\|eot_id\b(?:>)?|[\n\r]\s*(?:user|assistant)\b)[\s\S]*",
        "",
        text,
    ).strip()

    sentences = re.split(r"(?<=[.!?])\s+", text)
    if len(sentences) > 10:
        seen = {}
        cut_idx = None
        for i, s in enumerate(sentences):
            normalized = s.strip().lower()
            if len(normalized) < 15:
                continue
            seen[normalized] = seen.get(normalized, 0) + 1
            if seen[normalized] >= 5:
                cut_idx = i
                break
        if cut_idx is not None:
            text = " ".join(sentences[:cut_idx])
            if not text.endswith((".", "!", "?")):
                text += "."
            if "<think>" in text and "</think>" not in text:
                text += "\n</think>"

    return text


def translate_text(text: str, target_lang: str) -> str:
    target = target_lang.lower().strip()
    if not target:
        return text
    if target == "english":
        if detect_user_language(text) == "English":
            return text
        target = "en"

    try:
        from deep_translator import GoogleTranslator

        try:
            supported = GoogleTranslator().get_supported_languages(as_dict=True)
            if target not in supported and target not in supported.values():
                for name, code in supported.items():
                    if target in name:
                        target = code
                        break
        except Exception:
            pass
    except ImportError:
        return text

    code_blocks = []

    def protect_code(m):
        code_blocks.append(m.group(0))
        return f"\n<PROTECTED_CODE_{len(code_blocks) - 1}>\n"

    inline_code = []

    def protect_inline(m):
        inline_code.append(m.group(0))
        return f"<PROTECTED_INLINE_{len(inline_code) - 1}>"

    math_blocks = []

    def protect_math(m):
        math_blocks.append(m.group(0))
        return f"\n<PROTECTED_MATH_{len(math_blocks) - 1}>\n"

    think_blocks = []

    def protect_think(m):
        think_blocks.append(m.group(0))
        return f"\n<PROTECTED_THINK_BLOCK_{len(think_blocks) - 1}>\n"

    temp = re.sub(r"```[\s\S]*?```", protect_code, text)
    temp = re.sub(r"\$\$[\s\S]*?\$\$", protect_math, temp)
    temp = re.sub(r"`[^`]+`", protect_inline, temp)

    temp = re.sub(r"<think>[\s\S]*?(?:</think>|$)", protect_think, temp)

    temp = re.sub(
        r"<([\x80-\xff][\w]*)>([\s\S]*?)</\1>",
        lambda m: (
            think_blocks.append(m.group(0)),
            f"\n<PROTECTED_THINK_BLOCK_{len(think_blocks) - 1}>\n",
        )[1],
        temp,
    )

    temp = re.sub(
        r"</?think>",
        lambda m: (
            think_blocks.append(m.group(0)),
            f"<PROTECTED_THINK_BLOCK_{len(think_blocks) - 1}>",
        )[1],
        temp,
        flags=re.IGNORECASE,
    )
    temp = re.sub(
        r"<\|?/?thought(?:_(?:start|end))?\|?>",
        lambda m: (
            think_blocks.append(m.group(0)),
            f"<PROTECTED_THINK_BLOCK_{len(think_blocks) - 1}>",
        )[1],
        temp,
        flags=re.IGNORECASE,
    )

    lines = temp.split("\n")
    translated_lines = []

    try:
        translator = GoogleTranslator(source="auto", target=target)

        current_chunk_lines = []
        current_chunk_len = 0

        def translate_current_chunk():
            if not current_chunk_lines:
                return []
            text_to_translate = "\n".join(current_chunk_lines)

            if not text_to_translate.strip():
                return current_chunk_lines

            try:
                translated_text = translator.translate(text_to_translate)

                if translated_text is None:
                    return current_chunk_lines
                return translated_text.split("\n")
            except Exception as e:
                import logging

                logging.getLogger("iris").warning(f"Chunk translation failed: {e}")
                return current_chunk_lines

        for line in lines:
            is_protected = line.strip().startswith("<PROTECTED_")

            if is_protected:
                if current_chunk_lines:
                    translated_lines.extend(translate_current_chunk())
                    current_chunk_lines = []
                    current_chunk_len = 0
                translated_lines.append(line)
            else:

                if current_chunk_len + len(line) > 4500 and current_chunk_lines:
                    translated_lines.extend(translate_current_chunk())
                    current_chunk_lines = []
                    current_chunk_len = 0

                current_chunk_lines.append(line)
                current_chunk_len += len(line) + 1

        if current_chunk_lines:
            translated_lines.extend(translate_current_chunk())

        final_text = "\n".join(translated_lines)
    except Exception as e:
        logger.warning(f"Translation failed: {e}")
        return text

    for i, code in enumerate(code_blocks):
        final_text = re.sub(
            rf"<PROTECTED_CODE_{i}>",
            lambda m, c=code: c.replace("\\", r"\\"),
            final_text,
        )
    for i, math in enumerate(math_blocks):
        final_text = re.sub(
            rf"<PROTECTED_MATH_{i}>",
            lambda m, c=math: c.replace("\\", r"\\"),
            final_text,
        )
    for i, inline in enumerate(inline_code):
        final_text = re.sub(
            rf"<PROTECTED_INLINE_{i}>",
            lambda m, c=inline: c.replace("\\", r"\\"),
            final_text,
        )
    for i, think in enumerate(think_blocks):
        final_text = re.sub(
            rf"<PROTECTED_THINK_BLOCK_{i}>",
            lambda m, c=think: c.replace("\\", r"\\"),
            final_text,
        )

    return final_text


def _stream_tokens(
    role: ModelRole,
    messages: List[Dict[str, str]],
    max_tokens: int = 0,
    temperature: float = 0.7,
    think_mode: str = "pass",
    system_prompt_override: Optional[str] = None,
    settings: Optional[dict] = None,
    extra_stop_words: Optional[List[str]] = None,
    skip_repetition_guard: bool = False,
) -> Generator[Dict[str, str], None, None]:
    global _keep_loaded

    if not isinstance(messages, list) or not all(
        isinstance(msg, dict) and "role" in msg and "content" in msg for msg in messages
    ):
        yield {
            "type": "token",
            "content": "\n\n> [ERROR] **Iris Error:** Invalid messages format passed to generator.",
        }
        return

    if not messages or not messages[-1]["content"].strip():
        yield {"type": "token", "content": "Please enter a valid query."}
        return

    llm = load_model(role)
    if not llm:
        yield {
            "type": "token",
            "content": f"\n\n> [ERROR] **Iris Error:** Failed to load model for role `{role.value}`. Check memory or installation.",
        }
        return

    sys_prompt = (
        system_prompt_override
        if system_prompt_override is not None
        else _system_prompt_for(role)
    )
    if (
        role not in (ModelRole.TRIAGE, ModelRole.ROUTER)
        and messages
        and messages[-1]["role"] == "user"
    ):
        sys_prompt += _language_directive(messages[-1]["content"], role=role)

    try:
        session_file = os.path.join(os.getcwd(), ".iris_session.json")
        if os.path.exists(session_file):
            with open(session_file, "r") as f:
                contract_data = f.read().strip()
            if contract_data and contract_data != "{}":
                sys_prompt += f"\n\n[SESSION CONTRACT / PERSISTENT STATE]:\n{contract_data}\nAdhere to the above session constraints across all tasks."
    except Exception as e:
        logger.warning(f"Failed to load session contract: {e}")

    if role == ModelRole.CODE:
        import datetime

        try:
            sys_prompt += f"\n\n(If you need the current year for a copyright line or similar, it is {datetime.datetime.now().year}.)"
        except Exception as e:
            logger.warning(f"Failed to inject year hint: {e}")
    elif role not in (ModelRole.TRIAGE, ModelRole.ROUTER):
        import datetime

        try:
            now = datetime.datetime.now().astimezone()
            time_str = now.strftime("%A, %B %d, %Y, %H:%M:%S %Z")
            offset_str = now.strftime("%z")
            formatted_offset = (
                f"{offset_str[:3]}:{offset_str[3:]}"
                if len(offset_str) >= 5
                else offset_str
            )
            sys_prompt += f"\n\nSystem Time Context: The current local time is {time_str} (UTC{formatted_offset}). Use this context to accurately answer any date or time-related queries."
        except Exception as e:
            logger.warning(f"Failed to inject local time directive: {e}")

    def _sanitize_for_role(
        msgs: List[Dict[str, str]], target_role: ModelRole
    ) -> List[Dict[str, str]]:
        clean = []
        for m in msgs:
            content = m.get("content", "")
            role_tag = m.get("role", "user")

            content = re.sub(
                r"<think>[\s\S]*?</think>", "", content, flags=re.IGNORECASE
            ).strip()
            content = re.sub(
                r"<\|thought_start\|>[\s\S]*?<\|thought_end\|>",
                "",
                content,
                flags=re.IGNORECASE,
            ).strip()
            content = re.sub(
                r"<thought>[\s\S]*?</thought>", "", content, flags=re.IGNORECASE
            ).strip()

            content = re.sub(r"\[SYSTEM DIRECTIVE:[^\]]*\]", "", content).strip()

            content = re.sub(
                r"^System Instructions:\n.*?\n\nUser Query:\n",
                "",
                content,
                flags=re.DOTALL,
            ).strip()
            if target_role == ModelRole.CODE:

                content = re.sub(
                    r"\\(?:boxed|frac|sqrt|text|mathrm|left|right)\{[^}]*\}",
                    "",
                    content,
                )
                content = re.sub(r"\$\$[\s\S]*?\$\$", "", content)
                content = re.sub(r"\$([^$\n]*)\$", r"\1", content)
                content = re.sub(r"_\{([^}]+)\}", r"_\1", content)
                content = re.sub(r"\^\{([^}]+)\}", "", content)
            elif target_role in (
                ModelRole.REASONING,
                ModelRole.GENERAL,
                ModelRole.MATH,
            ):

                def _compress_code(m):
                    lines = m.group(0).count("\n")
                    if lines > 10:
                        lang = m.group(0).split("\n")[0].replace("```", "").strip()
                        return f"```{lang}\n[{lines}-line code block from previous turn — omitted]\n```"
                    return m.group(0)

                content = re.sub(r"```[\s\S]*?```", _compress_code, content)
            if content.strip():
                clean.append({"role": role_tag, "content": content})
        return clean

    sanitized_messages = _sanitize_for_role(messages, role)

    full_messages = [{"role": "system", "content": sys_prompt}] + sanitized_messages

    from .patcher import apply_patch

    _PATCH_OPEN_TRIGGER_RE = re.compile(r"<{3,}|<search>", re.IGNORECASE)

    _PATCH_CLOSE_TRIGGER_RE = re.compile(r">{3,}|</replace>", re.IGNORECASE)

    _PATCH_OPEN_CANDIDATES = ["<<<", "<search>"]

    def _partial_open_suffix_len(buf: str) -> int:
        buf_lower = buf.lower()
        best = 0
        for cand in _PATCH_OPEN_CANDIDATES:
            for i in range(1, len(cand)):
                if buf_lower.endswith(cand[:i]) and i > best:
                    best = i
        return best

    base_code = ""
    base_lang = "python"
    if role == ModelRole.CODE:

        candidates = []
        for _msg in full_messages:
            if _msg.get("role") in ("assistant", "user"):
                _blocks = extract_code_blocks(_msg.get("content", ""))
                for lang, code in _blocks:
                    candidates.append((lang, code))
        if candidates:
            base_lang, base_code = max(candidates, key=lambda c: len(c[1]))

    in_patch = False
    patch_buffer = ""
    patches_applied_this_turn = 0
    patches_failed_this_turn = 0
    _MAX_PATCHES_PER_TURN = 25

    cfg = load_generation_config()
    model_cfg = cfg.get("model_settings", {}).get(role.value, {})

    actual_temp = temperature
    rep_penalty = 1.1
    freq_penalty = 0.3 if role in (ModelRole.CODE, ModelRole.REASONING) else 0.05
    pres_penalty = 0.3 if role in (ModelRole.CODE, ModelRole.REASONING) else 0.05
    top_p = 0.9
    top_k = 40

    _min_p_defaults = {
        ModelRole.TRIAGE: 0.1,
        ModelRole.CONTROL: 0.1,
        ModelRole.MATH: 0.1,
        ModelRole.CODE: 0.05,
        ModelRole.REVIEWER: 0.05,
        ModelRole.REASONING: 0.05,
        ModelRole.GENERAL: 0.03,
    }
    min_p = _min_p_defaults.get(role, 0.05)

    actual_temp = cfg.get("temperature", actual_temp)
    rep_penalty = cfg.get("repetition_penalty", rep_penalty)
    freq_penalty = cfg.get("frequency_penalty", freq_penalty)
    pres_penalty = cfg.get("presence_penalty", pres_penalty)
    top_p = cfg.get("top_p", top_p)
    top_k = cfg.get("top_k", top_k)
    max_tokens = max_tokens or cfg.get("max_new_tokens", 4096)
    repeat_last_n = cfg.get("repeat_last_n", 256)

    actual_temp = model_cfg.get("temperature", actual_temp)
    rep_penalty = model_cfg.get("repetition_penalty", rep_penalty)
    freq_penalty = model_cfg.get("frequency_penalty", freq_penalty)
    pres_penalty = model_cfg.get("presence_penalty", pres_penalty)
    top_p = model_cfg.get("top_p", top_p)
    top_k = model_cfg.get("top_k", top_k)
    repeat_last_n = model_cfg.get("repeat_last_n", repeat_last_n)

    if settings:
        actual_temp = settings.get("temperature", actual_temp)
        rep_penalty = settings.get("repetition_penalty", rep_penalty)

    if role == ModelRole.CODE and rep_penalty < 1.15:
        rep_penalty = 1.15

    THINK_PAIRS = [
        ("<think>", "</think>"),
        ("<|thought_start|>", "<|thought_end|>"),
        ("<thought>", "</thought>"),
    ]
    CLOSE_TAG_MAP = {open_tag: close_tag for open_tag, close_tag in THINK_PAIRS}

    model_name = _get_model_filename(role)

    in_thinking = False
    thinking_tag = ""
    hidden_buffer = ""

    _consecutive_empty_fences = 0

    for loop_idx in range(5):
        _reserved_tokens = (
            4096
            if role in (ModelRole.CODE, ModelRole.REASONING, ModelRole.REVIEWER)
            else 1024
        )

        _ca_cfg = load_generation_config().get("compressed_attention", {})
        if _ca_cfg.get("enabled", False) and len(full_messages) > 4:
            _query = messages[-1].get("content", "") if messages else ""
            _compressed = smart_compress(
                full_messages,
                query=_query,
                n_ctx=llm.n_ctx(),
                max_output_tokens=(
                    min(max_tokens, _reserved_tokens)
                    if max_tokens
                    else _reserved_tokens
                ),
                llm=llm,
                profile=load_generation_config().get("size", "tiny"),
            )
            if _compressed.compressed_tokens < _compressed.original_tokens:
                logger.info(
                    f"[CA] {_compressed.strategy_used.value}: "
                    f"{_compressed.original_tokens}→{_compressed.compressed_tokens} tokens "
                    f"({100 * (1 - _compressed.compressed_tokens / max(_compressed.original_tokens, 1)):.0f}% saved)"
                )
                full_messages = _compressed.messages

        full_messages, _ = auto_compact_for_role(
            full_messages,
            role=role,
            max_output_tokens=(
                min(max_tokens, _reserved_tokens) if max_tokens else _reserved_tokens
            ),
        )

        logger.debug(f"[Model Start] Role: {role.value.upper()} | Model: {model_name}")
        stop_list = [
            "</s>",
            "<|eot_id|>",
            "<|end_of_text|>",
            "<|im_end|>",
            "<step_end>",
            "## Conversation",
        ]
        if extra_stop_words:
            stop_list.extend(extra_stop_words)

        actual_max_tokens = None if max_tokens >= 4000 else max_tokens
        stream = llm.create_chat_completion(
            messages=full_messages,
            stream=True,
            max_tokens=actual_max_tokens,
            temperature=actual_temp,
            repeat_penalty=rep_penalty,
            frequency_penalty=freq_penalty,
            presence_penalty=pres_penalty,
            top_p=top_p,
            top_k=top_k,
            min_p=min_p,
            seed=42 + loop_idx,
            stop=stop_list,
        )
        loop_content = ""
        raw_turn_text = ""
        finish_reason = "stop"
        buffer = ""
        token_count = 0

        stripped_leading_fence = (
            False
            if (loop_idx > 0 and role in (ModelRole.CODE, ModelRole.REASONING))
            else True
        )
        continuation_buffer = ""

        for chunk in stream:
            choices = chunk.get("choices", [])
            if not choices:
                continue
            choice = choices[0]

            if "finish_reason" in choice and choice["finish_reason"]:
                finish_reason = choice["finish_reason"]

            token = choice.get("delta", {}).get("content", "")
            if not token:
                continue

            raw_turn_text += token

            token_count += 1

            if not stripped_leading_fence:
                continuation_buffer += token
                if (
                    len(continuation_buffer) >= 20
                    or "\n" in continuation_buffer
                    or (
                        len(continuation_buffer) >= 10
                        and "`" not in continuation_buffer
                    )
                ):
                    match = re.match(
                        r"^\s*```(?:html|python|py|javascript|js|css|sh|bash|json|markdown|md)?\s*",
                        continuation_buffer,
                        re.IGNORECASE,
                    )
                    if match:
                        logger.info(
                            f"[Continuation] Stripped leading code fence from loop {loop_idx}: {continuation_buffer[: match.end()]!r}"
                        )
                        continuation_buffer = continuation_buffer[match.end() :]
                        _consecutive_empty_fences += 1
                        if _consecutive_empty_fences >= 3:
                            logger.warning(
                                f"[Continuation] Model stripped empty fence {_consecutive_empty_fences} times in a row — stopping loop."
                            )
                            finish_reason = "stop"
                            break
                    else:
                        _consecutive_empty_fences = 0
                    stripped_leading_fence = True
                    token = continuation_buffer
                    continuation_buffer = ""
                else:
                    continue

            test_content = loop_content + buffer + token
            if (
                "<NEEDS_MATH_CHECK>" in test_content
                and "</NEEDS_MATH_CHECK>" in test_content
            ):
                start = test_content.find("<NEEDS_MATH_CHECK>")
                end = test_content.find("</NEEDS_MATH_CHECK>") + len(
                    "</NEEDS_MATH_CHECK>"
                )
                expr = test_content[
                    start + len("<NEEDS_MATH_CHECK>") : end - len("</NEEDS_MATH_CHECK>")
                ].strip()

                yield {"type": "status", "content": f"MATH Escape Hatch Triggered..."}
                logger.info(f"[Escape Hatch] Evaluating Math: {expr}")

                try:
                    from src.iris.iris.coding import generate_internal_code

                    math_res = generate_internal_code(
                        "Solve this mathematical expression accurately.",
                        expr,
                        role=ModelRole.MATH,
                    )
                except Exception as e:
                    math_res = f"Math Error: {e}"

                math_result_block = f"\n\n[MATH RESULT: {math_res}]\n\n"

                full_messages.append(
                    {
                        "role": "assistant",
                        "content": test_content[:end] + math_result_block,
                    }
                )
                full_messages.append(
                    {
                        "role": "user",
                        "content": "Continue generation based on the math result above.",
                    }
                )

                finish_reason = "escape_hatch"
                break

            if (
                not skip_repetition_guard
                and role != ModelRole.CODE
                and token_count % 20 == 0
                and len(loop_content) > 400
            ):
                recent = loop_content[-1500:]
                n = len(recent)
                is_repetition = False

                for l in range(200, n // 2 + 1):
                    suffix = recent[-l:]
                    if suffix in recent[:-l]:
                        logger.warning(
                            f"[Repetition Guard] Detected exact repetition loop of length {l}. Stopping generation early."
                        )
                        is_repetition = True
                        break

                if not is_repetition and len(recent) > 400:
                    words = recent.replace("\n", " ").split()
                    if len(words) > 30:
                        for i in range(len(words) - 8):
                            ngram = " ".join(words[i : i + 8]).lower()

                            if len(ngram) > 25 and recent.lower().count(ngram) >= 4:
                                logger.warning(
                                    f"[Repetition Guard] Detected semantic loop '{ngram}'. Stopping generation early."
                                )
                                is_repetition = True
                                break

                if not is_repetition and len(recent) > 800:
                    deliberation_phrases = [
                        "wait but",
                        "alternatively,",
                        "hmm.",
                        "on the other hand",
                        "wait,",
                    ]
                    for phrase in deliberation_phrases:
                        if recent.lower().count(phrase) >= 6:
                            logger.warning(
                                f"[Repetition Guard] Detected deliberation loop ('{phrase}'). Stopping generation early."
                            )
                            is_repetition = True
                            break

                if is_repetition:
                    finish_reason = "stop"
                    break

            if think_mode == "pass":
                yield {"type": "token", "content": token}
                loop_content += token
                continue

            buffer += token

            _open_match = (
                _PATCH_OPEN_TRIGGER_RE.search(buffer)
                if not in_patch and base_code
                else None
            )
            if _open_match:
                idx = _open_match.start()
                if idx > 0:
                    pre_patch_text = buffer[:idx]

                    pre_patch_text = re.sub(r"```\s*```", "", pre_patch_text)

                    fence_count = len(re.findall(r"```", pre_patch_text))
                    if fence_count % 2 != 0:
                        last_fence = pre_patch_text.rfind("```")
                        if last_fence != -1:
                            pre_patch_text = (
                                pre_patch_text[:last_fence]
                                + pre_patch_text[last_fence + 3 :]
                            )
                    pre_patch_text = pre_patch_text.strip()
                    if pre_patch_text:
                        yield {"type": "token", "content": pre_patch_text}
                        loop_content += pre_patch_text
                in_patch = True
                patch_buffer = buffer[idx:]
                buffer = ""
                continue

            if not in_patch and base_code:
                _hold_len = _partial_open_suffix_len(buffer)
                if _hold_len:

                    if len(buffer) > _hold_len:
                        yield {"type": "token", "content": buffer[:-_hold_len]}
                        loop_content += buffer[:-_hold_len]
                        buffer = buffer[-_hold_len:]
                    continue

            if in_patch:
                patch_buffer += token
                buffer = ""
                _close_matches = list(_PATCH_CLOSE_TRIGGER_RE.finditer(patch_buffer))
                if _close_matches:

                    idx = _close_matches[-1].end()

                    final_patch = patch_buffer[:idx]

                    leftover = patch_buffer[idx:]

                    old_code_before_block = base_code
                    outcome = apply_patch(base_code, final_patch)

                    base_code = outcome.code
                    patches_applied_this_turn += outcome.blocks_applied
                    patches_failed_this_turn += outcome.blocks_failed

                    for r in outcome.results:
                        if not r.applied:
                            yield {
                                "type": "text",
                                "content": f'An edit didn\'t apply ({r.reason}): "{r.search_preview}"',
                            }

                    code_changed = (
                        outcome.blocks_applied > 0
                        and outcome.code != old_code_before_block
                    )
                    if code_changed:
                        patched_output = f"\n```{base_lang}\n{outcome.code}\n```\n"

                        chunk_size = 50
                        for i in range(0, len(patched_output), chunk_size):
                            yield {
                                "type": "token",
                                "content": patched_output[i : i + chunk_size],
                            }
                        loop_content += patched_output
                    elif outcome.blocks_applied == 0 and outcome.blocks_failed > 0:

                        yield {
                            "type": "token",
                            "content": f"\n> ⚠️ Patch could not be applied — the lines the model tried to change weren't found in the current file. You may need to ask again with more context.\n\n",
                        }
                        loop_content += f"\n> ⚠️ Patch could not be applied — the lines the model tried to change weren't found in the current file.\n\n"
                    in_patch = False
                    patch_buffer = ""

                    if outcome.blocks_failed > 0 and outcome.blocks_applied == 0:
                        logger.warning(
                            f"[Patch] All {outcome.blocks_failed} block(s) failed to apply — stopping generation."
                        )
                        finish_reason = "stop"
                        break

                    if (
                        patches_applied_this_turn + patches_failed_this_turn
                        >= _MAX_PATCHES_PER_TURN
                    ):
                        logger.warning(
                            f"[Patch] Hit the {_MAX_PATCHES_PER_TURN}-patch safety cap for one turn; stopping."
                        )
                        finish_reason = "stop"
                        break

                    buffer = leftover

                    if buffer:
                        buffer = re.sub(r"```\s*```", "", buffer).strip()
                continue
            if think_mode == "hide":
                while True:
                    if not in_thinking:
                        found = False
                        for tag, close in THINK_PAIRS:
                            if tag in buffer:
                                idx = buffer.index(tag)
                                if idx > 0:
                                    yield {"type": "token", "content": buffer[:idx]}
                                    loop_content += buffer[:idx]
                                in_thinking = True
                                thinking_tag = tag
                                loop_content += tag
                                buffer = buffer[idx + len(tag) :]
                                found = True
                                break
                        if found:
                            continue
                        partial = False
                        for tag, close in THINK_PAIRS:
                            for i in range(1, len(tag)):
                                if buffer.endswith(tag[:i]):
                                    before = buffer[:-i]
                                    if before:
                                        yield {"type": "token", "content": before}
                                        loop_content += before
                                    buffer = buffer[-i:]
                                    partial = True
                                    break
                            if partial:
                                break
                        if partial:
                            break
                        yield {"type": "token", "content": buffer}
                        loop_content += buffer
                        buffer = ""
                        break
                    else:
                        close_tag = CLOSE_TAG_MAP.get(thinking_tag, "</think>")
                        if close_tag in buffer:
                            idx = buffer.index(close_tag)
                            loop_content += buffer[:idx] + close_tag
                            in_thinking = False
                            thinking_tag = ""
                            buffer = buffer[idx + len(close_tag) :]
                            hidden_buffer = ""
                            continue
                        partial = False
                        for i in range(1, len(close_tag)):
                            if buffer.endswith(close_tag[:i]):
                                hidden_buffer += buffer[:-i]
                                buffer = buffer[-i:]
                                partial = True
                                break
                        if partial:
                            break
                        hidden_buffer += buffer
                        loop_content += buffer
                        buffer = ""

                        if len(hidden_buffer) > 500000:
                            think_mode = "pass"
                            content_to_yield = (
                                f"{thinking_tag}\n{hidden_buffer}"
                                if thinking_tag
                                else hidden_buffer
                            )
                            yield {"type": "token", "content": content_to_yield}
                            loop_content += content_to_yield
                            hidden_buffer = ""
                            continue
                        break

            elif think_mode == "show":
                while True:
                    if not in_thinking:
                        found = False
                        for tag, close in THINK_PAIRS:
                            if tag in buffer:
                                idx = buffer.index(tag)
                                if idx > 0:
                                    yield {"type": "token", "content": buffer[:idx]}
                                    loop_content += buffer[:idx]
                                in_thinking = True
                                thinking_tag = tag
                                loop_content += tag
                                buffer = buffer[idx + len(tag) :]
                                found = True
                                break
                        if found:
                            continue
                        partial = False
                        for tag, close in THINK_PAIRS:
                            for i in range(1, len(tag)):
                                if buffer.endswith(tag[:i]):
                                    before = buffer[:-i]
                                    if before:
                                        yield {"type": "token", "content": before}
                                        loop_content += before
                                    buffer = buffer[-i:]
                                    partial = True
                                    break
                            if partial:
                                break
                        if partial:
                            break
                        yield {"type": "token", "content": buffer}
                        loop_content += buffer
                        buffer = ""
                        break
                    else:
                        close_tag = CLOSE_TAG_MAP.get(thinking_tag, "</think>")
                        if close_tag in buffer:
                            idx = buffer.index(close_tag)
                            thinking_text = buffer[:idx]
                            if thinking_text.strip():
                                yield {"type": "thinking", "content": thinking_text}
                            loop_content += thinking_text + close_tag
                            in_thinking = False
                            thinking_tag = ""
                            buffer = buffer[idx + len(close_tag) :]
                            continue
                        partial = False
                        for i in range(1, len(close_tag)):
                            if buffer.endswith(close_tag[:i]):
                                before = buffer[:-i]
                                if before.strip():
                                    yield {"type": "thinking", "content": before}
                                loop_content += before
                                buffer = buffer[-i:]
                                partial = True
                                break
                        if partial:
                            break
                        if buffer.strip():
                            yield {"type": "thinking", "content": buffer}
                        loop_content += buffer
                        buffer = ""
                        break

            elif think_mode == "status":
                while True:
                    if not in_thinking:
                        found = False
                        for tag, close in THINK_PAIRS:
                            if tag in buffer:
                                idx = buffer.index(tag)
                                if idx > 0:
                                    yield {"type": "token", "content": buffer[:idx]}
                                    loop_content += buffer[:idx]
                                yield {"type": "status", "content": "Thinking..."}
                                in_thinking = True
                                thinking_tag = tag
                                loop_content += tag
                                buffer = buffer[idx + len(tag) :]
                                found = True
                                break
                        if found:
                            continue
                        partial = False
                        for tag, close in THINK_PAIRS:
                            for i in range(1, len(tag)):
                                if buffer.endswith(tag[:i]):
                                    before = buffer[:-i]
                                    if before:
                                        yield {"type": "token", "content": before}
                                        loop_content += before
                                    buffer = buffer[-i:]
                                    partial = True
                                    break
                            if partial:
                                break
                        if partial:
                            break
                        yield {"type": "token", "content": buffer}
                        loop_content += buffer
                        buffer = ""
                        break
                    else:
                        close_tag = CLOSE_TAG_MAP.get(thinking_tag, "</think>")
                        if close_tag in buffer:
                            idx = buffer.index(close_tag)
                            loop_content += buffer[:idx] + close_tag
                            in_thinking = False
                            thinking_tag = ""
                            buffer = buffer[idx + len(close_tag) :]
                            continue
                        partial = False
                        for i in range(1, len(close_tag)):
                            if buffer.endswith(close_tag[:i]):
                                buffer = buffer[-i:]
                                partial = True
                                break
                        if partial:
                            break
                        loop_content += buffer
                        buffer = ""
                        break

            if "finish_reason" in choice and choice["finish_reason"]:
                finish_reason = choice["finish_reason"]

        if not stripped_leading_fence and continuation_buffer:
            match = re.match(
                r"^\s*```(?:html|python|py|javascript|js|css|sh|bash|json|markdown|md)?\s*",
                continuation_buffer,
                re.IGNORECASE,
            )
            if match:
                continuation_buffer = continuation_buffer[match.end() :]
            buffer += continuation_buffer
            stripped_leading_fence = True
            continuation_buffer = ""

        if in_patch and finish_reason != "length":

            old_code_before_final = base_code
            outcome = apply_patch(base_code, patch_buffer)
            base_code = outcome.code
            patches_applied_this_turn += outcome.blocks_applied
            patches_failed_this_turn += outcome.blocks_failed
            for r in outcome.results:
                if not r.applied:
                    yield {
                        "type": "text",
                        "content": f'An edit didn\'t apply ({r.reason}): "{r.search_preview}"',
                    }
            code_changed = (
                outcome.blocks_applied > 0 and outcome.code != old_code_before_final
            )
            if code_changed:
                patched_output = f"\n```{base_lang}\n{outcome.code}\n```\n"
                yield {"type": "token", "content": patched_output}
                loop_content += patched_output
            elif outcome.blocks_applied == 0 and outcome.blocks_failed > 0:
                yield {
                    "type": "token",
                    "content": "\n> ⚠️ Patch could not be applied.\n\n",
                }
                loop_content += "\n> ⚠️ Patch could not be applied.\n\n"
            in_patch = False
            patch_buffer = ""
            buffer = ""

        if buffer:
            if think_mode == "hide" and in_thinking:
                pass
            elif think_mode == "status" and in_thinking:
                pass
            elif think_mode == "show" and in_thinking:
                if buffer.strip():
                    yield {"type": "thinking", "content": buffer}
                loop_content += buffer
            else:
                yield {"type": "token", "content": buffer}
                loop_content += buffer

        if finish_reason == "stop":
            looks_incomplete = False
            prompt_est = sum(len(m.get("content", "")) for m in full_messages) // 4
            if in_thinking:

                close_tag = CLOSE_TAG_MAP.get(thinking_tag, "</think>")
                synthetic_close = f"\n{close_tag}"
                yield {"type": "thinking", "content": synthetic_close}
                loop_content += synthetic_close
                in_thinking = False

            elif loop_content.count("```") % 2 != 0:
                looks_incomplete = True

            logger.debug(
                f"DEBUG LOOP CONTENT END: {repr(loop_content[-20:])} | Incomplete? {looks_incomplete}"
            )

            if looks_incomplete:
                finish_reason = "length"
            elif role == ModelRole.CODE:
                try:
                    from src.iris.iris.pro import verify_code_syntax

                    blocks = re.findall(r"```(\w*)\n(.*?)```", loop_content, re.DOTALL)
                    if blocks and patches_failed_this_turn == 0:
                        lang, code = blocks[-1]
                        err = verify_code_syntax(code, lang)
                        if err is not None:
                            logger.warning(
                                f"Syntax verification failed in normal mode: {err}"
                            )
                            yield {
                                "type": "status",
                                "content": "Fixing syntax errors...",
                            }
                            yield {"type": "clear"}
                            full_messages.append(
                                {"role": "assistant", "content": loop_content}
                            )
                            full_messages.append(
                                {
                                    "role": "user",
                                    "content": f"The following code you generated has a syntax error:\n\n```\n{err}\n```\n\nCode:\n```\n{code}\n```\n\nFix the error immediately and output the complete, corrected code.",
                                }
                            )
                            finish_reason = "error_fix"
                except Exception as exc:
                    logger.error(f"Error during syntax verification: {exc}")

        if finish_reason != "error_fix":
            yield {"type": "finish", "reason": finish_reason}

        if finish_reason == "length":

            source_text = raw_turn_text if raw_turn_text else loop_content
            content_to_keep = (
                source_text[-6000:] if len(source_text) > 6000 else source_text
            )
            prefix = "...[TRUNCATED]...\n" if len(source_text) > 6000 else ""
            full_messages.append(
                {"role": "assistant", "content": prefix + content_to_keep}
            )
            continue_note = (
                "Continue exactly where you left off, from the very next character. "
                "Do not repeat anything."
            )
            if in_patch:
                continue_note += (
                    " You were in the middle of a SEARCH/REPLACE block — continue "
                    "that exact block (do not restart it or open a new one) until you "
                    "reach its '====' separator and/or closing '>>>>' marker."
                )
            full_messages.append({"role": "user", "content": continue_note})
        elif finish_reason in ("error_fix", "escape_hatch"):
            continue
        else:
            break

    yield {
        "type": "patch_summary",
        "attempted": role == ModelRole.CODE and bool(base_code),
        "applied": patches_applied_this_turn,
        "failed": patches_failed_this_turn,
    }


_gen_config_cache: dict | None = None
_gen_config_mtime: float | None = None


def load_generation_config() -> dict:
    global _gen_config_cache, _gen_config_mtime
    defaults = {
        "max_new_tokens": 2048,
        "temperature": 0.6,
        "top_p": 0.95,
        "repetition_penalty": 1.05,
        "disable_rag": False,
        "n_ctx": None,
        "n_gpu_layers": DEFAULT_GPU_LAYERS,
        "n_threads": DEFAULT_THREADS,
        "models": dict(DEFAULT_MODEL_FILES),
    }
    if os.path.exists(CONFIG_PATH):
        try:
            mtime = os.path.getmtime(CONFIG_PATH)
            if _gen_config_cache is None or mtime != _gen_config_mtime:
                with open(CONFIG_PATH) as f:
                    loaded = json.load(f)
                    merged_models = {
                        **defaults.get("models", {}),
                        **loaded.pop("models", {}),
                    }
                    _gen_config_cache = {**defaults, **loaded}
                    _gen_config_cache["models"] = merged_models
                    apply_to_config(_gen_config_cache)
                _gen_config_mtime = mtime
            return _gen_config_cache
        except Exception:
            pass
    apply_to_config(defaults)
    return defaults


class _Device:
    def __init__(self, type_: str):
        self.type = type_

    def __repr__(self):
        return f"device(type='{self.type}')"


def get_device(force_cpu=False):
    return _Device("cpu" if force_cpu else "gpu")


def detect_user_language(text: str) -> Optional[str]:
    if not text or not text.strip():
        return None

    import re

    if len(text) < 50 and any(op in text for op in "+-=/*^()[]{}<>_"):

        if all(ord(c) < 128 for c in text) and not re.search(r"[a-zA-Z]{6,}", text):
            return "English"

    try:
        import requests
        from deep_translator import GoogleTranslator

        url = "https://translate.googleapis.com/translate_a/single"
        params = {
            "client": "gtx",
            "sl": "auto",
            "tl": "en",
            "dt": "t",
            "q": text[:500],
        }
        resp = requests.get(url, params=params, timeout=3.0)
        if resp.ok:
            data = resp.json()
            detected_code = data[2]
            if detected_code:
                detected_code = detected_code.lower()
                langs = GoogleTranslator().get_supported_languages(as_dict=True)
                code_to_name = {
                    code.lower(): name.title() for name, code in langs.items()
                }

                code_to_name["zh-cn"] = "Chinese"
                code_to_name["zh-tw"] = "Chinese"
                code_to_name["iw"] = "Hebrew"

                lang_name = code_to_name.get(detected_code)
                if lang_name:
                    logger.info(
                        f"[Iris] Online language detection: detected '{detected_code}' -> '{lang_name}'"
                    )
                    return lang_name
    except Exception as e:
        logger.debug(f"[Iris] Online language detection failed: {e}")

    sample = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)
    sample = re.sub(r"https?://\S+", " ", sample)

    counts: Dict[str, int] = {}
    for ch in sample:
        cp = ord(ch)
        if 0x0600 <= cp <= 0x06FF or 0x0750 <= cp <= 0x077F or 0x08A0 <= cp <= 0x08FF:
            counts["Arabic"] = counts.get("Arabic", 0) + 1
        elif 0x0400 <= cp <= 0x04FF:
            counts["Russian"] = counts.get("Russian", 0) + 1
        elif 0x4E00 <= cp <= 0x9FFF:
            counts["Chinese"] = counts.get("Chinese", 0) + 1
        elif 0x3040 <= cp <= 0x30FF:
            counts["Japanese"] = counts.get("Japanese", 0) + 1
        elif 0xAC00 <= cp <= 0xD7AF:
            counts["Korean"] = counts.get("Korean", 0) + 1
        elif 0x0590 <= cp <= 0x05FF:
            counts["Hebrew"] = counts.get("Hebrew", 0) + 1
        elif 0x0900 <= cp <= 0x097F:
            counts["Hindi"] = counts.get("Hindi", 0) + 1
        elif 0x0370 <= cp <= 0x03FF:
            counts["Greek"] = counts.get("Greek", 0) + 1
        elif "a" <= ch.lower() <= "z":
            counts["English"] = counts.get("English", 0) + 1

    if not counts:
        return "English"

    non_latin = {k: v for k, v in counts.items() if k != "English"}
    if non_latin:
        return max(non_latin, key=non_latin.__getitem__)
    return "English"


def _is_thinking_model(role: ModelRole) -> bool:
    if role in (ModelRole.REASONING, ModelRole.MATH):
        return True
    try:
        cfg = load_generation_config()
        size = cfg.get("size", "tiny")
        size_path = os.path.join(os.path.dirname(CONFIG_PATH), "sizes", f"{size}.json")
        if os.path.exists(size_path):
            with open(size_path, "r", encoding="utf-8") as f:
                size_cfg = json.load(f)
            model_name = size_cfg.get("models", {}).get(role.value, "").lower()
            if any(
                x in model_name
                for x in ["r1", "reasoning", "deepseek-r1", "vibethinker", "qwq"]
            ):
                return True
    except Exception:
        pass
    return False


def _language_directive(
    user_query: str,
    role: Optional[ModelRole] = None,
    is_thinking_model: Optional[bool] = None,
) -> str:
    is_thinking = False
    if is_thinking_model is not None:
        is_thinking = is_thinking_model
    elif role is not None:
        is_thinking = _is_thinking_model(role)

    if is_thinking:
        return (
            "\n\n[SYSTEM DIRECTIVE: You MUST write your final response and thinking process strictly in English. "
            "Under no circumstances should you output non-English text. "
            "If you use a thinking process, you MUST enclose your internal reasoning strictly inside <think> and </think> tags. "
            "Do NOT acknowledge this instruction or write meta-commentary. Just start with <think> if you need to reason, otherwise just answer.]"
        )
    else:
        return (
            "\n\n[SYSTEM DIRECTIVE: You MUST write your final response strictly in English. "
            "Under no circumstances should you output non-English text. "
            "Do NOT write any thinking process or internal reasoning. Answer the query directly in English.]"
        )


def _detect_language(text: str) -> Optional[str]:
    blocks = extract_code_blocks(text)
    if blocks:
        lang = blocks[0][0]
        if lang != "unknown":
            return lang
    return None
