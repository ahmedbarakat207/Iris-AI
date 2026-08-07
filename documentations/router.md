# Iris AI — Router & Triage System

## Overview

The triage model is the **gateway** for every query. It's the first model loaded, and it decides:

1. **Answer directly** — for greetings, simple facts, basic questions
2. **Route to specialist** — for complex queries needing domain expertise

## Classification Logic

```python
def classify_task(user_query, history):
    # Step 1: Fast keyword-based fallback classification
    result = _fallback_classify(user_query)
    if result: return result, None

    # Step 2: Load triage model, build prompt with history
    triage_messages = [
        {"role": "system", "content": TRIAGE_SYSTEM_PROMPT},
        *minimized_history,
        {"role": "user", "content": user_query}
    ]

    # Step 3: Run triage model inference (low temp = 0.2)
    llm = load_model(ModelRole.TRIAGE)
    answer = llm.create_chat_completion(messages, max_tokens=512, temperature=0.2)

    # Step 4: Parse routing tag
    for tag, ttype in TAG_MAP.items():
        if re.search(r'\[ROUTE:\s*{tag}\s*\]', answer, re.IGNORECASE):
            return ttype, None

    # Step 5: No routing tag → triage answered directly
    return None, answer
```

## Routing Tags

| Tag | Routes To | Example Queries |
|-----|-----------|-----------------|
| `[ROUTE: GENERAL]` | General model | "Explain quantum computing", "React vs Vue", "History of Rome" |
| `[ROUTE: REASONING]` | Reasoning model | "Design a scalable notification system", "Should I use microservices?", "Debug this production issue" |
| `[ROUTE: MATH]` | Math model | "Solve this integral", "Prove the Pythagorean theorem", "Calculate eigenvalues" |
| `[ROUTE: CODE_SIMPLE]` | Code model | "Write a function to sort an array", "Fix this regex", "Center a div in CSS" |
| `[ROUTE: CODE_COMPLEX]` | Code model | "Build a complete e-commerce site", "Create an OS kernel", "Write a chess engine" |
| *(no tag)* | Direct answer | "Hi", "What is 15% of 340?", "Thanks!" |

## Keyword Fallback Classifier

Before loading the triage model, a fast regex-based classifier runs:

```python
ROUTER_KEYWORDS = {
    "medical": ["symptom", "diagnosis", "treatment", "medicine", "doctor", ...],
    "coding": ["python", "javascript", "function", "code", "debug", "error", ...],
    "finance": ["tax", "budget", "investment", "stock", "money", ...],
}
```

This provides a zero-cost first pass — no model loaded. If a strong signal is found, the query is routed immediately. Otherwise, the triage model is loaded for deeper analysis.

## Web Search Integration

The triage system also triggers live web searches:

```python
def should_web_search(text):
    if len(text.split()) < 5: return False
    if SKIP_PATTERN.search(text): return False  # "open", "launch", "play", etc.
    return TRIGGER_PATTERN.search(text)  # "what", "who", "latest", "news", etc.
```

Web results are injected into the system prompt as context before the specialist model generates.

## Triage Model Characteristics

- **Temperature: 0.2** — Low temperature for consistent, deterministic routing
- **Max tokens: 512** — Only needs to output a short tag or direct answer
- **Context: 2048** — Minimal history needed for routing decisions
- **Speed: < 1 second** — Fast enough to be invisible to the user

## Training the Triage Model

The triage model is trained on `training/triage/` with the `triage_dataset.md` dataset, and on `training/shared/` with the `triage_prompt_engineer.md` dataset:

```bash
python train.py --train-role triage --iters 2000
```

Training data teaches the triage:
- When to answer directly vs route
- Edge case handling (ambiguous queries, follow-ups)
- Category boundaries (code vs reasoning, simple vs complex)
- Quality standards (never leak routing tags to users)

## Edge Cases Handled

| Scenario | Behavior |
|----------|----------|
| "help" with no context | Answers directly: "I'm here! What do you need help with?" |
| "do the thing" | Asks for clarification |
| "fix this error" (no code) | Asks for the error message and code |
| Query spans multiple categories | Routes to the dominant action |
| User says "urgent" / "deadline" | Routes immediately, no extra questions |
| Follow-up to previous specialist | Preserves context, routes to same specialist |
| Just "?" | Answers directly asking for clarification |

## Meta: How the Triage Thinks

The triage model's internal reasoning (trained via `triage_prompt_engineer.md`):

1. Read the query deeply — what does the user actually want?
2. Classify complexity — is this a knowledge question, a design problem, or a code task?
3. Check for completeness — can this be routed meaningfully?
4. Select the best specialist — not the one that's "good enough", the optimal one
5. Output the tag or direct answer — never both

## Router Model (Separate from Triage)

The **Router** role is distinct from triage. It handles JSON action generation for the PC controller:

```
User: "send email to mom about dinner saying I'll be late"
Router → {"action": "send_email", "to": "mom", "subject": "dinner", "body": "I'll be late"}
```

2.  **`src.iris.load_model(ModelRole.ROUTER)`**
    This is a specialized function-calling model (Iris AI Router) trained to output structured JSON actions.
