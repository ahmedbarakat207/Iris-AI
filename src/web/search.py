<<<<<<< HEAD
import os
import urllib.request
import re
import json
import time
import logging
import threading
import urllib.parse
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry

    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    from bs4 import BeautifulSoup

    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False

try:
    from ddgs import DDGS

    DDGS_AVAILABLE = True
except ImportError:
    DDGS_AVAILABLE = False

logger = logging.getLogger("iris.web_search")


@dataclass
class SearchResult:
    title: str = ""
    body: str = ""
    href: str = ""
    source: str = "web"

    def __post_init__(self):
        if self.body:
            patterns = [
                r"create a sex novel",
                r"cannot fulfill this request due to",
                r"unable to provide guidance on creating content",
                r"inappropriate answer, I will respond",
                r"sexual themes or activities",
            ]
            lines = self.body.splitlines()
            clean_lines = []
            for line in lines:
                if any(re.search(pat, line, re.IGNORECASE) for pat in patterns):
                    continue
                clean_lines.append(line)
            self.body = "\n".join(clean_lines)

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "body": self.body,
            "href": self.href,
            "source": self.source,
        }

    def to_context_str(self) -> str:
        parts = [f"**{self.title}**"]
        if self.body:
            parts.append(self.body[:600])
        if self.href:
            parts.append(f"[source]({self.href})")
        return "\n".join(parts)


