# Iris AI — Architecture

## High-Level Design

Iris AI uses a **multi-model routing architecture**. Instead of a single large model, 6-8 specialized GGUF models run sequentially. Only one model is loaded into RAM at any time.

```
                    ┌─────────────────────────────────┐
                    │         Iris AI System           │
                    └─────────────────────────────────┘
                                     │
                    User Query       │
                    ────────────────►│
                                     ▼
                    ┌─────────────────────────────────┐
                    │          app.py (Flask)          │
                    │  HTTP server, SSE streaming,     │
                    │  file upload, settings, chat API │
                    └──────────────┬──────────────────┘
                                   │
                    classify_task()│
                                   ▼
                    ┌─────────────────────────────────┐
                    │       TRIAGE MODEL (4B-32B)      │
                    │  Analyzes query intent           │
                    │  Outputs: [ROUTE: GENERAL]       │
                    │           [ROUTE: REASONING]     │
                    │           [ROUTE: MATH]          │
                    │           [ROUTE: CODE_SIMPLE]   │
                    │           [ROUTE: CODE_COMPLEX]  │
                    │    OR: answers directly          │
                    └──────────────┬──────────────────┘
                                   │
                    ┌──────────────┼──────────────┐
                    ▼              ▼              ▼
             ┌──────────┐  ┌──────────┐  ┌──────────┐
             │  GENERAL │  │   MATH   │  │REASONING │
             │  8B-70B  │  │  7B-72B  │  │ 14B-70B  │
             └──────────┘  └──────────┘  └──────────┘
                    │              │              │
                    └──────────────┼──────────────┘
                                   │
                            ┌──────┴──────┐
                            ▼             ▼
                     ┌──────────┐  ┌──────────┐
                     │   CODE   │  │  CODE    │
                     │  SIMPLE  │  │ COMPLEX  │
                     │  7B-32B  │  │ 14B-32B  │
                     └──────────┘  └──────────┘
```

## Component Map

```
app.py ──► src/iris.py ──► llama-cpp-python ──► GGUF models (.gguf files)
   │            │
   │            ├── classify_task()   ← Triage model
   │            ├── ask_stream()      ← Specialist model
   │            ├── solve_math()      ← Math model (direct)
   │            ├── analyze_image()   ← Vision model
   │            ├── BookRetriever     ← RAG knowledge base
   │            └── load_model()      ← Model lifecycle
   │
   ├── src/iris_pro.py   ← Multi-agent pipeline (Pro mode)
   ├── src/harness.py    ← Code/math output post-processing
   └── src/syntax_checker.py ← Syntax validation
```

## Data Flow

### 1. Web Chat Flow
```
Browser → POST /chat (SSE) → classify_task()
    → TRIAGE model classifies query
    → ask_stream() loads specialist model
    → Streams tokens via Server-Sent Events
    → Browser renders streaming text
```

### 2. PC Controller Flow
```
CLI input → detect_intent() → regex + keyword matching
    → Action dispatch (open app, run command, web search, etc.)
    → Optional: ai_agent_handle() → Iris LLM for complex tasks
    → Result printed to terminal
```

### 3. Training Flow
```
train.py --train-role code
    → Load datasets (HuggingFace + local Markdown)
    → Apply LoRA adapters via MLX (Apple) or PyTorch (CUDA/CPU)
    → Merge adapters into base model
    → Convert to GGUF format (via convert_hf_to_gguf.py)
    → Quantize (Q4_K_M by default)
    → Output: models/iris-code.gguf
```

### 4. Model Lifecycle
```
load_model(role)
    → Check if requested role already loaded (cached) → return
    → _unload_locked() frees current model from RAM
    → Llama(model_path, **ctx_params) loads new GGUF
    → _active_role, _active_llm set
    → Return Llama instance

unload_model()
    → _active_llm.reset() frees memory
    → gc.collect() runs Python garbage collector

Hot model optimization: if same role requested twice consecutively,
the model stays loaded. Switching roles triggers unload → reload.
```

## Key Design Decisions

### Why multi-model instead of one large model?
- **Specialization**: A 7B math model trained on math beats a 70B general model on math
- **Memory efficiency**: Only load what you need. 16GB RAM can serve 14B models one at a time
- **Modularity**: Swap individual specialists without retraining everything
- **Cost**: Smaller models train faster, require less hardware

### Why GGUF?
- **Quantized**: 4-bit models run on consumer hardware
- **Single file**: One `.gguf` file = model weights + tokenizer + metadata
- **llama.cpp ecosystem**: Battle-tested inference engine, Metal/CUDA/Vulkan backends
- **Portable**: Same file works on Mac, Windows, Linux, ARM

### Why LoRA for fine-tuning?
- **Parameter efficient**: Only 1-5% of weights modified, adapters are 50-200MB
- **Fast iteration**: Train a specialist in 30-60 minutes on consumer GPU
- **Mergeable**: LoRA adapters merge into base weights for GGUF conversion
- **Composable**: Multiple adapters could be combined (not yet implemented in Iris)

## System Context Windows

| Role | Context (tokens) | Rationale |
|------|-----------------|-----------|
| Triage | 2,048 | Only needs query + short routing tag |
| Router | 2,048 | JSON action matrices are compact |
| Math | 4,096 | Equations and step-by-step solutions |
| Code | 8,192 | Large code files, full apps |
| Reasoning | 2,048 | Design and strategy (compact prompts) |
| General | 4,096 | Broad knowledge, longer explanations |
| Vision | 4,096 | Image description + conversation |

## RAG (Retrieval-Augmented Generation)

The `BookRetriever` class indexes documents from `raw_data/` and retrieves relevant chunks:

```
User query → sentence-transformers embedding
    → Cosine similarity against indexed chunks
    → Top-k chunks injected into system prompt
    → Specialist model generates context-aware answer
```

Category-aware retrieval: if the router detects "medical", only medical documents are searched — faster and more relevant.

## Streaming Architecture

```
ask_stream() → load_model(role) → create_chat_completion(stream=True)
    → For each chunk:
        yield {"type": "token", "content": chunk_text}
    → On completion:
        yield {"type": "done", "content": full_response}

Iris AI Reasoning thinking mode:
    <think>...</think> blocks detected and separated
    think_mode="show" → yields thinking events
    think_mode="hide" → strips thinking, yields only final answer
    think_mode="status" → shows spinner during thinking
```

## Error Handling

- **Model not found**: Falls back to `config/sizes/{size}.json` → `download_gguf()` auto-downloads
- **OOM on load**: Smaller context window, fewer GPU layers
- **Streaming failure**: Falls back to non-streaming completion
- **RAG failure**: Continues without RAG (graceful degradation)
