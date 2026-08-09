from src.iris import load_model, ModelRole
import time

def test():
    print("Loading reasoning model...")
    llm = load_model(ModelRole.REASONING)
    
    print("\n--- Starting Generation ---")
    start = time.time()
    
    res = llm.create_chat_completion(
        messages=[{"role": "user", "content": "Write a highly detailed explanation of how a jet engine works, step by step."}],
        max_tokens=200,
        stream=True
    )
    
    tokens = 0
    for chunk in res:
        token = chunk["choices"][0].get("delta", {}).get("content", "")
        if token:
            print(token, end="", flush=True)
            tokens += 1
            
    elapsed = time.time() - start
    print(f"\n\n--- Performance ---")
    print(f"Total Tokens: {tokens}")
    print(f"Total Time: {elapsed:.2f} seconds")
    print(f"TPS: {tokens/elapsed:.2f} tokens/sec")

test()