class WebSearch:

    _singleton = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._singleton is None:
            with cls._lock:
                if cls._singleton is None:
                    cls._singleton = super().__new__(cls)
                    cls._singleton._initialized = False
        return cls._singleton

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._session = None
        self._ddg_available = DDGS_AVAILABLE
        self._ddg_rate_limited_until = 0.0
        if REQUESTS_AVAILABLE:
            self._session = requests.Session()
            retry = Retry(
                total=2, backoff_factor=0.5, status_forcelist=[429, 500, 502, 503, 504]
            )
            adapter = HTTPAdapter(max_retries=retry)
            self._session.mount("https://", adapter)
            self._session.mount("http://", adapter)
        self._user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

    def _search_ddg(
        self, query: str, max_results: int, timeout: float = 8.0
    ) -> List[SearchResult]:

        if not self._ddg_available:
            return []
        now = time.time()
        if now < self._ddg_rate_limited_until:
            logger.warning(
                "[WebSearch] DDG rate-limited until %.0f seconds from now",
                self._ddg_rate_limited_until - now,
            )
            return []
        results: List[SearchResult] = []
        try:
            with DDGS() as ddgs:
                for r in ddgs.text(query, max_results=max_results, backend="html"):
                    results.append(
                        SearchResult(
                            title=r.get("title", ""),
                            body=r.get("body", ""),
                            href=r.get("href", ""),
                            source="ddg_text",
                        )
                    )
                    if len(results) >= max_results:
                        break
        except Exception as e:
            err = str(e).lower()
            if "202" in err or "403" in err or "rate" in err or "limited" in err:
                self._ddg_rate_limited_until = time.time() + 30.0
                logger.warning("[WebSearch] DDG rate-limited, backoff 30s")
            else:
                logger.warning(f"[WebSearch] DDG text failed: {e}")

        if len(results) < max_results and time.time() >= self._ddg_rate_limited_until:
            try:
                with DDGS() as ddgs:
                    for r in ddgs.news(
                        query, max_results=max((max_results - len(results)), 1)
                    ):
                        results.append(
                            SearchResult(
                                title=r.get("title", ""),
                                body=r.get("body", ""),
                                href=r.get("url", r.get("href", "")),
                                source="ddg_news",
                            )
                        )
                        if len(results) >= max_results:
                            break
            except Exception as e:
                logger.debug(f"[WebSearch] DDG news failed: {e}")
        return results[:max_results]

    def _search_wikipedia(
        self, query: str, max_results: int, timeout: float = 6.0
    ) -> List[SearchResult]:

        if not REQUESTS_AVAILABLE:
            return []
        results: List[SearchResult] = []
        try:
            encoded = urllib.parse.quote(query)
            is_ar = bool(re.search(r"[\u0600-\u06FF]", query))
            wiki_domain = "ar.wikipedia.org" if is_ar else "en.wikipedia.org"
            url = (
                f"https://{wiki_domain}/w/api.php?action=query&generator=search"
                f"&gsrsearch={encoded}&gsrlimit={max(3, max_results)}"
                f"&prop=extracts&exintro=1&explaintext=1&exlimit={max(3, max_results)}&utf8=&format=json"
            )
            resp = self._session.get(
                url, timeout=timeout, headers={"User-Agent": self._user_agent}
            )
            resp.raise_for_status()
            data = resp.json()

            pages = data.get("query", {}).get("pages", {})

            sorted_pages = sorted(pages.values(), key=lambda p: p.get("index", 999))

            for item in sorted_pages[:max_results]:
                extract = item.get("extract", "").strip()
                if not extract:
                    continue
                results.append(
                    SearchResult(
                        title=item.get("title", ""),
                        body=f"Wikipedia: {extract}",
                        href=f"https://{wiki_domain}/wiki/{urllib.parse.quote(item.get('title', ''))}",
                        source="wikipedia",
                    )
                )
        except Exception as e:
            logger.warning(f"[WebSearch] Wikipedia API failed: {e}")
        return results[:max_results]

    def _search_google_scrape(
        self, query: str, timeout: float = 8.0
    ) -> List[SearchResult]:

        if not REQUESTS_AVAILABLE or not BS4_AVAILABLE:
            return []
        results: List[SearchResult] = []
        try:
            encoded = urllib.parse.quote(query)
            is_ar = bool(re.search(r"[\u0600-\u06FF]", query))
            hl = "ar" if is_ar else "en"
            url = f"https://www.google.com/search?q={encoded}&hl={hl}"
            resp = self._session.get(
                url, timeout=timeout, headers={"User-Agent": self._user_agent}
            )
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")

            for g in soup.select("div.g, div[data-sokoban-container], div.tF2Cxc")[:3]:
                title_el = g.select_one("h3")
                snippet_el = g.select_one("div.VwiC3b, span.st, div[data-sncf]")
                link_el = g.select_one("a[href]")
                title = title_el.get_text(separator=" ", strip=True) if title_el else ""
                snippet = (
                    snippet_el.get_text(separator=" ", strip=True) if snippet_el else ""
                )
                href = link_el.get("href", "") if link_el else ""
                if title and (snippet or href):
                    results.append(
                        SearchResult(
                            title=title, body=snippet[:600], href=href, source="google"
                        )
                    )
        except Exception as e:
            logger.warning(f"[WebSearch] Google scrape failed: {e}")
        return results[:3]

    def search(
        self,
        query: str,
        max_results: int = 3,
        include_full_text: bool = True,
        timeout: float = 12.0,
        bypass_cache: bool = False,
    ) -> List[SearchResult]:

        query = query.strip()
        if not query:
            return []

        try:
            from src.iris.engine import detect_user_language, translate_text

            query_lang = detect_user_language(query)
            if query_lang and query_lang != "English":
                translated_query = translate_text(query, "English")
                if translated_query and translated_query != query:
                    logger.info(
                        f"[WebSearch] Translated search query '{query}' to English: '{translated_query}'"
                    )
                    query = translated_query
        except Exception as e:
            logger.warning(f"[WebSearch] Failed to auto-translate search query: {e}")

        max_results = max(1, min(max_results, 10))
        deadline = time.time() + timeout
        merged_results: List[SearchResult] = []

        import concurrent.futures

        results_ddg = []
        results_google = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            future_ddg = executor.submit(
                self._search_ddg, query, max_results, min(6.0, timeout)
            )
            future_google = executor.submit(
                self._search_google_scrape, query, min(6.0, timeout)
            )

            try:
                results_ddg = future_ddg.result(timeout=min(7.0, timeout))
            except Exception as e:
                logger.debug(f"[WebSearch] Parallel DDG failed: {e}")

            try:
                results_google = future_google.result(timeout=min(7.0, timeout))
            except Exception as e:
                logger.debug(f"[WebSearch] Parallel Google failed: {e}")

        seen_urls = set()
        non_wiki_results = []
        wiki_results = []
        for r in results_ddg + results_google:
            url_clean = r.href.strip().lower().rstrip("/")
            url_clean = re.sub(r"^https?://(www\.)?", "", url_clean)
            if url_clean not in seen_urls:
                seen_urls.add(url_clean)
                if "wikipedia.org" in r.href.lower():
                    wiki_results.append(r)
                else:
                    non_wiki_results.append(r)

        merged_results = non_wiki_results + wiki_results

        if len(merged_results) == 0 and time.time() < deadline:
            try:
                wiki_results = self._search_wikipedia(query, max_results=max_results)
                if wiki_results:
                    for r in wiki_results:
                        url_clean = r.href.strip().lower().rstrip("/")
                        url_clean = re.sub(r"^https?://(www\.)?", "", url_clean)
                        if url_clean not in seen_urls:
                            seen_urls.add(url_clean)
                            merged_results.append(r)
            except Exception as e:
                logger.debug(f"[WebSearch] Wikipedia fallback failed: {e}")

        if include_full_text and merged_results and time.time() < deadline:
            targets = merged_results[:3]
            with concurrent.futures.ThreadPoolExecutor(
                max_workers=len(targets)
            ) as executor:
                futures = {
                    executor.submit(self._fetch_full_text, r.href, timeout=4.0): r
                    for r in targets
                }
                for future in concurrent.futures.as_completed(futures, timeout=5.0):
                    r = futures[future]
                    try:
                        full_content = future.result()
                        if full_content:
                            r.body = full_content[:4000]
                    except Exception as e:
                        logger.debug(
                            f"[WebSearch] Parallel full-text fetch failed for {r.href}: {e}"
                        )

        return merged_results[:max_results]

    def search_to_context(self, query: str, max_results: int = 3) -> str:

        results = self.search(query, max_results)
        if not results:
            return ""
        lines = []
        for i, r in enumerate(results, 1):
            lines.append(f"Result {i}: {r.to_context_str()}")
        return "\n".join(lines)

    def _fetch_full_text(self, url: str, timeout: float = 4.0) -> str:

        if not REQUESTS_AVAILABLE or not BS4_AVAILABLE:
            return ""
        try:
            resp = self._session.get(
                url, timeout=timeout, headers={"User-Agent": self._user_agent}
            )
            if resp.status_code != 200:
                return ""
            soup = BeautifulSoup(resp.text, "html.parser")
            for tag in soup(
                [
                    "script",
                    "style",
                    "nav",
                    "footer",
                    "header",
                    "noscript",
                    "iframe",
                    "form",
                ]
            ):
                tag.extract()
            text = soup.get_text(separator=" ", strip=True)

            text = re.sub(r"\s+", " ", text)
            if len(text) > 200:
                return text[:4000]
            return text
        except Exception as e:
            logger.debug(f"[WebSearch] Full-text fetch failed for {url[:60]}: {e}")
            return ""


