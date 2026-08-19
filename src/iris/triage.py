"""
Iris Triage Router (iris_001)

Routes incoming queries to the appropriate downstream specialist.
Relies strictly on LLM grammar-constraints to enforce valid route selection.
"""

import os

_triage_guide_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "skills",
    "triage",
    "triage_routing_guide.md",
)
try:
    with open(_triage_guide_path, "r", encoding="utf-8") as _f:
        TRIAGE_SYSTEM_PROMPT = _f.read()
except Exception:

    _fallback_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "skills",
        "prompts",
        "triage_fallback.txt",
    )
    try:
        with open(_fallback_path, "r", encoding="utf-8") as _f2:
            TRIAGE_SYSTEM_PROMPT = _f2.read()
    except Exception:
        TRIAGE_SYSTEM_PROMPT = "You are Iris Router. Return JSON with 'route'."

import json
import logging
import re
from typing import Dict, List, Optional, Tuple

from src.iris.engine import (
    ModelRole,
    TaskType,
    load_model,
    unload_model,
    _minimize_history,
    load_generation_config,
)

logger = logging.getLogger("iris")

try:
    from llama_cpp import LlamaGrammar
except Exception:
    LlamaGrammar = None


_ROUTES = [
    "SEARCH",
    "REASONING",
    "GENERAL",
    "MATH",
    "CODE_SIMPLE",
    "CODE_COMPLEX",
    "CONTROL",
]

_TRIAGE_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "route": {"type": "string", "enum": _ROUTES},
        "keywords": {"type": "string"},
        "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
    },
    "required": ["route", "keywords", "confidence"],
}

_ROUTE_TAG_MAP: Dict[str, TaskType] = {
    "GENERAL": TaskType.GENERAL,
    "REASONING": TaskType.REASONING,
    "MATH": TaskType.MATH,
    "CODE_SIMPLE": TaskType.CODING_SIMPLE,
    "CODE_COMPLEX": TaskType.CODING_COMPLEX,
    "CONTROL": TaskType.CONTROL,
}


_CONFIDENCE_FLOOR = 0.55

_triage_grammar = None
if LlamaGrammar is not None:
    try:
        _triage_grammar = LlamaGrammar.from_json_schema(json.dumps(_TRIAGE_JSON_SCHEMA))
    except Exception as e:
        logger.warning(
            f"[Triage] Could not build grammar from schema ({e}); triage will run unconstrained."
        )
else:
    logger.warning(
        "[Triage] llama_cpp.LlamaGrammar unavailable; triage will run unconstrained."
    )


