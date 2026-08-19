import os
os.environ["GGML_CUDA_NO_VMM"] = "1"
os.environ["OMP_WAIT_POLICY"] = "passive"
os.environ["OMP_NUM_THREADS"] = "4"
os.environ["OPENBLAS_NUM_THREADS"] = "4"
os.environ["MKL_NUM_THREADS"] = "4"
os.environ["VECLIB_MAXIMUM_THREADS"] = "4"
os.environ["NUMEXPR_NUM_THREADS"] = "4"
import json
import time
import uuid
from flask import Flask, request, jsonify, Response
from src.core.controller import ai_agent_handle, ai_agent_handle_pro
from src.core import controller

# Ensure interactive mode is off for background server
controller.IS_INTERACTIVE = False

app = Flask(__name__)

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

def generate_chat_id():
    return f"chatcmpl-{uuid.uuid4().hex}"

def generate_response_id():
    return f"resp-{uuid.uuid4().hex}"


@app.route("/v1/models", methods=["GET", "OPTIONS"])
def list_models():
    if request.method == "OPTIONS":
        return jsonify({}), 200
    """Dummy endpoint to list models to satisfy some clients."""
    return jsonify({
        "object": "list",
        "data": [
            {"id": "iris-local", "object": "model", "created": int(time.time()), "owned_by": "iris"},
            {"id": "iris-pro", "object": "model", "created": int(time.time()), "owned_by": "iris"}
        ]
    })


def extract_text(content_data):
    if isinstance(content_data, list):
        text_parts = []
        for item in content_data:
            if isinstance(item, dict) and "text" in item:
                text_parts.append(item["text"])
        return " ".join(text_parts)
    return str(content_data)


def parse_request(data):
    """Normalize both Chat Completions ('messages') and Responses ('input')
    request shapes into (user_input, history)."""
    messages = data.get("messages")
    if not messages:
        messages = data.get("input", [])

    if not messages:
        if "prompt" in data:
            messages = [{"role": "user", "content": data["prompt"]}]
        else:
            return None, None, f"No messages provided. Keys found: {list(data.keys())}"

    user_input = extract_text(messages[-1].get("content", ""))

    history = []
    for msg in messages[:-1]:
        history.append({
            "role": msg.get("role", "user"),
            "content": extract_text(msg.get("content", ""))
        })

    return user_input, history, None


def consume_event(item):
    """Turn one controller event into a content string, or '' if it doesn't
    represent visible chat output.

    NOTE: "raw_response" is the FULL accumulated final answer (used internally
    for context-compaction bookkeeping), not an incremental delta. It must
    never be treated as visible content here, or the client sees the whole
    response duplicated at the end of the stream/message.
    "status" and "action_result" are progress/log events, not chat output.
    """
    if isinstance(item, dict):
        item_type = item.get("type")
        if item_type == "text":
            return item.get("content", "")
        elif item_type == "code":
            lang = item.get("language", "")
            code = item.get("code", "")
            return f"\n```{lang}\n{code}\n```\n"
        return ""
    elif isinstance(item, str):
        return item
    return ""


