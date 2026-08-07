# Iris AI — API Reference

## Web API (Flask)

Base URL: `http://localhost:5000`

### `GET /`
Render the web chat interface.

**Response:** HTML page (`templates/index.html`)

---

### `POST /chat`
Send a message and receive a streaming SSE response.

**Request:**
```json
{
  "chat_id": "abc123",
  "message": "Write a Python function to sort a list",
  "history": "[{\"role\": \"user\", \"content\": \"...\"}]",
  "settings": {
    "temperature": 0.4,
    "max_tokens": 4096
  }
}
```

Or as multipart form (with optional image upload):
```
message=Analyze this image
image=<file upload>
chat_id=abc123
```

**Response:** Server-Sent Events stream

```
data: {"type": "status", "content": "Routing to: CODING_SIMPLE"}

data: {"type": "token", "content": "def"}

data: {"type": "token", "content": " sort"}

data: {"type": "token", "content": "_list"}

...

data: {"type": "done", "content": "def sort_list(arr):\n    return sorted(arr)"}

data: {"type": "stats", "content": "1.2s, 45 tokens"}

data: {"type": "action_result", "content": "Code generated successfully"}
```

### Event Types

| Type | Description | Example Content |
|------|-------------|-----------------|
| `status` | System status (routing decision) | `"Routing to: MATH"` |
| `token` | Incremental text token | `"def sort_list"` |
| `thinking` | Iris AI Reasoning thinking process | `"Let me analyze..."` |
| `done` | Complete response | Full generated text |
| `stats` | Performance statistics | `"1.2s, 45 tokens"` |
| `error` | Error message | `"Model failed to load: OOM"` |
| `action_result` | PC controller action result | `"File created: /path/to/file"` |

---

### `POST /train`
Trigger model training.

**Request:**
```json
{
  "role": "code",
  "iters": 2000,
  "size": "medium"
}
```

**Response:**
```json
{
  "status": "started",
  "role": "code",
  "output_file": "outputs/train_output.txt"
}
```

Training runs asynchronously in a subprocess. Output is written to `outputs/train_output.txt`.

---

### `GET /train/status`
Check training status.

**Response:**
```json
{
  "running": true,
  "role": "code",
  "progress": "Training iteration 450/2000"
}
```

---

### `POST /upload`
Upload an image for vision analysis.

**Request:** Multipart form with `image` file field.

**Response:**
```json
{
  "path": "uploads/image.png",
  "status": "uploaded"
}
```

---

### `GET /settings`
Get current inference settings.

**Response:**
```json
{
  "temperature": 0.4,
  "max_new_tokens": 4096,
  "size": "medium",
  "models": {
    "triage": "iris_001.gguf",
    "code": "iris_005.gguf"
  }
}
```

---

### `POST /settings`
Update inference settings (writes to `config/iris.conf`).

**Request:**
```json
{
  "temperature": 0.7,
  "max_new_tokens": 2048
}
```

---

## Pro Mode API (`iris_pro.py`)

When started with `--pro` flag, Iris runs a multi-agent pipeline:

### `POST /pro/chat`
Multi-agent chat with automatic task decomposition.

**Request:** Same as `/chat`.

**Response:** SSE stream with additional agent events:
```
data: {"type": "agent_start", "agent": "planner", "content": "Decomposing task..."}
data: {"type": "agent_output", "agent": "coder", "content": "```python...```"}
data: {"type": "agent_output", "agent": "reviewer", "content": "Fixed edge case..."}
data: {"type": "done", "content": "Final result"}
```

---

## Python API (`src/iris.py`)

### `ask_stream(user_query, history, retriever=None, force_role=None)`
Stream tokens from the appropriate specialist model.

```python
from src.iris import ask_stream

for event in ask_stream("What is quantum computing?", history=[]):
    if event["type"] == "token":
        print(event["content"], end="", flush=True)
```

### `load_model(role: ModelRole) -> Llama`
Load a model by role. Throws if model file not found.

```python
from src.iris import load_model, ModelRole

llm = load_model(ModelRole.CODE)
response = llm.create_chat_completion(messages=[...])
```

### `classify_task(user_query, history) -> Tuple[Optional[TaskType], Optional[str]]`
Classify a query. Returns `(TaskType, None)` if routed, `(None, answer)` if answered directly.

### `solve_math(user_query) -> Optional[str]`
Attempt to solve math directly. Returns solution or None.

### `BookRetriever(raw_data_dir)`
RAG knowledge base. Indexes documents and retrieves relevant chunks.

```python
retriever = BookRetriever(raw_data_dir="raw_data")
retriever.load_and_index()
context = retriever.retrieve("quantum computing", top_k=3)
```

### `analyze_image(image_path, prompt="Describe this image") -> str`
Analyze an image using the vision model.

---

## C++ Controller API

### Main entry point
```cpp
int main(int argc, char** argv) {
    json config = load_config();
    // Interactive loop: getline → detect_intent → dispatch
}
```

### Key functions (all in `controller.cpp`)
```cpp
// File operations
std::string handle_create_file(const std::string& path, const std::string& content);
std::string handle_read_file(const std::string& path);
std::string handle_delete_file(const std::string& path);
std::string handle_download_file(const std::string& url, const std::string& path);

// App & system
std::string handle_app_by_name(const std::string& name, const json& cfg);
std::string handle_volume(const std::string& action);
std::string handle_brightness(const std::string& action);
std::string handle_lock_screen();
std::string handle_media(const std::string& action);

// YouTube / Spotify
std::string handle_youtube_video_from_query(const std::string& query);
std::string handle_spotify_song(const std::string& query);

// Web search
std::string web_search(const std::string& query, int max_results=5);

// Intent detection
std::pair<std::string, std::smatch> detect_intent(const std::string& text);
```
