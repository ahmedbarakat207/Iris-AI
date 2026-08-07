# Iris AI — Models & Routing

## Role Architecture

Iris uses **8 distinct roles**, each backed by a specialized GGUF model. The role defines the model's system prompt, context window, and training data.

| Role | Enum Value | GGUF File | Context | System Prompt |
|------|-----------|-----------|---------|---------------|
| **Triage** | `triage` | `iris_001.gguf` | 2048 | Classify query intent, output routing tag |
| **Router** | `router` | `iris_004.gguf` | 2048 | Output JSON action matrices for automation |
| **Control** | `control` | `iris_003.gguf` | 2048 | Output automation actions in JSON |
| **Math** | `math` | `iris_004.gguf` | 4096 | Solve math/algorithmic problems step-by-step |
| **Code** | `code` | `iris_005.gguf` | 8192 | Generate working production-quality code |
| **Reasoning** | `reasoning` | `iris_006.gguf` | 2048 | Chain-of-thought for complex problems |
| **General** | `general` | `iris_007.gguf` | 4096 | Broad knowledge, explanations, comparisons |
| **Vision** | `vision` | `iris_008.gguf` | 4096 | Analyze images, describe visual content |

---

## Model Selection By Tier

### Tiny — 14B params (4 GB RAM)
| Role | Model | Parameters |
|------|-------|------------|
| Triage | Iris AI Triage | 1.7B |
| Router | Iris AI Router | 1.7B |
| Math | Iris AI Math | 1.5B |
| Code | Iris AI Code | 3B |
| Reasoning | Iris AI Reasoning | 4B |
| General | Iris AI General | 4B |
| Vision | Iris AI Vision | 3B |

### Small — 36B params (8 GB RAM)
| Role | Model | Parameters |
|------|-------|------------|
| Triage | Iris AI Triage | 4B |
| Router | Iris AI Router | 4B |
| Control | Iris AI Control | 3B |
| Math | Iris AI Math | 7B |
| Code | Iris AI Code | 8B |
| Reasoning | Iris AI Reasoning | 7B |
| General | Iris AI General | 7B |
| Vision | Iris AI Vision | 7B |

### Medium — 53B params (16 GB RAM) [DEFAULT]
| Role | Model | Parameters |
|------|-------|------------|
| Triage | Iris AI Triage | 4B |
| Router | Iris AI Router | 4B |
| Control | Iris AI Control | 7B |
| Math | Iris AI Math | 7B |
| Code | Iris AI Code | 14B |
| Reasoning | Iris AI Reasoning | 14B |
| General | Iris AI General | 14B |
| Vision | Iris AI Vision | 7B |

### Large — 112B params (24 GB RAM)
| Role | Model | Parameters |
|------|-------|------------|
| Triage | Iris AI Triage | 8B |
| Router | Iris AI Router | 32B |
| Control | Iris AI Control | 32B |
| Math | Iris AI Math | 32B |
| Code | Iris AI Code | 32B |
| Reasoning | Iris AI Reasoning | 32B |
| General | Iris AI General | 32B |
| Vision | Iris AI Vision | 8B |

### Max — 264B params (48 GB RAM)
| Role | Model | Parameters |
|------|-------|------------|
| Triage | Iris AI Triage | 32B |
| Router | Iris AI Router | 32B |
| Control | Iris AI Control | 32B |
| Math | Iris AI Math | 72B |
| Code | Iris AI Code | 32B+ |
| Reasoning | Iris AI Reasoning | 70B |
| General | Iris AI General | 70B |
| Vision | Iris AI Vision | 26B |



---

## Quantization

All models use **Q4_K_M** quantization (4-bit with medium quality). This provides the best balance of quality, size, and speed:

| Quant | Quality | Size (7B) | Speed |
|-------|---------|-----------|-------|
| Q2_K | Lowest | ~2.5 GB | Fastest |
| Q3_K_M | Low | ~3.5 GB | Fast |
| **Q4_K_M** | **High** | **~4.5 GB** | **Fast** |
| Q5_K_M | Higher | ~5.5 GB | Moderate |
| Q6_K | Very High | ~6.5 GB | Slower |
| Q8_0 | Best | ~7.5 GB | Slow |
| F16 | Lossless | ~14 GB | Slowest |

---

## Model Download

Models are downloaded automatically from HuggingFace using `hf_hub_download`:

```bash
# Download all models for a tier:
python train.py --size medium --download-models

# Download a specific model:
python -c "from src.iris import download_gguf; download_gguf('iris_001.gguf')"
```

Models are cached in `models/`. If a model already exists (non-zero size), download is skipped.

---

## System Prompts

Each role has a dedicated system prompt:

### Triage
```
You are the Iris AI Triage node.
Rules:
1. If the user is just greeting, saying hi/hello, asking simple conversational
   or factual questions, answer them directly. Do NOT output any routing tags.
2. If the query needs a specialist model, output EXACTLY ONE routing tag:
   [ROUTE: GENERAL]     — general knowledge, explanations, broad topics
   [ROUTE: REASONING]   — complex logic, system design, strategy, architecture
   [ROUTE: MATH]        — math, equations, proofs, algorithmic problems
   [ROUTE: CODE_SIMPLE]  — simple single-file code, small functions, snippets
   [ROUTE: CODE_COMPLEX] — large projects, games, multi-file, kernels, bootloaders

Be precise. If unsure, default to [ROUTE: GENERAL].
```

### Code
```
You are the Iris AI Coding Specialist. Generate clean, fully working,
production-quality code. Ensure correctness, edge-case handling, and
error-free syntax. Do NOT include comments in your code. After the code
block, provide a concise explanation of the code, its key features,
and clear instructions on how to compile/run it.
```

### Math
```
You are the Iris AI Math Core. Solve mathematical/algorithmic problems
step-by-step. Use precise notation.
```

### Reasoning
```
You are the Iris AI Reasoning Specialist. Think step-by-step using
chain-of-thought reasoning. Break down complex problems methodically
before giving the final answer.
```

### Reviewer
```
You are the Iris AI Code Reviewer. Review and refine code for correctness,
efficiency, edge cases, and readability. Ensure the final output is
production-ready. Fix any errors, fill missing logic, and optimize
where possible. Return the final code and explanation.
```
