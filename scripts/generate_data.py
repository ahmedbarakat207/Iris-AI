import os
import random
from datasets import load_dataset

def format_dolly_to_markdown(num_samples=500, output_file="training/generated_dolly.md"):
    if os.path.exists(output_file):
        print(f"[#] {output_file} already exists. Skipping.")
        return
    print(f"[*] Downloading Databricks Dolly dataset...")
    try:
        dataset = load_dataset("databricks/databricks-dolly-15k", split="train", trust_remote_code=True)
    except Exception as e:
        print(f"[!] Error loading dataset: {e}")
        return

    samples = list(dataset)
    random.shuffle(samples)
    selected = samples[:num_samples]

    print(f"[*] Formatting {num_samples} samples into Iris Markdown style...")
    
    os.makedirs("training", exist_ok=True)
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# Generated Training Data - Databricks Dolly\n\n")
        
        for i, row in enumerate(selected):
            instruction = row['instruction']
            context = row['context']
            response = row['response']
            category = row['category']

            if context:
                user_text = f"Context: {context}\n\nTask: {instruction}"
            else:
                user_text = instruction

            f.write(f"USER: {user_text}\n")
            f.write(f"BOT: {response}\n\n")
            
            if (i + 1) % 100 == 0:
                print(f"    - Processed {i+1}/{num_samples} items")

    print(f"[+] Success! Data saved to {output_file}")

def generate_synthetic_math(num_samples=100, output_file="training/generated_math.md"):
    if os.path.exists(output_file):
        print(f"[#] {output_file} already exists. Skipping.")
        return
    print(f"[*] Generating {num_samples} synthetic math problems...")
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# Generated Synthetic Math - Chain of Thought\n\n")
        
        for _ in range(num_samples):
            a = random.randint(2, 10)
            x = random.randint(1, 20)
            b = random.randint(1, 50)
            c = a * x + b
            
            user_text = f"Solve for x: {a}x + {b} = {c}"
            bot_text = (
                f"Let's solve this step-by-step:\n"
                f"1. Subtract {b} from both sides: {a}x = {c} - {b} => {a}x = {c-b}.\n"
                f"2. Divide by {a} to isolate x: x = {c-b} / {a}.\n"
                f"3. x = {x}.\n"
                f"The final answer is x = {x}."
            )
            
            f.write(f"USER: {user_text}\n")
            f.write(f"BOT: {bot_text}\n\n")

    print(f"[+] Success! Math data saved to {output_file}")

def format_code_alpaca(num_samples=500, output_file="training/generated_code.md"):
    if os.path.exists(output_file):
        print(f"[#] {output_file} already exists. Skipping.")
        return
    print(f"[*] Downloading CodeAlpaca dataset...")
    try:
        dataset = load_dataset("sahil2801/CodeAlpaca-20k", split="train")
    except Exception as e:
        print(f"[!] Error loading code dataset: {e}")
        return

    samples = list(dataset)
    random.shuffle(samples)
    selected = samples[:num_samples]
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# Generated Coding Data - CodeAlpaca\n\n")
        for row in selected:
            instr = row['instruction']
            inp = row.get('input', '')
            out = row['output']
            
            user_text = f"{instr}\n{inp}".strip()
            f.write(f"USER: {user_text}\n")
            f.write(f"BOT: {out}\n\n")
    print(f"[+] Success! Code data saved to {output_file}")

def generate_logic_puzzles(num_samples=100, output_file="training/generated_logic.md"):
    if os.path.exists(output_file):
        print(f"[#] {output_file} already exists. Skipping.")
        return
    print(f"[*] Generating {num_samples} logic puzzles...")
    puzzles = [
        ("If all bloops are razzies, and all razzies are snazzies, are all bloops snazzies?", "Yes. This is a syllogism: if A=B and B=C, then A=C."),
        ("A father and son are in a car crash. The father dies, the son is rushed to surgery. The surgeon says 'I can't operate, this is my son!' Who is the surgeon?", "The surgeon is the boy's mother."),
        ("What has keys but can't open locks?", "A piano."),
    ]
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# Generated Logic Puzzles\n\n")
        for _ in range(num_samples):
            q, a = random.choice(puzzles)
            f.write(f"USER: {q}\n")
            f.write(f"BOT: {a}\n\n")
    print(f"[+] Success! Logic data saved to {output_file}")

def format_egyptian_arabic(num_samples=500, output_file="training/generated_arabic.md"):
    if os.path.exists(output_file):
        print(f"[#] {output_file} already exists. Skipping.")
        return
    print(f"[*] Downloading Egyptian Arabic dataset...")
    try:
        dataset = load_dataset("MBZUAI-Paris/Egyptian-SFT-Mixture", split="train")
    except Exception as e:
        print(f"[!] Error loading Arabic dataset: {e}")
        return

    samples = list(dataset)
    random.shuffle(samples)
    selected = samples[:num_samples]
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# Generated Egyptian Arabic Data\n\n")
        for row in selected:
            prompt = row.get('prompt', row.get('instruction', ''))
            completion = row.get('completion', row.get('output', ''))
            
            if prompt and completion:
                f.write(f"USER: {prompt}\n")
                f.write(f"BOT: {completion}\n\n")
    print(f"[+] Success! Arabic data saved to {output_file}")

