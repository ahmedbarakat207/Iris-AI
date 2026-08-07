import logging
from typing import Generator, Dict, Any
from src.iris.iris.engine import (
    ModelRole,
    load_model,
    unload_model,
    _keep_loaded,
    _load_skill_prompt,
)

logger = logging.getLogger("iris")


def get_control_prompt(identity: str = "") -> str:
    prompt = _load_skill_prompt("control/control_prompt.txt")
    return f"{identity}\n{prompt}"


def run_stream(
    user_query: str, history: list, retriever: Any, settings: dict
) -> Generator[Dict[str, str], None, None]:
    yield {"type": "status", "content": "Executing command via Open Interpreter..."}
    from src.core.controller import _run_oi_task

    result = yield from _run_oi_task(user_query)
    reply_text = f"Executed via Open Interpreter.\n\nResult:\n{result}"
    yield {
        "type": "action_result",
        "content": f"Executed via Open Interpreter.\nResult:\n{result}",
    }
    yield {"type": "token", "content": reply_text}
    yield {"type": "raw_response", "content": reply_text}
