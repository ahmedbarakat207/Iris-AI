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
from src.iris import ModelRole

FIELDNAMES = ["Benchmark", "Role", "Prompt", "Expected", "Model_Answer", "Passed", "Time_Sec"]

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

def _clean_math_answer(answer: str | None) -> str:
                                                                                    
    if answer is None:
        return ""
                       
    answer = re.sub(r"\s+", "", answer)
                         
    answer = answer.replace("$", "")
    
    answer = answer.lower()
    
                                       
    answer = re.sub(r"^[a-z]=", "", answer)
    
                                                     
    answer = re.sub(r"^[a-z]\\in", "", answer)
    
                                                            
    answer = re.sub(r"_\{([^}]+)\}", r"_\1", answer)
    
    return answer.strip()

def run_math_benchmark(csv_path: str, num_samples: int = 100):
    items = []
    dataset_options = [
        ("HuggingFaceH4/MATH-500", "test"),
        ("lighteval/MATH-500", "test"),
        ("competition_math", "test"),
    ]
    
    for repo, split in dataset_options:
        try:
            from datasets import load_dataset
            ds = load_dataset(repo, split=split)
            items = list(ds)
            random.shuffle(items)
            if num_samples > 0:
                items = items[:num_samples]
            print(f"[MATH] Loaded {len(items)} questions from HF dataset: {repo}.")
            break
        except Exception as e:
            print(f"[MATH] Could not load {repo}: {e}")

    if not items:
        print("[MATH] Falling back to local built-in competition math problems.")
        items = [
            {
                "problem": "Find the sum of all real numbers x such that x^2 - 5x + 6 = 0.",
                "solution": "The equation factors as (x-2)(x-3) = 0, so the roots are 2 and 3. The sum is 2+3=5. The answer is \\boxed{5}."
            },
            {
                "problem": "What is the value of 1 - 2 + 3 - 4 + ... + 99 - 100?",
                "solution": "Grouping in pairs: (1-2) + (3-4) + ... + (99-100) = -1 * 50 = -50. The answer is \\boxed{-50}."
            },
            {
                "problem": "In a right triangle, the hypotenuse has length 13 and one leg has length 5. Find the length of the other leg.",
                "solution": "By Pythagorean theorem, b^2 = 13^2 - 5^2 = 169 - 25 = 144. So b = 12. The answer is \\boxed{12}."
            },
            {
                "problem": "Calculate the coefficient of x^2 in the expansion of (x + 3)^4.",
                "solution": "By Binomial Theorem, the term is \\binom{4}{2} x^2 3^2 = 6 * 9 * x^2 = 54x^2. So the coefficient is \\boxed{54}."
            },
            {
                "problem": "Find the minimum value of the quadratic expression x^2 - 6x + 10 for all real x.",
                "solution": "Completing the square gives (x-3)^2 + 1. The minimum value is 1. The answer is \\boxed{1}."
            }
        ]

    print(f"\n{'='*50}")
    print(f" [MATH] Evaluating Iris Tiny  ({len(items)} questions)")
    print(f"{'='*50}")
    passed_count = 0

    for i, item in enumerate(items, 1):
        problem = item.get("problem") or item.get("question", "")
        solution = item.get("solution") or item.get("answer", "")
        
        ground_truth_raw = _extract_boxed_content(solution)
        if ground_truth_raw is None:
                                                                            
            nums = re.findall(r"\b([\-]?\d[\d,\.]*)\b", solution)
            ground_truth_raw = nums[-1] if nums else "unknown"

        math_prompt = (
            f"Solve the following competition math problem step by step. "
            f"At the very end, write your final answer in LaTeX inside a \\boxed{{}} block "
            f"(e.g., \\boxed{{42}} or \\boxed{{\\frac{{1}}{{2}}}}).\n\n"
            f"Problem: {problem}"
        )
        response, _, t = run_inference_sc(
            math_prompt,
            role=ModelRole.MATH,
            extract_fn=_extract_boxed_content,
            n=3,
            keep_loaded=True,
        )
        model_answer_raw = _extract_boxed_content(response)

        # Formatting-only cleanup of the model's own answer. No ground truth
        # is passed in here — this cannot nudge the answer toward correct.
        if model_answer_raw is not None:
            corrected, was_fixed, _ = auto_correct_math_answer(
                problem=problem,
                model_raw_output=response,
            )
            if was_fixed:
                model_answer_raw = corrected

                                                           
        passed = False
        if ground_truth_raw and model_answer_raw:
            gt_norm = _clean_math_answer(ground_truth_raw)
            model_norm = _clean_math_answer(model_answer_raw)

                                     
            passed, reason = match_with_verifier(
                ground_truth_raw, model_answer_raw,
                problem=problem,
            )
            if not passed:
                                                    
                passed = (gt_norm == model_norm) and (model_norm != "")
        if passed:
            passed_count += 1

        short_p = problem.replace("\n", " ")[:60]
        print(f"  [{i:02d}/{len(items)}] {short_p}... | Expected: {ground_truth_raw} | Got: {model_answer_raw} | {'✓' if passed else '✗'} ({t}s)")

        append_to_csv(csv_path, {
            "Benchmark":    "MATH",
            "Role":         "Iris Tiny",
            "Prompt":       problem[:200],
            "Expected":     ground_truth_raw,
            "Model_Answer": model_answer_raw,
            "Passed":       passed,
            "Time_Sec":     t,
        }, FIELDNAMES)

    try:
        from src.iris import unload_model
        unload_model()
    except Exception:
        pass

    pct = (passed_count / len(items)) * 100 if items else 0
    print(f"\n  [MATH][Iris Tiny] Score: {passed_count}/{len(items)} ({pct:.1f}%)\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MATH benchmark")
    parser.add_argument("--samples", type=int, default=100, help="Number of questions to evaluate (default: 100). Use 0 for all.")
    args = parser.parse_args()

    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "outputs")
    os.makedirs(out_dir, exist_ok=True)
    
    from benchmark.utils import get_size_name, write_summary_csv
    size_name = get_size_name()
    raw_csv = os.path.join(out_dir, f"raw_{size_name}.csv")
    summary_csv = os.path.join(out_dir, f"benchmark_{size_name}.csv")
    
    run_math_benchmark(raw_csv, num_samples=args.samples)
    write_summary_csv(raw_csv, summary_csv)
    print(f"  Summary updated at: {os.path.abspath(summary_csv)}")
