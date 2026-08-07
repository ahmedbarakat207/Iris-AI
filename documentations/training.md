# Iris AI — Training Guide

## Overview

Iris AI fine-tunes specialist models using **LoRA** (Low-Rank Adaptation) on domain-specific training data. After fine-tuning, adapters are merged into the base model and converted to quantized GGUF format.

## Training Pipeline

```
train.py --train-role code --iters 2000
    │
    ├── 1. Load Datasets
    │   ├── HuggingFace datasets (from config/datasets.json)
    │   └── Local Markdown files (USER:/BOT: format)
    │
    ├── 2. Format Training Data
    │   └── Convert to (system_prompt, user, assistant) triples
    │
    ├── 3. Apply LoRA Adapters
    │   ├── Apple Silicon: MLX (mlx-lm)
    │   └── CUDA/CPU: PyTorch + HuggingFace PEFT
    │
    ├── 4. Merge Adapters
    │   └── Combine LoRA weights into base model
    │
    ├── 5. Convert to GGUF
    │   └── scripts/convert_hf_to_gguf.py → F16 GGUF
    │
    └── 6. Quantize
        └── llama-quantize → Q4_K_M GGUF
```

## Quick Start

```bash
# Setup (one-time)
bash setup.sh

# Train a single role
python train.py --train-role code --iters 2000

# Train using a specific size tier
python train.py --size large --train-role math --iters 3000

# Train all roles
python train.py --size medium --iters 2000

# Quick iteration (skip GGUF conversion)
python train.py --train-role code --skip-gguf
```

## CLI Reference

```bash
python train.py [options]

Options:
  --size {tiny,small,medium,large,max}
                        Size tier (default: medium)
  --train-role {triage,router,control,math,code,reasoning,general,vision,all}
                        Which role to train (default: all)
  --iters N             Training iterations (default: 2000)
  --batch-size N        Batch size (default: 1)
  --accum-steps N       Gradient accumulation steps (default: 8)
  --max-seq-length N    Maximum sequence length (default: 512)
  --learning-rate R     Learning rate (default: auto based on model size)
  --num-layers N        LoRA layers to target (default: 16, 8-32 for quality/speed)
  --quant-type {q4_k_m,q5_k_m,q8_0,f16}
                        Quantization format (default: q4_k_m)
  --skip-gguf           Skip GGUF conversion (adapter only)
  --skip-training       Skip training (GGUF conversion from existing adapter)
  --download-models     Download all GGUF files for the tier without training
```

## Training Data Format

Training data is **Markdown files** with `USER:` / `BOT:` pairs:

```markdown
# File: training/coding/my_data.md

USER: Write a function to reverse a linked list
BOT: ```python
def reverse_list(head):
    prev = None
    current = head
    while current:
        next_node = current.next
        current.next = prev
        prev = current
        current = next_node
    return prev
```

USER: What is the time complexity?
BOT: O(n) time, O(1) space — single pass through the list.
```

