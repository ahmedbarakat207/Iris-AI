import os
import re
import math
import json
import time
import random
import hashlib
import subprocess
import tempfile
import sys
from typing import List, Dict, Optional, Tuple, Generator, Any
from dataclasses import dataclass, field
from enum import Enum

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader

from src.grpo.reward_scoring import RewardDomain, RewardScorer
from src.grpo.data import GRPOSample, GRPOMetrics, GRPODataset
from src.grpo.bridge import GGUFPolicyBridge







@dataclass
class GRPOConfig:

    group_size: int = 4
    num_generations: int = 1

    clip_epsilon: float = 0.2
    kl_coeff: float = 0.04
    kl_target: float = 0.01
    sft_coeff: float = 0.3

    learning_rate: float = 1e-5
    max_grad_norm: float = 1.0
    warmup_steps: int = 100
    total_steps: int = 5000

    max_new_tokens: int = 512
    temperature: float = 0.8
    top_p: float = 0.95

    gradient_accumulation_steps: int = 4
    max_prompt_length: int = 1024


class GRPOTrainer:

    def __init__(
        self,
        policy_model: nn.Module,
        tokenizer: Any,
        config: GRPOConfig = None,
        reward_function: Optional[RewardScorer] = None,
        reference_model: Optional[nn.Module] = None,
        generation_model: Optional[Any] = None,
        device: torch.device = None,
    ):
        self.config = config or GRPOConfig()
        self.policy = policy_model
        self.tokenizer = tokenizer
        self.generation_model = generation_model or policy_model
        self.scorer = reward_function or RewardScorer()
        self.device = device or torch.device(
            "cuda"
            if torch.cuda.is_available()
            else "mps" if torch.backends.mps.is_available() else "cpu"
        )

        if reference_model is not None:
            self.reference = reference_model
        else:
            self.reference = self._clone_model(policy_model)

        self.policy.to(self.device)
        self.reference.to(self.device)
        for p in self.reference.parameters():
            p.requires_grad = False

        self.optimizer = torch.optim.AdamW(
            self.policy.parameters(), lr=self.config.learning_rate
        )
        self.kl_coeff = self.config.kl_coeff
        self.step_count = 0
        self.metrics_history: List[GRPOMetrics] = []

    def _clone_model(self, model: nn.Module) -> nn.Module:

        import copy

        clone = copy.deepcopy(model)
        clone.eval()
        return clone

    def generate_responses(
        self,
        prompts: List[str],
        num_per_prompt: int = None,
    ) -> List[List[str]]:

        if num_per_prompt is None:
            num_per_prompt = self.config.group_size

        all_responses = []
        for prompt in prompts:
            group = []
            for i in range(num_per_prompt):
                seed = i * 42 + self.step_count
                response = self._generate_single(prompt, seed=seed)
                group.append(response)
            all_responses.append(group)
        return all_responses

    def _generate_single(self, prompt: str, seed: int = 0) -> str:

        if hasattr(self.generation_model, "generate") and not hasattr(
            self.generation_model, "create_chat_completion"
        ):

            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                truncation=True,
                max_length=self.config.max_prompt_length,
            ).to(self.device)

            torch.manual_seed(seed)
            with torch.no_grad():
                outputs = self.generation_model.generate(
                    **inputs,
                    max_new_tokens=self.config.max_new_tokens,
                    temperature=self.config.temperature,
                    top_p=self.config.top_p,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                )
            return self.tokenizer.decode(
                outputs[0][inputs.input_ids.shape[1] :], skip_special_tokens=True
            )

        try:
            response = self.generation_model.create_chat_completion(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.config.max_new_tokens,
                temperature=self.config.temperature,
                top_p=self.config.top_p,
                seed=seed,
            )
            return response["choices"][0]["message"]["content"]
        except Exception:
            return "[generation failed]"

    def compute_rewards(
        self, prompts: List[str], all_responses: List[List[str]]
    ) -> List[GRPOSample]:

        samples = []
        for prompt, group in zip(prompts, all_responses):
            rewards = [self.scorer.score(prompt, resp) for resp in group]

            rewards_t = torch.tensor(rewards, dtype=torch.float32)
            mean_r = rewards_t.mean()
            std_r = rewards_t.std() + 1e-8
            advantages = ((rewards_t - mean_r) / std_r).tolist()

            token_counts = [
                (
                    len(self.tokenizer.encode(resp))
                    if self.tokenizer
                    else len(resp.split())
                )
                for resp in group
            ]

            samples.append(
                GRPOSample(
                    prompt=prompt,
                    responses=group,
                    raw_rewards=rewards,
                    advantages=advantages,
                    response_tokens=token_counts,
                )
            )
        return samples

    def _compute_log_probs(
        self, model: nn.Module, input_ids: torch.Tensor, attention_mask: torch.Tensor
    ) -> torch.Tensor:

        outputs = model(input_ids=input_ids, attention_mask=attention_mask)
        logits = outputs.logits[:, :-1, :]
        labels = input_ids[:, 1:]

        shift_attention = attention_mask[:, 1:] if attention_mask is not None else None
        log_probs = F.log_softmax(logits, dim=-1)
        token_log_probs = torch.gather(log_probs, -1, labels.unsqueeze(-1)).squeeze(-1)

        if shift_attention is not None:
            token_log_probs = token_log_probs * shift_attention

        return token_log_probs.sum(dim=-1)

    def _kl_divergence(
        self,
        policy_model: nn.Module,
        ref_model: nn.Module,
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor,
    ) -> torch.Tensor:

        with torch.no_grad():
            ref_outputs = ref_model(input_ids=input_ids, attention_mask=attention_mask)
            ref_logits = ref_outputs.logits

        pol_outputs = policy_model(input_ids=input_ids, attention_mask=attention_mask)
        pol_logits = pol_outputs.logits

        pol_log_probs = F.log_softmax(pol_logits, dim=-1)
        ref_log_probs = F.log_softmax(ref_logits, dim=-1)

        kl = F.kl_div(pol_log_probs, ref_log_probs, reduction="none", log_target=True)
        kl = kl.sum(dim=-1).mean()
        return kl

    def hybrid_loss(
        self,
        samples: List[GRPOSample],
        references: Optional[List[str]] = None,
        old_log_probs: Optional[List[torch.Tensor]] = None,
    ) -> Tuple[torch.Tensor, Dict[str, float]]:

        total_loss = torch.tensor(0.0, device=self.device, requires_grad=True)
        total_kl = torch.tensor(0.0, device=self.device)

        n_samples = 0
        all_advantages = []
        all_ratios = []

        for i, sample in enumerate(samples):
            for j, (response, advantage) in enumerate(
                zip(sample.responses, sample.advantages)
            ):
                if advantage == 0.0 and all(a == 0.0 for a in sample.advantages):
                    continue

                full_text = sample.prompt + "\n" + response
                encoded = self.tokenizer(
                    full_text,
                    return_tensors="pt",
                    truncation=True,
                    max_length=self.config.max_prompt_length
                    + self.config.max_new_tokens,
                ).to(self.device)

                new_log_prob = self._compute_log_probs(
                    self.policy, encoded.input_ids, encoded.attention_mask
                ).mean()

                with torch.no_grad():
                    old_log_prob = self._compute_log_probs(
                        self.reference, encoded.input_ids, encoded.attention_mask
                    ).mean()
                    if old_log_probs is not None and i < len(old_log_probs):
                        old_log_prob = old_log_probs[i]

                ratio = torch.exp(new_log_prob - old_log_prob)
                all_ratios.append(ratio.item())

                adv = torch.tensor(advantage, device=self.device)
                clipped_ratio = torch.clamp(
                    ratio, 1 - self.config.clip_epsilon, 1 + self.config.clip_epsilon
                )
                policy_loss = -torch.min(ratio * adv, clipped_ratio * adv)

                kl = self._kl_divergence(
                    self.policy,
                    self.reference,
                    encoded.input_ids,
                    encoded.attention_mask,
                )

                total_loss = total_loss + policy_loss - self.kl_coeff * kl
                total_kl = total_kl + kl
                n_samples += 1
                all_advantages.append(advantage)

        if n_samples == 0:
            return torch.tensor(0.0, device=self.device), {
                "loss": 0.0,
                "kl": 0.0,
                "sft_loss": 0.0,
            }

        total_loss = total_loss / n_samples
        avg_kl = (total_kl / n_samples).item()

        sft_loss_val = 0.0
        has_sft = references and any(ref and len(ref) > 5 for ref in references)
        if has_sft and self.config.sft_coeff > 0:
            sft_total = torch.tensor(0.0, device=self.device)
            sft_count = 0
            for i, sample in enumerate(samples):
                if i >= len(references) or not references[i] or len(references[i]) <= 5:
                    continue
                ref_text = sample.prompt + "\n" + references[i]
                encoded = self.tokenizer(
                    ref_text,
                    return_tensors="pt",
                    truncation=True,
                    max_length=self.config.max_prompt_length
                    + self.config.max_new_tokens,
                ).to(self.device)
                outputs = self.policy(
                    input_ids=encoded.input_ids, attention_mask=encoded.attention_mask
                )
                logits = outputs.logits[:, :-1, :]
                labels = encoded.input_ids[:, 1:]
                mask = (
                    encoded.attention_mask[:, 1:]
                    if encoded.attention_mask is not None
                    else None
                )
                ce = F.cross_entropy(
                    logits.reshape(-1, logits.size(-1)),
                    labels.reshape(-1),
                    reduction="none",
                ).view(labels.shape)
                if mask is not None:
                    ce = ce * mask
                    sft_total += ce.sum() / mask.sum().clamp(min=1)
                else:
                    sft_total += ce.mean()
                sft_count += 1

            if sft_count > 0:
                sft_loss_val = (sft_total / sft_count).item()
                total_loss = total_loss + self.config.sft_coeff * (
                    sft_total / sft_count
                )

        if avg_kl > self.config.kl_target * 2:
            self.kl_coeff *= 1.1
        elif avg_kl < self.config.kl_target / 2:
            self.kl_coeff *= 0.9
        self.kl_coeff = max(1e-4, min(0.2, self.kl_coeff))

        info = {
            "loss": total_loss.item(),
            "kl": avg_kl,
            "kl_coeff": self.kl_coeff,
            "sft_loss": sft_loss_val,
            "mean_ratio": sum(all_ratios) / len(all_ratios) if all_ratios else 0.0,
            "mean_advantage": (
                sum(all_advantages) / len(all_advantages) if all_advantages else 0.0
            ),
        }
        return total_loss, info

    def train_step(
        self,
        prompts: List[str],
        references: List[str] = None,
    ) -> GRPOMetrics:

        self.policy.train()
        G = self.config.group_size

        all_responses = self.generate_responses(prompts, num_per_prompt=G)

        samples = self.compute_rewards(prompts, all_responses)

        loss, loss_info = self.hybrid_loss(samples, references=references)

        if loss.requires_grad:
            loss.backward()
            torch.nn.utils.clip_grad_norm_(
                self.policy.parameters(), self.config.max_grad_norm
            )
            self.optimizer.step()
            self.optimizer.zero_grad()

        self.step_count += 1

        all_rewards = [r for s in samples for r in s.raw_rewards]
        metrics = GRPOMetrics(
            step=self.step_count,
            mean_reward=sum(all_rewards) / len(all_rewards) if all_rewards else 0.0,
            std_reward=torch.tensor(all_rewards).std().item() if all_rewards else 0.0,
            mean_advantage=loss_info.get("mean_advantage", 0.0),
            policy_loss=loss_info.get("loss", 0.0),
            kl_divergence=loss_info.get("kl", 0.0),
            sft_loss=loss_info.get("sft_loss", 0.0),
            learning_rate=self.config.learning_rate,
            group_size=G,
            num_groups=len(samples),
        )
        self.metrics_history.append(metrics)

        avg_kl = loss_info.get("kl", 0.0)
        if avg_kl > 0.05:
            print(
                f"  ⚠️  KL={avg_kl:.4f} — model drifting, consider reducing lr or increasing KL coeff"
            )

        return metrics

    def train(
        self,
        dataset: Dataset,
        batch_size: int = 16,
        num_epochs: int = 1,
        save_every: int = 500,
        save_dir: str = "./grpo_checkpoints",
    ) -> List[GRPOMetrics]:

        os.makedirs(save_dir, exist_ok=True)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
        all_metrics = []

        has_references = getattr(dataset, "has_references", False)

        print(f"\n{'='*60}")
        print(f"GRPO+SFT Hybrid Training — Group Size: {self.config.group_size}")
        print(
            f"KL Coeff: {self.kl_coeff:.4f}  |  SFT Coeff: {self.config.sft_coeff}  |  LR: {self.config.learning_rate}"
        )
        print(f"Device: {self.device}  |  Steps: {self.config.total_steps}")
        print(
            f"References: {'✓ available' if has_references else '✗ none (pure GRPO)'}"
        )
        print(f"{'='*60}\n")

        for epoch in range(num_epochs):
            for batch_idx, batch in enumerate(dataloader):
                if self.step_count >= self.config.total_steps:
                    break

                refs = None
                if isinstance(batch, dict):
                    prompts = batch.get(
                        "prompt", batch.get("text", batch.get("instruction", []))
                    )
                    refs = batch.get("reference", None)
                    if isinstance(prompts, torch.Tensor):
                        prompts = [
                            self.tokenizer.decode(p, skip_special_tokens=True)
                            for p in prompts
                        ]
                    if refs is not None:
                        if isinstance(refs, torch.Tensor):
                            refs = [
                                self.tokenizer.decode(r, skip_special_tokens=True)
                                for r in refs
                            ]
                        elif isinstance(refs, (list, tuple)):
                            refs = list(refs)
                        else:
                            refs = [str(refs)]
                elif isinstance(batch, (list, tuple)):
                    prompts = batch
                else:
                    prompts = [str(batch)]

                if isinstance(prompts, str):
                    prompts = [prompts]

                metrics = self.train_step(prompts, references=refs)
                all_metrics.append(metrics)

                if self.step_count % 10 == 0:
                    sft_str = (
                        f" SFT={metrics.sft_loss:.4f}" if metrics.sft_loss > 0 else ""
                    )
                    print(
                        f"Step {self.step_count:5d} | "
                        f"Reward: {metrics.mean_reward:.3f}±{metrics.std_reward:.3f} | "
                        f"Loss: {metrics.policy_loss:.4f} | "
                        f"KL: {metrics.kl_divergence:.4f}{sft_str} | "
                        f"β: {self.kl_coeff:.4f}"
                    )

                if self.step_count % save_every == 0:
                    ckpt_path = os.path.join(save_dir, f"grpo_step_{self.step_count}")
                    self.save_checkpoint(ckpt_path)

            if self.step_count >= self.config.total_steps:
                break

        final_path = os.path.join(save_dir, "grpo_final")
        self.save_checkpoint(final_path)
        print(
            f"\n[SUCCESS] GRPO+SFT hybrid training complete. {len(all_metrics)} steps. Model saved to {final_path}"
        )

        return all_metrics

    def save_checkpoint(self, path: str):

        os.makedirs(path, exist_ok=True)
        torch.save(
            {
                "policy_state_dict": self.policy.state_dict(),
                "optimizer_state_dict": self.optimizer.state_dict(),
                "step": self.step_count,
                "kl_coeff": self.kl_coeff,
                "config": self.config,
            },
            os.path.join(path, "grpo_checkpoint.pt"),
        )

    def load_checkpoint(self, path: str):

        ckpt = torch.load(
            os.path.join(path, "grpo_checkpoint.pt"), map_location=self.device
        )
        self.policy.load_state_dict(ckpt["policy_state_dict"])
        self.optimizer.load_state_dict(ckpt["optimizer_state_dict"])
        self.step_count = ckpt["step"]
        self.kl_coeff = ckpt["kl_coeff"]
        print(f"[GRPO] Resumed from step {self.step_count}")




