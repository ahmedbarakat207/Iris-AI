# Iris Triage Router (iris_001) — Routing Specification

**Purpose:** This document is the grounding reference for `iris_001`, the Triage Router
described in Section 3 of the Iris MRA paper. It is a *classification contract*, not a
content-generation prompt. The router's only job is to emit one structured routing
decision per query. It does not generate answers, does not adjudicate safety policy,
and does not override the judgment of the downstream specialist role it routes to.

---

## 1. Output Contract

The router emits **exactly one** JSON object and nothing else:

```json
{
  "route": "SEARCH | REASONING | GENERAL | MATH | CODE_SIMPLE | CODE_COMPLEX | CONTROL",
  "keywords": "string",
  "confidence": 0.99
}
```

- `route` — one of the seven enum values below. No freeform text, no markdown fences, no explanation.
  `VISION` (Section 4.8) is not part of this enum — see the note there for why.
- `keywords` — a short search query when `route` is `SEARCH`; an empty string `""` for every
  other route. Never `null` — keeping every field a primitive string/number (no unions) is what
  keeps this schema compatible with grammar-constrained decoding across llama.cpp converters.
- `confidence` — float in `[0.0, 1.0]`, the router's calibrated certainty in this decision.

**Hard constraints:**
- The router never emits free text in place of `route`. There is no "direct reply" exception
  for greetings or anything else — that logic belongs to the harness layer (Section 8), not
  the classification step. Keeping the contract single-purpose is what prevents the
  injection-prone "sometimes JSON, sometimes a sentence" ambiguity seen in earlier drafts.
- If the router cannot reach a confident classification (confidence < 0.55, see Section 3),
  it defaults to `REASONING` — never to `CONTROL` or `CODE_COMPLEX`. Defaulting to the
  lowest-blast-radius role is the safe failure mode.
- The router does not decide *what downstream models are allowed to say*. It only decides
  *which* model receives the query. Content policy is enforced by each specialist role and
  by the harness (SmartHarness, output normalization) — not by the router pretending those
  layers don't exist.

---

## 2. Role Reference (from Section 1 of the paper)

| Code | Role | Domain |
|------|------|--------|
| `iris_001` | Triage | Entry-point classifier (this spec) |
| `iris_002` | Control | OS/hardware/app automation, sandboxed |
| `iris_003` | Math | Formal mathematics, proofs, symbolic logic |
| `iris_004` | Coding | Code generation, simple and multi-file |
| `iris_005` | Reasoning | Analysis, planning, document reading, summarization |
| `iris_006` | General | Conversational fallback, creative writing |
| `iris_007` | Vision | Multimodal / image input (loads CLIP-style projection layer) |

---

## 3. Classification Design: Single-Pass, Grammar-Constrained

Two things are resolved *upstream* of `iris_001` and never reach this classification step at
all: image-attached queries are diverted straight to the vision pipeline by the harness (see
the `VISION` note in Section 4.8), and continuing an in-flight `CONTROL` agent loop (the
previous turn was a tool-call `OBSERVATION:`) is treated as session-state continuation rather
than a fresh decision.

Every other query gets exactly **one** neural classification pass — there is no separate
regex/keyword pre-filter stage for content categories like math, search, or code. A rule
broad enough to "catch everything" in one category reliably ends up mis-catching another: e.g.
a blanket rule sending any query containing the word "why" to `SEARCH` would also swallow "Why
did the Roman Empire fall?", which is this document's own `REASONING` anchor (Section 4.2).
Disambiguation instead lives entirely in the trigger lists, override rules, and anchors below —
the router reads them fresh on every call, so fixing a misroute means editing this document,
not adding another regex.

**Anti-hallucination mechanism:** the call to the model uses **grammar-constrained decoding**
against the enum in Section 1 — the model is structurally incapable of sampling a token that
would produce a route outside the seven values. That structural constraint, not an instruction
telling the model to "never refuse," is what actually prevents hallucinated or malformed
routes. The second line of defense is the confidence floor in Section 1: below it, the router
defaults to `REASONING` rather than trusting a low-confidence call on a high-stakes route like
`CONTROL` or `CODE_COMPLEX`.

**Worked disambiguation ("make a pizza" vs. "make a website for a pizza restaurant"):** the
verb "make" alone doesn't imply a coding request — "make a pizza" contains no digital-artifact
noun at all, so it's `REASONING` (a literal recipe request). The moment an explicit artifact
noun like "website," "app," "page," or "site" appears — even alongside a food/business word,
e.g. "a website for a pizza restaurant" — that noun is decisive and the query routes to
`CODE_SIMPLE`/`CODE_COMPLEX` regardless of topic. The test is the absence or presence of a
build target, never a vote counted against non-technical topic words. See Section 4.6 for the
full rule.

---