_KEYWORD_EXTRACT_PROMPT = (
    "Extract exactly 2-4 search keywords from the text. Use the context to resolve "
    "pronouns. If no search is needed, output ONLY the word 'none'.\n\n"
    "Examples:\n"
    "Text: What is the capital of France?\nKeywords: capital France\n\n"
    "Text: How do I fix a ValueError in Python?\nKeywords: Python ValueError fix\n\n"
    "Text: Hello, how are you?\nKeywords: none\n\n"
    "Context: {context}\nText: {text}\nKeywords:"
)


def extract_search_keywords(text: str, context: str = "", llm=None) -> Optional[str]:

    text = text.strip()
    if not text or len(text.split()) <= 2:
        return None

    question_starters = (
        "what",
        "who",
        "when",
        "where",
        "why",
        "how",
        "tell me about",
        "explain",
        "define",
        "search for",
        "look up",
        "find",
        "latest",
        "news about",
        "update on",
    )
    lower = text.lower()
    fast_trigger = any(lower.startswith(s) for s in question_starters)

    if llm:
        try:
            prompt = _KEYWORD_EXTRACT_PROMPT.format(
                context=context[:300], text=text[:500]
            )
            resp = llm.create_completion(
                prompt=prompt, max_tokens=15, temperature=0.1, stop=["\n", "Text:"]
            )
            kw = resp["choices"][0]["text"].strip()
            if kw and kw.lower() != "none" and len(kw.split()) >= 1:
                return kw
        except Exception as e:
            logger.warning(f"[WebSearch] Keyword extraction LLM call failed: {e}")

    if not fast_trigger:
        return None

    return _extract_keywords_deterministic(text)