def train_with_grpo(
    role: str,
    base_model_id: str,
    gguf_path: str = None,
    prompts_dataset: str = None,
    steps: int = 5000,
    group_size: int = 4,
    lr: float = 1e-5,
    sft_coeff: float = 0.3,
    save_dir: str = "./grpo_models",
    device_type: str = None,
) -> List[GRPOMetrics]:

    device = torch.device(
        device_type
        or (
            "cuda"
            if torch.cuda.is_available()
            else "mps" if torch.backends.mps.is_available() else "cpu"
        )
    )

    if prompts_dataset and os.path.exists(prompts_dataset):
        dataset = GRPODataset.from_jsonl(prompts_dataset)
    elif prompts_dataset:
        dataset = GRPODataset.from_huggingface(prompts_dataset, max_samples=steps)
    else:

        role_datasets = {
            "code": "WithinUsAI/claude_mythos_distilled_25k",
            "math": "EleutherAI/hendrycks_math",
            "reasoning": "attentionAllYouNeed/Vibe-Coding-Claude-Fable-5",
            "general": "teknium/OpenHermes-2.5",
        }
        ds_name = role_datasets.get(role, "teknium/OpenHermes-2.5")
        print(f"[GRPO] Using default dataset: {ds_name}")
        dataset = GRPODataset.from_huggingface(ds_name, max_samples=steps)

    print(
        f"[GRPO] Loaded {len(dataset)} prompts for role '{role}' (refs: {'yes' if getattr(dataset, 'has_references', False) else 'no'}, λ_SFT={sft_coeff})"
    )

    gguf = gguf_path or _find_gguf_for_role(role)
    bridge = GGUFPolicyBridge(
        gguf_path=gguf,
        base_model_name=base_model_id,
        device=device,
        use_4bit=True,
    )
    bridge.setup()

    policy = bridge.get_trainable_model()
    tokenizer = bridge.get_tokenizer()

    config = GRPOConfig(
        group_size=group_size,
        learning_rate=lr,
        sft_coeff=sft_coeff,
        total_steps=steps,
        max_new_tokens=512,
        temperature=0.8,
        top_p=0.95,
    )

    domain_map = {
        "code": RewardDomain.CODE,
        "math": RewardDomain.MATH,
        "reasoning": RewardDomain.REASONING,
        "general": RewardDomain.GENERAL,
    }
    scorer = RewardScorer(domain=domain_map.get(role, RewardDomain.MIXED))

    trainer = GRPOTrainer(
        policy_model=policy,
        tokenizer=tokenizer,
        config=config,
        reward_function=scorer,
        generation_model=bridge.gguf_llm,
        device=device,
    )

    metrics = trainer.train(
        dataset=dataset,
        batch_size=4,
        num_epochs=1,
        save_every=500,
        save_dir=os.path.join(save_dir, role),
    )

    return metrics