def format_summarization(num_samples=300, output_file="training/generated_summaries.md"):
    if os.path.exists(output_file):
        print(f"[#] {output_file} already exists. Skipping.")
        return
    print(f"[*] Downloading Summarization dataset...")
    try:
        dataset = load_dataset("cnn_dailymail", "3.0.0", split="train")
    except Exception as e:
        print(f"[!] Error loading summary dataset: {e}")
        return

    samples = list(dataset)
    random.shuffle(samples)
    selected = samples[:num_samples]
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# Generated Summarization Data\n\n")
        for row in selected:
            article = row['article']
            highlights = row['highlights']
            
            user_text = f"Please summarize the following article:\n\n{article}"
            f.write(f"USER: {user_text}\n")
            f.write(f"BOT: {highlights}\n\n")
    print(f"[+] Success! Summarization data saved to {output_file}")

def format_orca_reasoning(num_samples=500, output_file="training/generated_orca.md"):
    if os.path.exists(output_file):
        print(f"[#] {output_file} already exists. Skipping.")
        return
    print(f"[*] Downloading Open-Orca reasoning dataset...")
    try:
        dataset = load_dataset("Open-Orca/SlimOrca", split="train")
    except Exception as e:
        print(f"[!] Error loading Orca dataset: {e}")
        return

    samples = list(dataset)
    random.shuffle(samples)
    selected = samples[:num_samples]
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# Generated Deep Reasoning Data - Orca Style\n\n")
        for row in selected:
            convs = row.get('conversations', [])
            if len(convs) >= 2:
                user_msg = convs[0]['value']
                bot_msg = convs[1]['value']
                f.write(f"USER: {user_msg}\n")
                f.write(f"BOT: {bot_msg}\n\n")
    print(f"[+] Success! Orca reasoning data saved to {output_file}")

def format_science_sciq(num_samples=400, output_file="training/generated_science.md"):
    if os.path.exists(output_file):
        print(f"[#] {output_file} already exists. Skipping.")
        return
    print(f"[*] Downloading SciQ science dataset...")
    try:
        dataset = load_dataset("sciq", split="train")
    except Exception as e:
        print(f"[!] Error loading SciQ dataset: {e}")
        return

    samples = list(dataset)
    random.shuffle(samples)
    selected = samples[:num_samples]
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# Generated Scientific Reasoning Data - SciQ\n\n")
        for row in selected:
            q = row['question']
            ans = row['correct_answer']
            support = row.get('support', '')
            
            user_text = f"Scientific Question: {q}"
            bot_text = f"The answer is: {ans}\n\nExplanation: {support}" if support else ans
            
            f.write(f"USER: {user_text}\n")
            f.write(f"BOT: {bot_text}\n\n")
    print(f"[+] Success! Science data saved to {output_file}")

def generate_web_design_data(num_samples=200, output_file="training/generated_web_design.md"):
    if os.path.exists(output_file):
        print(f"[#] {output_file} already exists. Skipping.")
        return
    print(f"[*] Generating {num_samples} web design & development lessons...")
    
    design_tasks = [
        ("Create a modern CSS button with a gradient and hover effect.", 
         "```html\n<button class='btn'>Click Me</button>\n```\n```css\n.btn {\n  padding: 12px 24px;\n  background: linear-gradient(135deg, #6e8efb, #a777e3);\n  color: white;\n  border: none;\n  border-radius: 8px;\n  cursor: pointer;\n  transition: transform 0.2s;\n}\n.btn:hover {\n  transform: translateY(-2px);\n  box-shadow: 0 4px 15px rgba(0,0,0,0.2);\n}\n```"),
        ("What is 'Glassmorphism' in web design and how do I implement it?", 
         "Glassmorphism is a design trend characterized by semi-transparent backgrounds, background-blur, and subtle borders. It gives a 'frosted glass' look.\n\nExample:\n```css\n.card {\n  background: rgba(255, 255, 255, 0.1);\n  backdrop-filter: blur(10px);\n  border: 1px solid rgba(255, 255, 255, 0.2);\n  border-radius: 16px;\n}```"),
        ("How do I make a website responsive for mobile devices?", 
         "1. Use the viewport meta tag: `<meta name='viewport' content='width=device-width, initial-scale=1'>`.\n2. Use CSS Flexbox and Grid for layouts.\n3. Use Media Queries: `@media (max-width: 768px) { ... }`.\n4. Use relative units like `rem`, `%`, or `vw` instead of fixed `px`.")
    ]
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# Generated Web Design & Development Data\n\n")
        for _ in range(num_samples):
            q, a = random.choice(design_tasks)
            f.write(f"USER: {q}\n")
            f.write(f"BOT: {a}\n\n")

    print(f"[+] Success! Web design data saved to {output_file}")

if __name__ == "__main__":
    format_dolly_to_markdown(num_samples=1000)
    
    generate_synthetic_math(num_samples=200)

    format_code_alpaca(num_samples=500)

    generate_logic_puzzles(num_samples=100)

    format_egyptian_arabic(num_samples=500)



    format_science_sciq(num_samples=400)

    generate_web_design_data(num_samples=200)