def _extract_keywords_deterministic(text: str) -> Optional[str]:

    stop = {
        "what",
        "who",
        "when",
        "where",
        "why",
        "how",
        "is",
        "are",
        "the",
        "a",
        "an",
        "can",
        "you",
        "i",
        "me",
        "tell",
        "about",
        "do",
        "does",
        "did",
        "will",
        "would",
        "could",
        "should",
        "please",
        "explain",
        "define",
        "search",
        "look",
        "find",
        "get",
        "give",
        "show",
        "hello",
        "hi",
        "hey",
        "ok",
        "okay",
        "thanks",
        "thank",
    }
    words = [
        w.strip(".,;:!?\"'")
        for w in text.lower().split()
        if w.strip(".,;:!?\"'") not in stop
    ]

    meaningful = [w for w in words if len(w) >= 3]
    if not meaningful:
        return None


def perform_web_search(query: str, num_results: int = 3) -> str:
    """
    Performs a lightweight web search using DuckDuckGo HTML version.
    Returns a formatted string of search results.
    """
    url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
    req = urllib.request.Request(
        url,
        data=None,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode("utf-8")

        snippets = re.findall(
            r'<a class="result__snippet[^>]*>(.*?)</a>', html, re.IGNORECASE | re.DOTALL
        )
        titles = re.findall(
            r'<h2 class="result__title">.*?<a[^>]*>(.*?)</a>',
            html,
            re.IGNORECASE | re.DOTALL,
        )

        results = []
        for i in range(min(num_results, len(snippets))):
            title = (
                re.sub(r"<[^>]+>", "", titles[i]).strip()
                if i < len(titles)
                else f"Result {i+1}"
            )
            snippet = re.sub(r"<[^>]+>", "", snippets[i]).strip()
            results.append(f"[{title}]\n{snippet}")

        if not results:
            return "No search results found."

        return "\n\n".join(results)
    except Exception as e:
        return f"Web search failed: {str(e)}"
=======
import os
import urllib.request
import re
import json
import time
import logging
import threading
import urllib.parse
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry

    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    from bs4 import BeautifulSoup

    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False

try:
    from ddgs import DDGS

    DDGS_AVAILABLE = True
except ImportError:
    DDGS_AVAILABLE = False

logger = logging.getLogger("iris.web_search")


@dataclass
class SearchResult:
    title: str = ""
    body: str = ""
    href: str = ""
    source: str = "web"

    def __post_init__(self):
        if self.body:
            patterns = [
                r"create a sex novel",
                r"cannot fulfill this request due to",
                r"unable to provide guidance on creating content",
                r"inappropriate answer, I will respond",
                r"sexual themes or activities",
            ]
            lines = self.body.splitlines()
            clean_lines = []
            for line in lines:
                if any(re.search(pat, line, re.IGNORECASE) for pat in patterns):
                    continue
                clean_lines.append(line)
            self.body = "\n".join(clean_lines)

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "body": self.body,
            "href": self.href,
            "source": self.source,
        }

    def to_context_str(self) -> str:
        parts = [f"**{self.title}**"]
        if self.body:
            parts.append(self.body[:600])
        if self.href:
            parts.append(f"[source]({self.href})")
        return "\n".join(parts)


