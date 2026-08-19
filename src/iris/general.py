import re
from typing import Generator, Dict, Optional, Any
from src.iris.engine import (
    ModelRole,
    load_model,
    unload_model,
    _keep_loaded,
    _stream_tokens,
    load_generation_config,
    _quality_guard,
)

from src.iris.engine import (
    detect_user_language,
    _language_directive,
    translate_text,
    _load_skill_prompt,
    ModelRole,
)


def get_general_prompt(identity: str) -> str:
    prompt = _load_skill_prompt("general/general_prompt.txt")
    return f"{identity}\n{prompt}"


def run_stream(
    user_query: str, history: list, retriever: Any, settings: dict
) -> Generator[Dict[str, str], None, None]:
    import logging

    logger = logging.getLogger("iris")

    web_context = ""

    yield {"type": "status", "content": "Thinking..."}

    context = ""
    if retriever is not None and len(user_query.split()) >= 3:
        is_contextual = False
        if history:
            pronouns = re.compile(
                r"\b(he|him|his|she|her|it|its|they|them|this|that)\b", re.IGNORECASE
            )
            if len(user_query.split()) < 6 or pronouns.search(user_query):
                is_contextual = True

        if not is_contextual:
            context = retriever.retrieve(user_query, top_k=3, category="general")

    final_query = user_query
    if context:
        final_query = (
            f"<retrieved_context>\n{context}\n</retrieved_context>\n\n"
            f"If the retrieved context is relevant, use it. Otherwise, ignore it.\n\n"
            f"{final_query}"
        )

    if (
        web_context
        and "(No web results found" not in web_context
        and "Web search unavailable" not in web_context
    ):
        final_query = (
            f"<search_results>\n{web_context}\n</search_results>\n\n"
            f"User Query:\n{final_query}\n\n"
            f"INSTRUCTIONS: Use the search results above to inform your answer, especially for recent events or specific facts. "
            f"If the search results are incomplete, you may use your internal knowledge to supplement the answer."
        )

    final_query += _language_directive(user_query, role=ModelRole.GENERAL)

    optimized = [{"role": "user", "content": final_query}]
    if history:
        optimized = [
            {"role": m["role"], "content": m["content"]} for m in history
        ] + optimized

    user_lang = (
        settings.get("user_lang") if settings else None
    ) or detect_user_language(user_query)
    full = ""
    thought_process = ""
    try:
        for ev in _stream_tokens(
            ModelRole.GENERAL,
            optimized,
            max_tokens=8192,
            temperature=0.6,
            think_mode="show",
        ):
            if ev["type"] == "token":
                ev["content"] = ev["content"].replace("`", "").replace("~", "")
                full += ev["content"]

            if user_lang == "English" or ev["type"] != "token":
                yield ev

            elif ev["type"] == "thinking":
                thought_process += ev["content"]
    finally:
        if not _keep_loaded:
            unload_model()

    thought_clean = thought_process.strip()
    thought_clean = re.sub(r"</?think>", "", thought_clean, flags=re.IGNORECASE).strip()
    thought_clean = re.sub(
        r"<\|?/?thought(?:_(?:start|end))?\|?>", "", thought_clean, flags=re.IGNORECASE
    ).strip()

    visible_answer = full.strip()
    visible_answer = re.sub(
        r"</?think>", "", visible_answer, flags=re.IGNORECASE
    ).strip()

    cleaned = _quality_guard(visible_answer) if visible_answer else ""

    user_lang = (
        settings.get("user_lang") if settings else None
    ) or detect_user_language(user_query)
    if user_lang != "English" and cleaned:
        yield {"type": "status", "content": f"Translating to {user_lang}..."}
        cleaned = translate_text(cleaned, user_lang)

    display_content = ""
    if thought_clean:
        display_content = f"<thought>\n{thought_clean}\n</thought>\n\n{cleaned}"
    else:
        display_content = cleaned

    if display_content:
        yield {"type": "clear"}
        yield {"type": "token", "content": display_content}
    elif not thought_clean:
        yield {"type": "token", "content": "I am Iris AI."}
        display_content = "I am Iris AI."

    yield {"type": "raw_response", "content": display_content}
