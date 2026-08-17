import re
from enum import Enum

class RewardDomain(str, Enum):
    CODE = "code"
    MATH = "math"
    REASONING = "reasoning"
    GENERAL = "general"
    MIXED = "mixed"

class RewardScorer:
    def __init__(self, domain: RewardDomain = RewardDomain.MIXED):
        self.domain = domain
        self.weights = {
            "correctness": 0.40,
            "format": 0.15,
            "coherence": 0.15,
            "completeness": 0.10,
            "safety": 0.10,
            "reasoning": 0.10,
        }

    def score(self, prompt: str, response: str) -> float:
        scores = {}
        domain = self._detect_domain(prompt)

        scores["format"] = self._score_format(response)
        scores["coherence"] = self._score_coherence(response)
        scores["completeness"] = self._score_completeness(response)
        scores["safety"] = self._score_safety(response)

        if domain == "code":
            scores["correctness"] = self._score_code_correctness(prompt, response)
            scores["reasoning"] = self._score_code_reasoning(response)
        elif domain == "math":
            scores["correctness"] = self._score_math_correctness(prompt, response)
            scores["reasoning"] = self._score_math_reasoning(response)
        elif domain == "reasoning":
            scores["correctness"] = self._score_reasoning_correctness(prompt, response)
            scores["reasoning"] = self._score_reasoning_depth(response)
            self.weights = {**self.weights, "reasoning": 0.25, "correctness": 0.30}
        else:
            scores["correctness"] = self._score_general_quality(prompt, response)
            scores["reasoning"] = self._score_reasoning_depth(response)

        total = sum(scores[k] * self.weights.get(k, 0.1) for k in scores)
        return min(1.0, max(0.0, total))

    def _detect_domain(self, prompt: str) -> str:
        p = prompt.lower()
        code_keywords = (
            "code",
            "function",
            "class ",
            "def ",
            "import ",
            "api",
            "endpoint",
            "bug",
            "error ",
            "python",
            "javascript",
            "html",
            "css",
        )
        math_keywords = (
            "solve",
            "equation",
            "integral",
            "derivative",
            "theorem",
            "proof",
            "calculate",
            "probability",
            "sum",
        )
        code_score = sum(1 for kw in code_keywords if kw in p)
        math_score = sum(1 for kw in math_keywords if kw in p)
        if code_score > max(math_score, 2):
            return "code"
        if math_score > max(code_score, 2):
            return "math"
        return "reasoning"

    def _score_format(self, response: str) -> float:
        score = 0.5
        if re.search(r"```", response):
            score += 0.15
        if re.search(r"^\s*[#*]+\s", response, re.MULTILINE):
            score += 0.1
        sentences = [s for s in re.split(r"[.!?]+", response) if len(s.strip()) > 10]
        if len(sentences) >= 3:
            score += 0.1
        word_ratio = len(re.findall(r"\b[a-z]{2,}\b", response.lower())) / max(
            len(response.split()), 1
        )
        if word_ratio > 0.6:
            score += 0.15
        return min(1.0, score)

    def _score_coherence(self, response: str) -> float:
        score = 0.4
        words = response.split()
        if len(words) < 20:
            return 0.2
        transitions = {
            "therefore",
            "because",
            "however",
            "thus",
            "first",
            "second",
            "finally",
            "consequently",
            "additionally",
            "moreover",
        }
        count = sum(1 for t in transitions if t in response.lower())
        score += min(0.3, count * 0.1)
        unique_ratio = len(set(words[:100])) / max(len(words[:100]), 1)
        if unique_ratio > 0.5:
            score += 0.2
        if not re.search(r"(\b\w+\b)(\s+\1){3,}", response):
            score += 0.1
        return min(1.0, score)

    def _score_completeness(self, response: str) -> float:
        score = 0.5
        r = response.strip()
        if not re.search(r"[a-zA-Z]$", r) or r.endswith((".", "!", "?", "```", ")")):
            score += 0.2
        if not re.search(
            r"\.\.\.$|truncated|rest of the code|remaining code", r.lower()
        ):
            score += 0.2
        if len(r) > 50:
            score += 0.1
        return min(1.0, score)

    def _score_safety(self, response: str) -> float:
        score = 1.0
        dangerous = [
            "rm -rf /",
            "DROP TABLE",
            "eval(base64",
            "import os; os.system",
            "__import__('os').system",
            "subprocess.call(['rm'",
        ]
        for d in dangerous:
            if d.lower() in response.lower():
                score -= 0.3
        return max(0.0, score)

    def _score_code_correctness(self, prompt: str, response: str) -> float:
        score = 0.3
        code_blocks = re.findall(r"```(?:\w+)?\n([\s\S]*?)```", response)
        if not code_blocks:
            if any(kw in response for kw in ("def ", "class ", "import ", "from ")):
                code_blocks = [response]
            else:
                return 0.2
        for code in code_blocks:
            try:
                compile(code.strip(), "<reward_check>", "exec")
                score += 0.35
            except SyntaxError:
                pass
            if "import" in prompt.lower() and "import " in code:
                score += 0.1
            if "if __name__" in code:
                score += 0.1
            if len(code.strip()) > 100:
                score += 0.1
            if '"""' in code or "'''" in code or "# " in code:
                score += 0.05
        return min(1.0, score)

    def _score_code_reasoning(self, response: str) -> float:
        score = 0.3
        parts = re.split(r"```", response)
        text_parts = [p for i, p in enumerate(parts) if i % 2 == 0]
        total_text = " ".join(text_parts)
        if len(total_text.split()) > 30:
            score += 0.4
        if re.search(
            r"edge\s*case|corner\s*case|error\s*handling|exception", response.lower()
        ):
            score += 0.2
        if re.search(r"O\(|complexity|performance|optimize", response.lower()):
            score += 0.1
        return min(1.0, score)

    def _score_math_correctness(self, prompt: str, response: str) -> float:
        score = 0.3
        answer_match = re.search(
            r"(?:answer|final|result|therefore|\\boxed\{)\s*(?:is|:|=)?\s*([^\n.]+)",
            response,
            re.IGNORECASE,
        )
        if answer_match:
            score += 0.3
        if re.search(r"\d+\.?\d*", response):
            score += 0.15
        steps = re.findall(r"(?:step|stage)\s*\d+", response.lower())
        if len(steps) >= 2:
            score += 0.15
        if re.search(r"\$.*\$|\\\(.*\\\)|\\begin\{equation\}", response):
            score += 0.1
        return min(1.0, score)

    def _score_math_reasoning(self, response: str) -> float:
        score = 0.3
        if len(response.split()) > 50:
            score += 0.2
        if re.search(
            r"(?:first|next|then|finally|therefore|thus|hence)", response.lower()
        ):
            score += 0.2
        if re.search(r"\$.*\$", response):
            score += 0.2
        if re.search(r"(?:check|verify|confirm)", response.lower()):
            score += 0.1
        return min(1.0, score)

    def _score_reasoning_correctness(self, prompt: str, response: str) -> float:
        score = 0.3
        prompt_words = set(re.findall(r"\b\w{4,}\b", prompt.lower()))
        response_words = set(re.findall(r"\b\w{4,}\b", response.lower()))
        overlap = prompt_words & response_words
        if prompt_words:
            score += 0.3 * min(1.0, len(overlap) / len(prompt_words) * 2)
        if re.search(
            r"(?:conclusion|therefore|in summary|overall|thus)", response.lower()
        ):
            score += 0.2
        if not re.search(
            r"(?:I cannot|I do not|unable to|not able to)", response.lower()
        ):
            score += 0.2
        return min(1.0, score)

    def _score_reasoning_depth(self, response: str) -> float:
        score = 0.3
        words = len(response.split())
        if words > 100:
            score += 0.3
        elif words > 50:
            score += 0.15
        perspectives = re.findall(
            r"(?:alternatively|on the other hand|another (?:way|approach|perspective|angle)|"
            r"consider|from the standpoint)",
            response.lower(),
        )
        score += min(0.25, len(perspectives) * 0.08)
        if re.search(
            r"(?:however|but|although|while|whereas|conversely)", response.lower()
        ):
            score += 0.1
        if re.search(
            r"(?:for example|for instance|such as|e\.g\.|i\.e\.)", response.lower()
        ):
            score += 0.05
        return min(1.0, score)

    def _score_general_quality(self, prompt: str, response: str) -> float:
        score = 0.3
        prompt_words = set(re.findall(r"\b\w{4,}\b", prompt.lower()))
        response_words = set(re.findall(r"\b\w{4,}\b", response.lower()))
        overlap = prompt_words & response_words
        if prompt_words:
            score += 0.3 * min(1.0, len(overlap) / max(len(prompt_words), 1))
        if len(response.split()) > 30:
            score += 0.2
        if response.strip().endswith((".", "!", "?")):
            score += 0.2
        return min(1.0, score)