class WebSearch:

    _singleton = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._singleton is None:
            with cls._lock:
                if cls._singleton is None:
                    cls._singleton = super().__new__(cls)
                    cls._singleton._initialized = False
        return cls._singleton

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._session = None
        self._ddg_available = DDGS_AVAILABLE
        self._ddg_rate_limited_until = 0.0
        if REQUESTS_AVAILABLE:
            self._session = requests.Session()
            retry = Retry(
                total=2, backoff_factor=0.5, status_forcelist=[429, 500, 502, 503, 504]
            )
            adapter = HTTPAdapter(max_retries=retry)
            self._session.mount("https://", adapter)
            self._session.mount("http://", adapter)
        self._user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

    def _search_ddg(
        self, query: str, max_results: int, timeout: float = 8.0
    ) -> List[SearchResult]:

        if not self._ddg_available:
            return []
        now = time.time()
        if now < self._ddg_rate_limited_until:
            logger.warning(
                "[WebSearch] DDG rate-limited until %.0f seconds from now",
                self._ddg_rate_limited_until - now,
            )
            return []
        results: List[SearchResult] = []
        try:
            with DDGS() as ddgs:
                for r in ddgs.text(query, max_results=max_results, backend="html"):
                    results.append(
                        SearchResult(
                            title=r.get("title", ""),
                            body=r.get("body", ""),
                            href=r.get("href", ""),
                            source="ddg_text",
                        )
                    )
                    if len(results) >= max_results:
                        break
        except Exception as e:
            err = str(e).lower()
            if "202" in err or "403" in err or "rate" in err or "limited" in err:
                self._ddg_rate_limited_until = time.time() + 30.0
                logger.warning("[WebSearch] DDG rate-limited, backoff 30s")
            else:
                logger.warning(f"[WebSearch] DDG text failed: {e}")

        if len(results) < max_results and time.time() >= self._ddg_rate_limited_until:
            try:
                with DDGS() as ddgs:
                    for r in ddgs.news(
                        query, max_results=max((max_results - len(results)), 1)
                    ):
                        results.append(
                            SearchResult(
                                title=r.get("title", ""),
                                body=r.get("body", ""),
                                href=r.get("url", r.get("href", "")),
                                source="ddg_news",
                            )
                        )
                        if len(results) >= max_results:
                            break
            except Exception as e:
                logger.debug(f"[WebSearch] DDG news failed: {e}")
        return results[:max_results]

    def _search_wikipedia(
        self, query: str, max_results: int, timeout: float = 6.0
    ) -> List[SearchResult]:

        if not REQUESTS_AVAILABLE:
            return []
        results: List[SearchResult] = []
        try:
            encoded = urllib.parse.quote(query)
            is_ar = bool(re.search(r"[\u0600-\u06FF]", query))
            wiki_domain = "ar.wikipedia.org" if is_ar else "en.wikipedia.org"
            url = (
                f"https://{wiki_domain}/w/api.php?action=query&generator=search"
                f"&gsrsearch={encoded}&gsrlimit={max(3, max_results)}"
                f"&prop=extracts&exintro=1&explaintext=1&exlimit={max(3, max_results)}&utf8=&format=json"
            )
            resp = self._session.get(
                url, timeout=timeout, headers={"User-Agent": self._user_agent}
            )
            resp.raise_for_status()
            data = resp.json()

            pages = data.get("query", {}).get("pages", {})

            sorted_pages = sorted(pages.values(), key=lambda p: p.get("index", 999))

            for item in sorted_pages[:max_results]:
                extract = item.get("extract", "").strip()
                if not extract:
                    continue
                results.append(
                    SearchResult(
                        title=item.get("title", ""),
                        body=f"Wikipedia: {extract}",
                        href=f"https://{wiki_domain}/wiki/{urllib.parse.quote(item.get('title', ''))}",
                        source="wikipedia",
                    )
                )
        except Exception as e:
            logger.warning(f"[WebSearch] Wikipedia API failed: {e}")
        return results[:max_results]

    def _search_google_scrape(
        self, query: str, timeout: float = 8.0
    ) -> List[SearchResult]:

        if not REQUESTS_AVAILABLE or not BS4_AVAILABLE:
            return []
        results: List[SearchResult] = []
        try:
            encoded = urllib.parse.quote(query)
            is_ar = bool(re.search(r"[\u0600-\u06FF]", query))
            hl = "ar" if is_ar else "en"
            url = f"https://www.google.com/search?q={encoded}&hl={hl}"
            resp = self._session.get(
                url, timeout=timeout, headers={"User-Agent": self._user_agent}
            )
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")

            for g in soup.select("div.g, div[data-sokoban-container], div.tF2Cxc")[:3]:
                title_el = g.select_one("h3")
                snippet_el = g.select_one("div.VwiC3b, span.st, div[data-sncf]")
                link_el = g.select_one("a[href]")
                title = title_el.get_text(separator=" ", strip=True) if title_el else ""
                snippet = (
                    snippet_el.get_text(separator=" ", strip=True) if snippet_el else ""
                )
                href = link_el.get("href", "") if link_el else ""
                if title and (snippet or href):
                    results.append(
                        SearchResult(
                            title=title, body=snippet[:600], href=href, source="google"
                        )
                    )
        except Exception as e:
            logger.warning(f"[WebSearch] Google scrape failed: {e}")
        return results[:3]

    def search(
        self,
        query: str,
        max_results: int = 3,
        include_full_text: bool = True,
        timeout: float = 12.0,
        bypass_cache: bool = False,
    ) -> List[SearchResult]:

        query = query.strip()
        if not query:
            return []

        try:
            from src.iris.engine import detect_user_language, translate_text

            query_lang = detect_user_language(query)
            if query_lang and query_lang != "English":
                translated_query = translate_text(query, "English")
                if translated_query and translated_query != query:
                    logger.info(
                        f"[WebSearch] Translated search query '{query}' to English: '{translated_query}'"
                    )
                    query = translated_query
        except Exception as e:
            logger.warning(f"[WebSearch] Failed to auto-translate search query: {e}")

        max_results = max(1, min(max_results, 10))
        deadline = time.time() + timeout
        merged_results: List[SearchResult] = []

        import concurrent.futures

        results_ddg = []
        results_google = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            future_ddg = executor.submit(
                self._search_ddg, query, max_results, min(6.0, timeout)
            )
            future_google = executor.submit(
                self._search_google_scrape, query, min(6.0, timeout)
            )

            try:
                results_ddg = future_ddg.result(timeout=min(7.0, timeout))
            except Exception as e:
                logger.debug(f"[WebSearch] Parallel DDG failed: {e}")

            try:
                results_google = future_google.result(timeout=min(7.0, timeout))
            except Exception as e:
                logger.debug(f"[WebSearch] Parallel Google failed: {e}")

        seen_urls = set()
        non_wiki_results = []
        wiki_results = []
        for r in results_ddg + results_google:
            url_clean = r.href.strip().lower().rstrip("/")
            url_clean = re.sub(r"^https?://(www\.)?", "", url_clean)
            if url_clean not in seen_urls:
                seen_urls.add(url_clean)
                if "wikipedia.org" in r.href.lower():
                    wiki_results.append(r)
                else:
                    non_wiki_results.append(r)

        merged_results = non_wiki_results + wiki_results

        if len(merged_results) == 0 and time.time() < deadline:
            try:
                wiki_results = self._search_wikipedia(query, max_results=max_results)
                if wiki_results:
                    for r in wiki_results:
                        url_clean = r.href.strip().lower().rstrip("/")
                        url_clean = re.sub(r"^https?://(www\.)?", "", url_clean)
                        if url_clean not in seen_urls:
                            seen_urls.add(url_clean)
                            merged_results.append(r)
            except Exception as e:
                logger.debug(f"[WebSearch] Wikipedia fallback failed: {e}")

        if include_full_text and merged_results and time.time() < deadline:
            targets = merged_results[:3]
            with concurrent.futures.ThreadPoolExecutor(
                max_workers=len(targets)
            ) as executor:
                futures = {
                    executor.submit(self._fetch_full_text, r.href, timeout=4.0): r
                    for r in targets
                }
                for future in concurrent.futures.as_completed(futures, timeout=5.0):
                    r = futures[future]
                    try:
                        full_content = future.result()
                        if full_content:
                            r.body = full_content[:4000]
                    except Exception as e:
                        logger.debug(
                            f"[WebSearch] Parallel full-text fetch failed for {r.href}: {e}"
                        )

        return merged_results[:max_results]

    def search_to_context(self, query: str, max_results: int = 3) -> str:

        results = self.search(query, max_results)
        if not results:
            return ""
        lines = []
        for i, r in enumerate(results, 1):
            lines.append(f"Result {i}: {r.to_context_str()}")
        return "\n".join(lines)

    def _fetch_full_text(self, url: str, timeout: float = 4.0) -> str:

        if not REQUESTS_AVAILABLE or not BS4_AVAILABLE:
            return ""
        try:
            resp = self._session.get(
                url, timeout=timeout, headers={"User-Agent": self._user_agent}
            )
            if resp.status_code != 200:
                return ""
            soup = BeautifulSoup(resp.text, "html.parser")
            for tag in soup(
                [
                    "script",
                    "style",
                    "nav",
                    "footer",
                    "header",
                    "noscript",
                    "iframe",
                    "form",
                ]
            ):
                tag.extract()
            text = soup.get_text(separator=" ", strip=True)

            text = re.sub(r"\s+", " ", text)
            if len(text) > 200:
                return text[:4000]
            return text
        except Exception as e:
            logger.debug(f"[WebSearch] Full-text fetch failed for {url[:60]}: {e}")
            return ""


