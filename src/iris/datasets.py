import os
import re
import glob
import json
import random
import logging
from typing import Dict, List, Tuple, Callable, Optional, Any

try:
    from datasets import load_dataset
    DATASETS_AVAILABLE = True
except ImportError:
    DATASETS_AVAILABLE = False

try:
    import torch
    from torch.utils.data import Dataset
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

logger = logging.getLogger("iris_datasets")

class DatasetRegistry:
    """Registry pattern for loading and managing datasets professionally."""
    _registry: Dict[str, Callable] = {}

    @classmethod
    def register(cls, name: str) -> Callable:
        """Decorator to register a custom dataset parser."""
        def wrapper(func: Callable) -> Callable:
            cls._registry[name] = func
            return func
        return wrapper

    @classmethod
    def load(cls, hf_path: str, subset_size: Optional[int] = None, **kwargs) -> List[Tuple[str, str]]:
        """Loads a dataset either via a registered custom parser or the generic parser."""
        if not DATASETS_AVAILABLE:
            logger.warning("datasets module not found. Returning empty list.")
            return []
            
        if hf_path in cls._registry:
            logger.info(f"Loading {hf_path} using custom registered parser.")
            return cls._registry[hf_path](subset_size, **kwargs)
            
        logger.info(f"Loading {hf_path} using generic parser.")
        return _load_generic(hf_path, subset_size, **kwargs)


def _shuffle_and_limit(ds: Any, subset_size: Optional[int]) -> Any:
    if subset_size:
        try:
            ds = ds.shuffle(buffer_size=10000, seed=42)
        except BaseException as e:
            logger.debug(f"Failed to shuffle dataset: {e}")
    return ds


def _load_generic(hf_path: str, subset_size: Optional[int] = None, split: str = "train", name: Optional[str] = None) -> List[Tuple[str, str]]:
    if not DATASETS_AVAILABLE:
        return []
    try:
        kwargs = dict(split=split, streaming=True)
        if name:
            kwargs["name"] = name
        ds = load_dataset(hf_path, **kwargs)
        ds = _shuffle_and_limit(ds, subset_size)
        
        pairs = []
        for row in ds:
            if subset_size and len(pairs) >= subset_size:
                break

            msgs = row.get("messages") or row.get("conversations") or []
            if msgs and isinstance(msgs, list) and len(msgs) >= 2:
                user_turn = next((m.get("content", "") or m.get("value", "") for m in msgs if m.get("role", "") in ("user", "human")), "")
                asst_turn = next((m.get("content", "") or m.get("value", "") for m in msgs if m.get("role", "") in ("assistant", "gpt", "bot")), "")
                if user_turn and asst_turn:
                    pairs.append((user_turn.strip(), asst_turn.strip()))
                    continue

            u = (row.get("instruction") or row.get("prompt") or row.get("input") or row.get("question") or "").strip()
            b = (row.get("output") or row.get("response") or row.get("answer") or row.get("completion") or "").strip()
            ctx = (row.get("context") or row.get("input") or "").strip()
            if ctx and u and ctx != u:
                u = f"{u}\n\n{ctx}"
            if u and b:
                pairs.append((u, b))
        return pairs
    except BaseException as e:
        logger.error(f"Failed to load {hf_path}: {e}")
        return []


@DatasetRegistry.register("blended_skill_talk")
def load_blended_skill_talk(subset_size: Optional[int] = None) -> List[Tuple[str, str]]:
    try:
        ds = load_dataset("blended_skill_talk", split="train", streaming=True)
        ds = _shuffle_and_limit(ds, subset_size)
        pairs = []
        for row in ds:
            if subset_size and len(pairs) >= subset_size:
                break
            utts, free = row.get("previous_utterance", []), row.get("free_messages", [])
            for i in range(0, len(utts) - 1, 2):
                if utts[i] and utts[i + 1]:
                    pairs.append((utts[i].strip(), utts[i + 1].strip()))
            if utts and free:
                for r in free:
                    if r:
                        pairs.append((utts[-1].strip(), r.strip()))
                        break
        return pairs
    except BaseException as e:
        logger.error(f"Failed to load blended_skill_talk: {e}")
        return []


@DatasetRegistry.register("daily_dialog")
def load_daily_dialog(subset_size: Optional[int] = None) -> List[Tuple[str, str]]:
    try:
        ds = load_dataset("daily_dialog", split="train", streaming=True)
        ds = _shuffle_and_limit(ds, subset_size)
        pairs = []
        for row in ds:
            if subset_size and len(pairs) >= subset_size:
                break
            d = row.get("dialog", [])
            for i in range(len(d) - 1):
                if d[i] and d[i + 1]:
                    pairs.append((d[i].strip(), d[i + 1].strip()))
        return pairs
    except BaseException as e:
        logger.error(f"Failed to load daily_dialog: {e}")
        return []