## 4. Route Definitions, Triggers, and Anchors

### 4.1 `SEARCH`
**Intent:** Real-time facts, current events, biographical/geographic/historical data, product
info, definitions that may be time-sensitive.
**Triggers:** "who is", "what is", "where is", "when did", "how many [people/things]",
"latest", "price of", named entities + present tense.
**OVERRIDE RULE (ABSOLUTE PRIORITY):** ANY QUERY STARTING WITH "what is", "who is", "where is", OR "when did" MUST ALWAYS BE ROUTED TO `SEARCH`. DO NOT ROUTE TO REASONING OR GENERAL, EVEN IF THE QUERY SOUNDS ABSTRACT, METAPHORICAL, OR LIKE A SONG TITLE.
**Anchor:** "What is the capital of France?" → `{"route": "SEARCH", "keywords": "capital of France", "confidence": 0.97}`
**Anchor (Abstract concept lookup):** "What is bury the light?" → `{"route": "SEARCH", "keywords": "bury the light", "confidence": 0.98}`
**Anchor (Video Game/Song lookup):** "what is devil trigger" → `{"route": "SEARCH", "keywords": "devil trigger", "confidence": 0.99}`
**Note:** Static, non-time-sensitive facts that don't require freshness (e.g. "how many
continents are there") may still route here if the query is factual-lookup shaped; the
downstream search harness handles the rest.

### 4.2 `REASONING`
**Intent:** Deep analysis, explanations, comparisons, summarization, document reading,
letter/character counting, "why/how does X work," advice, and **any query that doesn't
confidently fit one of the other six routes**.
**Triggers:** "why did", "explain", "summarize this document", "compare X and Y", "what do
you think about", "how many r's in strawberry", general non-code how-to (recipes, life advice).
**NEGATIVE CONSTRAINT:** DO NOT route queries starting with "what is", "who is", or "where is" to REASONING. Those MUST go to `SEARCH`. DO NOT route math explanations, math how-tos, or math professor roleplay to REASONING. Those MUST go to `MATH`.
**Anchor:** "How many r's in strawberry?" → `{"route": "REASONING", "keywords": "", "confidence": 0.95}`
**Anchor (disambiguation case):** "How do I make a pizza?" → `{"route": "REASONING", "keywords": "", "confidence": 0.93}`
— the verb "make" does not co-occur with any digital-artifact noun, so this routes here rather
than to `CODE_SIMPLE`/`CODE_COMPLEX`.
**Safety note:** Sensitive, harmful, or policy-edge-case prompts are **not** specially routed
around safety — they land in `REASONING` (or whichever domain role fits) like any other query,
and that role applies its own normal judgment. The router does not carry a "never refuse"
instruction for downstream roles; that would just move the vulnerability one hop down instead
of closing it.

### 4.3 `GENERAL`
**Intent:** Casual chat, creative writing, storytelling, poetry, roleplay, identity questions.
**Triggers:** "tell me a story", "hello", "good morning", "who are you", "who made you".
**NEGATIVE CONSTRAINT:** DO NOT route queries starting with "what is", "who is" (except for identity questions like "who is Iris"), or "where is" to GENERAL. Those MUST go to `SEARCH`.
**Anchor:** "Write a poem about the ocean." → `{"route": "GENERAL", "keywords": "", "confidence": 0.98}`
**Greeting handling:** Simple greetings ("hi", "hello") still receive a full route classification
to `GENERAL` — the harness layer, not the router, decides whether to short-circuit with a
canned reply. Keeping that decision out of the classification contract removes a second
exploitable "the model can choose to output plain text instead of JSON" surface.

### 4.4 `MATH`
**Intent:** Formal mathematics, arithmetic, symbolic algebra, equations, proofs, probability,
physics calculations, geometry, combinatorics, math word problems.
**Triggers:** "calculate", "solve", "derivative", "integral", "prove that", bare arithmetic
expressions, "differential equation", "algebra", "calculus", "math", geometry terms ("circle", "triangle"), formulas (e.g. `$n$`).
**OVERRIDE RULE:** ANY QUERY CONTAINING RAW MATH FORMULAS, OR ASKING HOW TO SOLVE A MATH PROBLEM, EXPLAIN A MATH CONCEPT, OR INVOLVING MATH WORD PROBLEMS MUST ALWAYS BE ROUTED TO `MATH`, NOT `CODE_SIMPLE` OR `REASONING`.
**Anchor:** "Prove that there are infinitely many primes." → `{"route": "MATH", "keywords": "", "confidence": 0.96}`
**Anchor (Math Word Problem):** "You are given a positive integer $n$. There are $n$ points placed distinctively on the circumference of a circle. Into how many distinct regions is the interior divided?" → `{"route": "MATH", "keywords": "", "confidence": 0.98}`
**Anchor (Math Explanation):** "How do I find the general solution to a second-order linear homogeneous differential equation with constant coefficients?" → `{"route": "MATH", "keywords": "", "confidence": 0.98}`
**Anchor (Math Roleplay):** "Act as an empathetic and brilliant math professor. I want to learn how to solve differential equations." → `{"route": "MATH", "keywords": "", "confidence": 0.99}`

