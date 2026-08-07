import torch

class GGUFPolicyBridge:
    def __init__(
        self,
        gguf_path: str,
        base_model_name: str,
        device: torch.device = None,
        use_4bit: bool = True,
    ):
        self.gguf_path = gguf_path
        self.base_model_name = base_model_name
        self.device = device or torch.device(
            "cuda"
            if torch.cuda.is_available()
            else "mps" if torch.backends.mps.is_available() else "cpu"
        )
        self.use_4bit = use_4bit
        self.gguf_llm = None
        self.policy_model = None
        self.tokenizer = None

    def setup(self):
        from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
        from llama_cpp import Llama

        self.gguf_llm = Llama(
            model_path=self.gguf_path,
            n_ctx=4096,
            n_gpu_layers=-1,
            verbose=False,
        )

        self.tokenizer = AutoTokenizer.from_pretrained(
            self.base_model_name, trust_remote_code=True
        )

        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        if self.use_4bit:
            quant_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_use_double_quant=True,
            )
            self.policy_model = AutoModelForCausalLM.from_pretrained(
                self.base_model_name,
                quantization_config=quant_config,
                device_map="auto",
                trust_remote_code=True,
            )
        else:
            self.policy_model = AutoModelForCausalLM.from_pretrained(
                self.base_model_name,
                torch_dtype=torch.float16,
                device_map="auto",
                trust_remote_code=True,
            )

    def generate(self, prompt: str, seed: int = 0, **kwargs) -> str:
        if self.gguf_llm is None:
            self.setup()

        response = self.gguf_llm.create_chat_completion(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=kwargs.get("max_new_tokens", 512),
            temperature=kwargs.get("temperature", 0.8),
            top_p=kwargs.get("top_p", 0.95),
            seed=seed,
        )
        return response["choices"][0]["message"]["content"]

    def get_trainable_model(self):
        if self.policy_model is None:
            self.setup()
        return self.policy_model

    def get_tokenizer(self):
        if self.tokenizer is None:
            self.setup()
        return self.tokenizer
