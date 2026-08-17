import os
import sys
import csv
import re
import time
import asyncio
import logging
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import benchmark.utils
from src.iris.pro import ask_stream

_latest_metrics = {"ttft": 0.0, "speed": 0.0}
_hop_log_lines: list[str] = []

_HOP_RE = re.compile(
    r"HOP\s+(\S+)\s+\|\s+model=(\S+)\s+\|\s+tokens=\[prompt=(\d+),\s*completion=(\d+),\s*total=(\d+)\]"
)


class _HopCapture(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        msg = self.format(record)
        if "HOP" in msg and "tokens=" in msg:
            _hop_log_lines.append(msg)


_hop_handler = _HopCapture()
logging.getLogger("iris_ai").addHandler(_hop_handler)


def _print_hop_token_table(hop_lines: list[str]) -> None:
    rows = []
    for line in hop_lines:
        m = _HOP_RE.search(line)
        if m:
            rows.append({
                "stage": m.group(1),
                "model": m.group(2),
                "prompt": int(m.group(3)),
                "completion": int(m.group(4)),
                "total": int(m.group(5)),
            })
    if not rows:
        return

    col_w = {"stage": 28, "model": 36, "prompt": 10, "completion": 12, "total": 8}
    header = (
        f"  {'Stage':<{col_w['stage']}} "
        f"{'Model':<{col_w['model']}} "
        f"{'Prompt':>{col_w['prompt']}} "
        f"{'Completion':>{col_w['completion']}} "
        f"{'Total':>{col_w['total']}}"
    )
    sep = "  " + "-" * (sum(col_w.values()) + len(col_w) - 1)
    print(sep)
    print(header)
    print(sep)
    total_p = total_c = total_t = 0
    for r in rows:
        print(
            f"  {r['stage']:<{col_w['stage']}} "
            f"{r['model']:<{col_w['model']}} "
            f"{r['prompt']:>{col_w['prompt']},} "
            f"{r['completion']:>{col_w['completion']},} "
            f"{r['total']:>{col_w['total']},}"
        )
        total_p += r["prompt"]
        total_c += r["completion"]
        total_t += r["total"]
    print(sep)
    print(
        f"  {'TOTAL':<{col_w['stage']}} "
        f"{'':<{col_w['model']}} "
        f"{total_p:>{col_w['prompt']},} "
        f"{total_c:>{col_w['completion']},} "
        f"{total_t:>{col_w['total']},}"
    )
    print(sep)


def run_inference_pro(prompt: str, role=None, use_routing=True, keep_loaded=False, verify_math=False) -> tuple[str, float]:
    start_t = time.time()
    full_response = ""
    ttft = 0.0
    tokens = 0

    _hop_log_lines.clear()

    async def _run():
        nonlocal full_response, ttft, tokens
        try:
            agen = ask_stream(prompt, [], mode="smart", workspace_root=os.getcwd())
            async for event in agen:
                if event["type"] == "token":
                    if tokens == 0:
                        ttft = time.time() - start_t
                    tokens += 1
                    full_response += event["content"]
        except Exception as e:
            full_response = f"ERROR: {e}"

    asyncio.run(_run())

    end_t = time.time()

    if verify_math and full_response and "ERROR" not in full_response:
        try:
            from benchmark.verify_math import verify_and_refine
            full_response, was_fixed = verify_and_refine(full_response, prompt, keep_loaded=keep_loaded)
            if was_fixed:
                end_t = time.time()
        except Exception as e:
            print(f"[MathVerifier Error] {e}")

    elapsed = round(end_t - start_t, 2)
    decoding_speed = tokens / (elapsed - ttft) if (elapsed - ttft) > 0 else 0.0
    _latest_metrics["ttft"] = ttft
    _latest_metrics["speed"] = decoding_speed

    _print_hop_token_table(list(_hop_log_lines))

    return full_response, elapsed


benchmark.utils.run_inference = run_inference_pro

original_append = benchmark.utils.append_to_csv
def patched_append(csv_path, row_dict, fieldnames):
    if "TTFT" not in fieldnames:
         fieldnames.extend(["TTFT", "Speed"])
    row_dict["TTFT"] = round(_latest_metrics["ttft"], 2)
    row_dict["Speed"] = round(_latest_metrics["speed"], 2)
    original_append(csv_path, row_dict, fieldnames)
benchmark.utils.append_to_csv = patched_append

from benchmark.test_gsm8k   import run_gsm8k_benchmark
from benchmark.test_math   import run_math_benchmark
from benchmark.test_coding import run_coding_benchmark
from benchmark.test_mmlu   import run_mmlu_benchmark
from benchmark.test_gpqa   import run_gpqa_benchmark
from benchmark.test_swebench import run_swebench_benchmark
from benchmark.utils import write_summary_csv

def compute_summary_stats(csv_path: str) -> dict:
    summary = {}
    try:
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                bench = row.get("Benchmark", "unknown").split("-")[0]
                role  = row.get("Role", "Pro")
                key   = f"{bench} [{role}]"
                if key not in summary:
                    summary[key] = {"latencies": [], "ttfts": [], "speeds": []}

                try:
                    lat = float(row.get("Time_Sec", 0.0))
                    summary[key]["latencies"].append(lat)
                except ValueError:
                    pass

                try:
                    ttft = float(row.get("TTFT", 0.0))
                    summary[key]["ttfts"].append(ttft)
                except ValueError:
                    pass

                try:
                    speed = float(row.get("Speed", 0.0))
                    summary[key]["speeds"].append(speed)
                except ValueError:
                    pass

    except Exception as e:
        print(f"Error reading stats: {e}")

    return summary

def generate_ieee_report(summary: dict):
    report = "| Pipeline Stage / Task Type | Routed Model Baseline | Target Workload / Task Scope | TTFT (TTTFT) | Decoding Speed | Avg Hop Latency (Lavg) | P95 Latency (LP95) |\n"
    report += "|----------------------------|-----------------------|------------------------------|--------------|----------------|------------------------|--------------------|\\n"

    for key, data in sorted(summary.items()):
        lats = data["latencies"]
        ttfts = data["ttfts"]
        speeds = data["speeds"]

        avg_ttft = np.mean(ttfts) if ttfts else 0.0
        avg_speed = np.mean(speeds) if speeds else 0.0
        avg_lat = np.mean(lats) if lats else 0.0
        p95_lat = np.percentile(lats, 95) if lats else 0.0

        if "GSM" in key or "MATH" in key:
            stage = "Math Expert"
        elif "Human" in key or "SWE" in key:
            stage = "Coding Expert"
        else:
            stage = "Knowledge Retrieval"

        workload = key.split(" ")[0]

        report += f"| {stage:<26} | {'Iris Pro':<21} | {workload:<28} | {avg_ttft:>12.2f} | {avg_speed:>14.2f} | {avg_lat:>22.2f} | {p95_lat:>18.2f} |\n"

    with open("outputs/ieee_report_iris_pro.md", "w", encoding="utf-8") as f:
        f.write(report)

    print("\n" + "="*80)
    print("  IEEE REPORT GENERATED: outputs/ieee_report_iris_pro.md")
    print("="*80 + "\n")
    print(report)


def main():
    os.makedirs("outputs", exist_ok=True)
    raw_csv = "outputs/raw_iris_pro.csv"
    summary_csv = "outputs/benchmark_iris_pro.csv"

    if os.path.exists(raw_csv):
        os.remove(raw_csv)

    print("\n" + "="*80)
    print("  IRIS PRO — IEEE BENCHMARK EVALUATION")
    print("="*80)

    import benchmark.test_coding
    import benchmark.test_swebench
    import benchmark.test_gsm8k
    import benchmark.test_math
    import benchmark.test_mmlu
    import benchmark.test_gpqa

    benchmarks = [
        (run_coding_benchmark, None),
        (run_swebench_benchmark, None),
        (run_gsm8k_benchmark, None),
        (run_math_benchmark, None),
        (run_mmlu_benchmark, None),
        (run_gpqa_benchmark, None),
    ]

    try:
        for i, (benchmark_func, num_samples) in enumerate(benchmarks):
            print(f"\\n--- Running Benchmark {i+1}/{len(benchmarks)}: {benchmark_func.__name__} ---")
            if num_samples is not None:
                benchmark_func(raw_csv, num_samples=num_samples)
            else:
                benchmark_func(raw_csv)
    except KeyboardInterrupt:
        print("\n\n[!] Benchmark suite interrupted by user. Generating partial report...")
    finally:
        summary = compute_summary_stats(raw_csv)
        generate_ieee_report(summary)

if __name__ == "__main__":
    main()
