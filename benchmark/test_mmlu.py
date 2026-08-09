

import re
import random
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from benchmark.utils import run_inference, append_to_csv
from benchmark.compare import match, fix_common_format_issues
from src.iris import ModelRole

NUM_SAMPLES    = 100
FIELDNAMES     = ["Benchmark", "Role", "Prompt", "Expected", "Model_Answer", "Passed", "Time_Sec"]
CHOICE_LABELS  = ["A", "B", "C", "D"]

SUBJECTS = [
    "abstract_algebra",
    "high_school_mathematics",
    "high_school_physics",
    "high_school_computer_science",
    "logical_fallacies",
    "world_history",
    "philosophy",
    "college_medicine",
]

def _format_question(item: dict) -> tuple[str, str]:
    
    q       = item["question"]
    choices = item["choices"]
    answer  = item["answer"]

    choices_text = "\n".join(f"  {CHOICE_LABELS[i]}. {choices[i]}" for i in range(len(choices)))
    prompt = (
        f"Answer the following multiple-choice question.\n"
        f"Reason through the options carefully. After your reasoning, write EXACTLY: 'Answer: X' "
        f"where X is the correct letter (A, B, C, or D). Do not write anything after 'Answer: X'.\n\n"
        f"Question: {q}\n\n{choices_text}"
    )
    correct_letter = CHOICE_LABELS[answer]
    return prompt, correct_letter

def _extract_letter(response: str) -> str | None:
    
    response = response.strip()
    
    
    m = re.search(r"[Aa]nswer\s*[:\-]?\s*([ABCD])\b", response)
    if m:
        return m.group(1).upper()

    
    m = re.search(r"\*{1,2}([ABCD])\*{1,2}", response)
    if m:
        return m.group(1).upper()

    
    m = re.search(r"[\[\(]([ABCD])[\]\)]", response)
    if m:
        return m.group(1).upper()

    
    
    for ch in reversed(response):
        if ch in "ABCD":
            
            idx = response.rfind(ch)
            before = response[idx-1] if idx > 0 else ' '
            after  = response[idx+1] if idx < len(response)-1 else ' '
            if not before.isalpha() and not after.isalpha():
                return ch
    
    return None

def run_mmlu_benchmark(csv_path: str):
    per_subject = max(1, NUM_SAMPLES // len(SUBJECTS))
    items_with_subject: list[tuple[str, dict]] = []

    try:
        from datasets import load_dataset
        for subject in SUBJECTS:
            try:
                ds = load_dataset("cais/mmlu", subject, split="test")
                sample = list(ds)
                random.shuffle(sample)
                for row in sample[:per_subject]:
                    items_with_subject.append((subject, row))
            except Exception as e:
                print(f"[MMLU] Could not load subject '{subject}': {e}")

        print(f"[MMLU] Loaded {len(items_with_subject)} questions across {len(SUBJECTS)} subjects.")
    except Exception as e:
        print(f"[MMLU] Could not load dataset: {e}. Skipping MMLU benchmark.")
        return

    if not items_with_subject:
        print("[MMLU] No questions loaded. Skipping.")
        return

    size_label = f"Iris {get_size_name().capitalize()}"
    print(f"\n{'='*50}")
    print(f" [MMLU] Evaluating {size_label}  ({len(items_with_subject)} questions)")
    print(f"{'='*50}")
    passed_count = 0

    for i, (subject, item) in enumerate(items_with_subject, 1):
        prompt, correct_letter = _format_question(item)
        response, t = run_inference(prompt, role=ModelRole.REASONING, use_routing=False, keep_loaded=True)
        model_letter = _extract_letter(response)
        if model_letter:
            model_letter = fix_common_format_issues(model_letter)
        passed = (model_letter == correct_letter)
        if passed:
            passed_count += 1

        print(f"  [{i:02d}/{len(items_with_subject)}] [{subject}] Expected: {correct_letter} | Got: {model_letter} | {'✓' if passed else '✗'} ({t}s)")

        append_to_csv(csv_path, {
            "Benchmark":    f"MMLU-{subject}",
            "Role":         size_label,
            "Prompt":       item["question"][:200],
            "Expected":     correct_letter,
            "Model_Answer": model_letter,
            "Passed":       passed,
            "Time_Sec":     t,
        }, FIELDNAMES)

    pct = (passed_count / len(items_with_subject)) * 100 if items_with_subject else 0
    print(f"\n  [MMLU][{size_label}] Score: {passed_count}/{len(items_with_subject)} ({pct:.1f}%)\n")

    
    try:
        from src.iris import unload_model
        unload_model()
    except Exception:
        pass

if __name__ == "__main__":
    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "outputs")
    os.makedirs(out_dir, exist_ok=True)
    
    from benchmark.utils import get_size_name, write_summary_csv
    size_name = get_size_name()
    raw_csv = os.path.join(out_dir, f"raw_{size_name}.csv")
    summary_csv = os.path.join(out_dir, f"benchmark_{size_name}.csv")
    
    run_mmlu_benchmark(raw_csv)
    write_summary_csv(raw_csv, summary_csv)
    print(f"  Summary updated at: {os.path.abspath(summary_csv)}")
