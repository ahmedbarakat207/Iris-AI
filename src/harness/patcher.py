"""
Iris code patcher (3B-model friendly).

Parses SEARCH/REPLACE-style patch text and applies it to a source file.
Designed for the realities of a 3B model:

  - Both this project's native "<<<<" / "====" / ">>>>" style AND Aider-style
    "<<<<<<< SEARCH" / "=======" / ">>>>>>> REPLACE" are accepted, with or
    without trailing label words.
  - We also accept the small-model inventions like <SEARCH> / <REPLACE> /
    <==== / ====> etc., which a 3B will sometimes generate instead of
    adhering to either canonical style.
  - An empty SEARCH side is treated as an INSERT (the REPLACE block is
    spliced in at the location indicated by surrounding context, or at
    the top of the file if there's no context). The 3B model frequently
    does this when it can't decide where exactly to insert.
  - Fuzzy matching tolerates a 3B model's inevitable typos and line-context
    drift:
      * Whitespace/indentation is normalised before comparison.
      * Each SEARCH line is matched against each candidate file line with
        a per-line similarity score, not a binary equal/unequal.
      * The best matching CONTIGUOUS run of file lines is picked, not just
        runs of exactly len(search) lines. If the model grabbed one extra
        or one too few context lines, the matcher can stretch or shrink
        the window to find the right spot.
      * A unique best match applies even at moderate (>= 0.70) similarity.
        The threshold of 0.92 in the old code was tuned for an exact-style
        SEARCH block; a 3B model that paraphrases a comment line will
        never hit that. We instead require the best match to be
        meaningfully better than the runner-up (gap > 0.10), which is
        the actual signal that "this is the right region".
"""

import logging
import re
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from typing import List, Optional, Tuple

try:
    from src.core.logger import get_logger

    logger = get_logger("iris")
except Exception:
    logger = logging.getLogger("iris")


_OPEN_RE = re.compile(r"^\s*(?:<{3,}[^\n]*|<SEARCH>)$", re.IGNORECASE)
_SEP_RE = re.compile(r"^\s*(?:={3,}[^\n]*|<====*|</SEARCH>|<REPLACE>)$", re.IGNORECASE)
_CLOSE_RE = re.compile(r"^\s*(?:>{3,}[^\n]*|</REPLACE>|====>)$", re.IGNORECASE)
_FENCE_RE = re.compile(r"^\s*```\w*\s*$")


@dataclass
class PatchBlockResult:
    search_preview: str
    applied: bool
    match_kind: str
    reason: str = ""
    similarity: float = 0.0


@dataclass
class PatchOutcome:
    code: str
    blocks_found: int = 0
    blocks_applied: int = 0
    blocks_failed: int = 0
    results: List[PatchBlockResult] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return self.blocks_found > 0 and self.blocks_failed == 0


def _preview(text: str, limit: int = 60) -> str:
    text = " ".join(text.split())
    return (text[:limit] + "…") if len(text) > limit else (text or "(empty)")


def _strip_outer_fence(text: str) -> str:
    """If the model wrapped the ENTIRE patch (all blocks) in one markdown code
    fence, drop just that outer fence."""
    lines = text.splitlines()
    if len(lines) >= 2 and _FENCE_RE.match(lines[0]) and lines[-1].strip() == "```":
        return "\n".join(lines[1:-1])
    return text


def _strip_fence_lines(lines: List[str]) -> List[str]:
    """Strip a leading or trailing ``` fence line from a per-block list."""
    lines = list(lines)
    if lines and lines[0].strip().startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].strip().startswith("```"):
        lines = lines[:-1]
    return lines


def _trim_blank_edges(lines: List[str]) -> List[str]:
    lines = list(lines)
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return lines


def _normalize(s: str) -> str:
    """Collapse all whitespace to single spaces and strip. Used for tolerant
    line comparison."""
    return " ".join(s.split())


