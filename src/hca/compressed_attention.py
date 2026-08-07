import re
import os
import json
import gc
import threading
import platform
from typing import List, Dict, Tuple, Optional, Any
from enum import Enum
from dataclasses import dataclass, field

from src.core.logger import get_logger

logger = get_logger("compressed_attention")


class KVQuantLevel(str, Enum):

    Q4_0 = "q4_0"
    Q8_0 = "q8_0"
    F16 = "f16"
    AUTO = "auto"


class CompactionStrategy(str, Enum):
    CSA = "csa"
    HCA = "hca"
    HYBRID = "hybrid"
    NONE = "none"


@dataclass
class BlockScore:

    block_idx: int
    start_msg_idx: int
    end_msg_idx: int
    relevance_score: float
    compressed_text: str
    token_estimate: int


@dataclass
class CompressionResult:
    messages: List[Dict[str, str]]
    strategy_used: CompactionStrategy
    original_tokens: int
    compressed_tokens: int
    blocks_kept: int
    blocks_dropped: int
    kv_quant: KVQuantLevel
    estimated_ram_mb: float


_LLAMA_FTYPE_MOSTLY_Q4_0 = 2
_LLAMA_FTYPE_MOSTLY_Q8_0 = 7
_LLAMA_FTYPE_MOSTLY_F16 = 1


def _get_ftype(q: KVQuantLevel) -> int:
    if q == KVQuantLevel.Q4_0:
        return _LLAMA_FTYPE_MOSTLY_Q4_0
    elif q == KVQuantLevel.Q8_0:
        return _LLAMA_FTYPE_MOSTLY_Q8_0
    else:
        return _LLAMA_FTYPE_MOSTLY_F16


def select_kv_quant(
    model_size_gb: float = 2.5,
    n_ctx: int = 8192,
    ram_gb: float = 16.0,
    preference: KVQuantLevel = KVQuantLevel.AUTO,
    profile: str = "tiny",
) -> KVQuantLevel:

    if preference != KVQuantLevel.AUTO:
        return preference

    kv_per_token = _estimate_kv_per_token(model_size_gb)
    q8_kv = kv_per_token * n_ctx / (1024**3)
    f16_kv = q8_kv * 2

    free_ram_est = ram_gb - model_size_gb - 2.0

    if free_ram_est > 8.0 and profile not in ("tiny",):
        return KVQuantLevel.F16
    return KVQuantLevel.Q8_0


def _estimate_kv_per_token(model_size_gb: float) -> int:

    if model_size_gb <= 1.0:
        return 8000
    elif model_size_gb <= 2.0:
        return 12000
    elif model_size_gb <= 3.0:
        return 18000
    elif model_size_gb <= 5.0:
        return 25000
    elif model_size_gb <= 8.0:
        return 32000
    elif model_size_gb <= 14.0:
        return 46000
    else:
        return 60000


def estimate_kv_cache_ram(
    model_size_gb: float,
    n_ctx: int,
    kv_quant: KVQuantLevel,
) -> float:

    elements = _estimate_kv_per_token(model_size_gb)
    if kv_quant == KVQuantLevel.Q4_0:
        bytes_per = 0.5
    elif kv_quant == KVQuantLevel.Q8_0:
        bytes_per = 1.0
    else:
        bytes_per = 2.0
    return (elements * n_ctx * bytes_per) / (1024**2)


def _estimate_msg_tokens(msg: Dict[str, str]) -> int:
    content = msg.get("content", "")
    code_blocks = re.findall(r"```[\s\S]*?```", content)
    non_code = content
    for cb in code_blocks:
        non_code = non_code.replace(cb, "")
    return len(non_code) // 4 + sum(len(cb) // 3 for cb in code_blocks) + 4


def _estimate_tokens(messages: List[Dict[str, str]]) -> int:
    return sum(_estimate_msg_tokens(m) for m in messages) + 50


def _format_messages_as_text(messages: List[Dict[str, str]]) -> str:
    parts = []
    for m in messages:
        role = m.get("role", "user")
        content = m.get("content", "")
        content_clean = re.sub(r"```[\s\S]*?```", "[code]", content)
        if len(content_clean) > 500:
            content_clean = content_clean[:500] + "..."
        parts.append(f"[{role}] {content_clean}")
    return "\n\n".join(parts)


CSA_BLOCK_SIZE = 4

