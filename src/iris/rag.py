import os
import re
import hashlib
import logging
from typing import Dict, List, Optional
import glob
import pickle

logger = logging.getLogger("iris")

RAG_AVAILABLE = True
try:
    import torch
    from sentence_transformers import SentenceTransformer, util
except Exception as e:
    logger.warning(f"[RAG] Failed to import sentence-transformers: {e}")
    RAG_AVAILABLE = False


class BookRetriever:
    def __init__(self, raw_data_dir="raw_data"):
        self.raw_data_dir = raw_data_dir
        self.chunks: list = []
        self.embeddings = None
        self.embedder = None
        self._cat_index: Dict[str, list] = {}

    def _cache_key(self, file_entries: list) -> str:
        parts = sorted(
            f"{path}:{os.path.getmtime(path):.3f}" for path, _ in file_entries
        )
        return hashlib.md5("\n".join(parts).encode()).hexdigest()

    def _cache_path(self) -> str:
        return os.path.join(self.raw_data_dir, ".rag_index_cache.pkl")

    def load_and_index(self):
        if not RAG_AVAILABLE:
            logger.info("[RAG] sentence-transformers not installed. RAG disabled.")
            return

        if not os.path.exists(self.raw_data_dir):
            os.makedirs(self.raw_data_dir, exist_ok=True)
            logger.info(
                f"[RAG] Created {self.raw_data_dir}/. Drop markdown/txt files here."
            )
            return

        logger.info("[RAG] Loading embedding model (all-MiniLM-L6-v2)...")
        try:
            self.embedder = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")
        except Exception as e:
            logger.warning(
                f"[RAG] Online check failed ({e}). Attempting offline load from cache..."
            )
            os.environ["HF_HUB_OFFLINE"] = "1"
            self.embedder = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")

        file_entries: list = []
        abs_root = os.path.abspath(self.raw_data_dir)

        for ext in [
            "*.md",
            "*.txt",
            "*.pdf",
            "*.docx",
            "*.xlsx",
            "*.pptx",
            "*.csv",
            "*.html",
            "*.json",
            "*.xml",
        ]:
            for path in glob.glob(os.path.join(abs_root, ext)):
                file_entries.append((path, "general"))
            for path in glob.glob(os.path.join(abs_root, "**", ext), recursive=True):
                rel = os.path.relpath(path, abs_root)
                parts = rel.split(os.sep)
                category = parts[0] if len(parts) > 1 else "general"
                file_entries.append((path, category))

        seen: set = set()
        unique_entries = []
        for path, cat in file_entries:
            if path not in seen:
                seen.add(path)
                unique_entries.append((path, cat))
        file_entries = unique_entries

        if not file_entries:
            logger.info("[RAG] No text found in raw_data/. Skipping index creation.")
            return

        categories_found = sorted({c for _, c in file_entries})
        logger.info(
            f"[RAG] Found {len(file_entries)} files across categories: {categories_found}"
        )
        cache_key = self._cache_key(file_entries)
        cache_file = self._cache_path()
        if os.path.exists(cache_file):
            try:
                with open(cache_file, "rb") as f:
                    cached = pickle.load(f)
                if cached.get("key") == cache_key:
                    self.chunks = cached["chunks"]
                    self.embeddings = cached["embeddings"]
                    self._cat_index = cached["cat_index"]
                    logger.info(
                        f"[RAG] Loaded {len(self.chunks)} chunks from disk cache (skipped re-encode)."
                    )
                    return
                else:
                    logger.info(
                        "[RAG] Cache stale (files changed) \u2014 rebuilding index."
                    )
            except Exception as e:
                logger.info(f"[RAG] Cache load failed ({e}) \u2014 rebuilding index.")
        self.chunks = []
        self._cat_index = {}

        for path, category in file_entries:

            if "gorgeous_websites_rag_corpus.md" in path:
                has_subfolder_files = any("rag_corpus" in p for p, _ in file_entries)
                if has_subfolder_files:
                    logger.info(
                        f"[RAG] Skipping redundant merged file: {os.path.basename(path)}"
                    )
                    continue

            try:
                ext = os.path.splitext(path)[1].lower()
                if ext in [".md", ".txt", ".json", ".xml", ".csv"]:
                    with open(path, "r", encoding="utf-8") as f:
                        raw_text = f.read()
                else:
                    try:
                        from markitdown import MarkItDown

                        md = MarkItDown()
                        result = md.convert(path)
                        raw_text = result.text_content
                    except ImportError:
                        logger.warning(
                            f"[RAG] markitdown not installed. Cannot read {path}"
                        )
                        continue
            except Exception as e:
                logger.warning(f"[RAG] Could not read {path}: {e}")
                continue

            is_coding_kb = "coding" in path.lower() or category == "coding"

            if is_coding_kb:

                paragraphs = re.split(r"\n\s*\n", raw_text)
                current_chunk = ""
                for para in paragraphs:
                    para = para.strip()
                    if not para:
                        continue
                    if len(current_chunk) + len(para) > 12000 and current_chunk:
                        self._add_chunk(current_chunk.strip(), path, category)
                        current_chunk = para + "\n\n"
                    else:
                        current_chunk += para + "\n\n"
                if current_chunk.strip():
                    self._add_chunk(current_chunk.strip(), path, category)
            else:
                paragraphs = re.split(r"\n\s*\n", raw_text)
                current_chunk = ""
                for para in paragraphs:
                    para = para.strip()
                    if not para:
                        continue
                    if len(current_chunk) + len(para) > 1500 and current_chunk:
                        self._add_chunk(current_chunk.strip(), path, category)
                        current_chunk = para + "\n\n"
                    else:
                        current_chunk += para + "\n\n"
                if current_chunk.strip():
                    self._add_chunk(current_chunk.strip(), path, category)

        if not self.chunks:
            logger.info("[RAG] No chunks created. Check that files contain text.")
            return

        for idx, chunk in enumerate(self.chunks):
            cat = chunk["category"]
            self._cat_index.setdefault(cat, []).append(idx)

        cat_summary = {c: len(v) for c, v in self._cat_index.items()}
        logger.info(
            f"[RAG] {len(self.chunks)} chunks indexed. Distribution: {cat_summary}"
        )
        chunk_texts = [c["text"] for c in self.chunks]
        self.embeddings = self.embedder.encode(chunk_texts, convert_to_tensor=True)
        logger.info("[RAG] Indexing complete!")
        try:
            with open(cache_file, "wb") as f:
                pickle.dump(
                    {
                        "key": cache_key,
                        "chunks": self.chunks,
                        "embeddings": self.embeddings,
                        "cat_index": self._cat_index,
                    },
                    f,
                )
            logger.info(
                f"[RAG] Index cached to {cache_file} \u2014 future startups will be instant."
            )
        except Exception as e:
            logger.warning(
                f"[RAG] Could not save cache ({e}) \u2014 index will rebuild next time."
            )

    def _add_chunk(self, text: str, source_file: str, category: str) -> None:
        self.chunks.append(
            {"text": text, "source_file": source_file, "category": category}
        )

    def retrieve(
        self, query: str, top_k: int = 3, category: Optional[str] = None
    ) -> str:
        if self.embeddings is None or self.embedder is None or not self.chunks:
            return ""

        query_embedding = self.embedder.encode(query, convert_to_tensor=True)
        candidate_indices: Optional[list] = None

        if category is not None:
            pool = self._cat_index.get(category, [])
            if len(pool) < max(1, top_k):
                fallback = self._cat_index.get("general", [])
                pool = pool + [i for i in fallback if i not in set(pool)]
            if len(pool) < max(1, top_k):
                pool = list(range(len(self.chunks)))
                logger.info(f"[RAG] Category '{category}' sparse; using full index.")
            candidate_indices = pool

        if candidate_indices is not None:
            subset_embeddings = self.embeddings[candidate_indices]
            hits_raw = util.semantic_search(
                query_embedding, subset_embeddings, top_k=top_k
            )[0]
            hits_global = [
                {"corpus_id": candidate_indices[h["corpus_id"]], "score": h["score"]}
                for h in hits_raw
                if h["score"] > 0.3
            ]
        else:
            hits_raw = util.semantic_search(
                query_embedding, self.embeddings, top_k=top_k
            )[0]
            hits_global = [
                {"corpus_id": h["corpus_id"], "score": h["score"]}
                for h in hits_raw
                if h["score"] > 0.3
            ]

        retrieved_texts = [self.chunks[h["corpus_id"]]["text"] for h in hits_global]
        return "\n\n---\n\n".join(retrieved_texts) if retrieved_texts else ""


from src.iris.datasets import *
