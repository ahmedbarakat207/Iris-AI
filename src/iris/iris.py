import re
import json
import logging
from typing import Generator, Dict
import threading
import os
from src.iris.engine import (
    TaskType,
    ModelRole,
    _keep_loaded,
    detect_user_language,
    translate_text,
    prefetch_model_file,
    _get_model_filename,
    _quality_guard,
)
import src.iris.engine
from src.iris.vision import analyze_image
from src.iris.triage import classify_task
from src.iris.control import run_stream as control_run_stream
from src.iris.reasoning import run_stream as reasoning_run_stream
from src.iris.general import run_stream as general_run_stream
from src.iris.math import run_stream as math_run_stream
from src.iris.coding import run_stream as coding_run_stream

logger = logging.getLogger("iris")


def ask_stream(
    user_query: str,
    history: list = None,
    stream: bool = True,
    retriever=None,
    settings: dict = None,
    force_role=None,
    keep_loaded: bool = False,
    **kwargs,
) -> Generator[Dict[str, str], None, None]:
    if history is None:
        history = []
    if settings is None:
        settings = {}

    kw_en_pattern = (
        r"\b(?:backend|server|api|full stack|full-stack|node|express|skeleton)\b"
    )
    kw_ar_pattern = r"(?:هيكل|قالب|فراغات)"

    import re

    lower_q = user_query.lower()
    is_fullstack = bool(
        re.search(
            r"\b(?:backend|server|api|full stack|full-stack|node|express)\b", lower_q
        )
    )
    is_skeleton = bool(re.search(r"\b(?:skeleton)\b", lower_q)) or bool(
        re.search(r"(?:هيكل|قالب|فراغات)", lower_q)
    )

    settings["is_fullstack"] = is_fullstack
    settings["is_skeleton"] = is_skeleton

    try:
        import threading

        def _bg_prefetch():
            try:
                from src.iris.engine import (
                    prefetch_model_file,
                    _get_model_filename,
                    ModelRole,
                )

                for r in [ModelRole.GENERAL, ModelRole.CODE]:
                    try:
                        prefetch_model_file(_get_model_filename(r))
                    except Exception:
                        pass
            except Exception:
                pass

        threading.Thread(target=_bg_prefetch, daemon=True).start()
    except Exception:
        pass

    original_query = user_query
    img_match = re.match(
        r"^\[IMAGE_UPLOADED:\s*(.+?)\]\s*(.*)$", user_query, flags=re.DOTALL
    )
    if img_match:
        image_path = img_match.group(1).strip()
        prompt = img_match.group(2).strip()
        if not prompt:
            prompt = "Describe this image in detail."
        yield {"type": "status", "content": "Analyzing image with Vision model..."}
        from src.iris.vision import analyze_image

        res = analyze_image(image_path, prompt, unload_after=not keep_loaded)

        try:
            import os

            os.unlink(image_path)
        except Exception:
            pass

        yield {"type": "token", "content": res}
        yield {"type": "raw_response", "content": res}
        return
    direct_answer = ""

    src.iris.engine._keep_loaded = keep_loaded

    user_lang = detect_user_language(user_query)
    is_translated = False

    if user_lang and user_lang != "English":
        translated_query = translate_text(user_query, "English")
        if translated_query and translated_query != user_query:
            user_query = translated_query
            is_translated = True
            settings["user_lang"] = user_lang

        if history:
            translated_history = []
            for msg in history:
                role = msg.get("role")
                content = msg.get("content", "")
                if detect_user_language(content) != "English":
                    translated_content = translate_text(content, "English")
                else:
                    translated_content = content
                translated_history.append({"role": role, "content": translated_content})
            history = translated_history

    task_type_override = None
    if user_query.strip().startswith("/route "):
        parts = user_query.strip().split(" ", 2)
        if len(parts) >= 3:
            route_name = parts[1].lower()
            if route_name == "code_complex":
                route_name = "coding_complex"
            elif route_name == "code_simple":
                route_name = "coding_simple"

            for t in TaskType:
                if t.value.lower() == route_name:
                    task_type_override = t
                    user_query = parts[2]
                    break

    if task_type_override:
        task_type = task_type_override
        direct_answer = ""
    elif force_role:
        if isinstance(force_role, str):
            try:
                force_role = ModelRole(force_role)
            except ValueError:
                pass

        role_map = {
            ModelRole.CODE: TaskType.CODING_COMPLEX,
            ModelRole.MATH: TaskType.MATH,
            ModelRole.REASONING: TaskType.REASONING,
            ModelRole.GENERAL: TaskType.GENERAL,
            ModelRole.CONTROL: TaskType.CONTROL,
        }
        task_type = role_map.get(force_role, None)
        if task_type is None:
            from src.iris.triage import classify_task

            task_type, direct_answer = classify_task(user_query, history)
    else:
        from src.iris.triage import classify_task

        task_type, direct_answer = classify_task(user_query, history)

    if task_type == TaskType.CODING_SIMPLE:
        q_clean = user_query.strip().lower()

        if len(q_clean) < 50 and any(
            op in q_clean
            for op in ["+", "-", "*", "/", "=", "sin", "cos", "tan", "log"]
        ):

            if not any(
                cw in q_clean
                for cw in ["code", "python", "script", "c++", "html", "css"]
            ):
                task_type = TaskType.MATH

    gen = None
    if task_type == TaskType.CONTROL:
        from src.iris.control import run_stream

        gen = run_stream(user_query, history, retriever, settings)

    elif task_type == TaskType.SEARCH:
        from src.iris.reasoning import run_stream

        gen = run_stream(
            user_query,
            history,
            retriever,
            settings,
            do_search=True,
            direct_answer=direct_answer,
        )

    elif task_type is None:
        if direct_answer:
            cleaned = _quality_guard(direct_answer)
            if is_translated:
                cleaned = translate_text(cleaned, user_lang)
            yield {"type": "token", "content": cleaned}
            yield {"type": "raw_response", "content": cleaned}
        return
    else:
        yield {"type": "status", "content": f"Task: {task_type.value.upper()}"}
        if task_type == TaskType.GENERAL:
            from src.iris.general import run_stream

            gen = run_stream(user_query, history, retriever, settings)
        elif task_type == TaskType.REASONING:
            from src.iris.reasoning import run_stream

            gen = run_stream(user_query, history, retriever, settings, do_search=False)
        elif task_type == TaskType.MATH:
            from src.iris.math import run_stream

            gen = run_stream(user_query, history, retriever, settings)
        elif task_type == TaskType.CODING_SIMPLE:
            from src.iris.coding import run_stream

            gen = run_stream(user_query, history, retriever, settings, is_complex=False)
        elif task_type == TaskType.CODING_COMPLEX:
            from src.iris.coding import run_stream

            gen = run_stream(user_query, history, retriever, settings, is_complex=True)

    if gen is not None:
        yield from gen
