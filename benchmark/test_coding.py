

import re
import random
import sys
import os
import signal

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from benchmark.utils import run_inference, append_to_csv
from src.iris import ModelRole

NUM_SAMPLES = 100
FIELDNAMES = ["Benchmark", "Role", "Prompt", "Expected", "Model_Answer", "Passed", "Time_Sec"]

class TimeoutException(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutException("Execution timed out (infinite loop?)")

def _extract_python_code(response: str) -> str:
    
    m = re.search(r"```(?:python)?\s*\n(.*?)```", response, re.DOTALL | re.IGNORECASE)
    if m:
        return m.group(1).strip()
    m = re.search(r"(def\s+\w+.*)", response, re.DOTALL)
    if m:
        return m.group(1).strip()
    return response.strip()

def run_unit_tests(code_text: str, test_text: str, timeout_sec: int = 2) -> tuple[bool, str | None]:
    
    
    old_handler = signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout_sec)
    
    exec_globals = {}
    try:
        
        full_code = f"{code_text}\n\n{test_text}"
        exec(full_code, exec_globals)
        return True, None
    except AssertionError as ae:
        return False, f"AssertionError: {ae}"
    except TimeoutException as te:
        return False, str(te)
    except Exception as e:
        return False, f"Exception: {e}"
    finally:
        
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old_handler)

def run_coding_benchmark(csv_path: str):
    try:
        from datasets import load_dataset
        ds = load_dataset("openai/openai_humaneval", split="test")
        items = list(ds)
        random.shuffle(items)
        items = items[:NUM_SAMPLES]
        print(f"[HumanEval] Loaded {len(items)} problems from HuggingFace.")
    except Exception as e:
        print(f"[HumanEval] Could not load dataset: {e}. Falling back to built-in prompts.")
        items = [
            {
                "prompt": "def add(a, b):\n    \"\"\"Return sum of a and b.\"\"\"\n", 
                "entry_point": "add",
                "test": "def check(candidate):\n    assert candidate(2, 3) == 5\n    assert candidate(-1, 1) == 0\ncheck(add)\n"
            },
            {
                "prompt": "def is_palindrome(s):\n    \"\"\"Return True if s is a palindrome.\"\"\"\n", 
                "entry_point": "is_palindrome",
                "test": "def check(candidate):\n    assert candidate('racecar') == True\n    assert candidate('hello') == False\ncheck(is_palindrome)\n"
            },
            {
                "prompt": "def factorial(n):\n    \"\"\"Return n!.\"\"\"\n", 
                "entry_point": "factorial",
                "test": "def check(candidate):\n    assert candidate(5) == 120\n    assert candidate(0) == 1\ncheck(factorial)\n"
            },
            {
                "prompt": "def fizzbuzz(n):\n    \"\"\"Return FizzBuzz list up to n.\"\"\"\n", 
                "entry_point": "fizzbuzz",
                "test": "def check(candidate):\n    res = candidate(5)\n    assert res == [1, 2, 'Fizz', 4, 'Buzz']\ncheck(fizzbuzz)\n"
            },
        ]

    print(f"\n{'='*50}")
    print(f" [HumanEval] Evaluating Iris Ai  ({len(items)} problems)")
    print(f"{'='*50}")
    passed_count = 0

    for i, item in enumerate(items, 1):
        func_signature = item["prompt"]
        entry_point    = item.get("entry_point", "function")
        test_suite     = item.get("test", "")

        
        plan_prompt = (
            f"You are a master programmer. Analyze the following coding problem and write a step-by-step plan to solve it.\n\n"
            f"Problem:\n```python\n{func_signature}\n```\n\nPlan the solution:"
        )
        plan_out, t1 = run_inference(plan_prompt, role=ModelRole.REASONING, use_routing=False, keep_loaded=True)

        
        code_prompt = (
            f"You are an expert Python developer. Complete the following Python function based on the provided plan. "
            f"Return ONLY valid Python code inside a ```python``` block.\n\n"
            f"Problem:\n```python\n{func_signature}\n```\n\n"
            f"Plan:\n{plan_out}\n\nCode:"
        )
        code_out, t2 = run_inference(code_prompt, role=ModelRole.CODE, use_routing=False, keep_loaded=True)
        initial_code = _extract_python_code(code_out)

        
        review_prompt = (
            f"You are an expert Code Reviewer. Review the following Python code for correctness, edge cases, and bugs.\n"
            f"Fix any issues and return the final corrected Python code inside a ```python``` block.\n\n"
            f"Problem:\n```python\n{func_signature}\n```\n\n"
            f"Initial Code:\n```python\n{initial_code}\n```\n\nFinal Corrected Code:"
        )
        final_out, t3 = run_inference(review_prompt, role=ModelRole.REVIEWER, use_routing=False, keep_loaded=True)
        final_code = _extract_python_code(final_out)
        
        t = round(t1 + t2 + t3, 2)

        
        
        call_line = f"check({entry_point})"
        if call_line.strip() not in test_suite:
            full_test_suite = f"{test_suite}\n{call_line}\n"
        else:
            full_test_suite = test_suite
        passed, test_err = run_unit_tests(final_code, full_test_suite)
        
        if passed:
            passed_count += 1

        short_sig = func_signature.strip().split("\n")[0][:60]
        status_char = "✓" if passed else "✗"
        note = f" ({test_err})" if test_err else ""
        print(f"  [{i:02d}/{len(items)}] {short_sig} | Tests: {status_char}{note} ({t}s)")

        append_to_csv(csv_path, {
            "Benchmark":    "HumanEval",
            "Role":         "Iris Tiny",
            "Prompt":       func_signature.replace("\n", " "),
            "Expected":     f"Valid passing code for {entry_point}()",
            "Model_Answer": final_code.replace("\n", " ")[:300],
            "Passed":       passed,
            "Time_Sec":     t,
        }, FIELDNAMES)

    try:
        from src.iris import unload_model
        unload_model()
    except Exception:
        pass

    pct = (passed_count / len(items)) * 100 if items else 0
    print(f"\n  [HumanEval][Iris Tiny] Score: {passed_count}/{len(items)} ({pct:.1f}%)\n")

if __name__ == "__main__":
    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "outputs")
    os.makedirs(out_dir, exist_ok=True)
    
    from benchmark.utils import get_size_name, write_summary_csv
    size_name = get_size_name()
    raw_csv = os.path.join(out_dir, f"raw_{size_name}.csv")
    summary_csv = os.path.join(out_dir, f"benchmark_{size_name}.csv")
    
    run_coding_benchmark(raw_csv)
    write_summary_csv(raw_csv, summary_csv)
    print(f"  Summary updated at: {os.path.abspath(summary_csv)}")