CSA_SCORING_PROMPT = """You are a relevance scorer. Rate how relevant this conversation block is to the user's latest question.

User's current question: {query}

Conversation block:
{block_text}

Return ONLY a number from 1 to 10 where:
1 = completely irrelevant
5 = somewhat relevant
10 = highly relevant (directly answers or relates to the current question)

Score:"""


def _score_block_with_model(
    block_text: str,
    query: str,
    llm=None,
) -> float:

    if True:
        keyword_score = _keyword_score(block_text, query)
        return keyword_score * 5.0
        return keyword_score * 5.0

    prompt = CSA_SCORING_PROMPT.format(query=query, block_text=block_text[:1200])
    try:
        resp = llm.create_chat_completion(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=5,
            temperature=0.0,
        )
        text = resp["choices"][0]["message"]["content"].strip()
        nums = re.findall(r"(\d+(?:\.\d+)?)", text)
        if nums:
            score = float(nums[0])
            return min(max(score, 1.0), 10.0) / 10.0
    except Exception as e:
        logger.warning(f"[CSA] Scoring failed: {e}")

    return _keyword_score(block_text, query)


def _keyword_score(block_text: str, query: str) -> float:

    q_words = set(re.findall(r"\w{3,}", query.lower()))
    b_words = set(re.findall(r"\w{3,}", block_text.lower()))
    if not q_words:
        return 0.5
    overlap = len(q_words & b_words)
    return min(overlap / len(q_words), 1.0)


def csa_compress(
    messages: List[Dict[str, str]],
    query: str,
    max_blocks: int = 6,
    block_size: int = CSA_BLOCK_SIZE,
    llm=None,
) -> Tuple[List[Dict[str, str]], List[BlockScore]]:

    if not messages:
        return [], []

    if len(messages) <= block_size + 1:
        return messages, []

    history = messages[:-1]
    current = messages[-1:]

    blocks: List[BlockScore] = []
    for i in range(0, len(history), block_size):
        chunk = history[i : i + block_size]
        block_text = _format_messages_as_text(chunk)
        est_tokens = _estimate_tokens(chunk)
        blocks.append(
            BlockScore(
                block_idx=i // block_size,
                start_msg_idx=i,
                end_msg_idx=min(i + block_size, len(history)),
                relevance_score=0.0,
                compressed_text=block_text,
                token_estimate=est_tokens,
            )
        )

    for b in blocks:
        b.relevance_score = _score_block_with_model(b.compressed_text, query, llm)

    blocks.sort(key=lambda b: b.relevance_score, reverse=True)

    kept_blocks = blocks[:max_blocks]
    kept_blocks.sort(key=lambda b: b.start_msg_idx)

    result = []
    for b in kept_blocks:
        for i in range(b.start_msg_idx, b.end_msg_idx):
            result.append(history[i])
    result.extend(current)

    return result, blocks


def csa_with_summary(
    messages: List[Dict[str, str]],
    query: str,
    max_blocks: int = 6,
    block_size: int = CSA_BLOCK_SIZE,
    llm=None,
    summarizer_llm=None,
) -> Tuple[List[Dict[str, str]], str]:

    kept, all_scores = csa_compress(messages, query, max_blocks, block_size, llm)

    dropped_scores = [b for b in all_scores if b.relevance_score < 0.3]
    if not dropped_scores:
        return kept, ""

    dropped_text = "\n---\n".join(b.compressed_text for b in dropped_scores[:8])
    summary = _summarize_dropped(dropped_text, summarizer_llm or llm)
    digest = {
        "role": "system",
        "content": f"[EARLIER CONTEXT (low relevance, summarized)]\n{summary}",
    }

    result = [kept[0]] if kept and kept[0].get("role") == "system" else []
    result.append(digest)
    if kept and kept[0].get("role") == "system":
        result.extend(kept[1:])
    else:
        result.extend(kept)
    return result, summary


HCA_COMPRESSION_RATIO = 8
HCA_TARGET_ENTRIES = 32

HCA_SUMMARY_PROMPT = """You are a context compressor. Compress the following conversation into a dense factual digest.

Rules:
- Preserve the user's original requests, goals, and preferences
- Keep all decisions made (tech stack, architecture, approach)
- Keep all key facts, numbers, filenames, error messages
- Drop greetings, filler, and repetitive confirmation
- Write in telegram style: short sentences, no filler
- Maximum 300 words
- CRITICAL: You MUST write the summary in ENGLISH ONLY. Do NOT use Esperanto or any other language. Do NOT include your internal thought process. Just output the summary directly.

Conversation to compress:
{conversation}

Dense digest in ENGLISH ONLY:"""


