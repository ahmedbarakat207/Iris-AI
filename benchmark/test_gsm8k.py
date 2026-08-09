\
\
\
\
\
   

import re
import random
import sys
import os
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from benchmark.utils import run_inference, run_inference_sc, append_to_csv
from benchmark.compare import match, match_with_verifier, fix_common_format_issues
from benchmark.auto_correct import auto_correct_math_answer
from benchmark.verify_math import verify_and_refine
from src.iris import ModelRole

FIELDNAMES = ["Benchmark", "Role", "Prompt", "Expected", "Model_Answer", "Passed", "Time_Sec"]

def _extract_gsm8k_answer(text: str) -> str | None:
                                                                       
    m = re.search(r"####\s*(\-?\d+[\d,\.]*)", text)
    if m:
        return m.group(1).replace(",", "").strip()
    return None

def _extract_boxed_content(text: str) -> str | None:
                                                                                                
    idx = text.rfind(r"\boxed{")
    if idx == -1:
        idx = text.rfind(r"boxed{")
        if idx == -1:
            return None
        start = idx + 6
    else:
        start = idx + 7
    
    braces = 1
    content = []
    for char in text[start:]:
        if char == "{":
            braces += 1
        elif char == "}":
            braces -= 1
        
        if braces == 0:
            break
        content.append(char)
        
    if braces == 0:
        return "".join(content).strip()
    return None

def _extract_model_answer(response: str) -> str | None:
\
\
\
\
\
\
\
\
       
    boxed = _extract_boxed_content(response)
    if boxed:
                                                        
        nums = re.findall(r"([\-]?\d[\d,\.]*)", boxed)
        if nums:
            return nums[-1].replace(",", "").strip()

    m = re.search(r"####\s*(\-?\d+[\d,\.]*)", response)
    if m:
        return m.group(1).replace(",", "").strip()
    m = re.search(r"(?:answer(?:\s+is)?|result(?:\s+is)?)\s*[:\-]?\s*(\-?\d+[\d,\.]*)", response, re.IGNORECASE)
    if m:
        return m.group(1).replace(",", "").strip()
    m = re.search(r"\*{1,2}(\-?\d+[\d,\.]*)\*{1,2}\s*$", response.strip())
    if m:
        return m.group(1).replace(",", "").strip()
    nums = re.findall(r"\b([\-]?\d[\d,\.]*)\b", response)
    if nums:
        return nums[-1].replace(",", "").strip()
    return None

def run_gsm8k_benchmark(csv_path: str, num_samples: int = 100):
    try:
        from datasets import load_dataset
        ds = load_dataset("openai/gsm8k", "main", split="test")
        items = list(ds)
        random.shuffle(items)
        if num_samples > 0:
            items = items[:num_samples]
        print(f"[GSM8K] Loaded {len(items)} questions from HuggingFace.")
    except Exception as e:
        print(f"[GSM8K] Could not load dataset: {e}. Falling back to built-in questions.")
        items = [
            {"question": "What is 15 + 27?",                                          "answer": "#### 42"},
            {"question": "A train travels 60 mph for 2 hours. How far does it go?",   "answer": "#### 120"},
            {"question": "Solve for x: 3x - 5 = 10",                                  "answer": "#### 5"},
            {"question": "What is the square root of 144?",                            "answer": "#### 12"},
            {"question": "If you have 3 apples and eat 1, how many are left?",         "answer": "#### 2"},
        ]

    print(f"\n{'='*50}")
    print(f" [GSM8K] Evaluating Iris Tiny  ({len(items)} questions)")
    print(f"{'='*50}")
    passed_count = 0

    for i, item in enumerate(items, 1):
        question      = item["question"]
        ground_truth  = _extract_gsm8k_answer(item["answer"])
        math_prompt = (
            f"Solve the following math problem step by step. "
            f"At the very end, write your final answer in LaTeX inside a \\boxed{{}} block "
            f"(e.g., \\boxed{{42}}).\\n\\nProblem: {question}"
        )
        response, model_answer, t = run_inference_sc(
            math_prompt,
            role=ModelRole.MATH,
            extract_fn=_extract_model_answer,
            n=3,
            keep_loaded=True,
        )


        # Formatting-only cleanup of the model's own answer. No ground truth
        # is passed in here — this cannot nudge the answer toward correct.
        if model_answer is not None:
            corrected, was_fixed, log = auto_correct_math_answer(
                problem=question,
                model_raw_output=response,
            )
            if was_fixed:
                model_answer = corrected

                                         
        passed = False
        reason = ""
        if model_answer is not None and ground_truth is not None:
            passed, reason = match_with_verifier(
                ground_truth, model_answer,
                problem=question[:200],
            )
        if passed:
            passed_count += 1

        print(f"  [{i:02d}/{len(items)}] Expected: {ground_truth} | Got: {model_answer} | {'✓' if passed else '✗'} ({t}s)")

        append_to_csv(csv_path, {
            "Benchmark":    "GSM8K",
            "Role":         "Iris Tiny",
            "Prompt":       question,
            "Expected":     ground_truth,
            "Model_Answer": model_answer,
            "Passed":       passed,
            "Time_Sec":     t,
        }, FIELDNAMES)

                                                                     
    try:
        from src.iris import unload_model
        unload_model()
    except Exception:
        pass

    pct = (passed_count / len(items)) * 100 if items else 0
    print(f"\n  [GSM8K][Iris Tiny] Score: {passed_count}/{len(items)} ({pct:.1f}%)\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GSM8K benchmark")
    parser.add_argument("--samples", type=int, default=100, help="Number of questions to evaluate (default: 100). Use 0 for all.")
    args = parser.parse_args()

    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "outputs")
    os.makedirs(out_dir, exist_ok=True)
    
    from benchmark.utils import get_size_name, write_summary_csv
    size_name = get_size_name()
    raw_csv = os.path.join(out_dir, f"raw_{size_name}.csv")
    summary_csv = os.path.join(out_dir, f"benchmark_{size_name}.csv")
    
    run_gsm8k_benchmark(raw_csv, num_samples=args.samples)
    write_summary_csv(raw_csv, summary_csv)
    print(f"  Summary updated at: {os.path.abspath(summary_csv)}")