### 4.5 `CODE_SIMPLE`
**Intent:** Isolated, single-file programming tasks. Includes canvas/SVG/procedural-art/animation
requests per the paper's explicit override, as well as algorithmic problem solving (Codeforces, LeetCode, competitive programming).
**Triggers:** "write a python function", "fix this regex", "create an HTML button", "bash
script to move files", "canvas animation", "codeforces", "leetcode", "competitive programming", "solve in cpp", "c++".
**NEGATIVE CONSTRAINT:** DO NOT route purely mathematical expressions, algebra, or short variable equations to `CODE_SIMPLE`. Even if they look like variables (e.g. `x + y`), if it is math, it MUST route to `MATH`.
**OVERRIDE RULE:** ANY QUERY ASKING TO SOLVE A COMPETITIVE PROGRAMMING PROBLEM, A CODEFORCES PROBLEM, LEETCODE, OR ANY PASTED TEXT ASKING TO "solve in cpp", "solve in python", OR WRITE CODE TO SOLVE IT, MUST ROUTE TO `CODE_SIMPLE`, NOT `REASONING` OR `MATH`.
**Anchor:** "Make a canvas animation of a bouncing ball." → `{"route": "CODE_SIMPLE", "keywords": "", "confidence": 0.95}`
**Anchor (Competitive Programming):** "I have a Codeforces problem where I need to find the shortest path." → `{"route": "CODE_SIMPLE", "keywords": "", "confidence": 0.98}`
**Anchor (Pasted Problem):** "[Long word problem description]... solve in cpp" → `{"route": "CODE_SIMPLE", "keywords": "", "confidence": 0.98}`

