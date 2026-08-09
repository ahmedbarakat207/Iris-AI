

import re
import time
import sys
import os
import signal

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from benchmark.utils import run_inference, append_to_csv
from src.iris import ModelRole

NUM_SAMPLES = 3
FIELDNAMES = ["Benchmark", "Role", "Prompt", "Expected", "Model_Answer", "Passed", "Time_Sec"]

class TimeoutException(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutException("Execution timed out (infinite loop?)")


PROBLEMS = [
    {
        "id": "calculator_parser",
        "description": (
            "Fix the buggy `calculate` function. It should parse a simple arithmetic expression "
            "string (like '1.2e2 + 10' or ' 10   *   2.5 ') with arbitrary spaces and scientific "
            "notation floats correctly. Crucially, if division by zero is attempted (e.g. '5 / 0'), "
            "it must raise a `ValueError` with the exact message 'Cannot divide by zero'. "
            "Do NOT raise a standard ZeroDivisionError."
        ),
        "buggy_code": (
            "def calculate(expr: str) -> float:\n"
            "    parts = expr.split()\n"
            "    a = float(parts[0])\n"
            "    op = parts[1]\n"
            "    b = float(parts[2])\n"
            "    if op == '+': return a + b\n"
            "    elif op == '-': return a - b\n"
            "    elif op == '*': return a * b\n"
            "    elif op == '/': return a / b\n"
        ),
        "test": (
            "def check(candidate):\n"
            "    # Test division by zero\n"
            "    try:\n"
            "        candidate('5 / 0')\n"
            "        assert False, 'Should raise ValueError for divide by zero'\n"
            "    except ValueError as e:\n"
            "        assert str(e) == 'Cannot divide by zero', f'Wrong message: {e}'\n"
            "    except ZeroDivisionError:\n"
            "        assert False, 'Raised ZeroDivisionError instead of ValueError'\n"
            "    \n"
            "    # Test scientific notation\n"
            "    assert abs(candidate('1.2e2 + 10') - 130) < 1e-9\n"
            "    \n"
            "    # Test arbitrary spaces\n"
            "    assert abs(candidate(' 10   *   2.5 ') - 25.0) < 1e-9\n"
            "check(calculate)\n"
        )
    },
    {
        "id": "json_flattener",
        "description": (
            "Fix the buggy `flatten_json` function. It flattens a nested dictionary into a "
            "single-level dictionary (keys concatenated with underscores). The buggy version "
            "overwrites duplicate keys during flattening. The fixed version must raise a "
            "`KeyError` (with a message indicating key collision) if a key collision would "
            "occur (e.g. when flattening `{'a': {'b': 1}, 'a_b': 2}`). It should also handle lists "
            "and nested dicts within lists correctly."
        ),
        "buggy_code": (
            "def flatten_json(y):\n"
            "    out = {}\n"
            "    def flatten(x, name=''):\n"
            "        if type(x) is dict:\n"
            "            for a in x:\n"
            "                flatten(x[a], name + a + '_')\n"
            "        elif type(x) is list:\n"
            "            i = 0\n"
            "            for a in x:\n"
            "                flatten(a, name + str(i) + '_')\n"
            "                i += 1\n"
            "        else:\n"
            "            out[name[:-1]] = x\n"
            "    flatten(y)\n"
            "    return out\n"
        ),
        "test": (
            "def check(candidate):\n"
            "    # Test collision\n"
            "    try:\n"
            "        candidate({'a': {'b': 1}, 'a_b': 2})\n"
            "        assert False, 'Should raise KeyError on collision'\n"
            "    except KeyError:\n"
            "        pass\n"
            "    \n"
            "    # Test normal flattening\n"
            "    res = candidate({'x': [1, {'y': 2}]})\n"
            "    assert res.get('x_0') == 1, f'Got {res}'\n"
            "    assert res.get('x_1_y') == 2, f'Got {res}'\n"
            "check(flatten_json)\n"
        )
    },
    {
        "id": "rate_limiter",
        "description": (
            "Fix the buggy `TokenBucket` class. This is a token bucket rate limiter for API requests. "
            "It has two bugs: (1) it uses integer floor division when calculating elapsed time, "
            "which prevents tokens from refilling when checked frequently; (2) it updates `self.last_update` "
            "on every consume call even if no tokens were refilled, which causes tokens to stay at 0 if "
            "called more than once per second. Fix it to calculate fractional refill tokens and track updates correctly."
        ),
        "buggy_code": (
            "import time\n"
            "class TokenBucket:\n"
            "    def __init__(self, capacity: int, refill_rate: float):\n"
            "        self.capacity = capacity\n"
            "        self.refill_rate = refill_rate # tokens per second\n"
            "        self.tokens = float(capacity)\n"
            "        self.last_update = time.time()\n"
            "    def consume(self, amount: int) -> bool:\n"
            "        now = time.time()\n"
            "        elapsed = int(now - self.last_update)\n"
            "        refilled = elapsed * self.refill_rate\n"
            "        self.tokens = min(self.capacity, self.tokens + refilled)\n"
            "        self.last_update = now\n"
            "        if self.tokens >= amount:\n"
            "            self.tokens -= amount\n"
            "            return True\n"
            "        return False\n"
        ),
        "test": (
            "import time\n"
            "def check(candidate_class):\n"
            "    bucket = candidate_class(10, 2.0)\n"
            "    assert bucket.consume(10) == True\n"
            "    assert bucket.consume(1) == False\n"
            "    \n"
            "    time.sleep(0.5)\n"
            "    # After 0.5s, should have refilled 1 token\n"
            "    assert bucket.consume(1) == True, 'Should have refilled 1 token'\n"
            "    \n"
            "    time.sleep(0.25)\n"
            "    # Consume frequently — sleep another 0.25s to sum to 0.5s\n"
            "    assert bucket.consume(1) == False\n"
            "    time.sleep(0.25)\n"
            "    assert bucket.consume(1) == True, 'Frequent checks should not prevent refilling'\n"
            "check(TokenBucket)\n"
        )
    }
]

def _extract_python_code(response: str) -> str:
    
    m = re.search(r"```(?:python)?\s*\n(.*?)```", response, re.DOTALL | re.IGNORECASE)
    if m:
        return m.group(1).strip()
    return response.strip()

def run_swe_test(code_text: str, test_text: str, timeout_sec: int = 3) -> tuple[bool, str | None]:
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

def run_swebench_benchmark(csv_path: str):
    print(f"\n{'='*50}")
    print(f" [SWE-Bench] Evaluating Iris Tiny  ({len(PROBLEMS)} codebase repair tasks)")
    print(f"{'='*50}")
    passed_count = 0

    for i, prob in enumerate(PROBLEMS, 1):
        prompt = (
            f"You are given a codebase bug and its description. Fix the code to resolve the issue. "
            f"Return ONLY valid Python code containing the corrected function/class inside a ```python``` block.\n\n"
            f"Issue description: {prob['description']}\n\n"
            f"Buggy Code:\n```python\n{prob['buggy_code']}```"
        )

        response, t = run_inference(prompt, role=ModelRole.CODE, use_routing=False, keep_loaded=True)
        extracted_code = _extract_python_code(response)

        passed, test_err = run_swe_test(extracted_code, prob["test"])
        if passed:
            passed_count += 1

        status_char = "✓" if passed else "✗"
        note = f" ({test_err})" if test_err else ""
        print(f"  [{i:02d}/{len(PROBLEMS)}] Task: {prob['id']} | Test: {status_char}{note} ({t}s)")

        append_to_csv(csv_path, {
            "Benchmark":    f"SWE-Bench-{prob['id']}",
            "Role":         "Iris Tiny",
            "Prompt":       prob["description"][:200],
            "Expected":     "Passing tests",
            "Model_Answer": extracted_code.replace("\n", " ")[:300],
            "Passed":       passed,
            "Time_Sec":     t,
        }, FIELDNAMES)

    pct = (passed_count / len(PROBLEMS)) * 100 if PROBLEMS else 0
    print(f"\n  [SWE-Bench][Iris Tiny] Score: {passed_count}/{len(PROBLEMS)} ({pct:.1f}%)\n")

if __name__ == "__main__":
    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "outputs")
    os.makedirs(out_dir, exist_ok=True)
    
    from benchmark.utils import get_size_name, write_summary_csv
    size_name = get_size_name()
    raw_csv = os.path.join(out_dir, f"raw_{size_name}.csv")
    summary_csv = os.path.join(out_dir, f"benchmark_{size_name}.csv")
    
    run_swebench_benchmark(raw_csv)
    write_summary_csv(raw_csv, summary_csv)
    print(f"  Summary updated at: {os.path.abspath(summary_csv)}")