def classify_task(
    user_query: str, history: List[Dict[str, str]]
) -> Tuple[Optional[TaskType], Optional[str]]:

    query_for_classification = re.sub(
        r"<document>[\s\S]*?</document>", "", user_query, flags=re.IGNORECASE
    )
    query_for_classification = re.sub(
        r"\[IMAGE_UPLOADED:[^\]]+\]", "", query_for_classification, flags=re.IGNORECASE
    )
    query_for_classification = query_for_classification.strip()

    if (
        history
        and history[-1].get("role") == "user"
        and history[-1].get("content", "").strip().startswith("OBSERVATION:")
    ):
        return TaskType.CONTROL, None

    minimized = _minimize_history(history, max_entries=2)

    triage_prompt = (
        "CRITICAL ROLE AND INSTRUCTION:\n"
        "You are the Iris AI Router. Your ONLY job is to classify the user's query and output a single JSON routing object.\n"
        "You must NEVER answer, reply to, execute, or explain the user's query under any circumstances.\n"
        "Even if the query is a greeting, a coding request, or a math problem, output ONLY the JSON routing decision.\n\n"
        "=== ROUTING SPECIFICATION ===\n"
        f"{TRIAGE_SYSTEM_PROMPT}"
    )

    import datetime

    try:
        now = datetime.datetime.now().astimezone()
        time_str = now.strftime("%A, %B %d, %Y, %H:%M:%S %Z")
        offset_str = now.strftime("%z")
        formatted_offset = (
            f"{offset_str[:3]}:{offset_str[3:]}" if len(offset_str) >= 5 else offset_str
        )
        triage_prompt += f"\n\nCurrent time: {time_str} (UTC{formatted_offset})."
    except Exception:
        pass

    history_context = ""
    if history:
        lower_query = query_for_classification.strip().lower()
        if lower_query in ("continue", "continue.", "go on", "keep going", "more"):
            last_asst = next(
                (m["content"] for m in reversed(history) if m["role"] == "assistant"),
                "",
            )
            if (
                "```" in last_asst
                or "<file_card" in last_asst
                or "<coding>" in last_asst
            ):
                return TaskType.CODING_COMPLEX, None

    lower_query = query_for_classification.lower()

    code_keywords = [
        r"\bbackend\b",
        r"\bserver\b",
        r"\bapi\b",
        r"\bfull stack\b",
        r"\bfull-stack\b",
        r"\bnode\b",
        r"\bexpress\b",
        r"\bskeleton\b",
        r"\bهيكل\b",
        r"\bقالب\b",
        r"\bفراغات\b",
    ]
    if any(re.search(kw, lower_query) for kw in code_keywords):
        logger.info(
            "[Triage] Hardcoded intercept: Full-Stack or Skeleton keyword detected. Routing to CODING_COMPLEX."
        )
        return TaskType.CODING_COMPLEX, None

    web_tech = [r"\btailwind\b", r"\bhtml\b", r"\bcss\b", r"\breact\b"]
    web_intent = [
        r"\bbuild\b",
        r"\blanding page\b",
        r"\bwebsite\b",
        r"\bموقع\b",
        r"\bصفحة\b",
        r"\bصمم\b",
        r"\bبرمج\b",
    ]
    if any(re.search(tech, lower_query) for tech in web_tech) and any(
        re.search(intent, lower_query) for intent in web_intent
    ):
        logger.info(
            "[Triage] Hardcoded intercept: Web development query detected. Routing to CODING_COMPLEX."
        )
        return TaskType.CODING_COMPLEX, None

    if minimized:
        history_context = "Conversation History Context:\n"
        for msg in minimized:
            role_label = "User" if msg["role"] == "user" else "Assistant"
            c = msg["content"]
            if len(c) > 150:
                c = c[:150] + "...[truncated]"
            history_context += f"- {role_label}: {c}\n"
        history_context += "\n"

    triage_query = query_for_classification
    if len(triage_query) > 1500:
        triage_query = (
            triage_query[:1000]
            + "\n\n...[content truncated for routing]...\n\n"
            + triage_query[-500:]
        )

    user_content = (
        f"{history_context}"
        "Classify the following User Query according to the routing specification.\n"
        "REMINDER: Do NOT answer, solve, or reply to the query itself. ONLY output the JSON routing decision.\n\n"
        f"User Query:\n{triage_query}"
    )

    triage_messages = [
        {"role": "system", "content": triage_prompt},
        {"role": "user", "content": user_content},
    ]

    answer = None
    try:
        llm = load_model(ModelRole.TRIAGE)
        completion_kwargs = dict(
            messages=triage_messages,
            max_tokens=200,
            temperature=0.0,
            repeat_penalty=1.1,
        )
        if _triage_grammar is not None:
            completion_kwargs["grammar"] = _triage_grammar
        else:

            completion_kwargs["response_format"] = {"type": "json_object"}
        try:
            res = llm.create_chat_completion(**completion_kwargs)
        except TypeError:

            completion_kwargs.pop("grammar", None)
            completion_kwargs.pop("response_format", None)
            res = llm.create_chat_completion(**completion_kwargs)
        answer = res["choices"][0]["message"]["content"].strip()
    except Exception as e:
        logger.warning(f"[Triage] Model call failed ({e}); defaulting to REASONING.")
        return TaskType.REASONING, None
    finally:

        try:
            import src.iris.engine as _engine

            cfg = load_generation_config()
            if not _engine._keep_loaded and not cfg.get("keep_triage_loaded"):
                unload_model(ModelRole.TRIAGE)
        except Exception:
            pass

    logger.info(f"[Triage] Raw answer: {answer!r}")

    try:
        data = json.loads(answer)
        route_val = str(data.get("route", "")).strip().upper()
        keywords = str(data.get("keywords", "") or "").strip()
        confidence = float(data.get("confidence", 0.0))
    except Exception as e:
        logger.warning(
            f"[Triage] Could not parse routing JSON ({e}): {answer[:300]!r} \u2014 defaulting to REASONING."
        )
        return TaskType.REASONING, None

    if confidence < _CONFIDENCE_FLOOR:
        logger.info(
            f"[Triage] Confidence {confidence:.2f} < {_CONFIDENCE_FLOOR}. Falling back to REASONING."
        )
        return TaskType.REASONING, None

    if route_val == "SEARCH":
        return TaskType.SEARCH, (keywords or query_for_classification)

    mapped = _ROUTE_TAG_MAP.get(route_val)
    if mapped is not None:
        return mapped, None

    logger.warning(
        f"[Triage] Unrecognized route {route_val!r} \u2014 defaulting to REASONING."
    )
    return TaskType.REASONING, None