_KEYWORD_EXTRACT_PROMPT = (
    "Extract exactly 2-4 search keywords from the text. Use the context to resolve "
    "pronouns. If no search is needed, output ONLY the word 'none'.\n\n"
    "Examples:\n"
    "Text: What is the capital of France?\nKeywords: capital France\n\n"
    "Text: How do I fix a ValueError in Python?\nKeywords: Python ValueError fix\n\n"
    "Text: Hello, how are you?\nKeywords: none\n\n"
    "Context: {context}\nText: {text}\nKeywords:"
)


def extract_search_keywords(text: str, context: str = "", llm=None) -> Optional[str]:

    text = text.strip()
    if not text or len(text.split()) <= 2:
        return None

    question_starters = (
        "what",
        "who",
        "when",
        "where",
        "why",
        "how",
        "tell me about",
        "explain",
        "define",
        "search for",
        "look up",
        "find",
        "latest",
        "news about",
        "update on",
    )
    lower = text.lower()
    fast_trigger = any(lower.startswith(s) for s in question_starters)

    if llm:
        try:
            prompt = _KEYWORD_EXTRACT_PROMPT.format(
                context=context[:300], text=text[:500]
            )
            resp = llm.create_completion(
                prompt=prompt, max_tokens=15, temperature=0.1, stop=["\n", "Text:"]
            )
            kw = resp["choices"][0]["text"].strip()
            if kw and kw.lower() != "none" and len(kw.split()) >= 1:
                return kw
        except Exception as e:
            logger.warning(f"[WebSearch] Keyword extraction LLM call failed: {e}")

    if not fast_trigger:
        return None

    return _extract_keywords_deterministic(text)


