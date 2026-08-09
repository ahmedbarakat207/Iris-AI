

import os
import sys
import csv
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from benchmark.test_gsm8k   import run_gsm8k_benchmark
from benchmark.test_math   import run_math_benchmark
from benchmark.test_coding import run_coding_benchmark
from benchmark.test_mmlu   import run_mmlu_benchmark
from benchmark.test_gpqa   import run_gpqa_benchmark
from benchmark.test_swebench import run_swebench_benchmark
from benchmark.utils import get_size_name, write_summary_csv

def compute_summary(csv_path: str) -> dict[str, dict]:
    
    summary: dict[str, dict] = {}
    try:
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                bench = row.get("Benchmark", "unknown").split("-")[0]
                role  = row.get("Role", "")
                key   = f"{bench} [{role}]"
                if key not in summary:
                    summary[key] = {"passed": 0, "total": 0}
                summary[key]["total"] += 1
                if str(row.get("Passed", "")).lower() in ("true", "1"):
                    summary[key]["passed"] += 1
    except Exception:
        pass
    return summary

def print_summary(summary: dict[str, dict]):
    print("\n" + "="*60)
    print("  BENCHMARK SUMMARY")
    print("="*60)  
    print(f"  {'Benchmark + Role':<35} {'Score':>8}  {'%':>6}")
    print("  " + "-"*52)
    for key, counts in sorted(summary.items()):
        p = counts["passed"]
        t = counts["total"]
        pct = (p / t * 100) if t else 0
        bar = "✓" * int(pct // 10) + "·" * (10 - int(pct // 10))
        print(f"  {key:<35} {p:>3}/{t:<3}  {pct:>5.1f}%  [{bar}]")
    print("="*60 + "\n")
    
    print("  Comparison engine: SmartAnswerMatcher (numeric → LaTeX → sympy → MathVerifier)")
    print("  Auto-correction:    Hermes-level format fix + sandbox re-computation")
    print()

def main():
    os.makedirs("outputs", exist_ok=True)
    
    size_name = get_size_name()
    raw_csv = f"outputs/raw_{size_name}.csv"
    summary_csv = f"outputs/benchmark_{size_name}.csv"

    if os.path.exists(raw_csv):
        os.remove(raw_csv)

    print("\n" + "="*60)
    print(f"  IRIS AI — BENCHMARK SUITE ({size_name.upper()})")
    print("="*60)
    print(f"  Benchmarks : GSM8K · MATH · HumanEval · MMLU · GPQA · SWE-Bench")
    print(f"  Raw Output : {raw_csv}")
    print(f"  Summary    : {summary_csv}")
    print("="*60 + "\n")

    total_start = time.time()

    benchmarks = [
        run_gsm8k_benchmark,
        run_math_benchmark,
        run_coding_benchmark,
        run_mmlu_benchmark,
        run_gpqa_benchmark,
        run_swebench_benchmark,
    ]

    try:
        for benchmark_func in benchmarks:
            benchmark_func(raw_csv)
            
            summary = compute_summary(raw_csv)
            write_summary_csv(raw_csv, summary_csv)
    except KeyboardInterrupt:
        print("\n\n[!] Benchmark suite interrupted by user. Saving partial summary...")
    finally:
        elapsed = round(time.time() - total_start, 1)

        summary = compute_summary(raw_csv)
        print_summary(summary)
        
        write_summary_csv(raw_csv, summary_csv)

        print(f"  Total time: {elapsed}s")
        print(f"  Summary results saved to: {os.path.abspath(summary_csv)}\n")

    try:
        from src.iris import unload_model
        unload_model()
    except Exception:
        pass

if __name__ == "__main__":
    main()