def _summarize_dropped(text: str, llm=None) -> str:
    if llm is None:
        lines = [
            l.strip() for l in text.split("\n") if l.strip() and len(l.strip()) > 20
        ]
        return "\n".join(lines[:6])

    prompt = HCA_SUMMARY_PROMPT.format(conversation=text[:3000])
    try:
        resp = llm.create_chat_completion(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.1,
        )
        return resp["choices"][0]["message"]["content"].strip()
    except Exception as e:
        logger.warning(f"[HCA] Summarization failed: {e}")
        lines = [
            l.strip() for l in text.split("\n") if l.strip() and len(l.strip()) > 20
        ]
        return "\n".join(lines[:6])


def hca_compress(
    messages: List[Dict[str, str]],
    ratio: int = HCA_COMPRESSION_RATIO,
    keep_recent: int = 2,
    llm=None,
) -> List[Dict[str, str]]:

    if not messages or len(messages) <= keep_recent + 2:
        return messages

    old = messages[:-keep_recent]
    recent = messages[-keep_recent:]

    if not old:
        return messages

    conversation_text = _format_messages_as_text(old)
    summary = _summarize_dropped(conversation_text, llm)

    digest = {
        "role": "system",
        "content": f"[CONVERSATION HISTORY — heavily compressed from {len(old)} messages]\n{summary}",
    }

    return [digest] + recent


def hca_multilevel(
    messages: List[Dict[str, str]],
    llm=None,
    level_sizes: Tuple[int, int, int] = (4, 12, 999),
) -> List[Dict[str, str]]:

    if not messages or len(messages) <= level_sizes[0]:
        return messages

    recent = messages[-level_sizes[0] :]
    mid = (
        messages[-level_sizes[1] : -level_sizes[0]]
        if len(messages) > level_sizes[0]
        else []
    )
    old = messages[: -level_sizes[1]] if len(messages) > level_sizes[1] else []

    result = []

    if old:
        old_text = _format_messages_as_text(old)
        old_summary = _summarize_dropped(old_text, llm)
        result.append(
            {
                "role": "system",
                "content": f"[DEEP HISTORY — {len(old)} messages compressed]\n{old_summary}",
            }
        )

    if mid:
        mid_text = _format_messages_as_text(mid)
        mid_summary = _summarize_dropped(mid_text, llm)
        result.append(
            {
                "role": "system",
                "content": f"[RECENT CONTEXT — {len(mid)} messages condensed]\n{mid_summary}",
            }
        )

    result.extend(recent)
    return result