### Rules:
- `USER:` must start the line (can have leading whitespace in practice)
- `BOT:` must start the line
- Code blocks use triple backticks (```) with language identifier
- Pairs should be related (same conversation thread)
- Avoid duplicates — the trainer may detect and skip them

## Dataset Configuration

Edit `config/datasets.json` to control which datasets each role trains on:

```json
{
  "code": {
    "huggingface": [
      {"path": "ise-uiuc/Magicoder-OSS-Instruct-75K", "max_samples": 8000},
      {"path": "nvidia/OpenCodeReasoning", "max_samples": 8000},
      {"path": "bigcode/self-oss-instruct-sc2-exec-filter-50k", "max_samples": 8000},
      {"path": "m-a-p/CodeFeedback-Filtered-Instruction", "max_samples": 8000}
    ],
    "local_dirs": ["training/coding", "training/shared"]
  }
}
```

### Role → Training Directory Mapping

| Role | Training Directories |
|------|---------------------|
| Triage | `training/triage`, `training/shared` |
| Router | `training/control`, `training/shared` |
| Control | `training/control`, `training/shared` |
| Math | `training/math`, `training/shared` |
| Code | `training/coding`, `training/shared` |
| Reasoning | `training/reasoning`, `training/shared` |
| General | `training/general`, `training/shared` |
| Vision | `training/general`, `training/shared` |

**Important:** `training/shared/` is included for **every role**. Data there affects ALL models.

## Training Data Directories

```
training/
├── coding/           # Code generation data
│   ├── convo_*.md    # Conversation transcripts
│   ├── generated_code.md
│   ├── generated_os_dev.md        # OS/kernel training
│   ├── generated_premium_web.md   # Premium website training
│   └── ...
├── reasoning/        # Reasoning & chain-of-thought
│   ├── chain_of_thought.md        # Step-by-step reasoning
│   ├── reasoning_examples.md      # Action reasoning
│   └── ...
├── math/             # Math & algorithms
├── triage/           # Triage query routing
│   ├── triage_dataset.md
│   └── ...
├── general/          # General knowledge
│   ├── chat_*.md                  # Conversational data
│   └── ...
├── control/          # PC controller actions
│   └── control.md
...
└── shared/           # Shared across all roles
    ├── iris_identity.md
    ├── chain_of_thought.md
    ├── generated_os_dev.md
    ├── generated_premium_web.md
    └── triage_prompt_engineer.md
```

## Training on Apple Silicon (MLX)

```bash
# Automatically detected. If mlx-lm is available, it's preferred.
python train.py --train-role general --iters 2000
```

MLX training on Apple Silicon:
- Trains directly on the Neural Engine / GPU
- LoRA adapters saved to `iris_adapters/{role}/`
- Merging uses `mlx_lm.fuse`
- Generally faster than PyTorch on Mac

## Training on CUDA / CPU

```bash
# Falls back to PyTorch + PEFT when MLX is not available
python train.py --train-role code --iters 2000 --batch-size 2
```

## Learning Rate Guidelines

| Model Size | Recommended LR |
|------------|----------------|
| 0.5B–3B | 3e-5 to 5e-5 |
| 7B–9B | 2e-5 to 3e-5 |
| 14B–32B | 1e-5 to 2e-5 |
| 70B+ | 5e-6 to 1e-5 |

## LoRA Layer Count

`--num-layers` controls how many transformer layers get LoRA adapters:

| Goal | `--num-layers` |
|------|---------------|
| Fast experiment | 8 |
| Balanced (default) | 16 |
| Maximum quality | 32 (all layers) |

## Adding Custom Training Data

### Method 1 — Local Markdown
1. Create a `.md` file with `USER:`/`BOT:` pairs
2. Drop it in the appropriate `training/` subfolder
3. Run training — file is picked up automatically

### Method 2 — HuggingFace Dataset
1. Add entry to `config/datasets.json` under the target role
2. The generic loader auto-detects common schemas: `messages`, `prompt`/`response`, `instruction`/`output`, `conversations`

### Method 3 — CLI Dataset
```bash
python train.py --train-role code --code-feedback 2000
```

## Skip GGUF for Faster Iteration

During experimentation:
```bash
python train.py --train-role code --skip-gguf
```

Test the raw adapter directly. When satisfied:
```bash
python train.py --train-role code --iters 0 --skip-training
# (converts existing adapter to GGUF without re-training)
```

## Output Files

```
models/
├── iris_001.gguf  (triage)
├── iris_004.gguf  (router)
├── iris_003.gguf  (control)
├── iris_004.gguf  (math)
├── iris_005.gguf  (code)
├── iris_006.gguf  (reasoning)
├── iris_007.gguf  (general)
└── iris_008.gguf  (vision)

iris_adapters/     (intermediate LoRA weights)
├── triage/
├── code/
├── math/
└── ...
```

## Total Training Data Statistics

| Role | Local Files | Approx Training Pairs |
|------|------------|----------------------|
| Code | 1,200+ `.md` files | 120,000+ pairs |
| Reasoning | 4 `.md` files | 5,000+ pairs |
| Math | 3 `.md` files | 20,000+ pairs |
| General | 17 `.md` files | 15,000+ pairs |
| Shared | 5 `.md` files | 3,000+ pairs |
