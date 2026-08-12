
from __future__ import annotations

import re
import time
import subprocess
import math
from typing import Optional, Tuple

from benchmark.compare import (
    match, match_with_verifier, normalize_answer,
    extract_numeric, fix_common_format_issues,
)


def auto_correct_math_answer(
    problem: str,
    model_raw_output: str,
) -> Tuple[str, bool, str]:
    """
    Extracts and lightly reformats the model's own final answer from its raw
    output. This function NEVER receives or consults a ground-truth value —
    it cannot "correct" an answer toward something it isn't permitted to see.

    Allowed operations:
      - extracting the final answer the model already gave (boxed / pattern)
      - normalizing its formatting (whitespace, LaTeX wrappers, trailing
        punctuation, degree-symbol notation, etc.)

    Disallowed (and removed in this version):
      - re-deriving the answer from the problem text independently
      - comparing against / nudging toward a ground-truth value
      - substituting any value the model did not itself produce
    """
    log_parts = []

    boxed = _extract_boxed(model_raw_output)
    if boxed is None:
        boxed = _extract_answer_pattern(model_raw_output)

    original = boxed or model_raw_output[-500:]
    log_parts.append(f"Extracted: {original[:80]}")

    fmt_fixed = fix_common_format_issues(original)
    if fmt_fixed != original:
        log_parts.append(f"Format fix: '{original[:40]}' -> '{fmt_fixed[:40]}'")
        return fmt_fixed, True, "; ".join(log_parts)

    return original, False, "; ".join(log_parts)


def auto_correct_code_answer(
    problem: str,
    code_output: str,
    test_cases: list | None = None,
) -> Tuple[str, bool, str]:
    """
    Code path is unchanged in spirit: it may check syntax validity and run the
    candidate code in a sandbox to report pass/fail, but it never injects or
    rewrites the model's logic with a "known correct" solution. Scoring still
    happens against the actual unit tests downstream, exactly as before.
    """
    log_parts = []

    try:
        import ast
        ast.parse(code_output)
        log_parts.append("Syntax: OK")
    except SyntaxError as e:
        log_parts.append(f"Syntax error: {e}")
        try:
            fixed = _basic_syntax_fix(code_output, e)
            ast.parse(fixed)
            code_output = fixed
            log_parts.append("Syntax fix applied (bracket balancing only)")
        except Exception:
            pass

    try:
        from src.harness.harness import CodeSandbox

        report = CodeSandbox.run(code_output, language="python")
        if report.result.value == "error":
            log_parts.append(f"Sandbox error: {report.runtime_errors[:2]}")
        elif report.result.value == "fail":
            log_parts.append(f"Sandbox: {report.tests_passed}/{report.tests_passed + report.tests_failed} tests")
        else:
            log_parts.append(f"Sandbox: {report.result.value}")

    except ImportError:
        log_parts.append("CodeSandbox unavailable")

    return code_output, False, "; ".join(log_parts)


def _extract_boxed(text: str) -> str | None:
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


def _extract_answer_pattern(text: str) -> str | None:
    m = re.search(r'\*\*Answer:?\*\*\s*(.+?)(?:\n|$)', text, re.IGNORECASE)
    if m:
        return m.group(1).strip()

    m = re.search(
        r'(?:Therefore|Thus|Hence|So|Final answer|The answer is)\s*,?\s*(.+?)(?:\.|$)\s*$',
        text, re.IGNORECASE | re.MULTILINE
    )
    if m:
        return m.group(1).strip()

    lines = [l.strip() for l in text.strip().split('\n') if l.strip()]
    for line in reversed(lines[-3:]):
        nums = re.findall(r'[\d.\-+eE]+', line.replace(',', ''))
        if nums:
            return nums[-1]

    return None


def _basic_syntax_fix(code: str, error: SyntaxError) -> str:
    # Bracket-balancing only — does not alter program logic or output values.
    if "'(' was never closed" in str(error) or "unexpected EOF" in str(error):
        open_parens = code.count('(') - code.count(')')
        open_braces = code.count('{') - code.count('}')
        open_brackets = code.count('[') - code.count(']')
        code = code.rstrip()
        code += ')' * max(0, open_parens)
        code += '}' * max(0, open_braces)
        code += ']' * max(0, open_brackets)
    return code


__all__ = [
    "auto_correct_math_answer",
    "auto_correct_code_answer",
]
