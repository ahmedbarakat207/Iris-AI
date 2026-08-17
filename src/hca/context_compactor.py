<<<<<<< HEAD
import re
from typing import List, Dict, Optional, Tuple
from enum import Enum
import src.iris.engine as iris_module


class CompactionLevel(str, Enum):
    NONE = "none"
    LIGHT = "light"
    MEDIUM = "medium"
    AGGRESSIVE = "aggressive"
    AUTOMATIC = "automatic"


def estimate_tokens(messages: List[Dict[str, str]]) -> int:

    total = 0
    for msg in messages:
        content = msg.get("content", "")
        code_blocks = re.findall(r"```[\s\S]*?```", content)
        non_code = content
        for cb in code_blocks:
            non_code = non_code.replace(cb, "")
        total += len(non_code) // 4
        total += sum(len(cb) // 3 for cb in code_blocks)
        total += 4
    total += 50
    return total


def compact_light(messages: List[Dict[str, str]]) -> List[Dict[str, str]]:

    result = []

    keep_intact_count = 3
    split_idx = max(0, len(messages) - keep_intact_count)

    for i, msg in enumerate(messages):
        role = msg.get("role", "user")
        content = msg.get("content", "")

        if i >= split_idx:

            result.append({"role": role, "content": content})
            continue

        content = re.sub(
            r"```[\s\S]*?```", "[code block omitted — preserved in digest]", content
        )
        if len(content) > 500:
            truncated = content[:500]
            last_period = max(
                truncated.rfind("."), truncated.rfind("!"), truncated.rfind("?")
            )
            if last_period > 200:
                content = content[: last_period + 1]
            else:
                content = truncated + "..."
        result.append({"role": role, "content": content})
    return result


_SUMMARIZE_PROMPT = """You are a conversation compressor. Summarize the following conversation excerpt into a dense, factual digest. Preserve:

1. The user's original request/goal
2. Any decisions made (tech stack, architecture, approach)
3. Key facts, numbers, names
4. Errors encountered and fixes applied
5. Code file paths that were created or modified

Keep it under 200 words. Write in telegram-style: short sentences, no filler.
CRITICAL INSTRUCTION: You MUST write the summary in ENGLISH ONLY. Do NOT use Esperanto or any other language. Do NOT include your internal thought process. Just output the summary directly.

Conversation excerpt:
{conversation}

Dense digest in ENGLISH ONLY:"""


def _summarize_with_model(
    messages: List[Dict[str, str]], max_output_tokens: int = 300
) -> str:

    conversation_text = _format_messages_for_summary(messages)
    prompt = _SUMMARIZE_PROMPT.format(conversation=conversation_text)

    try:
        llm = iris_module.load_model(iris_module.ModelRole.TRIAGE)
        response = llm.create_chat_completion(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_output_tokens,
            temperature=0.1,
        )
        content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
        return content.strip()
    except Exception:
        return _extractive_fallback(messages)


def _extractive_fallback(messages: List[Dict[str, str]]) -> str:

    key_lines = []
    for msg in messages:
        content = msg.get("content", "")
        role = msg.get("role", "user")
        for line in content.split("\n")[:3]:
            clean = line.strip()
            if clean and len(clean) > 20:
                prefix = "User asked:" if role == "user" else "Assistant:"
                key_lines.append(f"{prefix} {clean[:200]}")
        if role == "user" and len(content) > 50:
            key_lines.append(f"User said: {content[:200]}")
    return "\n".join(key_lines[-8:])


def _format_messages_for_summary(messages: List[Dict[str, str]]) -> str:

    parts = []
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        content_clean = re.sub(r"```[\s\S]*?```", "[code block]", content)
        if len(content_clean) > 400:
            content_clean = content_clean[:400] + "..."
        parts.append(f"[{role}] {content_clean}")
    return "\n\n".join(parts)


def compact_context(
    messages: List[Dict[str, str]],
    role=None,
    level: CompactionLevel = CompactionLevel.AUTOMATIC,
    n_ctx: Optional[int] = None,
    force_model_summary: bool = False,
) -> Tuple[List[Dict[str, str]], str]:

    if not messages:
        return [], "no_history"

    if role is not None:
        effective_ctx = n_ctx or iris_module.ROLE_CTX.get(role, iris_module.DEFAULT_CTX)
    else:
        effective_ctx = n_ctx or 4096

    available_ctx = effective_ctx - 512 - 1024
    if available_ctx < 512:
        available_ctx = 512

    estimated = estimate_tokens(messages)
    info = f"estimated_tokens={estimated}, available_ctx={available_ctx}, level={level.value}"

    if level == CompactionLevel.AUTOMATIC:
        ratio = estimated / max(available_ctx, 1)
        if ratio <= 0.5:
            level = CompactionLevel.NONE
        elif ratio <= 1.0:
            level = CompactionLevel.LIGHT
        elif ratio <= 2.0:
            level = CompactionLevel.MEDIUM
        else:
            level = CompactionLevel.AGGRESSIVE
        info += f" → chose {level.value} (ratio={ratio:.1f})"

    if level == CompactionLevel.NONE:
        return messages, info

    if level == CompactionLevel.LIGHT:
        compacted = compact_light(messages)
        info += f", compacted={len(compacted)} msgs, est_tokens={estimate_tokens(compacted)}"
        return compacted, info

    RECENT_KEEP = 4 if level == CompactionLevel.MEDIUM else 2
    old_messages = messages[:-RECENT_KEEP] if len(messages) > RECENT_KEEP else []
    recent_messages = messages[-RECENT_KEEP:]

    if not old_messages:
        compacted = compact_light(messages)
        info += f", only_recent, compacted={len(compacted)} msgs"
        return compacted, info

    summary = _summarize_with_model(old_messages, max_output_tokens=250)
    digest_msg = {
        "role": "system",
        "content": f"[CONVERSATION DIGEST — earlier messages summarized]\n{summary}",
    }
    compacted = [digest_msg] + recent_messages

    if level == CompactionLevel.AGGRESSIVE and recent_messages:
        last_user_msg = recent_messages[-1]
        if last_user_msg["role"] == "user":
            last_user_msg = dict(last_user_msg)
            last_user_msg["content"] = (
                f"[Previous context heavily summarized.\nKey points: {summary[:300]}]\n\n"
                f"{last_user_msg['content']}"
            )
            compacted[-1] = last_user_msg

    info += (
        f", compacted={len(compacted)} msgs, est_tokens={estimate_tokens(compacted)}"
    )
    return compacted, info


def auto_compact_for_role(
    messages: List[Dict[str, str]],
    role,
    max_output_tokens: int = 4096,
    force: bool = False,
) -> Tuple[List[Dict[str, str]], str]:

    if not messages:
        return [], "empty"

    system_msg = None
    history_msgs = messages
    if messages and messages[0].get("role") == "system":
        system_msg = messages[0]
        history_msgs = messages[1:]

    n_ctx = iris_module.ROLE_CTX.get(role, iris_module.DEFAULT_CTX)
    available = n_ctx - 256 - max_output_tokens

    tokens = estimate_tokens(messages)
    if tokens <= available and not force:
        return messages, f"no_compaction_needed ({tokens}/{available} tokens)"

    level = CompactionLevel.AUTOMATIC
    if tokens > available * 3:
        level = CompactionLevel.AGGRESSIVE

    compacted_history, info = compact_context(
        history_msgs, role=role, level=level, n_ctx=n_ctx
    )
    if system_msg:
        return [system_msg] + compacted_history, info
    return compacted_history, info
=======
import re
from typing import List, Dict, Optional, Tuple
from enum import Enum
import src.iris.engine as iris_module


class CompactionLevel(str, Enum):
    NONE = "none"
    LIGHT = "light"
    MEDIUM = "medium"
    AGGRESSIVE = "aggressive"
    AUTOMATIC = "automatic"


def estimate_tokens(messages: List[Dict[str, str]]) -> int:

    total = 0
    for msg in messages:
        content = msg.get("content", "")
        code_blocks = re.findall(r"```[\s\S]*?```", content)
        non_code = content
        for cb in code_blocks:
            non_code = non_code.replace(cb, "")
        total += len(non_code) // 4
        total += sum(len(cb) // 3 for cb in code_blocks)
        total += 4
    total += 50
    return total


def compact_light(messages: List[Dict[str, str]]) -> List[Dict[str, str]]:

    result = []

    keep_intact_count = 3
    split_idx = max(0, len(messages) - keep_intact_count)

    for i, msg in enumerate(messages):
        role = msg.get("role", "user")
        content = msg.get("content", "")

        if i >= split_idx:

            result.append({"role": role, "content": content})
            continue

        content = re.sub(
            r"```[\s\S]*?```", "[code block omitted — preserved in digest]", content
        )
        if len(content) > 500:
            truncated = content[:500]
            last_period = max(
                truncated.rfind("."), truncated.rfind("!"), truncated.rfind("?")
            )
            if last_period > 200:
                content = content[: last_period + 1]
            else:
                content = truncated + "..."
        result.append({"role": role, "content": content})
    return result


_SUMMARIZE_PROMPT = """You are a conversation compressor. Summarize the following conversation excerpt into a dense, factual digest. Preserve:

1. The user's original request/goal
2. Any decisions made (tech stack, architecture, approach)
3. Key facts, numbers, names
4. Errors encountered and fixes applied
5. Code file paths that were created or modified

Keep it under 200 words. Write in telegram-style: short sentences, no filler.
CRITICAL INSTRUCTION: You MUST write the summary in ENGLISH ONLY. Do NOT use Esperanto or any other language. Do NOT include your internal thought process. Just output the summary directly.

Conversation excerpt:
{conversation}

Dense digest in ENGLISH ONLY:"""


def _summarize_with_model(
    messages: List[Dict[str, str]], max_output_tokens: int = 300
) -> str:

    conversation_text = _format_messages_for_summary(messages)
    prompt = _SUMMARIZE_PROMPT.format(conversation=conversation_text)

    try:
        llm = iris_module.load_model(iris_module.ModelRole.TRIAGE)
        response = llm.create_chat_completion(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_output_tokens,
            temperature=0.1,
        )
        content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
        return content.strip()
    except Exception:
        return _extractive_fallback(messages)


def _extractive_fallback(messages: List[Dict[str, str]]) -> str:

    key_lines = []
    for msg in messages:
        content = msg.get("content", "")
        role = msg.get("role", "user")
        for line in content.split("\n")[:3]:
            clean = line.strip()
            if clean and len(clean) > 20:
                prefix = "User asked:" if role == "user" else "Assistant:"
                key_lines.append(f"{prefix} {clean[:200]}")
        if role == "user" and len(content) > 50:
            key_lines.append(f"User said: {content[:200]}")
    return "\n".join(key_lines[-8:])


def _format_messages_for_summary(messages: List[Dict[str, str]]) -> str:

    parts = []
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        content_clean = re.sub(r"```[\s\S]*?```", "[code block]", content)
        if len(content_clean) > 400:
            content_clean = content_clean[:400] + "..."
        parts.append(f"[{role}] {content_clean}")
    return "\n\n".join(parts)


def compact_context(
    messages: List[Dict[str, str]],
    role=None,
    level: CompactionLevel = CompactionLevel.AUTOMATIC,
    n_ctx: Optional[int] = None,
    force_model_summary: bool = False,
) -> Tuple[List[Dict[str, str]], str]:

    if not messages:
        return [], "no_history"

    if role is not None:
        effective_ctx = n_ctx or iris_module.ROLE_CTX.get(role, iris_module.DEFAULT_CTX)
    else:
        effective_ctx = n_ctx or 4096

    available_ctx = effective_ctx - 512 - 1024
    if available_ctx < 512:
        available_ctx = 512

    estimated = estimate_tokens(messages)
    info = f"estimated_tokens={estimated}, available_ctx={available_ctx}, level={level.value}"

    if level == CompactionLevel.AUTOMATIC:
        ratio = estimated / max(available_ctx, 1)
        if ratio <= 0.5:
            level = CompactionLevel.NONE
        elif ratio <= 1.0:
            level = CompactionLevel.LIGHT
        elif ratio <= 2.0:
            level = CompactionLevel.MEDIUM
        else:
            level = CompactionLevel.AGGRESSIVE
        info += f" → chose {level.value} (ratio={ratio:.1f})"

    if level == CompactionLevel.NONE:
        return messages, info

    if level == CompactionLevel.LIGHT:
        compacted = compact_light(messages)
        info += f", compacted={len(compacted)} msgs, est_tokens={estimate_tokens(compacted)}"
        return compacted, info

    RECENT_KEEP = 4 if level == CompactionLevel.MEDIUM else 2
    old_messages = messages[:-RECENT_KEEP] if len(messages) > RECENT_KEEP else []
    recent_messages = messages[-RECENT_KEEP:]

    if not old_messages:
        compacted = compact_light(messages)
        info += f", only_recent, compacted={len(compacted)} msgs"
        return compacted, info

    summary = _summarize_with_model(old_messages, max_output_tokens=250)
    digest_msg = {
        "role": "system",
        "content": f"[CONVERSATION DIGEST — earlier messages summarized]\n{summary}",
    }
    compacted = [digest_msg] + recent_messages

    if level == CompactionLevel.AGGRESSIVE and recent_messages:
        last_user_msg = recent_messages[-1]
        if last_user_msg["role"] == "user":
            last_user_msg = dict(last_user_msg)
            last_user_msg["content"] = (
                f"[Previous context heavily summarized.\nKey points: {summary[:300]}]\n\n"
                f"{last_user_msg['content']}"
            )
            compacted[-1] = last_user_msg

    info += (
        f", compacted={len(compacted)} msgs, est_tokens={estimate_tokens(compacted)}"
    )
    return compacted, info


def auto_compact_for_role(
    messages: List[Dict[str, str]],
    role,
    max_output_tokens: int = 4096,
    force: bool = False,
) -> Tuple[List[Dict[str, str]], str]:

    if not messages:
        return [], "empty"

    system_msg = None
    history_msgs = messages
    if messages and messages[0].get("role") == "system":
        system_msg = messages[0]
        history_msgs = messages[1:]

    n_ctx = iris_module.ROLE_CTX.get(role, iris_module.DEFAULT_CTX)
    available = n_ctx - 256 - max_output_tokens

    tokens = estimate_tokens(messages)
    if tokens <= available and not force:
        return messages, f"no_compaction_needed ({tokens}/{available} tokens)"

    level = CompactionLevel.AUTOMATIC
    if tokens > available * 3:
        level = CompactionLevel.AGGRESSIVE

    compacted_history, info = compact_context(
        history_msgs, role=role, level=level, n_ctx=n_ctx
    )
    if system_msg:
        return [system_msg] + compacted_history, info
    return compacted_history, info
>>>>>>> origin/main
