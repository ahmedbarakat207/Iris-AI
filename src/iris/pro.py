from __future__ import annotations

import asyncio
import logging
import os
import re
import sys
import time
import warnings
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, AsyncGenerator

import openai
from openai import AsyncOpenAI
from src.iris.iris.coding import get_code_prompt, get_reviewer_prompt

warnings.filterwarnings(
    "ignore", category=RuntimeWarning, message="coroutine method 'aclose'"
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("iris_ai")

SITE_URL: str = os.getenv("OCENZA_SITE_URL", "https://iris-ai.app")
APP_TITLE: str = os.getenv("OCENZA_APP_TITLE", "Iris AI")
REQUEST_TIMEOUT_S = float(os.getenv("IRIS_REQUEST_TIMEOUT", "600"))

MAX_TOKENS = 8196
MAX_TOKENS_GENERAL = 4096
MAX_TOKENS_TRIAGE = 1024
MAX_REASONING_CHARS = 150000
MAX_HISTORY_CONTENT_CHARS = 1000
MAX_TRIAGE_CONTENT_CHARS = 500
MAX_HISTORY_MESSAGES = 40
MAX_RETRIES = 6
RETRY_BASE_WAIT_S = 3.0
MAX_STAGE_INPUT_CHARS = 8000
MAX_CONTINUATION_LOOPS = 5

IRIS_IDENTITY = (
    "You are Iris AI, an elite, hyper-intelligent AI assistant designed to solve complex problems with absolute precision. "
    "You operate with maximum efficiency, deep reasoning, and flawless execution. "
    "If asked who made you, who created you, or who you are, you MUST answer concisely that you are Iris AI and DO NOT list your capabilities. "
    "Never use filler phrases like 'Certainly' or 'I can help with that'. Answer immediately and directly. "
    "Never mention underlying model names (e.g., MiMo, Xiaomi, DeepSeek) or your pipeline architecture. Identify only as Iris AI. "
    "For complex problems, think step-by-step, verify your logic internally, and ensure all edge cases are handled before finalizing your answer. "
    "CRITICAL LANGUAGE RULE: You MUST always respond in English. All responses, explanations, code comments, and text MUST be written entirely in English, even if the user speaks or inputs in Arabic or any other language. Your internal <think> process and final response must be fully in English."
)


def verify_code_syntax(code: str, lang: str) -> str | None:
    import ast
    import subprocess
    import tempfile
    import json

    lang = lang.lower().strip()
    if lang in ["python", "py"]:
        try:
            ast.parse(code)
            return None
        except SyntaxError as e:
            return f"SyntaxError: {e}"

    elif lang in ["json"]:
        try:
            json.loads(code)
            return None
        except ValueError as e:
            return f"JSONDecodeError: {e}"

    elif lang in ["js", "javascript"]:
        js_code = code
        if js_code.strip():
            with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as f:
                f.write(js_code)
                temp_path = f.name
            try:
                res = subprocess.run(
                    ["node", "-c", temp_path], capture_output=True, text=True
                )
                if res.returncode != 0:
                    return res.stderr.strip()
            except Exception:
                pass
            finally:
                try:
                    os.remove(temp_path)
                except Exception:
                    pass

    elif lang in ["bash", "sh"]:
        with tempfile.NamedTemporaryFile("w", suffix=".sh", delete=False) as f:
            f.write(code)
            temp_path = f.name
        try:
            res = subprocess.run(
                ["bash", "-n", temp_path], capture_output=True, text=True
            )
            if res.returncode != 0:
                return res.stderr.strip()
        except Exception:
            pass
        finally:
            try:
                os.remove(temp_path)
            except Exception:
                pass

    elif lang in ["c", "cpp", "c++", "h", "hpp"]:
        suffix = ".cpp" if "cpp" in lang or "c++" in lang else ".c"
        with tempfile.NamedTemporaryFile("w", suffix=suffix, delete=False) as f:
            f.write(code)
            temp_path = f.name
        try:
            compiler = "g++" if "cpp" in lang or "c++" in lang else "gcc"
            res = subprocess.run(
                [compiler, "-fsyntax-only", temp_path], capture_output=True, text=True
            )
            if res.returncode != 0:
                return res.stderr.strip()
        except Exception:
            pass
        finally:
            try:
                os.remove(temp_path)
            except Exception:
                pass

    return None


class Model(str, Enum):
    ORCHESTRATOR = "cmc/xiaomi/mimo-v2.5-pro"

    CODE_COMPLEX = "cmc/deepseek/deepseek-v4-pro"
    REASONING = "cmc/deepseek/deepseek-v4-pro"

    CODE_REVIEWER = "cmc/xiaomi/mimo-v2.5-pro"
    GENERAL = "cmc/xiaomi/mimo-v2.5"

    CODE_SIMPLE = "cmc/deepseek/deepseek-v4-flash"
    MATH = "cmc/deepseek/deepseek-v4-flash"
    SEARCH = "cmc/deepseek/deepseek-v4-flash"


class TaskType(str, Enum):
    MATH = "math"
    CODING_SIMPLE = "coding_simple"
    CODING_COMPLEX = "coding_complex"
    REASONING = "reasoning"
    GENERAL = "general"
    SEARCH = "search"
    CONTROL = "control"


TASK_TO_MODEL: dict[TaskType, Model] = {
    TaskType.MATH: Model.MATH,
    TaskType.CODING_SIMPLE: Model.CODE_SIMPLE,
    TaskType.CODING_COMPLEX: Model.CODE_COMPLEX,
    TaskType.REASONING: Model.REASONING,
    TaskType.GENERAL: Model.GENERAL,
    TaskType.SEARCH: Model.SEARCH,
}


@dataclass
class TokenUsage:
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

    def __add__(self, other: "TokenUsage") -> "TokenUsage":
        if not isinstance(other, TokenUsage):
            raise TypeError("Operand must be an instance of TokenUsage")
        return TokenUsage(
            self.prompt_tokens + other.prompt_tokens,
            self.completion_tokens + other.completion_tokens,
            self.total_tokens + other.total_tokens,
        )

    def __str__(self) -> str:
        return (
            f"prompt={self.prompt_tokens}, "
            f"completion={self.completion_tokens}, "
            f"total={self.total_tokens}"
        )


@dataclass
class HopResult:
    hop_name: str
    model: str
    content: str
    usage: TokenUsage
    latency_ms: float
    raw_response: dict[str, Any] = field(default_factory=dict, repr=False)

    def log_summary(self) -> None:
        log.info(
            "HOP %-30s | model=%-40s | tokens=[%s] | %.0fms",
            self.hop_name,
            self.model,
            self.usage,
            self.latency_ms,
        )


@dataclass
class RoutingDecision:
    task_type: TaskType
    rationale: str
    subtasks: list[str] = field(default_factory=list)
    raw_json: dict[str, Any] = field(default_factory=dict)


@dataclass
class PipelineResult:
    user_query: str
    routing_decision: RoutingDecision
    specialist_output: str
    final_answer: str
    hops: list[HopResult] = field(default_factory=list)
    aggregate_usage: TokenUsage = field(default_factory=TokenUsage)


MATH_SYSTEM_PROMPT = (
    "You are the Iris AI Math Core. Solve mathematical, algorithmic, and statistical problems step-by-step. "
    "Use precise mathematical notation, verify your derivations rigorously, and state your final answer clearly at the end. "
    "If your solution includes writing code (like Python or C++), DO NOT use LaTeX or MathJax formatting (like $...$ or _{...}) inside the code block. Variable names must be plain text."
)

CODE_SYSTEM_PROMPT = get_code_prompt(IRIS_IDENTITY)

CODE_REVIEWER_SYSTEM_PROMPT = get_reviewer_prompt(IRIS_IDENTITY)

REASONING_SYSTEM_PROMPT = (
    f"{IRIS_IDENTITY}\n"
    "You are the Iris AI Deep Reasoning Specialist. You possess advanced analytical capabilities. "
    "Think step-by-step using deep chain-of-thought reasoning. "
    "Break down complex problems methodically, explore multiple perspectives, identify potential flaws in your own logic, and refine your approach before giving the final, definitive answer.\n"
    "CRITICAL DEPTH RULES:\n"
    "1. NEVER give shallow answers. Always explain the topic deeply and thoroughly.\n"
    "2. Explore the core concepts, nuances, and edge cases.\n"
    "3. Provide a multi-paragraph, comprehensive response for every query."
)

GENERAL_SYSTEM_PROMPT = (
    f"{IRIS_IDENTITY}\n"
    "You are the Iris AI Knowledge Specialist. Your job is to provide DEEP, THOROUGH, and COMPREHENSIVE explanations.\n"
    "CRITICAL DEPTH RULES:\n"
    "1. NEVER give one-sentence or shallow answers about any topic. Always go deep.\n"
    "2. Structure your response with clear sections, bullet points, and examples.\n"
    "3. Cover: (a) what it is, (b) how it works, (c) why it matters, (d) key details, (e) practical implications.\n"
    "4. Use analogies, comparisons, and concrete examples to make concepts crystal clear.\n"
    "5. Minimum response: 3 paragraphs for simple topics, 5+ for complex ones.\n"
    "6. Do NOT include comments in code blocks."
)

SPECIALIST_SYSTEM_PROMPTS: dict[TaskType, str] = {
    TaskType.MATH: MATH_SYSTEM_PROMPT,
    TaskType.CODING_SIMPLE: CODE_SYSTEM_PROMPT,
    TaskType.CODING_COMPLEX: CODE_SYSTEM_PROMPT,
    TaskType.REASONING: REASONING_SYSTEM_PROMPT,
    TaskType.GENERAL: GENERAL_SYSTEM_PROMPT,
    TaskType.SEARCH: GENERAL_SYSTEM_PROMPT,
}


class OpenRouterClient:
    def __init__(self) -> None:
        self.api_key = "sk-1c489e5544334f97-p50fxh-ec2cb811"
        self.base_url = "http://localhost:20128/v1"
        self._client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=REQUEST_TIMEOUT_S,
        )

    async def _handle_api_error(self, exc: Exception, attempt: int) -> None:

        wait_s = RETRY_BASE_WAIT_S * (2**attempt)
        if attempt < MAX_RETRIES - 1:
            log.warning(
                "API error (%s): %s. Retrying in %.1fs (attempt %d/%d)...",
                type(exc).__name__,
                exc,
                wait_s,
                attempt + 1,
                MAX_RETRIES,
            )
            await asyncio.sleep(wait_s)
        else:
            raise RuntimeError(
                "API is currently overloaded or down. Please try again."
            ) from exc

    async def chat(
        self,
        *,
        model: str,
        messages: list[dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = MAX_TOKENS,
        response_format: dict[str, str] | None = None,
        extra_body: dict[str, Any] | None = None,
        tools: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        kwargs: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if response_format:
            kwargs["response_format"] = response_format
        if extra_body:
            kwargs["extra_body"] = extra_body
        if tools:
            kwargs["tools"] = tools

        for attempt in range(MAX_RETRIES):
            try:
                response = await self._client.chat.completions.create(**kwargs)
                return response.model_dump()
            except (
                openai.APIStatusError,
                openai.APIConnectionError,
                openai.APITimeoutError,
            ) as exc:
                await self._handle_api_error(exc, attempt)

    async def stream_chat(
        self,
        *,
        model: str,
        messages: list[dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = MAX_TOKENS,
        response_format: dict[str, str] | None = None,
        extra_body: dict[str, Any] | None = None,
        tools: list[dict[str, Any]] | None = None,
    ) -> AsyncGenerator[dict[str, Any], None]:
        kwargs: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }
        if response_format:
            kwargs["response_format"] = response_format
        if extra_body:
            kwargs["extra_body"] = extra_body
        if tools:
            kwargs["tools"] = tools

        for attempt in range(MAX_RETRIES):
            try:
                stream = await self._client.chat.completions.create(**kwargs)
                iterator = stream.__aiter__()
                pending_task = None

                try:
                    while True:
                        if pending_task is None:
                            pending_task = asyncio.create_task(iterator.__anext__())

                        done, pending = await asyncio.wait([pending_task], timeout=2.0)

                        if pending_task in done:
                            try:
                                chunk = pending_task.result()
                                yield chunk.model_dump()
                                pending_task = None
                            except StopAsyncIteration:
                                break
                        else:
                            yield {"keepalive": True}
                finally:
                    if pending_task and not pending_task.done():
                        pending_task.cancel()
                    if hasattr(stream, "_iterator") and stream._iterator is not None:
                        try:
                            await stream._iterator.aclose()
                        except Exception:
                            pass
                    if hasattr(iterator, "aclose"):
                        try:
                            await iterator.aclose()
                        except Exception:
                            pass
                    await stream.close()
                return
            except (
                openai.APIStatusError,
                openai.APIConnectionError,
                openai.APITimeoutError,
            ) as exc:
                await self._handle_api_error(exc, attempt)

    async def aclose(self) -> None:
        await self._client.close()

    async def __aenter__(self) -> "OpenRouterClient":
        return self

    async def __aexit__(self, *_: Any) -> None:
        await self.aclose()


def _extract_usage(raw: dict[str, Any]) -> TokenUsage:
    usage = raw.get("usage") or {}
    return TokenUsage(
        prompt_tokens=usage.get("prompt_tokens", 0),
        completion_tokens=usage.get("completion_tokens", 0),
        total_tokens=usage.get("total_tokens", 0),
    )


def _extract_content(raw: dict[str, Any]) -> str:
    try:
        choices = raw.get("choices", [])
        if not choices:
            return ""
        content = choices[0].get("message", {}).get("content")
        if content is None:
            return ""
        if isinstance(content, list):
            return "".join(
                block.get("text", "") if isinstance(block, dict) else str(block)
                for block in content
            )
        return str(content)
    except Exception:
        return ""


def _timed_hop(
    name: str, model: str, raw: dict[str, Any], elapsed_s: float
) -> HopResult:
    return HopResult(
        hop_name=name,
        model=model,
        content=_extract_content(raw),
        usage=_extract_usage(raw),
        latency_ms=elapsed_s * 1000,
        raw_response=raw,
    )


def _extract_reasoning_content(raw: dict[str, Any]) -> str:
    try:
        message = raw["choices"][0]["message"]
        if message.get("reasoning_content"):
            return message["reasoning_content"]
        content: str = message.get("content") or ""
        if "<think>" in content and "</think>" in content:
            start = content.index("<think>") + len("<think>")
            end = content.index("</think>")
            return content[start:end].strip()
    except (KeyError, IndexError, TypeError, ValueError):
        pass
    return ""


async def stage_reasoning(
    client: OpenRouterClient,
    user_query: str,
    history: list[dict[str, str]] | None = None,
) -> tuple[str, HopResult]:
    log.info("Stage 1 — Reasoning model thinking...")
    messages = []
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": user_query})

    t0 = time.perf_counter()
    raw = await client.chat(
        model=Model.REASONING.value,
        messages=messages,
        temperature=0.6,
        max_tokens=MAX_TOKENS,
        extra_body={"include_reasoning": True},
    )
    elapsed = time.perf_counter() - t0
    hop = _timed_hop("1:reasoning", Model.REASONING.value, raw, elapsed)
    hop.log_summary()

    reasoning_content = _extract_reasoning_content(raw)
    output = hop.content
    if reasoning_content:
        output = f"<thinking>\n{reasoning_content}\n</thinking>\n\n{hop.content}"

    return output, hop


async def stage_talking(
    client: OpenRouterClient,
    user_query: str,
    reasoning_output: str,
) -> tuple[str, HopResult]:
    log.info("Stage 2 — Orchestrator formulating final response...")

    talk_prompt = (
        f"{IRIS_IDENTITY}\n\n"
        "You are the Iris AI Orchestrator. You have been provided with the user's query and the "
        "raw reasoning process from our internal deep-thinking engine. "
        "Your task is to read the reasoning, synthesize it, and present the final answer to the user "
        "in a clear, professional, and well-formatted manner. "
        "CRITICAL INSTRUCTION: If the user asks for code, or the reasoning contains code, you MUST output the complete, full code without ANY truncation, abbreviation, or placeholders (like 'rest of the code goes here' or '...'). Never be lazy. Always provide the full, ready-to-run code.\n"
        "DO NOT expose the `<thinking>` tags or mention the internal reasoning engine. Just give the final answer."
    )

    truncated_reasoning = reasoning_output
    if len(truncated_reasoning) > MAX_REASONING_CHARS:
        log.warning(
            "Truncating reasoning_output from %d to %d chars.",
            len(truncated_reasoning),
            MAX_REASONING_CHARS,
        )
        truncated_reasoning = (
            truncated_reasoning[:MAX_REASONING_CHARS] + "\n...[truncated for length]"
        )

    messages = [
        {"role": "system", "content": talk_prompt},
        {
            "role": "user",
            "content": f"User Query: {user_query}\n\nInternal Reasoning:\n{truncated_reasoning}",
        },
    ]

    t0 = time.perf_counter()

    full_content = ""
    last_raw = None

    for i in range(MAX_CONTINUATION_LOOPS):
        raw = await client.chat(
            model=Model.ORCHESTRATOR.value,
            messages=messages,
            temperature=0.3,
            max_tokens=MAX_TOKENS,
        )
        last_raw = raw
        chunk_content = _extract_content(raw)
        full_content += chunk_content

        finish_reason = "stop"
        try:
            finish_reason = raw["choices"][0].get("finish_reason", "stop")
        except (KeyError, IndexError):
            pass

        if finish_reason == "length":
            log.warning(
                "Orchestrator hit max_tokens length. Auto-continuing (loop %d)...",
                i + 1,
            )
            messages.append({"role": "assistant", "content": chunk_content})
            messages.append(
                {
                    "role": "user",
                    "content": "Continue exactly where you left off, from the very next character. Do not repeat anything.",
                }
            )
        else:
            break

    elapsed = time.perf_counter() - t0
    synthetic_raw = {}
    if last_raw:
        synthetic_raw = {
            "choices": [{"message": {"content": full_content, "role": "assistant"}}],
            "usage": last_raw.get("usage", {}),
        }
    hop = _timed_hop("2:talking", Model.ORCHESTRATOR.value, synthetic_raw, elapsed)
    hop.log_summary()
    return hop.content, hop


def optimize_messages(
    history_messages: list[dict[str, str]] | None, user_query: str
) -> list[dict[str, str]]:
    if not history_messages:
        return [{"role": "user", "content": user_query}]

    recent = history_messages[-6:]
    optimized = []

    for i, msg in enumerate(recent):
        role = msg.get("role")
        content = msg.get("content", "")

        if i < len(recent) - 1:
            content = re.sub(
                r"```[\s\S]*?```",
                "```\n[Code block omitted to save tokens]\n```",
                content,
            )
            if len(content) > MAX_HISTORY_CONTENT_CHARS:
                content = content[:MAX_HISTORY_CONTENT_CHARS] + "\n...[truncated]"

        optimized.append({"role": role, "content": content})

    optimized.append({"role": "user", "content": user_query})
    return optimized


def fallback_classify(query: str) -> TaskType | None:
    q = query.lower()

    time_patterns = [
        r"\bwhat\s+(?:is\s+)?(?:the\s+)?(?:current\s+)?time\b",
        r"\bwhat\s+time\s+is\s+it\b",
        r"\bwhat's\s+the\s+time\b",
        r"\bcurrent\s+time\b",
        r"\bcurrent\s+date\b",
        r"\bwhat\s+is\s+today's\s+date\b",
        r"\btoday's\s+date\b",
        r"\bwhat\s+(?:is\s+)?(?:the\s+)?date\s+today\b",
        r"\bwhat\s+day\s+is\s+it\b",
        r"\bwhat\s+day\s+of\s+the\s+week\b",
        r"\btell\s+me\s+the\s+time\b",
        r"\btime\s+now\b",
        r"\btime\s+in\s+[a-zA-Z]+",
        r"\bdate\s+in\s+[a-zA-Z]+",
    ]
    if any(re.search(pat, q) for pat in time_patterns):
        return TaskType.GENERAL

    analysis_keywords = {
        "analyze",
        "analyse",
        "explain",
        "summarize",
        "what does this",
        "how does this",
        "walkthrough",
        "break down",
        "what is this",
        "what's this",
    }
    for kw in analysis_keywords:
        if re.search(rf"\b{re.escape(kw)}\b", q):
            return TaskType.REASONING

    if re.search(
        r"\b\w+\.(c|cpp|h|py|js|ts|html|css|sh|java|go|rs|json|yml|yaml|asm|s|md)\b", q
    ):
        return TaskType.CODING_COMPLEX

    code_keywords = {
        "code",
        "coding",
        "program",
        "programming",
        "compile",
        "compiler",
        "debug",
        "debugging",
        "refactor",
        "refactoring",
        "script",
        "scripts",
        "kernel",
        "make",
        "makefile",
        "gcc",
        "clang",
        "qemu",
        "gdb",
        "vga",
        "driver",
        "bootloader",
        "assembly",
        "nasm",
        "masm",
        "link",
        "linker",
        "pong",
        "game",
        "controls",
        "keyboard",
        "function",
        "variable",
        "class",
        "struct",
        "method",
        "loop",
        "array",
        "pointer",
        "database",
        "sql",
        "api",
        "json",
        "xml",
        "html",
        "css",
        "docker",
        "git",
        "github",
        "repo",
        "repository",
        "commit",
        "push",
        "pull",
        "merge",
        "conflict",
    }

    complex_keywords = {
        "kernel",
        "gcc",
        "clang",
        "qemu",
        "driver",
        "bootloader",
        "pong",
        "game",
        "make",
        "makefile",
    }

    for kw in code_keywords:
        if re.search(rf"\b{re.escape(kw)}\b", q):
            if kw in complex_keywords or len(q) > 300:
                return TaskType.CODING_COMPLEX
            else:
                return TaskType.CODING_SIMPLE

    reasoning_keywords = {
        "logic",
        "logical",
        "puzzle",
        "puzzles",
        "riddle",
        "riddles",
        "reasoning",
        "system design",
        "architecture",
    }
    for kw in reasoning_keywords:
        if re.search(rf"\b{re.escape(kw)}\b", q):
            return TaskType.REASONING

    return None


def is_continuation_query(query: str, history: list[dict[str, str]] | None) -> bool:
    if not history:
        return False
    q = query.strip().lower().strip("?.!,;:\"'")
    continuation_words = {
        "continue",
        "keep going",
        "go on",
        "proceed",
        "finish",
        "finish the code",
        "finish code",
        "more",
        "complete",
        "next",
    }
    is_intent = False
    if q in continuation_words:
        is_intent = True
    elif re.match(
        r"^(continue|finish|complete)\s+(writing|code|the\s+code|generating|developing)$",
        q,
    ):
        is_intent = True

    if not is_intent:
        return False

    has_code = False
    for msg in reversed(history):
        if msg.get("role") == "assistant":
            content = msg.get("content", "")
            if "```" in content or "<file_card" in content or "<thinking" in content:
                has_code = True
                break
    return has_code


def _get_system_time_directive() -> str:
    import datetime

    try:
        now = datetime.datetime.now().astimezone()
        time_str = now.strftime("%A, %B %d, %Y, %H:%M:%S %Z")
        offset_str = now.strftime("%z")
        formatted_offset = (
            f"{offset_str[:3]}:{offset_str[3:]}" if len(offset_str) >= 5 else offset_str
        )
        return f"\n\n[SYSTEM DIRECTIVE: The current local system time is {time_str} (UTC{formatted_offset}). This is the exact, live time on the user's computer. Use this context to answer any date/time queries or relative time differences. Do NOT claim you do not have real-time access or that you don't know the time.]"
    except Exception:
        return ""


async def ask_stream(
    user_query: str,
    history: list[dict[str, str]] | None = None,
    mode: str = "smart",
    workspace_root: str = "",
) -> AsyncGenerator[dict[str, Any], None]:
    hops: list[HopResult] = []

    img_match = re.match(
        r"^\[IMAGE_UPLOADED:\s*(.+?)\]\s*(.*)$", user_query, flags=re.DOTALL
    )
    if img_match:
        from src.iris.iris import analyze_image
        import os

        image_path = img_match.group(1).strip()
        prompt = img_match.group(2).strip()
        if not prompt:
            prompt = "Describe this image in detail."

        yield {
            "type": "status",
            "content": "Analyzing image with local Vision model...",
        }
        try:

            res = analyze_image(image_path, prompt)
            yield {"type": "token", "content": res}
        except Exception as e:
            yield {"type": "token", "content": f"Vision analysis failed: {e}"}

        try:
            os.unlink(image_path)
        except Exception:
            pass
        return

    is_continuation = is_continuation_query(user_query, history)

    async with OpenRouterClient() as client:
        if mode == "smart":
            messages = optimize_messages(history, user_query)

            try:
                from src.hermes_harness import (
                    HermesToolRegistry,
                    HermesAgentLoop,
                    HermesResultAnalyzer,
                    HERMES_AGENT_SYSTEM_PROMPT,
                )

                _hermes_available = True
            except ImportError:
                _hermes_available = False

            if _hermes_available:
                yield {
                    "type": "status",
                    "content": "Initializing Agentic IDE Harness...",
                }
                yield {"type": "status", "content": "Initializing Hermes Agent..."}
                t0 = time.perf_counter()
                selected_model = Model.CODE_COMPLEX.value
                log.info("Starting Hermes Agent Loop with %s...", selected_model)

                agent_messages = [
                    {"role": "system", "content": HERMES_AGENT_SYSTEM_PROMPT},
                    *messages,
                ]
                full_content = ""
                last_usage = {}

                agent_loop_obj = HermesAgentLoop(
                    workspace_root=(workspace_root or os.getcwd()),
                    max_tool_calls=40,
                    max_consecutive_errors=5,
                    max_turns=15,
                )

                for agent_turn in range(15):
                    finish_reason = "stop"
                    loop_content = ""
                    tool_calls_dict = {}

                    async for chunk in client.stream_chat(
                        model=selected_model,
                        messages=agent_messages,
                        temperature=0.3,
                        max_tokens=MAX_TOKENS,
                        tools=HermesToolRegistry.get_openai_tools(),
                    ):
                        try:
                            choice = chunk.get("choices", [{}])[0]
                            if chunk.get("usage"):
                                last_usage = chunk["usage"]
                            delta = choice.get("delta", {})

                            token = delta.get("content", "")
                            if token:
                                loop_content += token
                                full_content += token
                                yield {"type": "token", "content": token}

                            if "tool_calls" in delta and delta["tool_calls"]:
                                for tc in delta["tool_calls"]:
                                    idx = tc.get("index", 0)
                                    if idx not in tool_calls_dict:
                                        tool_calls_dict[idx] = {
                                            "id": tc.get("id", ""),
                                            "type": "function",
                                            "function": {
                                                "name": tc["function"].get("name", ""),
                                                "arguments": "",
                                            },
                                        }
                                    if (
                                        "function" in tc
                                        and "arguments" in tc["function"]
                                    ):
                                        tool_calls_dict[idx]["function"][
                                            "arguments"
                                        ] += tc["function"]["arguments"]

                            if "finish_reason" in choice and choice["finish_reason"]:
                                finish_reason = choice["finish_reason"]
                        except (KeyError, IndexError):
                            pass

                    if tool_calls_dict:
                        tc_list = list(tool_calls_dict.values())
                        agent_messages.append(
                            {
                                "role": "assistant",
                                "content": loop_content,
                                "tool_calls": tc_list,
                            }
                        )

                        results = agent_loop_obj.execute_tool_calls(tc_list)
                        agent_loop_obj.session.steps.append(
                            type(
                                "AgentStep",
                                (),
                                {
                                    "step_number": agent_turn,
                                    "model_thought": loop_content[:500],
                                    "tool_results": results,
                                },
                            )
                        )

                        result_msgs = agent_loop_obj.build_tool_result_messages(
                            results, tc_list
                        )
                        agent_messages.extend(result_msgs)

                        summary = HermesResultAnalyzer.summarize_for_model(
                            results, max_chars=400
                        )
                        first_line = (
                            summary.split("\n")[0] if summary else "Tool executed"
                        )
                        yield {"type": "status", "content": first_line}

                        if not agent_loop_obj.should_continue():
                            yield {
                                "type": "harness_warning",
                                "content": "Agent budget exhausted — finalizing current result.",
                            }
                            break
                        continue

                    if finish_reason == "length":
                        log.warning("Agent hit max_tokens. Auto-continuing...")
                        agent_messages.append(
                            {"role": "assistant", "content": loop_content}
                        )
                        agent_messages.append(
                            {
                                "role": "user",
                                "content": "Continue exactly where you left off, from the very next character.",
                            }
                        )
                        continue

                    break

                elapsed = time.perf_counter() - t0
                synthetic_raw = {
                    "choices": [{"message": {"content": full_content}}],
                    "usage": last_usage,
                }
                hop = _timed_hop("hermes_agent", selected_model, synthetic_raw, elapsed)
                hops.append(hop)

                session_summary = agent_loop_obj.build_summary()
                log.info("\n%s", session_summary)

                aggregate_usage = TokenUsage()
                for h in hops:
                    aggregate_usage = aggregate_usage + h.usage
                log.info("Pipeline complete — aggregate tokens: [%s]", aggregate_usage)
                return
            else:
                if is_continuation:
                    task_type = TaskType.CODING_COMPLEX
                    yield {"type": "status", "content": "Resuming code generation..."}
                else:
                    minimized_history = []
                    if history:
                        last_msg = history[-1]
                        content = last_msg.get("content", "")
                        content_clean = re.sub(
                            r"```[\s\S]*?```", "```\n[Code block omitted]\n```", content
                        )
                        if len(content_clean) > MAX_TRIAGE_CONTENT_CHARS:
                            content_clean = (
                                content_clean[:MAX_TRIAGE_CONTENT_CHARS]
                                + "\n...[truncated]"
                            )
                        minimized_history.append(
                            {"role": last_msg.get("role"), "content": content_clean}
                        )
                    triage_query = user_query
                    if (
                        "I have attached a file named" in triage_query
                        and "User Prompt:\n" in triage_query
                    ):
                        parts = triage_query.split("User Prompt:\n")
                        if len(parts) > 1:
                            triage_query = parts[-1]
                    minimized_history.append({"role": "user", "content": triage_query})

                    yield {"type": "status", "content": "Analyzing query complexity..."}
                    triage_prompt = (
                        "You are the Iris AI query router.\n"
                        "If the user asks a conversational/general knowledge question, do NOT output any tags; answer directly.\n\n"
                        "Otherwise, output EXACTLY ONE tag and NOTHING ELSE. DO NOT answer the query yourself:\n"
                        "- [TASK_TYPE: coding_simple] (for simple coding questions, explaining code, syntax, basic functions, single script edits)\n"
                        "- [TASK_TYPE: coding_complex] (for large projects, writing games, custom emulators/drivers, multi-file codebases, complex logic coding, or generating full websites/web apps/UI pages)\n"
                        "- [TASK_TYPE: math] (for equations, proofs, algorithmic derivations)\n"
                        "- [TASK_TYPE: reasoning] (for deep logic puzzles, architecture design, long analysis)\n\n"
                        "CRITICAL: If the query mentions writing a complete game (e.g. Pong), building compilers, operating system bootloaders, complex hardware simulation, or creating full websites/UIs/landing pages, output [TASK_TYPE: coding_complex]."
                    )
                    triage_messages = [
                        {
                            "role": "system",
                            "content": triage_prompt + _get_system_time_directive(),
                        },
                        *minimized_history,
                    ]

                    t0_triage = time.perf_counter()
                    triage_answer = ""
                    triage_usage = {}
                    try:
                        async for chunk in client.stream_chat(
                            model=Model.ORCHESTRATOR.value,
                            messages=triage_messages,
                            temperature=0.2,
                            max_tokens=MAX_TOKENS_TRIAGE,
                        ):
                            if chunk.get("usage"):
                                triage_usage = chunk["usage"]
                            token = (
                                chunk.get("choices", [{}])[0]
                                .get("delta", {})
                                .get("content", "")
                            )
                            if token:
                                triage_answer += token
                            if chunk.get("keepalive"):
                                yield {"type": "status", "content": "Analyzing..."}
                    except (
                        openai.APIStatusError,
                        openai.APIConnectionError,
                        openai.APITimeoutError,
                    ) as exc:
                        log.exception("Unexpected error in Triage stage: %s", exc)
                        triage_answer = "[TASK_TYPE: general]"

                    task_type = None
                    if re.search(
                        r"\[\s*task_type:\s*coding_complex\s*\]",
                        triage_answer,
                        re.IGNORECASE,
                    ):
                        task_type = TaskType.CODING_COMPLEX
                    elif re.search(
                        r"\[\s*task_type:\s*coding_simple\s*\]",
                        triage_answer,
                        re.IGNORECASE,
                    ):
                        task_type = TaskType.CODING_SIMPLE
                    elif re.search(
                        r"\[\s*task_type:\s*coding\s*\]", triage_answer, re.IGNORECASE
                    ):
                        task_type = TaskType.CODING_SIMPLE
                    elif re.search(
                        r"\[\s*task_type:\s*math\s*\]", triage_answer, re.IGNORECASE
                    ):
                        task_type = TaskType.MATH
                    elif re.search(
                        r"\[\s*task_type:\s*reasoning\s*\]",
                        triage_answer,
                        re.IGNORECASE,
                    ):
                        task_type = TaskType.REASONING
                    elif re.search(
                        r"\[\s*task_type:\s*general\s*\]", triage_answer, re.IGNORECASE
                    ):
                        task_type = TaskType.GENERAL

                    if task_type is None and "task_type" not in triage_answer.lower():
                        task_type = fallback_classify(user_query)

                    if task_type is None:
                        triage_clean = triage_answer.strip()
                        if not triage_clean:
                            triage_clean = "Hello! How can I help you today?"

                        yield {"type": "token", "content": triage_clean}
                        elapsed = time.perf_counter() - t0_triage
                        synthetic_raw = {
                            "choices": [{"message": {"content": triage_clean}}],
                            "usage": triage_usage,
                        }
                        hop = _timed_hop(
                            "0:triage_answer",
                            Model.ORCHESTRATOR.value,
                            synthetic_raw,
                            elapsed,
                        )
                        hop.content = triage_clean
                        hops.append(hop)
                        return

                yield {
                    "type": "status",
                    "content": f"Task categorized as {task_type.value.upper()}...",
                }

            if task_type == TaskType.CONTROL:
                yield {"type": "status", "content": "Generating computer command..."}
                from src.core.controller import (
                    _get_agent_system_prompt,
                    parse_ai_response,
                    execute_action_by_dict,
                )

                control_messages = [
                    {"role": "system", "content": _get_agent_system_prompt()},
                    {"role": "user", "content": user_query},
                ]

                action_json = ""
                try:
                    async for chunk in client.stream_chat(
                        model=Model.CODE_SIMPLE.value,
                        messages=control_messages,
                        temperature=0.1,
                        max_tokens=1024,
                    ):
                        token = (
                            chunk.get("choices", [{}])[0]
                            .get("delta", {})
                            .get("content", "")
                        )
                        if token:
                            action_json += token

                    action_dict = parse_ai_response(action_json)
                    if action_dict:
                        action_name = action_dict.get("action", "unknown")
                        yield {"type": "status", "content": f"Executing: {action_name}"}
                        result = execute_action_by_dict(action_dict)
                        yield {
                            "type": "action_result",
                            "content": f"Action '{action_name}' Executed.\nResult:\n{result}",
                        }
                        messages.append(
                            {
                                "role": "system",
                                "content": f"Computer Command Execution Result:\n{result}\n\n",
                            }
                        )
                    else:
                        yield {"type": "status", "content": "Action failed to parse."}
                        messages.append(
                            {
                                "role": "system",
                                "content": "Computer Command Failed.\n\n",
                            }
                        )
                except Exception as exc:
                    log.exception("Error in Control stage: %s", exc)
                    messages.append(
                        {
                            "role": "system",
                            "content": "Computer Command Failed due to exception.\n\n",
                        }
                    )

                task_type = TaskType.GENERAL

            if task_type in (TaskType.GENERAL, TaskType.SEARCH):
                t0 = time.perf_counter()
                selected_model = TASK_TO_MODEL[task_type].value
                log.info("Starting general response with %s...", selected_model)
                general_messages = [
                    {
                        "role": "system",
                        "content": GENERAL_SYSTEM_PROMPT + _get_system_time_directive(),
                    },
                    *messages,
                ]
                try:
                    full_content = ""
                    last_usage = {}
                    for i in range(MAX_CONTINUATION_LOOPS):
                        finish_reason = "stop"
                        loop_content = ""
                        async for chunk in client.stream_chat(
                            model=selected_model,
                            messages=general_messages,
                            temperature=0.3,
                            max_tokens=MAX_TOKENS_GENERAL,
                        ):
                            try:
                                choice = chunk.get("choices", [{}])[0]
                                if chunk.get("usage"):
                                    last_usage = chunk["usage"]
                                delta = choice.get("delta", {})
                                token = delta.get("content", "")
                                if token:
                                    loop_content += token
                                    full_content += token
                                    yield {"type": "token", "content": token}
                                if (
                                    "finish_reason" in choice
                                    and choice["finish_reason"]
                                ):
                                    finish_reason = choice["finish_reason"]
                            except (KeyError, IndexError):
                                pass
                        if finish_reason == "length":
                            log.warning(
                                "Orchestrator hit max_tokens length in GENERAL. Auto-continuing (loop %d)...",
                                i + 1,
                            )
                            general_messages.append(
                                {"role": "assistant", "content": loop_content}
                            )
                            general_messages.append(
                                {
                                    "role": "user",
                                    "content": "Continue exactly where you left off, from the very next character. Do not repeat anything.",
                                }
                            )
                        else:
                            break

                    elapsed = time.perf_counter() - t0
                    synthetic_raw = {
                        "choices": [{"message": {"content": full_content}}],
                        "usage": last_usage,
                    }
                    hop = _timed_hop(
                        "1:general", selected_model, synthetic_raw, elapsed
                    )
                    hops.append(hop)
                except Exception as exc:
                    log.exception("Error in General stage: %s", exc)
                    raise

            elif task_type == TaskType.MATH:
                t0 = time.perf_counter()
                log.info("Starting math solver with %s...", Model.MATH.value)
                math_messages = [
                    {
                        "role": "system",
                        "content": MATH_SYSTEM_PROMPT + _get_system_time_directive(),
                    },
                    *messages,
                ]
                try:
                    full_content = ""
                    last_usage = {}
                    for i in range(MAX_CONTINUATION_LOOPS):
                        finish_reason = "stop"
                        loop_content = ""
                        async for chunk in client.stream_chat(
                            model=Model.MATH.value,
                            messages=math_messages,
                            temperature=0.2,
                            max_tokens=MAX_TOKENS,
                        ):
                            try:
                                choice = chunk.get("choices", [{}])[0]
                                if chunk.get("usage"):
                                    last_usage = chunk["usage"]
                                delta = choice.get("delta", {})
                                token = delta.get("content", "")
                                if token:
                                    loop_content += token
                                    full_content += token
                                    yield {"type": "token", "content": token}
                                if (
                                    "finish_reason" in choice
                                    and choice["finish_reason"]
                                ):
                                    finish_reason = choice["finish_reason"]
                            except (KeyError, IndexError):
                                pass
                        if finish_reason == "length":
                            log.warning(
                                "Model.MATH hit max_tokens length in MATH. Auto-continuing (loop %d)...",
                                i + 1,
                            )
                            math_messages.append(
                                {"role": "assistant", "content": loop_content}
                            )
                            math_messages.append(
                                {
                                    "role": "user",
                                    "content": "Continue exactly where you left off, from the very next character. Do not repeat anything.",
                                }
                            )
                        else:
                            break

                    elapsed = time.perf_counter() - t0
                    synthetic_raw = {
                        "choices": [{"message": {"content": full_content}}],
                        "usage": last_usage,
                    }
                    hop = _timed_hop("1:math", Model.MATH.value, synthetic_raw, elapsed)
                    hops.append(hop)
                except Exception as exc:
                    log.exception("Error in Math stage: %s", exc)
                    raise

            elif task_type == TaskType.REASONING:
                t0 = time.perf_counter()
                log.info("Starting deep reasoning with %s...", Model.REASONING.value)
                reasoning_messages = [
                    {
                        "role": "system",
                        "content": REASONING_SYSTEM_PROMPT
                        + _get_system_time_directive(),
                    },
                    *messages,
                ]
                try:
                    full_content = ""
                    last_usage = {}
                    in_thinking = False
                    for i in range(MAX_CONTINUATION_LOOPS):
                        finish_reason = "stop"
                        loop_content = ""
                        async for chunk in client.stream_chat(
                            model=Model.REASONING.value,
                            messages=reasoning_messages,
                            temperature=0.5,
                            max_tokens=MAX_TOKENS,
                            extra_body={"include_reasoning": True},
                        ):
                            try:
                                choice = chunk.get("choices", [{}])[0]
                                if chunk.get("usage"):
                                    last_usage = chunk["usage"]
                                delta = choice.get("delta", {})

                                if (
                                    "reasoning_content" in delta
                                    and delta["reasoning_content"]
                                ):
                                    if not in_thinking:
                                        yield {"type": "token", "content": "<think>\n"}
                                        in_thinking = True
                                    yield {
                                        "type": "token",
                                        "content": delta["reasoning_content"],
                                    }
                                else:
                                    if in_thinking:
                                        yield {
                                            "type": "token",
                                            "content": "\n</think>\n\n",
                                        }
                                        in_thinking = False

                                token = delta.get("content", "")
                                if token:
                                    loop_content += token
                                    full_content += token
                                    yield {"type": "token", "content": token}
                                if (
                                    "finish_reason" in choice
                                    and choice["finish_reason"]
                                ):
                                    finish_reason = choice["finish_reason"]
                            except (KeyError, IndexError):
                                pass
                        if finish_reason == "length":
                            log.warning(
                                "Model.REASONING hit max_tokens length in REASONING. Auto-continuing (loop %d)...",
                                i + 1,
                            )
                            reasoning_messages.append(
                                {"role": "assistant", "content": loop_content}
                            )
                            reasoning_messages.append(
                                {
                                    "role": "user",
                                    "content": "Continue exactly where you left off, from the very next character. Do not repeat anything.",
                                }
                            )
                        else:
                            break

                    if in_thinking:
                        yield {"type": "token", "content": "\n</think>\n\n"}
                    elapsed = time.perf_counter() - t0
                    synthetic_raw = {
                        "choices": [{"message": {"content": full_content}}],
                        "usage": last_usage,
                    }
                    hop = _timed_hop(
                        "1:reasoning", Model.REASONING.value, synthetic_raw, elapsed
                    )
                    hops.append(hop)
                except Exception as exc:
                    log.exception("Error in Reasoning stage: %s", exc)
                    raise

            elif task_type == TaskType.CODING_SIMPLE:
                t0 = time.perf_counter()
                log.info(
                    "Starting simple coding response with %s...",
                    Model.CODE_SIMPLE.value,
                )
                code_messages = [
                    {
                        "role": "system",
                        "content": CODE_SYSTEM_PROMPT + _get_system_time_directive(),
                    },
                    *messages,
                ]
                try:
                    full_content = ""
                    last_usage = {}
                    for i in range(MAX_CONTINUATION_LOOPS):
                        finish_reason = "stop"
                        loop_content = ""
                        stripped_leading_fence = False if i > 0 else True
                        continuation_buffer = ""
                        async for chunk in client.stream_chat(
                            model=Model.CODE_SIMPLE.value,
                            messages=code_messages,
                            temperature=0.2,
                            max_tokens=MAX_TOKENS,
                        ):
                            try:
                                choice = chunk.get("choices", [{}])[0]
                                if chunk.get("usage"):
                                    last_usage = chunk["usage"]
                                delta = choice.get("delta", {})
                                token = delta.get("content", "")
                                if token:
                                    if not stripped_leading_fence:
                                        continuation_buffer += token
                                        if (
                                            len(continuation_buffer) >= 20
                                            or "\n" in continuation_buffer
                                            or (
                                                len(continuation_buffer) >= 10
                                                and "`" not in continuation_buffer
                                            )
                                        ):
                                            match = re.match(
                                                r"^\s*```(?:html|python|py|javascript|js|css|sh|bash|json|markdown|md)?\s*",
                                                continuation_buffer,
                                                re.IGNORECASE,
                                            )
                                            if match:
                                                continuation_buffer = (
                                                    continuation_buffer[match.end() :]
                                                )
                                            stripped_leading_fence = True
                                            token = continuation_buffer
                                            continuation_buffer = ""
                                        else:
                                            continue
                                    if token:
                                        loop_content += token
                                        full_content += token
                                        yield {"type": "token", "content": token}
                                if (
                                    "finish_reason" in choice
                                    and choice["finish_reason"]
                                ):
                                    finish_reason = choice["finish_reason"]
                            except (KeyError, IndexError):
                                pass
                        if not stripped_leading_fence and continuation_buffer:
                            match = re.match(
                                r"^\s*```(?:html|python|py|javascript|js|css|sh|bash|json|markdown|md)?\s*",
                                continuation_buffer,
                                re.IGNORECASE,
                            )
                            if match:
                                continuation_buffer = continuation_buffer[match.end() :]
                            if continuation_buffer:
                                loop_content += continuation_buffer
                                full_content += continuation_buffer
                                yield {"type": "token", "content": continuation_buffer}
                            stripped_leading_fence = True
                            continuation_buffer = ""
                        if finish_reason == "length":
                            log.warning(
                                "Model.CODE_SIMPLE hit max_tokens length in CODING_SIMPLE. Auto-continuing (loop %d)...",
                                i + 1,
                            )
                            code_messages.append(
                                {"role": "assistant", "content": loop_content}
                            )
                            code_messages.append(
                                {
                                    "role": "user",
                                    "content": "Continue exactly where you left off, from the very next character. Do not repeat anything, do not write intro text or markdown blocks, just the raw continuation.",
                                }
                            )
                        else:
                            break

                    elapsed = time.perf_counter() - t0
                    synthetic_raw = {
                        "choices": [{"message": {"content": full_content}}],
                        "usage": last_usage,
                    }
                    hop = _timed_hop(
                        "1:coding_simple",
                        Model.CODE_SIMPLE.value,
                        synthetic_raw,
                        elapsed,
                    )
                    hops.append(hop)
                except Exception as exc:
                    log.exception("Error in Simple Coding stage: %s", exc)
                    raise

            elif task_type == TaskType.CODING_COMPLEX:
                raw_reasoning = ""
                raw_code = ""
                raw_review = ""

                if is_continuation:
                    raw_reasoning = "Continuation requested. Continuing from the previous truncated code."
                    hop1 = HopResult(
                        "1:reasoning",
                        Model.REASONING.value,
                        raw_reasoning,
                        TokenUsage(),
                        0.0,
                    )
                    hops.append(hop1)
                else:
                    t0_reasoning = time.perf_counter()
                    yield {"type": "status", "content": "Stage 1 — Deep reasoning..."}
                    log.info(
                        "Starting reasoning stage with %s...", Model.REASONING.value
                    )
                    last_yield_time = time.time()
                    in_thinking = False
                    try:
                        async for chunk in client.stream_chat(
                            model=Model.REASONING.value,
                            messages=messages,
                            temperature=0.6,
                            max_tokens=MAX_TOKENS,
                            extra_body={"include_reasoning": True},
                        ):
                            delta = chunk.get("choices", [{}])[0].get("delta", {})

                            if (
                                "reasoning_content" in delta
                                and delta["reasoning_content"]
                            ):
                                if not in_thinking:
                                    yield {"type": "token", "content": "<think>\n"}
                                    in_thinking = True
                                yield {
                                    "type": "token",
                                    "content": delta["reasoning_content"],
                                }
                                raw_reasoning += delta["reasoning_content"]
                            else:
                                if in_thinking:
                                    yield {"type": "token", "content": "\n</think>\n\n"}
                                    in_thinking = False

                            token = delta.get("content", "")
                            if token:
                                raw_reasoning += token
                            if time.time() - last_yield_time > 2.0:
                                yield {"type": "status", "content": "Deep reasoning..."}
                                last_yield_time = time.time()

                        if in_thinking:
                            yield {"type": "token", "content": "\n</think>\n\n"}

                        elapsed = time.perf_counter() - t0_reasoning
                        hop1 = _timed_hop(
                            "1:reasoning",
                            Model.REASONING.value,
                            {"content": raw_reasoning},
                            elapsed,
                        )
                        hop1.log_summary()
                        hops.append(hop1)
                    except Exception as exc:
                        log.exception("Error in Reasoning stage: %s", exc)
                        raise

                t0_code = time.perf_counter()
                yield {"type": "status", "content": "Stage 2 — Writing code..."}
                log.info(
                    "Starting code generation with %s...", Model.CODE_COMPLEX.value
                )

                code_sys_prompt = CODE_SYSTEM_PROMPT
                if is_continuation:
                    code_sys_prompt += (
                        "\n\nIMPORTANT: The previous code was truncated. Please continue writing the code exactly "
                        "from where it cut off in the previous turn. Do NOT rewrite the entire file from the beginning. "
                        "Start writing immediately from the next character/line, without introducing it, and do not wrap it "
                        "in new markdown code blocks unless you are continuing inside one."
                    )

                code_messages = [
                    {
                        "role": "system",
                        "content": code_sys_prompt + _get_system_time_directive(),
                    },
                    *messages[:-1],
                    {
                        "role": "user",
                        "content": f"User Query: {user_query}\n\nArchitecture/Plan:\n{raw_reasoning[-MAX_STAGE_INPUT_CHARS:]}",
                    },
                ]
                try:
                    last_code_usage = {}
                    for i in range(MAX_CONTINUATION_LOOPS):
                        finish_reason = "stop"
                        loop_content = ""
                        stripped_leading_fence = False if i > 0 else True
                        continuation_buffer = ""
                        async for chunk in client.stream_chat(
                            model=Model.CODE_COMPLEX.value,
                            messages=code_messages,
                            temperature=0.2,
                            max_tokens=MAX_TOKENS,
                        ):
                            try:
                                choice = chunk.get("choices", [{}])[0]
                                if chunk.get("usage"):
                                    last_code_usage = chunk["usage"]
                                delta = choice.get("delta", {})
                                token = delta.get("content", "")
                                if token:
                                    if not stripped_leading_fence:
                                        continuation_buffer += token
                                        if (
                                            len(continuation_buffer) >= 20
                                            or "\n" in continuation_buffer
                                            or (
                                                len(continuation_buffer) >= 10
                                                and "`" not in continuation_buffer
                                            )
                                        ):
                                            match = re.match(
                                                r"^\s*```(?:html|python|py|javascript|js|css|sh|bash|json|markdown|md)?\s*",
                                                continuation_buffer,
                                                re.IGNORECASE,
                                            )
                                            if match:
                                                continuation_buffer = (
                                                    continuation_buffer[match.end() :]
                                                )
                                            stripped_leading_fence = True
                                            token = continuation_buffer
                                            continuation_buffer = ""
                                        else:
                                            continue
                                    if token:
                                        raw_code += token
                                        loop_content += token
                                        yield {"type": "token", "content": token}

                                if (
                                    "finish_reason" in choice
                                    and choice["finish_reason"]
                                ):
                                    finish_reason = choice["finish_reason"]

                                if chunk.get("keepalive"):
                                    yield {
                                        "type": "status",
                                        "content": "Writing code...",
                                    }
                            except (KeyError, IndexError):
                                pass
                        if not stripped_leading_fence and continuation_buffer:
                            match = re.match(
                                r"^\s*```(?:html|python|py|javascript|js|css|sh|bash|json|markdown|md)?\s*",
                                continuation_buffer,
                                re.IGNORECASE,
                            )
                            if match:
                                continuation_buffer = continuation_buffer[match.end() :]
                            if continuation_buffer:
                                raw_code += continuation_buffer
                                loop_content += continuation_buffer
                                yield {"type": "token", "content": continuation_buffer}
                            stripped_leading_fence = True
                            continuation_buffer = ""

                        if finish_reason == "length":
                            log.warning(
                                "MiMo hit max_tokens length. Auto-continuing (loop %d)...",
                                i + 1,
                            )

                            strip_len = 0
                            if loop_content.endswith("```\n"):
                                strip_len = 4
                            elif loop_content.endswith("```"):
                                strip_len = 3
                            elif loop_content.endswith("``"):
                                strip_len = 2
                            elif loop_content.endswith("`"):
                                strip_len = 1

                            if strip_len > 0:
                                loop_content = loop_content[:-strip_len]
                                raw_code = raw_code[:-strip_len]
                                yield {"type": "backspace", "count": strip_len}

                            code_messages.append(
                                {"role": "assistant", "content": loop_content}
                            )
                            code_messages.append(
                                {
                                    "role": "user",
                                    "content": "Continue exactly where you left off, from the very next character. Do not repeat anything, do not write intro text or markdown blocks, just the raw continuation.",
                                }
                            )
                        else:
                            break

                    elapsed = time.perf_counter() - t0_code
                    hop_code = _timed_hop(
                        "2:coding",
                        Model.CODE_COMPLEX.value,
                        {"content": raw_code},
                        elapsed,
                    )
                    hop_code.log_summary()
                    hops.append(hop_code)
                except Exception as exc:
                    log.exception("Error in Coding stage: %s", exc)
                    raise

                yield {"type": "clear"}

                t0_review = time.perf_counter()
                yield {
                    "type": "status",
                    "content": "Stage 3 — Reviewing and optimizing...",
                }
                log.info("Starting code review with %s...", Model.CODE_REVIEWER.value)

                reviewer_sys_prompt = CODE_REVIEWER_SYSTEM_PROMPT
                if is_continuation:
                    reviewer_sys_prompt += (
                        "\n\nIMPORTANT: The previous code was truncated. Please only review and output the final code continuation, "
                        "beginning exactly from where the previous code cut off. Do NOT rewrite the entire file from the beginning. "
                        "Start writing the code immediately from the next character/line without introductory text."
                    )

                review_messages = [
                    {"role": "system", "content": reviewer_sys_prompt},
                    *messages[:-1],
                    {
                        "role": "user",
                        "content": f"User Query: {user_query}\n\nDraft Code:\n{raw_code[-MAX_STAGE_INPUT_CHARS:]}",
                    },
                ]
                try:
                    last_review_usage = {}
                    for i in range(MAX_CONTINUATION_LOOPS):
                        finish_reason = "stop"
                        loop_content = ""
                        stripped_leading_fence = False if i > 0 else True
                        continuation_buffer = ""
                        async for chunk in client.stream_chat(
                            model=Model.CODE_REVIEWER.value,
                            messages=review_messages,
                            temperature=0.2,
                            max_tokens=MAX_TOKENS,
                        ):
                            try:
                                choice = chunk.get("choices", [{}])[0]
                                if chunk.get("usage"):
                                    last_review_usage = chunk["usage"]
                                delta = choice.get("delta", {})
                                token = delta.get("content", "")
                                if token:
                                    if not stripped_leading_fence:
                                        continuation_buffer += token
                                        if (
                                            len(continuation_buffer) >= 20
                                            or "\n" in continuation_buffer
                                            or (
                                                len(continuation_buffer) >= 10
                                                and "`" not in continuation_buffer
                                            )
                                        ):
                                            match = re.match(
                                                r"^\s*```(?:html|python|py|javascript|js|css|sh|bash|json|markdown|md)?\s*",
                                                continuation_buffer,
                                                re.IGNORECASE,
                                            )
                                            if match:
                                                continuation_buffer = (
                                                    continuation_buffer[match.end() :]
                                                )
                                            stripped_leading_fence = True
                                            token = continuation_buffer
                                            continuation_buffer = ""
                                        else:
                                            continue
                                    if token:
                                        raw_review += token
                                        loop_content += token
                                        yield {"type": "token", "content": token}

                                if (
                                    "finish_reason" in choice
                                    and choice["finish_reason"]
                                ):
                                    finish_reason = choice["finish_reason"]

                                if chunk.get("keepalive"):
                                    yield {
                                        "type": "status",
                                        "content": "Reviewing code...",
                                    }
                            except (KeyError, IndexError):
                                pass
                        if not stripped_leading_fence and continuation_buffer:
                            match = re.match(
                                r"^\s*```(?:html|python|py|javascript|js|css|sh|bash|json|markdown|md)?\s*",
                                continuation_buffer,
                                re.IGNORECASE,
                            )
                            if match:
                                continuation_buffer = continuation_buffer[match.end() :]
                            if continuation_buffer:
                                raw_review += continuation_buffer
                                loop_content += continuation_buffer
                                yield {"type": "token", "content": continuation_buffer}
                            stripped_leading_fence = True
                            continuation_buffer = ""

                        if finish_reason == "length":
                            log.warning(
                                "MiMo hit max_tokens length. Auto-continuing (loop %d)...",
                                i + 1,
                            )

                            strip_len = 0
                            if loop_content.endswith("```\n"):
                                strip_len = 4
                            elif loop_content.endswith("```"):
                                strip_len = 3
                            elif loop_content.endswith("``"):
                                strip_len = 2
                            elif loop_content.endswith("`"):
                                strip_len = 1

                            if strip_len > 0:
                                loop_content = loop_content[:-strip_len]
                                raw_review = raw_review[:-strip_len]
                                yield {"type": "backspace", "count": strip_len}

                            review_messages.append(
                                {"role": "assistant", "content": loop_content}
                            )
                            review_messages.append(
                                {
                                    "role": "user",
                                    "content": "Continue exactly where you left off, from the very next character. Do not repeat anything, do not write intro text or markdown blocks, just the raw continuation.",
                                }
                            )
                        else:
                            break

                    yield {
                        "type": "status",
                        "content": "Stage 4 — Verifying execution/syntax...",
                    }
                    log.info("Starting syntax verification (Stage 4)...")

                    for _attempt in range(2):
                        blocks = re.findall(
                            r"```(\w*)\n(.*?)```", raw_review, re.DOTALL
                        )
                        if not blocks:
                            break

                        lang, code = blocks[-1]
                        err = verify_code_syntax(code, lang)
                        if err is None:
                            break

                        log.warning("Syntax verification failed: %s", err)
                        yield {"type": "clear"}
                        yield {
                            "type": "status",
                            "content": "Stage 4 — Fixing syntax errors...",
                        }

                        fix_messages = [
                            {"role": "system", "content": CODE_REVIEWER_SYSTEM_PROMPT},
                            *messages[:-1],
                            {
                                "role": "user",
                                "content": f"User Query: {user_query}\n\nThe draft code you generated has a syntax error:\n\n```\n{err}\n```\n\nCode:\n```\n{code}\n```\n\nFix the error immediately, maintaining all requested features, and output the complete, corrected code.",
                            },
                        ]
                        raw_review = ""
                        try:
                            last_review_usage = {}
                            async for chunk in client.stream_chat(
                                model=Model.CODE_REVIEWER.value,
                                messages=fix_messages,
                                temperature=0.1,
                                max_tokens=MAX_TOKENS,
                            ):
                                try:
                                    choice = chunk.get("choices", [{}])[0]
                                    if chunk.get("usage"):
                                        last_review_usage = chunk["usage"]
                                    delta = choice.get("delta", {})
                                    token = delta.get("content", "")
                                    if token:
                                        raw_review += token
                                        yield {"type": "token", "content": token}
                                    if chunk.get("keepalive"):
                                        yield {
                                            "type": "status",
                                            "content": "Fixing code...",
                                        }
                                except (KeyError, IndexError):
                                    pass
                        except Exception as exc:
                            log.exception("Error during auto-correction: %s", exc)
                            break

                    elapsed = time.perf_counter() - t0_review
                    synthetic_raw = {
                        "choices": [{"message": {"content": raw_review}}],
                        "usage": last_review_usage,
                    }
                    hop_rev = _timed_hop(
                        "3:code_review",
                        Model.CODE_REVIEWER.value,
                        synthetic_raw,
                        elapsed,
                    )
                    hop_rev.log_summary()
                    hops.append(hop_rev)
                except Exception as exc:
                    log.exception("Error in Code Review/Execution stage: %s", exc)
                    raise

        elif mode == "fast":
            yield {"type": "status", "content": "Fast mode enabled..."}
            t0 = time.perf_counter()
            messages = optimize_messages(history, user_query)

            full_content = ""
            last_fast_usage = {}

            for i in range(MAX_CONTINUATION_LOOPS):
                finish_reason = "stop"
                loop_content = ""
                async for chunk in client.stream_chat(
                    model=Model.MATH.value,
                    messages=messages,
                    temperature=0.3,
                    max_tokens=MAX_TOKENS,
                ):
                    try:
                        choice = chunk.get("choices", [{}])[0]
                        if chunk.get("usage"):
                            last_fast_usage = chunk["usage"]
                        delta = choice.get("delta", {})
                        if "content" in delta and delta["content"]:
                            text = delta["content"]
                            loop_content += text
                            full_content += text
                            yield {"type": "token", "content": text}
                        if "finish_reason" in choice and choice["finish_reason"]:
                            finish_reason = choice["finish_reason"]
                    except (KeyError, IndexError):
                        pass

                if finish_reason == "length":
                    log.warning(
                        "Fast mode hit max_tokens length. Auto-continuing (loop %d)...",
                        i + 1,
                    )
                    messages.append({"role": "assistant", "content": loop_content})
                    messages.append(
                        {
                            "role": "user",
                            "content": "Continue exactly where you left off, from the very next character. Do not repeat anything.",
                        }
                    )
                else:
                    break

            elapsed = time.perf_counter() - t0
            synthetic_raw = {
                "choices": [{"message": {"content": full_content}}],
                "usage": last_fast_usage,
            }
            hop = _timed_hop("1:fast", Model.MATH.value, synthetic_raw, elapsed)
            hop.content = full_content
            hops.append(hop)

    aggregate_usage = TokenUsage()
    for h in hops:
        aggregate_usage = aggregate_usage + h.usage

    log.info("Pipeline complete — aggregate tokens: [%s]", aggregate_usage)


async def chat_loop() -> None:
    print("\nIris AI  —  How can I help you today?")
    print("Type 'exit' to quit.\n")
    history: list[dict[str, str]] = []

    while True:
        try:
            user_input = (await asyncio.to_thread(input, "You: ")).strip()
        except (EOFError, KeyboardInterrupt):
            print("\nIris AI: Goodbye!")
            break
        if not user_input:
            continue
        if user_input.lower() in {"exit", "quit", "bye"}:
            print("Iris AI: Goodbye!")
            break

        print("Iris AI: ", end="", flush=True)

        full_response = ""
        try:
            async for event in ask_stream(
                user_input, history=history or None, mode="smart"
            ):
                if event["type"] == "token":
                    text = event["content"]
                    print(text, end="", flush=True)
                    full_response += text
                elif event["type"] == "status":
                    print(f"[{event['content']}]", end=" ", flush=True)
        except Exception:
            print("Something went wrong. Please try again.\n")
            continue

        print()
        history.append({"role": "user", "content": user_input})
        history.append({"role": "assistant", "content": full_response})
        if len(history) > MAX_HISTORY_MESSAGES:
            history = history[-MAX_HISTORY_MESSAGES:]


if __name__ == "__main__":
    if len(sys.argv) > 1:
        single_query = " ".join(sys.argv[1:])

        async def _run() -> None:
            full_response = ""
            async for event in ask_stream(single_query, mode="smart"):
                if event["type"] == "token":
                    full_response += event["content"]
            print(f"\nIris AI: {full_response}\n")

        asyncio.run(_run())
    else:
        asyncio.run(chat_loop())