@app.route("/v1/chat/completions", methods=["POST", "OPTIONS"])
@app.route("/v1/responses", methods=["POST", "OPTIONS"])
def chat_completions():
    if request.method == "OPTIONS":
        return jsonify({}), 200
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.json
    try:
        with open("last_request.json", "w") as f:
            json.dump(data, f, indent=2)
    except OSError as e:
        print(f"DEBUG: could not write last_request.json: {e}")

    model = data.get("model", "iris-local")
    stream = data.get("stream", False)
    is_responses_api = request.path == "/v1/responses"

    user_input, history, err = parse_request(data)
    if err:
        return jsonify({"error": err}), 400

    chat_id = generate_chat_id()
    response_id = generate_response_id()
    item_id = f"msg-{uuid.uuid4().hex}"
    created = int(time.time())

    is_pro = "pro" in model.lower()

    def get_generator():
        from src.iris.engine import _model_pool, _model_paths, ModelRole, load_model
        from llama_cpp import Llama
        import gc

        # We must load a model with a manageable context size (32768) 
        # to prevent llama_decode returned -1. 32768 causes memory 
        # allocation failures on Mac, but 16384 is too small for 
        # OpenCode's massive 7.6k token prompt + generation length.
        if "opencode" not in _model_pool:
            import logging
            iris_logger = logging.getLogger('iris')
            old_level = iris_logger.level
            # Suppress INFO logs (like 'Instantiating Llama') for OpenCode
            iris_logger.setLevel(logging.WARNING)
            
            try:
                for k in list(_model_pool.keys()):
                    del _model_pool[k]
                gc.collect()
                
                # Use the reasoning/code model (3B in tiny config)
                # We call load_model normally to ensure the path gets populated, 
                # but we bypass its returned instance to create one with a custom n_ctx.
                # _model_paths is populated during initialization.
                path = _model_paths.get(ModelRole.CODE)
                if not path:
                    # Fallback to loading via iris_engine if _model_paths isn't fully populated
                    load_model(ModelRole.CODE, override_n_ctx=32768)
                    if ModelRole.CODE.value in _model_pool:
                        _model_pool["opencode"] = _model_pool[ModelRole.CODE.value]
                    else:
                        path = _model_paths.get(ModelRole.CODE)
                        _model_pool["opencode"] = Llama(
                            model_path=path,
                            n_gpu_layers=-1,
                            n_ctx=32768,
                            n_batch=1024,
                            verbose=False
                        )
                else:
                    _model_pool["opencode"] = Llama(
                        model_path=path,
                        n_gpu_layers=-1,
                        n_ctx=32768,
                        n_batch=1024,
                        verbose=False
                    )
            finally:
                iris_logger.setLevel(old_level)
            
        llm = _model_pool["opencode"]
        
        # Get raw messages directly from the request
        raw_msgs = data.get("messages")
        if not raw_msgs:
            raw_msgs = data.get("input", [])
            
        valid_msgs = []
        for m in raw_msgs:
            if m.get("role") in ["system", "user", "assistant"]:
                valid_msgs.append({
                    "role": m.get("role"),
                    "content": extract_text(m.get("content", ""))
                })
                
        has_assistant_code = any(m["role"] == "assistant" and "```" in m["content"] for m in valid_msgs)
        
        # Do not force a patch if the user is explicitly asking to continue a truncated block
        is_continue_request = valid_msgs and valid_msgs[-1]["role"] == "user" and valid_msgs[-1]["content"].strip().lower() in ["continue", "go on", "keep going", "continue code"]
        is_modification_request = valid_msgs and valid_msgs[-1]["role"] == "user" and any(word in valid_msgs[-1]["content"].lower() for word in ["change", "edit", "fix", "update", "add", "remove", "make it", "instead", "replace"])
        
        if has_assistant_code and is_modification_request and not is_continue_request:
            reminder = (
                "\n\n[CRITICAL SYSTEM REMINDER: You are modifying an existing file. "
                "DO NOT rewrite the entire file or output <!DOCTYPE html>. "
                "You MUST output exactly one SEARCH/REPLACE block. You MUST strictly use the 4-character markers (<<<<, ====, >>>>). "
                "The SEARCH block must exactly match the existing code.]"
            )
            valid_msgs[-1]["content"] += reminder
                
        import threading
        if not hasattr(llm, "inference_lock"):
            llm.inference_lock = threading.Lock()
            
        def safe_stream():
            with llm.inference_lock:
                generator = llm.create_chat_completion(
                    messages=valid_msgs,
                    tools=data.get("tools"),
                    tool_choice=data.get("tool_choice", "auto"),
                    stream=True,
                    temperature=0.2,
                    max_tokens=4096
                )
                for chunk in generator:
                    yield chunk
                    
        for chunk in safe_stream():
            yield {"type": "raw_chunk", "chunk": chunk}

    # ---- Responses API (used by OpenCode's built-in "openai" provider) ----
    if is_responses_api:
        def responses_object(status, output):
            return {
                "id": response_id,
                "object": "response",
                "created_at": created,
                "status": status,
                "error": None,
                "incomplete_details": None,
                "model": model,
                "output": output,
                "parallel_tool_calls": True,
                "previous_response_id": None,
                "tool_choice": data.get("tool_choice", "auto"),
                "truncation": "disabled",
                "usage": None,
                "metadata": {},
            }

        if stream:
            def sse(event_type, payload, seq):
                payload = dict(payload)
                payload["type"] = event_type
                payload["sequence_number"] = seq
                return f"event: {event_type}\ndata: {json.dumps(payload)}\n\n"

            def stream_generator():
                seq = 0

                def emit(event_type, payload):
                    nonlocal seq
                    seq += 1
                    return sse(event_type, payload, seq)

                try:
                    gen = get_generator()
                except Exception as e:
                    yield emit("error", {"message": f"Iris failed to start generation: {e}"})
                    return

                yield emit("response.created", {"response": responses_object("in_progress", [])})
                yield emit("response.in_progress", {"response": responses_object("in_progress", [])})

                message_item = {
                    "id": item_id,
                    "type": "message",
                    "role": "assistant",
                    "status": "in_progress",
                    "content": [],
                }
                yield emit("response.output_item.added", {"output_index": 0, "item": message_item})
                yield emit("response.content_part.added", {
                    "item_id": item_id, "output_index": 0, "content_index": 0,
                    "part": {"type": "output_text", "text": "", "annotations": []},
                })

                full_text = ""
                gen_error = None
                try:
                    for item in gen:
                        if isinstance(item, dict) and item.get("type") == "raw_chunk":
                            raw = item["chunk"]
                            delta = raw["choices"][0].get("delta", {})
                            if "content" in delta and delta["content"]:
                                full_text += delta["content"]
                                yield emit("response.output_text.delta", {
                                    "item_id": item_id, "output_index": 0, "content_index": 0,
                                    "delta": delta["content"],
                                })
                            if "tool_calls" in delta:
                                # Not fully implemented for Responses API, just skip or handle later
                                pass
                            continue

                        content_chunk = consume_event(item)
                        if content_chunk:
                            full_text += content_chunk
                            yield emit("response.output_text.delta", {
                                "item_id": item_id, "output_index": 0, "content_index": 0,
                                "delta": content_chunk,
                            })
                except Exception as e:
                    gen_error = str(e)

                if gen_error:
                    # Surface the failure as visible text so it isn't a silent
                    # dropped connection (e.g. a local model context overflow).
                    err_text = f"\n\n[Iris Error] {gen_error}"
                    full_text += err_text
                    yield emit("response.output_text.delta", {
                        "item_id": item_id, "output_index": 0, "content_index": 0,
                        "delta": err_text,
                    })

                yield emit("response.output_text.done", {
                    "item_id": item_id, "output_index": 0, "content_index": 0, "text": full_text,
                })
                yield emit("response.content_part.done", {
                    "item_id": item_id, "output_index": 0, "content_index": 0,
                    "part": {"type": "output_text", "text": full_text, "annotations": []},
                })
                message_item["status"] = "completed"
                message_item["content"] = [{"type": "output_text", "text": full_text, "annotations": []}]
                yield emit("response.output_item.done", {"output_index": 0, "item": message_item})
                yield emit("response.completed", {"response": responses_object("completed", [message_item])})

            return Response(stream_generator(), mimetype="text/event-stream")
        else:
            try:
                gen = get_generator()
                full_text = ""
                for item in gen:
                    full_text += consume_event(item)
            except Exception as e:
                full_text = f"[Iris Error] {e}"

            message_item = {
                "id": item_id,
                "type": "message",
                "role": "assistant",
                "status": "completed",
                "content": [{"type": "output_text", "text": full_text, "annotations": []}],
            }
            return jsonify(responses_object("completed", [message_item]))

    # ---- Chat Completions API ----
    if stream:
        def stream_generator():
            try:
                gen = get_generator()
            except Exception as e:
                err_chunk = {
                    "id": chat_id, "object": "chat.completion.chunk", "created": created, "model": model,
                    "choices": [{"index": 0, "delta": {"content": f"[Iris Error] {e}"}, "finish_reason": "stop"}],
                }
                yield f"data: {json.dumps(err_chunk)}\n\n"
                yield "data: [DONE]\n\n"
                return

            initial_chunk = {
                "id": chat_id,
                "object": "chat.completion.chunk",
                "created": created,
                "model": model,
                "choices": [{"index": 0, "delta": {"role": "assistant"}, "finish_reason": None}]
            }
            yield f"data: {json.dumps(initial_chunk)}\n\n"

            try:
                for item in gen:
                    if isinstance(item, dict) and item.get("type") == "raw_chunk":
                        raw = item["chunk"]
                        raw["id"] = chat_id
                        raw["model"] = model
                        yield f"data: {json.dumps(raw)}\n\n"
                        continue

                    content_chunk = consume_event(item)
                    if content_chunk:
                        chunk = {
                            "id": chat_id,
                            "object": "chat.completion.chunk",
                            "created": created,
                            "model": model,
                            "choices": [{"index": 0, "delta": {"content": content_chunk}, "finish_reason": None}]
                        }
                        yield f"data: {json.dumps(chunk)}\n\n"
            except Exception as e:
                err_chunk = {
                    "id": chat_id, "object": "chat.completion.chunk", "created": created, "model": model,
                    "choices": [{"index": 0, "delta": {"content": f"\n\n[Iris Error] {e}"}, "finish_reason": None}],
                }
                yield f"data: {json.dumps(err_chunk)}\n\n"

            final_chunk = {
                "id": chat_id,
                "object": "chat.completion.chunk",
                "created": created,
                "model": model,
                "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}]
            }
            yield f"data: {json.dumps(final_chunk)}\n\n"
            yield "data: [DONE]\n\n"

        return Response(stream_generator(), mimetype="text/event-stream")
    else:
        try:
            gen = get_generator()
            full_text = ""
            for item in gen:
                full_text += consume_event(item)
        except Exception as e:
            full_text = f"[Iris Error] {e}"

        response_data = {
            "id": chat_id,
            "object": "chat.completion",
            "created": created,
            "model": model,
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": full_text
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0
            }
        }
        return jsonify(response_data)

if __name__ == "__main__":
    print("Starting Iris API (OpenAI Compatible) on port 8000...")
    app.run(host="0.0.0.0", port=8000, threaded=True)
