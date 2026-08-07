import os
import sys
import random
import time
from urllib.request import urlretrieve
from datasets import load_dataset
from llama_cpp import Llama
from test_gpqa import _format_gpqa_question, _extract_letter
from compare import fix_common_format_issues
from utils import append_to_csv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

MODELS = {
    "Llama-3.1-8B-Instruct": "https://huggingface.co/bartowski/Meta-Llama-3.1-8B-Instruct-GGUF/resolve/main/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf",
    "Gemma-4-E2B-it": "https://huggingface.co/unsloth/gemma-4-E2B-it-GGUF/resolve/main/gemma-4-e2b-it-q4_k_m.gguf",
    "Phi-4-mini-reasoning": "https://huggingface.co/lmstudio-community/Phi-4-mini-reasoning-GGUF/resolve/main/Phi-4-mini-reasoning-Q4_K_M.gguf",
    "Qwen3.5-4B": "https://huggingface.co/unsloth/Qwen3.5-4B-Instruct-GGUF/resolve/main/qwen3.5-4b-instruct-q4_k_m.gguf"
}

NUM_SAMPLES = 100
FIELDNAMES = ["Benchmark", "Role", "Prompt", "Expected", "Model_Answer", "Passed", "Time_Sec"]

def download_model(url, dest_path):
    if not os.path.exists(dest_path):
        print(f"Downloading {dest_path} from {url}...")
        urlretrieve(url, dest_path)
    return dest_path

def run_custom_benchmark():
    # Load GPQA
    dataset_options = [
        ("lighteval/GPQA", "gpqa_diamond", "train"),
        ("Idavidrein/gpqa", "gpqa_diamond", "train"),
    ]
    items = []
    for repo, config, split in dataset_options:
        try:
            ds = load_dataset(repo, config, split=split)
            items = list(ds)
            random.shuffle(items)
            items = items[:NUM_SAMPLES]
            print(f"[GPQA Diamond] Loaded {len(items)} questions from {repo}.")
            break
        except Exception as e:
            print(f"[GPQA Diamond] Could not load {repo}: {e}")

    if not items:
        print("[GPQA Diamond] Falling back to local built-in PhD-level science questions.")
        items = [
            {
                "Question": "Two quantum states with energies $E_1$ and $E_2$ have a lifetime of $10^{-9}$ sec and $10^{-8}$ sec, respectively. We want to clearly distinguish these two energy levels. Which one of the following options could be their energy difference so that they can be clearly resolved?",
                "Correct Answer": "10^{-4} eV",
                "Incorrect Answer 1": "10^{-11} eV",
                "Incorrect Answer 2": "10^{-8} eV",
                "Incorrect Answer 3": "10^{-9} eV"
            }
        ]
        
    models_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")
    os.makedirs(models_dir, exist_ok=True)
    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "outputs")
    os.makedirs(out_dir, exist_ok=True)
    csv_path = os.path.join(out_dir, "custom_benchmark.csv")
    
    for model_name, url in MODELS.items():
        print(f"\n{'='*50}\nEvaluating {model_name}\n{'='*50}")
        model_path = os.path.join(models_dir, os.path.basename(url))
        try:
            download_model(url, model_path)
        except Exception as e:
            print(f"Failed to download {model_name}: {e}")
            continue
            
        try:
            llm = Llama(model_path=model_path, n_ctx=4096, verbose=False, n_gpu_layers=-1)
        except Exception as e:
            print(f"Failed to load {model_name}: {e}")
            continue
            
        passed_count = 0
        for i, item in enumerate(items, 1):
            prompt, correct_letter = _format_gpqa_question(item)
            
            start_t = time.time()
            try:
                res = llm.create_chat_completion(
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=1024,
                    temperature=0.0
                )
                response = res['choices'][0]['message']['content']
            except Exception as e:
                print(f"Error during inference: {e}")
                response = ""
            t = round(time.time() - start_t, 2)
            
            model_letter = _extract_letter(response)
            if model_letter:
                model_letter = fix_common_format_issues(model_letter)
            passed = (model_letter == correct_letter)
            if passed: passed_count += 1
            
            short_q = item.get("Question", "")[:60]
            print(f"  [{i:02d}/{len(items)}] {short_q}... | Expected: {correct_letter} | Got: {model_letter} | {'✓' if passed else '✗'} ({t}s)")
            
            append_to_csv(csv_path, {
                "Benchmark": "GPQA-Diamond",
                "Role": model_name,
                "Prompt": item.get("Question", "")[:200],
                "Expected": correct_letter,
                "Model_Answer": model_letter,
                "Passed": passed,
                "Time_Sec": t,
            }, FIELDNAMES)
            
        pct = (passed_count / len(items)) * 100 if items else 0
        print(f"\n  [{model_name}] Score: {passed_count}/{len(items)} ({pct:.1f}%)\n")
        
        del llm

if __name__ == "__main__":
    run_custom_benchmark()