def _find_gguf_for_role(role: str) -> str:

    model_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")

    role_to_pattern = {
        "code": "qwen2.5-coder",
        "math": "qwen2.5-math",
        "reasoning": "deepseek",
        "general": "qwen2",
        "control": "Hermes",
        "triage": "Llama-3.2-3B",
    }
    pattern = role_to_pattern.get(role, role)

    for fn in os.listdir(model_dir):
        if fn.endswith(".gguf") and pattern.lower() in fn.lower():
            return os.path.join(model_dir, fn)

    raise FileNotFoundError(f"No GGUF found for role '{role}' in {model_dir}")


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description="GRPO Training for Iris AI")
    ap.add_argument("--role", default="code", help="Role to train")
    ap.add_argument("--base-model", default="Qwen/Qwen2.5-Coder-7B-Instruct")
    ap.add_argument("--gguf", default=None, help="GGUF model path")
    ap.add_argument("--dataset", default=None, help="HF dataset or JSONL path")
    ap.add_argument("--steps", type=int, default=500)
    ap.add_argument("--group-size", type=int, default=4)
    ap.add_argument("--lr", type=float, default=1e-5)
    ap.add_argument("--save-dir", default="./grpo_models")
    ap.add_argument("--device", default=None)
    args = ap.parse_args()

    metrics = train_with_grpo(
        role=args.role,
        base_model_id=args.base_model,
        gguf_path=args.gguf,
        prompts_dataset=args.dataset,
        steps=args.steps,
        group_size=args.group_size,
        lr=args.lr,
        save_dir=args.save_dir,
        device_type=args.device,
    )

    final = metrics[-1] if metrics else None
    if final:
        print(f"\n{'='*60}")
        print(f"GRPO Training Summary")
        print(f"  Final reward: {final.mean_reward:.3f}±{final.std_reward:.3f}")
        print(f"  Final KL div: {final.kl_divergence:.4f}")
        print(f"  Policy loss:  {final.policy_loss:.4f}")
        print(f"  Steps: {len(metrics)}")
        print(f"{'='*60}")
