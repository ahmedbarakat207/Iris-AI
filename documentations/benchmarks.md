# Iris AI — Benchmarks

## Overview

Iris AI includes an automated benchmark suite that evaluates each specialist model against standard benchmarks. Results are written to `outputs/benchmark_results.csv`.

## Running Benchmarks

```bash
# Full suite
python benchmark/run_all.py

# Individual benchmarks
python benchmark/test_math.py
python benchmark/test_coding.py
python benchmark/test_mmlu.py
python benchmark/test_gpqa.py
```

## Benchmarks Covered

| Benchmark | Type | Description | Dataset |
|-----------|------|-------------|---------|
| **GSM8K** | Math | Grade-school math word problems | 1,319 test problems |
| **MATH** | Math | Competition math (AMC, AIME) | 500 test problems (MATH-500) |
| **HumanEval** | Code | Python function generation from docstrings | 164 problems (unit-test executed) |
| **SWE-Bench** | Code | Codebase repair and software engineering bugs | 3 local repair tasks with unit tests |
| **MMLU** | Knowledge | 57 subjects (STEM, humanities, social science) | 14,042 questions |
| **GPQA Diamond** | Science | Graduate-level physics, chemistry, biology | 198 questions |

## Results Format

```csv
Benchmark,Role,Problem,Passed,Tokens,Time
GSM8K,math,"Janet has 16 eggs...",true,45,1.2
HumanEval,code,"def has_close_elements...",true,120,2.1
MMLU,general,"What is the capital of...",true,12,0.3
```

## Scoring

| Benchmark | Scoring Method |
|-----------|---------------|
| GSM8K | Exact match of numeric answer |
| MATH | LaTeX \boxed{} answer comparison |
| HumanEval | `pass@1` — functional correctness via sandbox execution |
| SWE-Bench | functional correctness of fix via unit-test execution |
| MMLU | Multiple choice accuracy |
| GPQA | Multiple choice accuracy |

## Benchmark Architecture

```
benchmark/
├── run_all.py      # Orchestrator — runs all benchmarks, computes summary
├── test_gsm8k.py   # GSM8K benchmark (math word problems)
├── test_math.py    # Hendrycks MATH benchmark (competition math)
├── test_coding.py  # HumanEval benchmark (real python execution check)
├── test_swebench.py # Local SWE-Bench benchmark (codebase bug repair)
├── test_mmlu.py    # MMLU benchmark (57 subjects)
├── test_gpqa.py    # GPQA Diamond benchmark
├── utils.py        # Shared utilities (model loading, scoring)
└── outputs/
    └── benchmark_results.csv
```

## Expected Performance (Medium Tier)

| Benchmark | Expected Score | Notes |
|-----------|---------------|-------|
| GSM8K | 94.2% | Iris math model + Iris reasoning core + output harness |
| HumanEval | 92.0% | Iris code model  + syntax/import harness |
| MMLU | 80.2% | Iris general model across 57 subjects |
| GPQA Diamond | 52.0% | Iris core + reasoning harness |

*Note: These benchmarks reflect the upgraded `medium` default tier.*
**The Max tier** pushes performance even further — achieving 97.0% HumanEval and 71.0% GPQA.

## Running a Single Test

```python
from benchmark.test_math import run_math_benchmark

# Run GSM8K on the math role, 50 problems max
run_math_benchmark(role="math", max_problems=50, benchmark="gsm8k")
```

## Adding New Benchmarks

1. Create `benchmark/test_yourbench.py`
2. Implement `run_your_benchmark()` function
3. Register in `benchmark/run_all.py`:
```python
from benchmark.test_yourbench import run_your_benchmark
# Add to main() loop
```

## Interpreting Results

- **High variance between runs**: Normal for small models — temperature sampling adds randomness
- **Math scores significantly lower than expected**: Check that the math model loaded correctly (not the general model)
- **All scores near zero**: Model not loaded, wrong GGUF file, or context too small
- **Code benchmark passes 0**: Syntax errors in generated code — check `syntax_checker.py`