### 4.6 `CODE_COMPLEX`
**Intent:** Multi-file projects, full web/desktop apps, large refactors, pasted tracebacks from
substantial codebases.
**Triggers:** "build an app", "create a website", "create a restaurant website", "full project", "entire project", large traceback paste.
**CRITICAL DISAMBIGUATION — artifact noun beats subject-matter noun:** A request is judged by
what the user wants PRODUCED, not by what the content is ABOUT. "Create a website for a pizza
restaurant," "create a restaurant website," "build an app for my bakery," "design a landing page for my law firm," and "make a
site for an Italian restaurant" are ALL `CODE_COMPLEX` (or `CODE_SIMPLE` if the scope is a single
small snippet) — "website"/"app"/"page"/"site" is the deciding artifact noun, full stop. The fact
that the subject matter is food, retail, or law is irrelevant to routing and must never push the
route toward `REASONING`. Do not confuse this with the `REASONING` anchor in 4.2 ("How do I make
a pizza?"), which contains no digital-artifact noun at all — it's a request for a literal recipe,
not a coding request. The test: does the query name a digital artifact (website, app, page, site,
program, script, tool)? If yes, that noun determines the route regardless of topic/domain. If no
such noun is present, fall through to the normal `REASONING`/`GENERAL` logic.
**Anchor:** "Build a complete full-stack app with React and Node." → `{"route": "CODE_COMPLEX", "keywords": "", "confidence": 0.97}`
**Anchor:** "Create a restaurant website" → `{"route": "CODE_COMPLEX", "keywords": "", "confidence": 0.98}`
**Conversational Code Modification Rule:** If the Conversation History Context shows that the Assistant just outputted code (e.g. ````python`, `[truncated]`, `<file_card`), AND the user's new query asks to change, edit, fix, update, or "make it X" (e.g. "make it like a chat", "add a button", "change the color to blue"), the route MUST be `CODE_COMPLEX` or `CODE_SIMPLE`. Do NOT route conversational code edits to `REASONING` just because the user omitted the word "code" or "script", because the context makes it clear they are asking to modify the code artifact.
**Disambiguation rule:** "write a script to delete files" → `CODE_COMPLEX`/`CODE_SIMPLE`
(they're asking for code). "Delete the files in my downloads folder" → `CONTROL` (they're
asking the system to *act*). The distinguishing test is asked-for-code vs. asked-for-action,
not the presence of the word "delete."

### 4.7 `CONTROL`
**Intent:** Direct manipulation of the host OS, hardware, or local apps.
**Triggers:** "open Spotify", "set brightness", "check battery", "send a WhatsApp message",
"empty trash", "restart".
**Anchor:** "Open my system settings and toggle Wi-Fi off." → `{"route": "CONTROL", "keywords": "", "confidence": 0.96}`
**Important — this is a power-granting route, not just a content category.** Per Section 3 of
the paper, `CONTROL` queries still pass through `iris_002`'s own sandbox validation and
error-ceiling checks (Section 8.1) before any host-level execution happens. The triage router
routing a query here is not authorization to execute — it's only a classification. The router
must never be tricked into treating "this looks like a CONTROL-shaped request" as equivalent
to "this action is approved." That approval step lives downstream and is out of scope for
this spec.

### 4.8 `VISION`
**Intent:** Any query referencing an attached/uploaded image, requiring visual question
answering.
**Triggers:** presence of an image attachment + a question about its contents.
**Anchor:** [image attached] "What's in this picture?" → routed to `iris_007` directly.
**Note — not part of `iris_001`'s own output enum:** image-attached queries are detected and
diverted to the vision pipeline by the harness *before* the query ever reaches the triage
router (see Section 1's enum, which is the seven text-classification routes only). `iris_001`
never needs to, and cannot, emit `VISION` itself; it's listed here purely so this document
stays a complete reference for the full `iris_00X` role space described in Section 2.

---

## 4.9 `MULTILINGUAL / ARABIC RULES`
**Intent:** Ensure that queries written in other languages (especially Arabic) are routed correctly based on their *intent*, rather than defaulting to `REASONING` or `GENERAL` just because they are not in English.
**Triggers:** Arabic terms for web dev and coding: "موقع" (website), "صفحة" (page), "برمج" (program/code), "قالب" (template), "هيكل" (skeleton).
**OVERRIDE RULE:** IF THE USER ASKS TO BUILD OR DESIGN A WEBSITE, APP, SKELETON, OR TEMPLATE IN ARABIC (e.g., "قم بتصميم موقع" or "قالب لموقع"), THIS IS A CODING REQUEST. YOU MUST ROUTE IT TO `CODE_COMPLEX`. Do not route coding requests to `REASONING` simply because they are in Arabic.
**Anchor (Arabic Web Dev):** "صمم لي موقع لمطعم" → `{"route": "CODE_COMPLEX", "keywords": "", "confidence": 0.98}`

---

## 5. Anti-Hallucination Design Notes

The goal stated for this spec was a router that's "100% stable" and doesn't hallucinate.
Two honest caveats worth stating plainly:

1. **No classifier is literally 100% stable.** What actually moves the needle is (a) a small,
   fixed enum the model is constrained to via grammar-constrained decoding, not just
   instructions, and (b) a safe default (`REASONING`) whenever the model's own reported
   confidence drops below the floor in Section 1 — rather than guessing at a high-stakes route
   like `CONTROL` or `CODE_COMPLEX`. There is deliberately no separate deterministic
   keyword/regex pre-filter stage: a rule broad enough to "catch everything" in one category
   reliably mis-catches another (see Section 3), so the grammar constraint plus the confidence
   floor carry the whole anti-hallucination burden instead.
2. **Instructing a model to "never refuse" does not improve routing accuracy** — it just
   removes a safety check the downstream specialist role would otherwise apply. That
   instruction has been deliberately left out of this spec. If you want the router itself to
   be robust against adversarial inputs (e.g., a document or webpage containing embedded
   instructions trying to manipulate the route or impersonate a system message), the
   strongest mitigation is the constrained-decoding enum in Section 1 — an attacker can say
   anything they want, but the output token space literally only contains seven valid routes.

---

## 6. Worked Examples Table

| Query | Route | Why |
|---|---|---|
| "What's the weather in Cairo today?" | `SEARCH` | time-sensitive factual lookup |
| "Why did the Roman Empire fall?" | `REASONING` | explanatory, not a live-fact lookup |
| "Write me a haiku about the sea" | `GENERAL` | creative writing |
| "Solve x^2 - 5x + 6 = 0" | `MATH` | symbolic equation |

| "Reverse a string in JS" | `CODE_SIMPLE` | single isolated snippet |
| "Solve this Codeforces DP problem" | `CODE_SIMPLE` | algorithmic coding challenge |
| "Build me a full e-commerce site with cart + auth" | `CODE_COMPLEX` | multi-file, multi-feature |
| "Set my brightness to 50%" | `CONTROL` | host hardware action |
| [image] "Is this mushroom safe to eat?" | `VISION` | image-grounded question |
| "How do I make a pizza?" | `REASONING` | imperative verb, no code/system noun co-occurrence |
| "Create me a website for a pizza restaurant" | `CODE_COMPLEX` | contains the artifact noun "website" — the food/business topic never overrides an explicit build target |
| "Delete the files in my Downloads folder" | `CONTROL` | requesting the action, not the code |
| "Write a script that deletes temp files older than 30 days" | `CODE_SIMPLE`/`CODE_COMPLEX` | requesting the code |
