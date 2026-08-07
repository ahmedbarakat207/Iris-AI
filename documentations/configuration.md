# Iris AI — Configuration Guide

## Overview

Iris AI has three configuration layers:

| File | Purpose | Hot Reload |
|------|---------|-----------|
| `config/iris.conf` | Model paths, inference settings, size tier | Yes (per-request) |
| `config/control.conf` | PC controller: email, apps, contacts | On startup |
| `config/datasets.json` | Training dataset registry per role | On training start |

---

## `config/iris.conf` — Full Reference

```json
{
  "max_new_tokens": 4096,
  "do_sample": true,
  "temperature": 0.4,
  "top_p": 0.92,
  "top_k": 40,
  "repetition_penalty": 1.0,
  "no_repeat_ngram_size": 0,
  "confidence_threshold": 1.8,
  "rag_mode": "task_aware",

  "models": {
    "triage": "iris_001.gguf",
    "router": "iris_004.gguf",
    "control": "iris_003.gguf",
    "math": "iris_004.gguf",
    "code": "iris_005.gguf",
    "reasoning": "iris_006.gguf",
    "reviewer": "iris_006.gguf",
    "general": "iris_007.gguf",
    "vision": "iris_008.gguf",
    "clip": "iris_009.gguf"
  },

  "n_ctx_allocation": "auto",
  "compacting_profile": "medium",
  "n_gpu_layers": -1,
  "n_threads": 8,
  "size": "medium"
}
```

### Inference Settings

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `max_new_tokens` | int | 4096 | Maximum tokens to generate per response |
| `temperature` | float | 0.4 | Randomness (0.0 = deterministic, 1.0 = creative) |
| `top_p` | float | 0.92 | Nucleus sampling: only consider tokens with cumulative probability ≤ value |
| `top_k` | int | 40 | Only consider top K tokens at each step |
| `repetition_penalty` | float | 1.0 | >1.0 penalizes repeated tokens |
| `no_repeat_ngram_size` | int | 0 | N-gram size to prevent repetition (0 = disabled) |
| `do_sample` | bool | true | Use sampling (true) vs greedy (false) |
| `confidence_threshold` | float | 1.8 | Minimum confidence for auto-routing decisions |

### RAG Settings

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `rag_mode` | string | "task_aware" | `task_aware` = category-filtered, `always` = always search, `disabled` = no RAG |

### Model Paths

The `models` block maps each role name to the GGUF filename in `models/`. Files are downloaded automatically from HuggingFace if missing.

### Hardware Settings

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `n_ctx_allocation` | string or int | "auto" | Context window size ("auto" = scales dynamically with system RAM) |
| `compacting_profile` | string | "medium" | Strategy for truncating history when context is full (`low`, `medium`, `aggressive`) |
| `n_gpu_layers` | int | -1 | Layers to offload to GPU (-1 = all, 0 = CPU only) |
| `n_threads` | int | 8 | CPU threads for inference |
| `size` | string | "medium" | Size tier: `tiny`, `small`, `medium`, `large`, `max` |

---

## Size Tiers — `config/sizes/{tier}.json`

Each tier defines which HuggingFace models are used per role. The file is auto-read when training or downloading models.

### Example: `config/sizes/medium.json`
```json
{
  "_description": "Iris AI — Medium (59B total params). ~45 GB storage. 3B–14B models. Fits 16 GB RAM.",
  "models": {
    "triage": "iris-ai/triage",
    "router": "iris-ai/router",
    "control": "iris-ai/control",
    "math": "iris-ai/math",
    "code": "iris-ai/code",
    "reasoning": "iris-ai/reasoning",
    "general": "iris-ai/general",
    "vision": "iris-ai/vision"
  },
  "gguf": { ... },
  "download_urls": { ... },
  "source_filenames": { ... }
}
```

### Switching Tiers

```bash
# 1. Download models for the new tier
python train.py --size max --download-models

# 2. Update config
# Edit config/iris.conf: "size": "max"

# 3. Update models block in iris.conf to match sizes/max.json gguf section
```

### Tier Comparison

| Tier | Triage | Code | Math | Reasoning | General | Vision | Total Params |
|------|--------|------|------|-----------|---------|--------|-------|
| Tiny | 1.7B | 3B | 1.5B | 4B | 4B | 3B | 14B |
| Small | 4B | 8B | 7B | 7B | 7B | 7B | 36B |
| Medium | 4B | 14B | 7B | 14B | 14B | 7B | 53B |
| Large | 8B | 32B | 32B | 32B | 32B | 8B | 112B |
| Max | 32B | 32B+ | 72B | 70B | 70B | 26B | 264B |

---

## `config/control.conf` — PC Controller Config

```json
{
  "email": {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_address": "your_email@gmail.com",
    "sender_password": "your_app_password",
    "contacts": {
      "mom": "mom@example.com",
      "dad": "dad@example.com",
      "boss": "manager@company.com"
    }
  },
  "apps": {
    "notepad": "notepad.exe",
    "spotify": "spotify",
    "vscode": "code",
    "chrome": "google-chrome",
    "terminal": "cmd.exe"
  },
  "browser": "default"
}
```

| Section | Description |
|---------|-------------|
| `email` | SMTP credentials + contact aliases |
| `apps` | App name → launch command mapping |
| `browser` | Default browser ("default" = system default) |

---

## `config/datasets.json` — Training Datasets

```json
{
  "code": {
    "huggingface": [
      {"path": "ise-uiuc/Magicoder-OSS-Instruct-75K", "max_samples": 8000},
      {"path": "nvidia/OpenCodeReasoning", "max_samples": 8000}
    ],
    "local_dirs": ["training/coding", "training/shared"]
  }
}
```

| Field | Description |
|-------|-------------|
| `huggingface` | List of HuggingFace datasets to load |
| `path` | Dataset identifier (org/dataset-name or built-in name) |
| `max_samples` | Cap on training pairs from this dataset |
| `local_dirs` | Directories containing `USER:`/`BOT:` Markdown files |

---

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `IRIS_MODEL_ID` | Override model display name |
| `HF_HOME` | HuggingFace cache directory |
| `HF_TOKEN` | HuggingFace API token (for gated models) |

---

## Hot Reload Details

- `iris.conf` is reloaded on **every** API request — changes take effect immediately
- `control.conf` is read once at controller startup — restart to apply changes
- `datasets.json` is read at training start
- Training data Markdown files are hot-discovered — no config change needed
