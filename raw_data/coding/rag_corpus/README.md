# Gorgeous Websites RAG Corpus — README

This is a retrieval corpus for training/grounding a small (e.g. 3B) coding model to
generate beautiful, complete, single-file HTML websites — not a fine-tuning dataset.
It's built from your two reference styles (a Tailwind-CDN glassmorphic storefront and a
vanilla-CSS dealership site) plus 17 newly generated full examples spanning many
industries, so the model has broad style coverage instead of memorizing one look.

## What you got

Two equivalent forms of the same content:

1. **`gorgeous_websites_rag_corpus.md`** — one big file, all 30 documents concatenated,
   each preceded by a `## SOURCE: path` marker and a `---` divider. Simplest to ingest
   into a pipeline that does its own chunking (split on `---` to recover each original
   document, or just embed/chunk the whole file with a standard text splitter).

2. **`rag_corpus/` (zipped as `gorgeous_websites_rag_corpus.zip`)** — the same 30
   documents as separate files in their original folder structure, pre-split by type.
   Use this if your pipeline indexes files individually or you want per-category
   retrieval (e.g. "always retrieve from 02_patterns/ before 03_examples/").

## Folder / section structure

- `00_principles/` (3 docs) — design philosophy, anti-template guidance, motion/timing
  rules. Retrieve when deciding *what* to build before writing code.
- `01_architectures/` (2 docs) — the two reference CSS/JS architectures (Tailwind-CDN
  utility classes vs. vanilla CSS custom properties) with full boilerplate.
- `02_patterns/` (8 docs) — copy-adaptable components: navigation, hero, card grids,
  modals/drawers, cart state management, filters/search, forms/validation,
  footer/carousel.
- `03_examples/` (17 docs) — complete, working single-file HTML sites across 17
  different industries (coffee roaster, law firm, climbing gym, ceramics studio,
  fintech app, plant shop, MMA gym, bookstore, private aviation, kids' STEM camp,
  cocktail bar, architecture studio, pet grooming, vinyl shop, yoga studio, knife
  maker, e-bike startup), alternating between both architectures and between dark and
  light themes, each with its own distinct palette and one signature interactive
  element (none reuse the same gimmick twice).

## Notes on quality

- All 17 example files were checked for balanced braces/parens (a strong signal of
  JS syntax correctness) and valid `<!DOCTYPE>`/`<html>`/`<head>`/`<body>` structure.
  None should fail to render, but none have been executed in a real browser, so a
  spot-check after ingestion is still wise.
- Every example deliberately varies palette, type pairing, layout rhythm, and
  signature element so the model sees *patterns* (sticky header, reveal-on-scroll,
  cart state shape, validation flow) repeated across very different surface looks —
  this is what should generalize, rather than any single color scheme.
- Per your request, none of the 17 new examples reuse your uploaded files' exact
  colors; each picks its own palette while following the same structural and
  motion-quality bar.

## Suggested retrieval strategy at generation time

1. Retrieve from `00_principles/` to settle palette/type/motion decisions first.
2. Retrieve the matching architecture doc from `01_architectures/`.
3. Retrieve 2-4 relevant docs from `02_patterns/` for the specific sections requested.
4. Retrieve the 1-2 closest-niche examples from `03_examples/` as structural grounding
   (not copy source — model should still write its own palette/copy per the brief).
