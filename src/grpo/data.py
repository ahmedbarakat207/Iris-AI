import json
from dataclasses import dataclass, field
from typing import List
from torch.utils.data import Dataset

@dataclass
class GRPOSample:
    prompt: str
    responses: List[str] = field(default_factory=list)
    raw_rewards: List[float] = field(default_factory=list)
    advantages: List[float] = field(default_factory=list)
    response_tokens: List[int] = field(default_factory=list)

@dataclass
class GRPOMetrics:
    step: int
    mean_reward: float
    std_reward: float
    mean_advantage: float
    policy_loss: float
    kl_divergence: float
    sft_loss: float
    learning_rate: float
    group_size: int
    num_groups: int

class GRPODataset(Dataset):
    def __init__(
        self,
        prompts: List[str],
        references: List[str] = None,
        max_length: int = 1024,
    ):
        self.prompts = prompts
        self.references = references or []
        self.max_length = max_length
        self.has_references = len(self.references) > 0

    def __len__(self):
        return len(self.prompts)

    def __getitem__(self, idx):
        item = {"prompt": self.prompts[idx]}
        if self.has_references and idx < len(self.references):
            item["reference"] = self.references[idx]
        return item

    @classmethod
    def from_huggingface(
        cls,
        dataset_name: str,
        config: str = None,
        split: str = "train",
        prompt_field: str = "instruction",
        response_field: str = None,
        max_samples: int = 5000,
    ):
        from datasets import load_dataset
        ds = load_dataset(dataset_name, config, split=split)
        prompts = []
        references = []
        for i, item in enumerate(ds):
            if i >= max_samples:
                break
            if prompt_field and prompt_field in item:
                prompt = item[prompt_field]
                if (
                    prompt_field == "instruction"
                    and "input" in item
                    and item["input"]
                    and str(item["input"]).strip()
                ):
                    prompt = prompt + "\n\n" + str(item["input"]).strip()
            elif "instruction" in item:
                prompt = item["instruction"]
                if "input" in item and item["input"] and str(item["input"]).strip():
                    prompt = prompt + "\n\n" + str(item["input"]).strip()
            elif "question" in item:
                prompt = item["question"]
            elif "text" in item:
                prompt = item["text"]
            elif "prompt" in item:
                prompt = item["prompt"]
            else:
                for k, v in item.items():
                    if isinstance(v, str) and len(v) > 20:
                        prompt = v
                        break
                else:
                    continue
            prompts.append(prompt)
            ref = None
            for field_name in (
                [response_field]
                if response_field
                else ["output", "response", "answer", "completion", "chosen"]
            ):
                if (
                    field_name in item
                    and isinstance(item[field_name], str)
                    and len(item[field_name]) > 5
                ):
                    ref = item[field_name]
                    break
            references.append(ref if ref else "")
        return cls(prompts, references if any(references) else None)

    @classmethod
    def from_jsonl(
        cls,
        path: str,
        prompt_field: str = "prompt",
        response_field: str = "response",
        max_samples: int = 5000,
    ):
        prompts = []
        references = []
        with open(path, "r") as f:
            for i, line in enumerate(f):
                if i >= max_samples:
                    break
                data = json.loads(line.strip())
                if prompt_field in data:
                    prompts.append(data[prompt_field])
                    ref = data.get(response_field, "")
                    references.append(ref if isinstance(ref, str) else str(ref))
        return cls(prompts, references if any(references) else None)
