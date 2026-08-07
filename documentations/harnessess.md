# Technical Specification: Output Quality Harnesses (`src/harness.py`)

The Iris AI output harness is an deterministic, regex and AST-heuristic based pipeline designed to sanitize and normalize language model outputs. The pipeline returns a strictly typed `Tuple[str, List[dict]]` where warnings are human-readable debug events of `type: harness_warning`.

## 1. Code-Specific Pipeline (`apply_code_specific`)

Iterates through 8 modular stages.

### 1.1 `normalize_fences`
- **Regex Substitution**: Flattens `r'````+'` to standard ```` ``` ````.
- **Backtick Escaping**: Normalizes isolated double backticks `r'(?<![`\n])``([^`\n]+)``(?![`\n])'` to single backticks.
- **Unterminated Fences**: Counts `r'^```'` vs `r'\n```\s*$'`. If `opening > closing`, artificially appends `\n``` ` to prevent markdown parser crashes.

### 1.2 `strip_comments`
Enforces maximum token density by stripping inline comments via heuristic language parsing:
- **Python (`_strip_py_line`)**: Character-by-character scan simulating a state machine. Toggles `in_string` upon `"` or `'` (handling `'''`/`"""` and `\\` escapes). Identifies the first `#` token not within string state, slicing the string at `hash_idx`.
- **C/JS/Java**: `re.sub(r'/\*[^*]*\*+(?:[^/*][^*]*\*+)*/', '', text)` removes block comments. Scans line-by-line for `//`, explicitly ignoring `http:` and `https:` URI matches.
- **Shell**: `re.sub(r'(\s*)#[^\n]*', '', text)`.

### 1.3 `repair_truncation`
Maintains a LIFO `stack` of token pairs `{"{": "}", "(": ")", "[": "]"}` while iterating characters (skipping string literals). If `EOF` is reached and `len(stack) > 0`, it appends `"".join(reversed(stack))` to forcefully close code AST structures. 

### 1.4 `inject_imports`
Regex-based AST static analysis using `_PY_IMPORT_PATTERNS` (covering `sys`, `os`, `json`, `subprocess`, `threading`, etc.).
- Identifies the highest line index `insert_at` containing a valid shebang or `import`/`from` statement.
- Iterates over the generated text. If a target package pattern matches but is missing from `existing_imports`, it queues an `import {pkg}` and injects the sorted list at `insert_at`.

### 1.5 `normalize_header`
Detects CLI entrypoints via `r'if\s+__name__\s*==\s*["\']__main__["\']'` or `argparse.`. Mutates `lines.insert(0, "#!/usr/bin/env python3")` if missing.

### 1.6 `deduplicate_blocks`
Splits response by `r'\n\n+'`. Normalizes each block via `re.sub(r'\s+', ' ', block.strip().lower())`. Caches hashes of blocks `> 20` chars in a dictionary. Filters out any exact duplicate hash sequences to break LLM generative loops.

### 1.7 `clean_whitespace`
Stateful line iteration tracking `blank_count`. Collapses any sequence of `blank_count > 2` into standard PEP8 double newlines.

### 1.8 `redact_secrets`
Applies a 14-pattern regex dictionary against hallucinated credentials:
- `r'(sk-[a-zA-Z0-9_-]{20,}T3BlbkFJ[a-zA-Z0-9_-]{20,})'` → `[OPENAI_KEY_REDACTED]`
- AWS `AKIA`, GitHub PATs `ghp_`, and JWT `eyJ...` payloads.

---

## 2. Mathematical Pipeline (`apply_math`)

Targets inference anomalies in purely deterministic mathematical reasoning models.

### 2.1 `normalize_math_fences`
- **Double Dollar Padding**: Formats `r'\$\$\s+'` and `r'\s+\$\$'` into cleanly stripped `$$` blocks.
- **Unescaped Underscores**: If no `$` environment exists, finds bare `_` via `r'(?<!\\)_(?!_)(\w+)'` and converts to `math` mode `$_{\1}$` to prevent markdown italics hijacking.
- **Fractions**: Converts raw `\frac(\d)(\d)` tokens to `\frac{\1}{\2}`.

### 2.2 `normalize_math_notation`
- Enforces consistency. If `\cdot` or `\times` exists in the text, it upgrades standard asterisks `(?<!\\)\*(?!\*)` to `\cdot`. Otherwise, downconverts `\cdot` and `\times` to `*`.
- Formats algebraic negatives: `r'(?<=\w)\s*=\s*-(\d+)'` → ` = (-\1)`.

### 2.3 `extract_math_answer`
- Fallback heuristic for unformatted answers. Reverses line array. 
- Searches for `[=≈]\s*[\d\-.]+` or scalar variable bounds `\b[xXyYzZnNtT]\s*[=≈]\s*[\d\-.a-zA-Z√π]+`. 
- Injects a formatted `**Answer:** {candidate}` block if a matching heuristic is found.

### 2.4 `normalize_math_steps`
- Extracts sequences of `r'(?:^|\n)\s*(?:Step|step)\s*(\d+|[ivxlcdm]+)[\s:.\-)]'`. 
- Applies standard loop `enumerate(..., 1)` and aggressively overwrites numbering to `**Step {i}:** ` to correct LLM counting hallucinations.

### 2.5 `redact_hallucinated_refs`
- Strips hallucinated academic tagging: `r'\(([A-Z][a-z]+ et al\.,?\s*\d{4}[a-z]?)\)'` and invalid equation pointers `r'\\tag\{(\d+\.\d+)\}'`.

### 2.6 `deduplicate_math_steps`
- Splitting text by `\n\n+`, drops strictly identical logical step blocks where `len(normalized) >= 8`.
