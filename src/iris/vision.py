import os
import gc
import json
import threading
import logging
import re
from llama_cpp import Llama
import llama_cpp
from src.iris.iris.engine import load_generation_config, ModelRole, _HERE, ROLE_CTX

logger = logging.getLogger("iris")

CONFIG_PATH = os.path.join(_HERE, "..", "config", "iris.conf")

_vision_cache: dict = {}
_vision_lck = threading.Lock()


def _load_vision_model():
    global _vision_cache
    if _vision_cache:
        return _vision_cache

    with _vision_lck:
        if _vision_cache:
            return _vision_cache

        cfg = load_generation_config()
        models_dict = cfg.get("models", {})

        vision_file = models_dict.get("vision", "InternVL3_5-4B-Q4_K.gguf")
        clip_file = models_dict.get("clip", "mmproj-InternVL3_5-4B-f16.gguf")

        models_dir = os.path.join(os.path.dirname(_HERE), "models")
        vision_path = os.path.join(models_dir, vision_file)
        clip_path = os.path.join(models_dir, clip_file)

        if os.path.exists(vision_path):
            if "Qwen2.5-VL" in vision_file:
                logger.info(
                    "[Vision] Qwen2.5-VL GGUF projector is known to fail in llama.cpp. Forcing MLX backend."
                )
            else:
                logger.info(f"[Vision] Loading GGUF vision model: {vision_file}...")
                try:
                    n_gpu_layers = cfg.get("n_gpu_layers", -1)
                    n_threads = cfg.get("n_threads", 8)

                    chat_handler = None
                    if clip_file and os.path.exists(clip_path):
                        logger.info(f"[Vision] Found clip projector: {clip_file}")
                        from llama_cpp.llama_chat_format import Llava15ChatHandler

                        chat_handler = Llava15ChatHandler(
                            clip_model_path=clip_path, verbose=False
                        )

                    _main_gpu = cfg.get("main_gpu", 0)
                    model_kwargs = {
                        "model_path": vision_path,
                        "n_ctx": ROLE_CTX.get(ModelRole.VISION, 4096),
                        "n_gpu_layers": n_gpu_layers,
                        "n_threads": n_threads,
                        "flash_attn": cfg.get("flash_attn", True),
                        "type_k": getattr(llama_cpp, "LLAMA_FTYPE_MOSTLY_Q8_0", 7),
                        "type_v": getattr(llama_cpp, "LLAMA_FTYPE_MOSTLY_Q8_0", 7),
                        "verbose": False,
                        "main_gpu": _main_gpu,
                    }
                    if chat_handler:
                        model_kwargs["chat_handler"] = chat_handler

                    model = Llama(**model_kwargs)
                    _vision_cache = {"model": model, "backend": "gguf"}
                    logger.info("[Vision] GGUF vision model ready.")
                    return _vision_cache
                except Exception as e:
                    logger.info(
                        f"[Vision] GGUF VLM load failed: {e}. Falling back to MLX..."
                    )
        try:
            from mlx_vlm import load as vlm_load
            from mlx_vlm.utils import load_config as vlm_load_config

            mlx_repo = "mlx-community/Qwen2-VL-7B-Instruct-4bit"
            try:
                active_size = cfg.get("size", "tiny")
                size_path = os.path.join(
                    os.path.dirname(CONFIG_PATH), "sizes", f"{active_size}.json"
                )
                if os.path.exists(size_path):
                    with open(size_path) as f:
                        size_cfg = json.load(f)
                    size_vision = size_cfg.get("models", {}).get("vision")
                    if size_vision:
                        mlx_repo = size_vision
            except Exception:
                pass

            if mlx_repo == "Qwen/Qwen2.5-VL-3B-Instruct":
                mlx_repo = "mlx-community/Qwen2.5-VL-3B-Instruct-4bit"
            elif mlx_repo == "Qwen/Qwen2.5-VL-7B-Instruct":
                mlx_repo = "mlx-community/Qwen2.5-VL-7B-Instruct-4bit"
            logger.info(f"[Vision] Loading MLX vision model: {mlx_repo}...")
            model, processor = vlm_load(mlx_repo)
            config = vlm_load_config(mlx_repo)
            _vision_cache = {
                "model": model,
                "processor": processor,
                "config": config,
                "backend": "mlx",
            }
            logger.info("[Vision] MLX vision model ready.")
            return _vision_cache
        except Exception as e:
            logger.info(f"[Vision] MLX VLM load failed: {e}")
            return {}


def unload_vision_model() -> None:
    global _vision_cache
    with _vision_lck:
        if not _vision_cache:
            return
        backend = _vision_cache.get("backend")
        _vision_cache.pop("model", None)
        _vision_cache.clear()
        _vision_cache = {}
        if backend != "gguf":
            try:
                import mlx.core as mx

                mx.clear_cache()
            except Exception:
                pass
        gc.collect()
        if backend:
            logger.info(
                f"[Vision] Vision model ({backend}) unloaded \u2014 unified memory reclaimed."
            )


def analyze_image(
    image_path: str,
    prompt: str = "Describe this image in detail.",
    unload_after: bool = True,
) -> str:
    vision = _load_vision_model()
    if not vision:
        return "[Vision] Vision model not available."

    backend = vision.get("backend")
    model = vision["model"]

    if backend == "gguf":
        try:
            import base64

            with open(image_path, "rb") as f:
                img_data = f.read()
            img_b64 = base64.b64encode(img_data).decode("utf-8")
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"},
                        },
                    ],
                }
            ]
            res = model.create_chat_completion(messages=messages, max_tokens=512)
            return res["choices"][0]["message"]["content"].strip()
        except Exception as e:
            return f"[Vision] GGUF Analysis failed: {e}"
        finally:
            if unload_after:
                unload_vision_model()

    elif backend == "mlx":
        proc = vision["processor"]
        conf = vision.get("config")
        try:
            from mlx_vlm import generate as vlm_generate
            from mlx_vlm.prompt_utils import apply_chat_template

            formatted = apply_chat_template(proc, conf, prompt, num_images=1)
            result = vlm_generate(
                model, proc, formatted, image_path, max_tokens=512, verbose=False
            )
            if hasattr(result, "text"):
                return result.text.strip()
            return str(result).strip()
        except Exception as e:
            return f"[Vision] MLX Analysis failed: {e}"
        finally:
            if unload_after:
                unload_vision_model()

    return "[Vision] Unknown backend."
