import sys
import os
import csv
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.iris import ask_stream, ModelRole

def run_inference(prompt: str, role: ModelRole = None, use_routing: bool = True, keep_loaded: bool = False, verify_math: bool = False) -> tuple[str, float]:
    history = []
    start_t = time.time()
    
    full_response = ""
    try:
        f_role = None if use_routing else role
        for event in ask_stream(prompt, history, force_role=f_role, keep_loaded=keep_loaded):
            if event["type"] == "raw_response":
                full_response = event["content"]
                break
            elif event["type"] == "token":
                full_response += event["content"]
    except FileNotFoundError as e:
        full_response = f"ERROR: Model file missing ({e})"
    except Exception as e:
        full_response = f"ERROR: {e}"
            
    end_t = time.time()
    elapsed = round(end_t - start_t, 2)
    
    
    if verify_math and full_response and "ERROR" not in full_response:
        from benchmark.verify_math import verify_and_refine
        full_response, was_fixed = verify_and_refine(full_response, prompt, keep_loaded=keep_loaded)
        if was_fixed:
            elapsed = round(time.time() - start_t, 2)
    
    return full_response, elapsed

def run_inference_sc(
    prompt: str,
    role: ModelRole,
    extract_fn,
    n: int = 3,
    keep_loaded: bool = True,
) -> tuple[str, str | None, float]:
    
    from collections import Counter
    start_t = time.time()
    responses = []
    answers   = []
    
    for _ in range(n):
        resp, _ = run_inference(prompt, role=role, use_routing=False, keep_loaded=keep_loaded)
        ans = extract_fn(resp)
        responses.append(resp)
        answers.append(ans)
    
    
    valid = [a for a in answers if a is not None]
    if valid:
        majority, _ = Counter(valid).most_common(1)[0]
        
        for resp, ans in zip(responses, answers):
            if ans == majority:
                return resp, majority, round(time.time() - start_t, 2)
    
    
    return responses[-1], answers[-1], round(time.time() - start_t, 2)


def append_to_csv(csv_path: str, row_dict: dict, fieldnames: list[str]):
    file_exists = os.path.exists(csv_path)
    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row_dict)

def get_size_name() -> str:
    from src.iris import load_generation_config
    cfg = load_generation_config()
    size_name = cfg.get("size", "unknown")
    if size_name == "unknown":
        desc = cfg.get("_description", "")
        if "—" in desc:
            parts = desc.split("—")
            if len(parts) > 1:
                size_name = parts[1].strip().split()[0].lower()
    return size_name

def write_summary_csv(raw_csv_path: str, summary_csv_path: str):
    summary = {}
    try:
        with open(raw_csv_path, newline="", encoding="utf-8") as f:
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

    with open(summary_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Benchmark", "Passed", "Total", "Percentage"])
        for key, counts in sorted(summary.items()):
            p = counts["passed"]
            t = counts["total"]
            pct = round((p / t * 100), 1) if t else 0
            writer.writerow([key, p, t, f"{pct}%"])