@DatasetRegistry.register("MBZUAI-Paris/Egyptian-SFT-Mixture")
def load_mbzuai_egyptian_mixture(subset_size: Optional[int] = None) -> List[Tuple[str, str]]:
    try:
        ds = load_dataset("MBZUAI-Paris/Egyptian-SFT-Mixture", split="train", streaming=True)
        ds = _shuffle_and_limit(ds, subset_size)
        pairs = []
        for row in ds:
            if subset_size and len(pairs) >= subset_size:
                break
            m = row.get("messages")
            if m and len(m) >= 2:
                pairs.append((m[0]["content"].strip(), m[1]["content"].strip()))
        return pairs
    except BaseException as e:
        logger.error(f"Failed to load Egyptian SFT Mixture: {e}")
        return []


@DatasetRegistry.register("OpenAssistant/oasst1")
def load_oasst1_dataset(subset_size: Optional[int] = None) -> List[Tuple[str, str]]:
    try:
        ds = load_dataset("OpenAssistant/oasst1", split="train", streaming=False)
        pairs = []
        messages = {}
        for row in ds:
            messages[row["message_id"]] = row

        for row in ds:
            if row["role"] == "assistant" and row.get("parent_id") in messages:
                parent = messages[row["parent_id"]]
                if parent["role"] == "prompter":
                    pairs.append((parent["text"].strip(), row["text"].strip()))

        random.shuffle(pairs)
        if subset_size:
            pairs = pairs[:subset_size]
        return pairs
    except BaseException as e:
        logger.error(f"OASST1 load error: {e}")
        return []


def load_markdown_files(md_dir: str = "md", pattern: str = "**/*.md") -> List[Tuple[str, str]]:
    pairs = []
    tag_re = re.compile(r"^(SYSTEM|USER|BOT)\s*:\s*(.*)", re.IGNORECASE)
    for path in glob.glob(os.path.join(md_dir, pattern), recursive=True):
        u, b, s, last = [], [], [], None
        file_pairs = []
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
                f.seek(0)
                for line in f:
                    m = tag_re.match(line)
                    if m:
                        if m.group(1).upper() in ("USER", "SYSTEM") and u and b:
                            file_pairs.append(("\n".join(s + u).strip(), "\n".join(b).strip()))
                            u, b = [], []
                        tag, content_line = m.group(1).upper(), m.group(2)
                        last = tag
                        if tag == "SYSTEM":
                            s.append(content_line)
                        elif tag == "USER":
                            u.append(content_line)
                        elif tag == "BOT":
                            b.append(content_line)
                    elif last:
                        if last == "SYSTEM":
                            s.append(line.rstrip())
                        elif last == "USER":
                            u.append(line.rstrip())
                        elif last == "BOT":
                            b.append(line.rstrip())
                if u and b:
                    file_pairs.append(("\n".join(s + u).strip(), "\n".join(b).strip()))
                if not file_pairs:
                    sections = re.split(r"\n#+\s+", content)
                    for sec in sections:
                        lines = sec.strip().split("\n", 1)
                        if len(lines) == 2:
                            file_pairs.append((lines[0].strip(), lines[1].strip()))
            pairs.extend(file_pairs)
        except BaseException as e:
            logger.debug(f"Failed to process Markdown file {path}: {e}")
    return pairs


if TORCH_AVAILABLE:
    class SFTDataset(Dataset):
        def __init__(self, conversations: List[Tuple[str, str]], tokenizer: Any, max_length: int = 128):
            self.samples = []
            for u, b in conversations:
                msgs = [
                    {"role": "user", "content": u},
                    {"role": "assistant", "content": b},
                ]
                full_text = tokenizer.apply_chat_template(msgs, tokenize=False)
                full_ids = tokenizer.encode(full_text, truncation=True, max_length=max_length)
                
                prompt_text = tokenizer.apply_chat_template(msgs[:1], tokenize=False, add_generation_prompt=True)
                prompt_ids = tokenizer.encode(prompt_text, truncation=True, max_length=max_length)
                
                prompt_len = min(len(prompt_ids), len(full_ids))
                mask = [0] * prompt_len + [1] * (len(full_ids) - prompt_len)
                self.samples.append({"input_ids": full_ids, "loss_mask": mask})

        def __len__(self) -> int:
            return len(self.samples)

        def __getitem__(self, idx: int) -> Dict[str, Any]:
            return self.samples[idx]

    def collate_fn(batch: List[Dict[str, Any]], tokenizer: Any) -> Dict[str, torch.Tensor]:
        pad = tokenizer.pad_token_id
        max_len = max(len(s["input_ids"]) for s in batch)
        ids, masks = [], []
        for s in batch:
            ids.append(s["input_ids"] + [pad] * (max_len - len(s["input_ids"])))
            masks.append(s["loss_mask"] + [0] * (max_len - len(s["loss_mask"])))
        return {
            "input_ids": torch.tensor(ids, dtype=torch.long),
            "loss_mask": torch.tensor(masks, dtype=torch.float),
        }

def cleanup_epoch_checkpoints(pattern: str = "*.pt") -> None:
    for p in glob.glob(pattern):
        try:
            os.remove(p)
        except BaseException as e:
            logger.debug(f"Failed to clean up checkpoint {p}: {e}")