def _line_similarity(a: str, b: str) -> float:
    """Per-line similarity in [0.0, 1.0]. We deliberately do NOT use
    SequenceMatcher.ratio() for single lines — its behaviour on short strings
    is unintuitive (two very different 10-char lines can score >0.5 just from
    shared characters). Instead, exact-after-normalise = 1.0, else ratio of
    the shorter string in the longer one clamped to 1.0."""
    an, bn = _normalize(a), _normalize(b)
    if not an or not bn:
        return 0.0
    if an == bn:
        return 1.0
    sm = SequenceMatcher(None, an, bn)

    return sm.ratio()


def _split_blocks(patch_text: str) -> Tuple[List[Tuple[List[str], List[str]]], int]:
    """Parse patch_text into (search_lines, replace_lines) tuples. Tolerant
    of the mistakes a 3B model actually makes — see module docstring.

    Returns (blocks, malformed_count)."""
    lines = patch_text.splitlines()
    blocks: List[Tuple[List[str], List[str]]] = []
    malformed = 0
    i, n = 0, len(lines)

    while i < n:
        if not _OPEN_RE.match(lines[i]):
            i += 1
            continue

        i += 1
        search_lines: List[str] = []
        found_sep = False
        while i < n:
            if _SEP_RE.match(lines[i]):
                found_sep = True
                i += 1
                break
            if _OPEN_RE.match(lines[i]):

                break
            search_lines.append(lines[i])
            i += 1

        if not found_sep:
            malformed += 1
            continue

        while i < n and _SEP_RE.match(lines[i]):
            i += 1

        replace_lines: List[str] = []
        while i < n and not _CLOSE_RE.match(lines[i]) and not _OPEN_RE.match(lines[i]):
            replace_lines.append(lines[i])
            i += 1
        if i < n and _CLOSE_RE.match(lines[i]):
            i += 1

        search_lines = [
            line for line in search_lines if line.strip() not in ("<think>", "</think>")
        ]
        replace_lines = [
            line
            for line in replace_lines
            if line.strip() not in ("<think>", "</think>")
        ]

        blocks.append((search_lines, replace_lines))

    return blocks, malformed


_LINE_MATCH_THRESHOLD = 0.72


_MIN_FRACTION_OF_LINES_MATCHING = 0.55


_MIN_GAP_BETWEEN_BEST_AND_RUNNERUP = 0.15


_MAX_WINDOW_STRETCH = 4


_MIN_MEAN_SIMILARITY = 0.78


def _windows_overlap(a_start, a_end, b_start, b_end) -> bool:
    """Two windows "overlap" if they share at least 60% of their content. A
    looser definition than strict line intersection \u2014 we want to consider
    windows that are slightly shifted versions of each other as the "same
    region" so the gap-to-runnerup check doesn't penalise legitimate matches
    just because the matcher evaluated them with a few different window sizes.
    """
    a_len = max(a_end - a_start, 1)
    b_len = max(b_end - b_start, 1)
    inter_start = max(a_start, b_start)
    inter_end = min(a_end, b_end)
    inter = max(0, inter_end - inter_start)
    return inter / min(a_len, b_len) >= 0.6


def _fuzzy_find_window(
    code_lines: List[str],
    norm_search: List[str],
) -> Optional[Tuple[int, int, float, float]]:
    """Search `code_lines` for the best window matching `norm_search`.

    Returns (start, end_exclusive, mean_similarity, runnerup_mean_similarity)
    or None if nothing usable was found.

    Strategy: for each starting position, try several window sizes (the model's
    line count, +/- a small stretch), score it as the mean per-line similarity
    over the *best alignment* of each SEARCH line to a code line in the window.
    Track the best score, and also the best NON-OVERLAPPING score. The caller
    requires the best to beat the non-overlapping runner-up by
    `_MIN_GAP_BETWEEN_BEST_AND_RUNNERUP` to actually accept a match.

    The "non-overlapping" part matters: many window sizes map to the same
    physical region of the file (e.g. (16, 20), (15, 20), (16, 21) are all
    roughly the same code), and we don\u0027t want to treat those as ambiguous
    "runners-up". A real ambiguity is a different region of the file scoring
    nearly as well.
    """
    n = len(code_lines)
    k = len(norm_search)
    if n == 0 or k == 0:
        return None

    candidates = []
    for win_extra in range(-_MAX_WINDOW_STRETCH, _MAX_WINDOW_STRETCH + 1):
        win = k + win_extra
        if win <= 0 or win > n:
            continue
        for start in range(0, n - win + 1):
            end = start + win
            mean, frac_matched = _score_window(code_lines, start, end, norm_search)
            if frac_matched < _MIN_FRACTION_OF_LINES_MATCHING:
                continue
            candidates.append((start, end, mean))

    if not candidates:
        return None

    candidates.sort(key=lambda c: (-c[2], c[1] - c[0]))
    best = candidates[0]
    best_mean = best[2]

    if best_mean < _MIN_MEAN_SIMILARITY:
        return None

    best_overlap_mean = 0.0
    non_overlap_mean = 0.0
    for cand in candidates[1:]:
        if _windows_overlap(best[0], best[1], cand[0], cand[1]):
            if cand[2] > best_overlap_mean:
                best_overlap_mean = cand[2]
        else:
            if cand[2] > non_overlap_mean:
                non_overlap_mean = cand[2]

    return best[0], best[1], best_mean, non_overlap_mean


