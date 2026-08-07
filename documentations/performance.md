# Iris AI — Performance & Optimization

## Latency Budget

For a typical query through the full pipeline:

| Phase | Time (Medium Tier, M2) | Time (Max Tier, M2 Ultra) |
|-------|----------------------|--------------------------|
| Triage classification | ~300ms | ~500ms |
| Model load/unload | ~1-2s (3B→14B) | ~3-5s (32B→70B) |
| Specialist inference | ~2-5s (200 tokens) | ~3-8s (200 tokens) |
| **Total (cold)** | **3-7s** | **6-13s** |
| **Total (hot, same role)** | **2-5s** | **3-8s** |

## Bottlenecks by Order of Impact

1. **Model loading** (1-5s) — Disk I/O to read GGUF into RAM
2. **Token generation** (20-50ms/token) — Autoregressive, cannot be parallelized
3. **Prompt processing** (500ms-2s) — Full context window prefill
4. **Python overhead** (50-100ms) — Negligible relative to inference

## Optimization Techniques

### 1. Keep Models Hot (Recommended)
```python
# In iris.conf:
# Future: "keep_models_hot": true
# Keeps frequently-used models in RAM instead of unload/reload
```

Currently models are unloaded after each request. A hot model cache would eliminate the 1-5s load penalty for repeat queries to the same role.

### 2. GPU Layer Offloading
```json
// iris.conf
"n_gpu_layers": -1    // Offload ALL layers to GPU (fastest)
"n_gpu_layers": 0     // CPU only (slowest)
"n_gpu_layers": 33    // Offload 33 layers (balance RAM usage)
```

**Metal (Apple Silicon):**
- Offload all layers if RAM permits (unified memory)
- Each offloaded layer ≈ 200-500MB depending on model size

**CUDA (NVIDIA):**
- Offload as many layers as VRAM allows
- Remaining layers run on CPU — slower but preserves VRAM for other tasks

### 3. Context Window Sizing
```json
"n_ctx_allocation": "auto"   // Dynamically scales context (4096-32768) based on available system RAM
"n_ctx_allocation": 4096     // Smaller = faster prefill, less RAM
"n_ctx_allocation": 8192     // Larger = handles bigger inputs, more RAM
```

**Rule of thumb:** Use `"auto"` to let the system safely maximize context based on your RAM. The triage model only needs 512 tokens, so dynamic scaling prevents wasting RAM and slowing prefill.

### 3.1. Compacting Profile
```json
"compacting_profile": "medium"     // Keeps last 5 messages when near context limit
"compacting_profile": "aggressive" // Keeps last 2 messages (saves most context)
"compacting_profile": "low"        // Keeps last 10 messages (highest memory use)
```

### 4. Thread Count
```json
"n_threads": 8     // Match physical core count
"n_threads": 4     // Leave cores for other processes
```

Performance scales nearly linearly with threads up to the physical core count. Hyper-threading (logical cores) provides minimal additional benefit for inference.

### 5. Quantization Tradeoff
```
Q4_K_M → 4-bit, fast, ~95% quality      (RECOMMENDED)
Q5_K_M → 5-bit, medium speed, ~97%      (Better quality)
Q8_0   → 8-bit, slow, ~99%              (Near-lossless)
F16    → 16-bit, slowest, 100%           (Lossless)
```

For most tasks, Q4_K_M is indistinguishable from higher quants. Upgrade to Q5_K_M or Q8_0 only if you notice quality issues and have spare RAM.

### 6. Batch Processing
Future optimization: When multiple users query the same model, batch their prompts together. llama.cpp supports continuous batching — 2x-4x throughput improvement for concurrent users.

## Hardware-Specific Tuning

### Apple Silicon (M1/M2/M3)
```json
{
  "n_gpu_layers": -1,
  "n_threads": 4,
  "n_ctx_allocation": "auto"
}
```
- Metal backend uses unified memory — no CPU↔GPU transfer overhead
- Neural Engine is NOT used by llama.cpp (only GPU)
- M2 Ultra (192GB) can run the entire Max tier with layers to spare

### NVIDIA GPU
```json
{
  "n_gpu_layers": 99,
  "n_threads": 8,
  "n_ctx_allocation": "auto"
}
```
- CUDA backend is mature and highly optimized
- Watch VRAM usage: each offloaded layer = model_size / num_layers bytes
- Use `nvidia-smi` to monitor

### CPU-Only (Server / Cloud)
```json
{
  "n_gpu_layers": 0,
  "n_threads": 16,
  "n_ctx_allocation": "auto"
}
```
- AVX2/AVX512 acceleration is automatic in llama.cpp
- Each additional thread improves latency up to physical core count
- RAM bandwidth is the main bottleneck (not compute)

## Memory Usage Estimates

| Model Size | Q4_K_M Size | RAM at Runtime | VRAM if Offloaded |
|------------|------------|----------------|-------------------|
| 0.5B | 0.4 GB | 1.0 GB | 0.5 GB |
| 3B | 2.0 GB | 3.5 GB | 2.5 GB |
| 7B | 4.5 GB | 7.0 GB | 5.0 GB |
| 14B | 9.0 GB | 13.0 GB | 10.0 GB |
| 32B | 20.0 GB | 28.0 GB | 22.0 GB |
| 70B | 42.0 GB | 55.0 GB | 45.0 GB |
| 72B | 43.0 GB | 56.0 GB | 46.0 GB |

Runtime RAM = model size + context buffer + overhead. Add ~500MB for the Python process.

## Benchmarking Your Setup

```bash
# Time a query end-to-end:
time curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Explain quantum computing in one paragraph", "chat_id": "test"}'

# Profile model loading:
python -c "
import time
from src.iris import load_model, ModelRole, unload_model
t0 = time.time()
llm = load_model(ModelRole.CODE)
print(f'Load: {time.time()-t0:.1f}s')
t0 = time.time()
llm.create_chat_completion(messages=[{'role':'user','content':'hi'}], max_tokens=10)
print(f'Inference: {time.time()-t0:.1f}s')
unload_model()
"
```

## Production Deployment

For serving Iris to multiple users:

1. **Run multiple instances** — one per GPU/CPU set
2. **Load balance** via nginx or similar
3. **Pin models to instances**: Instance A always has code model loaded, Instance B always has general
4. **Use larger models**: The Max tier on a dedicated server
5. **Cache common responses**: Simple queries that return identical answers
6. **Async I/O**: Flask + gunicorn with gevent for concurrent connections
