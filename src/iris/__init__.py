from .iris import ask_stream
from .engine import (
    download_gguf,
    load_model,
    unload_model,
    ModelRole,
    TaskType,
    get_device,
    load_generation_config,
    detect_user_language,
    translate_text,
    prefetch_model_file,
    _get_model_filename,
    _quality_guard,
    _force_unload_all_models,
)
from .vision import analyze_image, unload_vision_model, _vision_cache
from .rag import BookRetriever
from .coding import get_code_prompt, get_reviewer_prompt, generate_internal_code
from .triage import classify_task, TRIAGE_SYSTEM_PROMPT
from .control import get_control_prompt
from .general import get_general_prompt
from .math import get_math_prompt
from .reasoning import get_reasoning_prompt
from .datasets import DatasetRegistry, load_markdown_files
