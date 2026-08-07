
import re
import math
import time
from typing import Tuple, Optional


def clean_answer(text: str) -> str:
    """Cosmetic cleanup only: trims stray trailing periods and normalizes
    integer-valued floats (e.g. '12.0' -> '12'). Never changes the
    mathematical value of the answer and never consults a ground truth."""
    text = text.strip()

    if re.match(r'^\d+\.$', text):
        text = text[:-1]

    text = text.strip()

    try:
        val = float(text.replace(',', ''))
        if val == int(val) and '.' in text:
            text = str(int(val))
    except ValueError:
        pass

    return text


def _extract_boxed(text: str) -> Optional[str]:
    idx = text.rfind(r"\boxed{")
    if idx == -1:
        return None
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


def verify_and_refine(solution: str, problem: str,
                       keep_loaded: bool = False) -> Tuple[str, bool]:
    """
    Applies cosmetic normalization to the model's own boxed answer.

    IMPORTANT: this function no longer re-derives an answer from the problem
    text and substitutes it in. The previous version used
    `sandbox_compute_arithmetic` to eval() the problem statement directly and
    overwrite the model's boxed answer whenever it disagreed with that
    independently-computed value — which meant the harness, not the model,
    could end up answering the question. That path has been removed.

    The `problem` argument is kept in the signature for interface
    compatibility with existing callers, but is intentionally unused: nothing
    in this function may read the problem to determine what the "right"
    answer should be.
    """
    original = solution

    boxed = _extract_boxed(solution)
    if boxed:
        cleaned = clean_answer(boxed)
        if cleaned != boxed:
            solution = solution.replace(boxed, cleaned, 1)

    # Trim a stray trailing period after a bare number outside any box
    # (e.g. "...the answer is 42." at the very end of a response).
    solution = re.sub(r'(\d+)\.(\s|$)', r'\1\2', solution)

    return solution, (solution != original)


__all__ = [
    "verify_and_refine",
    "clean_answer",
]