class HybridCompressionManager:

    def __init__(
        self,
        n_ctx: int = 8192,
        kv_quant: KVQuantLevel = KVQuantLevel.AUTO,
        profile: str = "tiny",
        enable_csa: bool = True,
        enable_hca: bool = True,
    ):
        self.n_ctx = n_ctx
        self.kv_quant = kv_quant
        self.profile = profile
        self.enable_csa = enable_csa
        self.enable_hca = enable_hca

    def compress(
        self,
        messages: List[Dict[str, str]],
        query: str = "",
        llm=None,
        max_output_tokens: int = 4096,
        force_strategy: Optional[CompactionStrategy] = None,
    ) -> CompressionResult:

        if not messages:
            return CompressionResult(
                messages=[],
                strategy_used=CompactionStrategy.NONE,
                original_tokens=0,
                compressed_tokens=0,
                blocks_kept=0,
                blocks_dropped=0,
                kv_quant=self.kv_quant,
                estimated_ram_mb=0.0,
            )

        original_tokens = _estimate_tokens(messages)
        available = self.n_ctx - 256 - max_output_tokens
        pressure = original_tokens / max(available, 1)

        if force_strategy:
            strategy = force_strategy
        elif pressure < 0.5 and not self.enable_csa:
            strategy = CompactionStrategy.NONE
        elif pressure < 0.8 and self.enable_csa:
            strategy = CompactionStrategy.CSA
        elif self.enable_hca:
            strategy = CompactionStrategy.HCA
        else:
            strategy = CompactionStrategy.NONE

        if strategy == CompactionStrategy.NONE:
            compressed = messages
            blocks_kept = 0
            blocks_dropped = 0
        elif strategy == CompactionStrategy.CSA:
            max_blocks = max(4, available // (CSA_BLOCK_SIZE * 200))
            compressed, scores = csa_compress(
                messages, query, max_blocks, CSA_BLOCK_SIZE, llm
            )
            blocks_kept = len([s for s in scores if s.relevance_score >= 0.3])
            blocks_dropped = len(scores) - blocks_kept
        elif strategy == CompactionStrategy.HCA:
            compressed = hca_multilevel(messages, llm)
            blocks_kept = 0
            blocks_dropped = 0
        else:
            compressed, scores = csa_compress(messages, query, 6, CSA_BLOCK_SIZE, llm)
            compressed = hca_multilevel(compressed, llm)
            blocks_kept = 0
            blocks_dropped = 0

        compressed_tokens = _estimate_tokens(compressed)
        est_ram = estimate_kv_cache_ram(2.5, self.n_ctx, self.kv_quant)

        return CompressionResult(
            messages=compressed,
            strategy_used=strategy,
            original_tokens=original_tokens,
            compressed_tokens=compressed_tokens,
            blocks_kept=blocks_kept,
            blocks_dropped=blocks_dropped,
            kv_quant=self.kv_quant,
            estimated_ram_mb=est_ram,
        )

    def auto_compact(self, messages, query="", llm=None, max_output_tokens=4096):

        result = self.compress(messages, query, llm, max_output_tokens)
        return result.messages


def deduplicate_system_prompts(
    messages: List[Dict[str, str]],
) -> List[Dict[str, str]]:

    if not messages:
        return messages

    system_msgs = []
    non_system = []
    seen_prefixes = set()

    for msg in messages:
        if msg.get("role") != "system":
            non_system.append(msg)
            continue
        content = msg.get("content", "")
        prefix = content[:80].strip()
        if prefix in seen_prefixes:
            continue
        seen_prefixes.add(prefix)
        system_msgs.append(msg)

    return system_msgs + non_system


def estimate_savings(result: CompressionResult) -> Dict[str, Any]:

    if result.original_tokens <= 0:
        return {"savings_pct": 0.0, "summary": "No compression needed"}
    savings = 1.0 - (result.compressed_tokens / result.original_tokens)
    return {
        "strategy": result.strategy_used.value,
        "original_tokens": result.original_tokens,
        "compressed_tokens": result.compressed_tokens,
        "savings_pct": round(savings * 100, 1),
        "blocks_kept": result.blocks_kept,
        "blocks_dropped": result.blocks_dropped,
        "kv_quant": result.kv_quant.value,
        "kv_ram_mb": round(result.estimated_ram_mb, 1),
        "summary": (
            f"{result.strategy_used.value.upper()}: {result.original_tokens}"
            f"→{result.compressed_tokens} tokens ({savings*100:.0f}% saved), "
            f"KV cache: {result.estimated_ram_mb:.0f} MB ({result.kv_quant.value})"
        ),
    }


_hm_cache: Dict[str, HybridCompressionManager] = {}
_hm_lock = threading.Lock()


def get_compressor(
    n_ctx: int = 8192,
    kv_quant: KVQuantLevel = KVQuantLevel.AUTO,
    profile: str = "tiny",
) -> HybridCompressionManager:

    cache_key = f"{n_ctx}:{kv_quant.value}:{profile}"
    with _hm_lock:
        if cache_key not in _hm_cache:
            _hm_cache[cache_key] = HybridCompressionManager(
                n_ctx=n_ctx,
                kv_quant=kv_quant,
                profile=profile,
            )
        return _hm_cache[cache_key]


def smart_compress(
    messages: List[Dict[str, str]],
    query: str = "",
    n_ctx: int = 8192,
    max_output_tokens: int = 4096,
    llm=None,
    profile: str = "tiny",
    kv_quant: KVQuantLevel = KVQuantLevel.AUTO,
) -> CompressionResult:

    messages = deduplicate_system_prompts(messages)

    compressor = get_compressor(n_ctx, kv_quant, profile)
    return compressor.compress(messages, query, llm, max_output_tokens)


def unload_compressors():

    global _hm_cache
    with _hm_lock:
        _hm_cache.clear()
    gc.collect()