def _score_window(
    code_lines: List[str],
    start: int,
    end: int,
    norm_search: List[str],
) -> Tuple[float, float]:
    """Score how well `norm_search` fits into code_lines[start:end].

    We align each SEARCH line to the most-similar code line in the window and
    take the mean similarity as the score. This handles the 3B-model case
    where the SEARCH has 4 lines and the matching window has 6 — the extra
    2 lines just get low scores, but the alignment still works.

    Also returns the fraction of SEARCH lines that hit at least the
    `_LINE_MATCH_THRESHOLD` similarity — used to reject windows where most
    SEARCH lines have nothing close to them in the file at all.
    """
    window = [_normalize(l) for l in code_lines[start:end]]
    n_search = len(norm_search)
    total = 0.0
    matched = 0
    for s in norm_search:
        best = 0.0
        for cl in window:
            sim = _line_similarity(s, cl)
            if sim > best:
                best = sim
        total += best
        if best >= _LINE_MATCH_THRESHOLD:
            matched += 1
    mean = total / n_search if n_search else 0.0
    frac = matched / n_search if n_search else 0.0
    return mean, frac


def _find_insert_position(
    code_lines: List[str],
    replace_lines: List[str],
) -> int:
    """Return the 0-based line index BEFORE which to splice the REPLACE block.

    Heuristic: find the first non-blank line of REPLACE, look for any
    contiguous region in the file where that line (or a near-match) appears;
    insert AFTER the matching line. Falls back to the end of the file.
    """
    if not code_lines:
        return 0
    if not replace_lines:
        return len(code_lines)

    anchor = next((_normalize(l) for l in replace_lines if l.strip()), "")
    if not anchor:
        return len(code_lines)

    for i, line in enumerate(code_lines):
        if _normalize(line) == anchor:

            return i + 1

    best_i, best_sim = -1, 0.0
    for i, line in enumerate(code_lines):
        sim = _line_similarity(anchor, line)
        if sim > best_sim:
            best_sim = sim
            best_i = i
    if best_i >= 0 and best_sim >= 0.75:
        return best_i + 1

    return len(code_lines)


