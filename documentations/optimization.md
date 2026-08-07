# Technical Specification: Memory and KV-Cache Context Optimization

Iris AI manages memory constraints across two critical vectors: VRAM weight allocation (Hardware Mapping) and KV-Cache expansion (Context Compactor).

## 1. Hardware RAM/VRAM Scheduling (`src/iris.py`)

### 1.1 Sequential `llama-cpp-python` Loading
Multi-agent mixtures typically require loading all models into VRAM simultaneously. Iris AI forces strict sequential allocation via `load_model(role: ModelRole)`. 
- Executing `load_model` unconditionally calls `unload_model()` to clear the existing `Llama` pointer and issues Python garbage collection `gc.collect()`.
- Maximum peak VRAM consumption is strictly bounded to `max(size(M_triage), size(M_target)) + KV_Cache`.

### 1.2 Multi-threading Deadlock Protection
Concurrency at the Flask web server or terminal agent level could trigger overlapping `load_model` calls, resulting in catastrophic Out-Of-Memory (OOM) SEGFAULTS in the backend. 
- Iris AI wraps the loader in a global threading primitive `_model_lock = threading.Lock()`.
- A request will dynamically acquire the lock, spawn its target model via `mmap`, generate the token stream, and release the lock safely.

GGUF loading relies on `use_mmap=True`. Instead of copying a 40GB `Iris AI` tensor layer into physical RAM, it maps the NVMe file descriptor to the virtual address space. Page fault latency between sequential model swaps runs on the order of 10-50ms on modern PCIe Gen 4 SSDs.

---

## 2. Context Compactor Algorithm (`src/context_compactor.py`)

LLM inference KV-Cache scales linearly (or quadratically in some attention implementations) with sequence length. Iris AI uses a deterministic Compaction Matrix to prune chat history.

### 2.1 Heuristic Token Estimation
Instead of running expensive exact tokenizer encoding calls per message, `estimate_tokens` applies a fast character ratio:
```python
total_tokens = len(non_code_text) // 4 + sum(len(cb) // 3 for cb in code_blocks) + 54
```
It computes an `available_ctx` threshold: `n_ctx - 256 - max_output_tokens`.

### 2.2 Threshold Ratio Trigger (`CompactionLevel.AUTOMATIC`)
`ratio = estimated / max(available_ctx, 1)`
- `ratio <= 0.5` → **Level 0 (NONE)**
- `ratio <= 1.0` → **Level 1 (LIGHT)**
- `ratio <= 2.0` → **Level 2 (MEDIUM)**
- `ratio > 2.0`  → **Level 3 (AGGRESSIVE)**

### 2.3 Compaction Handlers

#### Level 1: `LIGHT`
No LLM summarization. Applies rigid regex to discard heavy markdown while maintaining conversational structure.
- Substitutes `r'```[\s\S]*?```'` with `[code block omitted — preserved in digest]`.
- Truncates strings `> 500` chars dynamically, using `max(rfind('.'), rfind('!'), rfind('?'))` to cut at the nearest linguistic boundary.

#### Level 2: `MEDIUM`
Extracts `old_messages = messages[:-4]` and `recent_messages = messages[-4:]`.
- Iterates `old_messages` into a compressed format string and passes it directly to `ModelRole.TRIAGE` at `temperature=0.1`.
- The Triage model generates a dense, factual `system` block under 250 tokens tracking original goals, bugs, and paths.
- **Result Output Array**: `[ {role: "system", content: "[DIGEST]\n..."} ] + recent_messages`
- **Fallback**: If `TRIAGE` fails or crashes, triggers `_extractive_fallback()`, which blindly slices the first 200 characters of the first 3 lines of each message.

#### Level 3: `AGGRESSIVE`
Identical logic to `MEDIUM`, but strictly enforces `messages[-2:]`. 
- To preserve maximum context window, it heavily mutates the final User string payload, prepending it with a violently truncated 300-char string of the digest output: `[Previous context heavily summarized... {summary[:300]}] \n\n {original_msg}`.