def _extract_keywords_deterministic(text: str) -> Optional[str]:

    stop = {
        "what",
        "who",
        "when",
        "where",
        "why",
        "how",
        "is",
        "are",
        "the",
        "a",
        "an",
        "can",
        "you",
        "i",
        "me",
        "tell",
        "about",
        "do",
        "does",
        "did",
        "will",
        "would",
        "could",
        "should",
        "please",
        "explain",
        "define",
        "search",
        "look",
        "find",
        "get",
        "give",
        "show",
        "hello",
        "hi",
        "hey",
        "ok",
        "okay",
        "thanks",
        "thank",
    }
    words = [
        w.strip(".,;:!?\"'")
        for w in text.lower().split()
        if w.strip(".,;:!?\"'") not in stop
    ]

    meaningful = [w for w in words if len(w) >= 3]
    if not meaningful:
        return None


def perform_web_search(query: str, num_results: int = 3) -> str:
    """
    Performs a lightweight web search using DuckDuckGo HTML version.
    Returns a formatted string of search results.
    """
    url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
    req = urllib.request.Request(
        url,
        data=None,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode("utf-8")

        snippets = re.findall(
            r'<a class="result__snippet[^>]*>(.*?)</a>', html, re.IGNORECASE | re.DOTALL
        )
        titles = re.findall(
            r'<h2 class="result__title">.*?<a[^>]*>(.*?)</a>',
            html,
            re.IGNORECASE | re.DOTALL,
        )

        results = []
        for i in range(min(num_results, len(snippets))):
            title = (
                re.sub(r"<[^>]+>", "", titles[i]).strip()
                if i < len(titles)
                else f"Result {i+1}"
            )
            snippet = re.sub(r"<[^>]+>", "", snippets[i]).strip()
            results.append(f"[{title}]\n{snippet}")

        if not results:
            return "No search results found."

        return "\n\n".join(results)
    except Exception as e:
        return f"Web search failed: {str(e)}"
>>>>>>> origin/main