def apply_patch(original_code: str, patch_text: str) -> PatchOutcome:
    """Apply one or more SEARCH/REPLACE blocks in `patch_text` to
    `original_code`, returning a `PatchOutcome` that records what happened.

    Per-block outcomes are independent: a block that doesn't match is
    recorded in `results` as `applied=False, match_kind="failed"` rather than
    aborting the whole patch. Callers can inspect `outcome.results` to
    surface a useful error to the user.
    """

    if patch_text:
        patch_text = patch_text.lstrip("\ufeff\u200b\u200c\u200d")
    text = _strip_outer_fence(patch_text.strip())
    raw_blocks, malformed = _split_blocks(text)

    code = original_code
    outcome = PatchOutcome(code=code)
    outcome.blocks_found = len(raw_blocks) + malformed

    for search_lines, replace_lines in raw_blocks:
        s_lines = _trim_blank_edges(search_lines)
        r_lines = _strip_fence_lines(replace_lines)
        search_block = "\n".join(s_lines)
        replace_block = "\n".join(r_lines)
        preview = _preview(search_block)

        if not s_lines:
            insert_at = _find_insert_position(code.splitlines(), r_lines)
            lines = code.splitlines()
            lines = lines[:insert_at] + r_lines + lines[insert_at:]
            code = "\n".join(lines)
            outcome.blocks_applied += 1
            outcome.results.append(
                PatchBlockResult(
                    preview,
                    True,
                    "insert",
                    reason="empty SEARCH treated as insertion",
                    similarity=1.0,
                )
            )
            continue

        if _normalize(search_block) == _normalize(replace_block):
            outcome.results.append(
                PatchBlockResult(
                    preview,
                    False,
                    "noop",
                    reason="SEARCH and REPLACE are identical — nothing to change",
                )
            )
            outcome.blocks_failed += 1
            logger.warning(f"[Patcher] No-op block detected: {preview!r}")
            continue

        if search_block in code:
            code = code.replace(search_block, replace_block, 1)
            outcome.blocks_applied += 1
            outcome.results.append(
                PatchBlockResult(preview, True, "exact", similarity=1.0)
            )
            continue

        code_lines = code.splitlines()
        norm_search = [_normalize(l) for l in s_lines]
        matched = False
        for i in range(len(code_lines) - len(s_lines) + 1):
            if all(
                _normalize(code_lines[i + j]) == norm_search[j]
                for j in range(len(s_lines))
            ):
                code_lines = code_lines[:i] + r_lines + code_lines[i + len(s_lines) :]
                code = "\n".join(code_lines)
                matched = True
                outcome.blocks_applied += 1
                outcome.results.append(
                    PatchBlockResult(preview, True, "exact", similarity=1.0)
                )
                break

        if not matched and len(s_lines) >= 2:
            result = _fuzzy_find_window(code_lines, norm_search)
            if result is not None:
                start, end, mean, runnerup = result

                if mean >= 0.95:
                    required_gap = 0.08
                elif mean >= 0.85:
                    required_gap = 0.15
                else:
                    required_gap = _MIN_GAP_BETWEEN_BEST_AND_RUNNERUP
                gap = mean - runnerup
                if gap >= required_gap:
                    code_lines = code_lines[:start] + r_lines + code_lines[end:]
                    code = "\n".join(code_lines)
                    matched = True
                    outcome.blocks_applied += 1
                    outcome.results.append(
                        PatchBlockResult(
                            preview,
                            True,
                            "fuzzy",
                            reason=f"fuzzy match at line {start} (similarity={mean:.2f}, "
                            f"runner-up gap={gap:.2f}, required={required_gap:.2f})",
                            similarity=mean,
                        )
                    )
                    logger.info(
                        f"[Patcher] Fuzzy match at line {start} "
                        f"(sim={mean:.2f}, gap={gap:.2f}): {preview!r}"
                    )
                else:
                    logger.warning(
                        f"[Patcher] Fuzzy match ambiguous "
                        f"(best sim={mean:.2f}, runner-up gap={gap:.2f}, "
                        f"required {required_gap:.2f}): {preview!r}"
                    )

        if not matched:
            outcome.blocks_failed += 1
            outcome.results.append(
                PatchBlockResult(
                    preview,
                    False,
                    "failed",
                    reason="couldn't find that text in the file",
                )
            )
            logger.warning(
                f"[Patcher] SEARCH block did not match anything: {preview!r}"
            )

    if malformed:
        outcome.blocks_failed += malformed
        outcome.results.append(
            PatchBlockResult(
                "(unterminated block)",
                False,
                "malformed",
                "a block was opened but never had a '====' separator",
            )
        )
        logger.warning(f"[Patcher] {malformed} unterminated patch block(s) discarded.")

    if outcome.blocks_found == 0:
        logger.warning("[Patcher] No SEARCH/REPLACE blocks found in patch text.")

    if outcome.blocks_found > 0 and outcome.blocks_applied == 0:
        logger.warning(
            f"[Patcher] Found {outcome.blocks_found} block(s) but NONE applied — "
            f"failures: {outcome.blocks_failed}"
        )

    outcome.code = code
    return outcome
