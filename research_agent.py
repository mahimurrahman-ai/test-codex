#!/usr/bin/env python3
"""Research AI Agent: search the web, read sources, and generate a research brief."""

from __future__ import annotations

import argparse
import html
import sys
import re
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable
from urllib.error import URLError
from urllib.parse import parse_qs, urlencode, urljoin, urlparse
from urllib.request import Request, urlopen

DDG_HTML_SEARCH_URL = "https://html.duckduckgo.com/html/"
USER_AGENT = "ResearchAIAgent/1.1 (+https://github.com/)"


@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str


@dataclass
class SourceDocument:
    title: str
    url: str
    snippet: str
    content: str


def normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def extract_ddg_redirect_url(raw_url: str) -> str:
    parsed = urlparse(raw_url)
    if parsed.path.startswith("/l/"):
        params = parse_qs(parsed.query)
        uddg = params.get("uddg", [""])[0]
        return uddg or raw_url
    return raw_url


class DDGResultParser(HTMLParser):
    """Minimal parser for DuckDuckGo HTML result blocks."""

    def __init__(self) -> None:
        super().__init__()
        self.results: list[SearchResult] = []
        self._in_result = False
        self._result_depth = 0
        self._in_link = False
        self._in_snippet = False
        self._current_url = ""
        self._title_parts: list[str] = []
        self._snippet_parts: list[str] = []

    def _finish_result(self) -> None:
        title = normalize_whitespace("".join(self._title_parts))
        snippet = normalize_whitespace("".join(self._snippet_parts))
        url = extract_ddg_redirect_url(self._current_url)
        if title and url:
            self.results.append(SearchResult(title=title, url=url, snippet=snippet))

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        classes = set(attrs_dict.get("class", "").split())

        if tag == "div" and "result" in classes and not self._in_result:
            self._in_result = True
            self._result_depth = 1
            self._in_link = False
            self._in_snippet = False
            self._current_url = ""
            self._title_parts = []
            self._snippet_parts = []
            return

        if self._in_result and tag == "div":
            self._result_depth += 1

        if self._in_result and tag == "a" and "result__a" in classes:
            self._in_link = True
            self._current_url = attrs_dict.get("href", "")

        # Snippet might be in <a>, <div>, or <span> depending on DDG template.
        if self._in_result and "result__snippet" in classes:
            self._in_snippet = True

    def handle_endtag(self, tag):
        if self._in_link and tag == "a":
            self._in_link = False

        if self._in_snippet and tag in {"a", "span", "div"}:
            self._in_snippet = False

        if self._in_result and tag == "div":
            self._result_depth -= 1
            if self._result_depth <= 0:
                self._finish_result()
                self._in_result = False
                self._result_depth = 0

    def handle_data(self, data):
        if self._in_link:
            self._title_parts.append(data)
        if self._in_snippet:
            self._snippet_parts.append(data)


def parse_duckduckgo_results(raw_html: str, limit: int = 8) -> list[SearchResult]:
    parser = DDGResultParser()
    parser.feed(raw_html)
    return parser.results[:limit]


def http_get(url: str, timeout: int = 20) -> str:
    req = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(req, timeout=timeout) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(charset, errors="replace")


def search_web(query: str, max_results: int = 8, timeout: int = 20) -> list[SearchResult]:
    params = urlencode({"q": query})
    raw_html = http_get(f"{DDG_HTML_SEARCH_URL}?{params}", timeout=timeout)
    parsed = parse_duckduckgo_results(raw_html, limit=max_results)
    return [SearchResult(r.title, urljoin("https://duckduckgo.com", r.url), r.snippet) for r in parsed]


def extract_main_text(raw_html: str) -> str:
    text = re.sub(r"<script[\s\S]*?</script>", " ", raw_html, flags=re.IGNORECASE)
    text = re.sub(r"<style[\s\S]*?</style>", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    return normalize_whitespace(html.unescape(text))


def fetch_document(result: SearchResult, timeout: int = 20) -> SourceDocument:
    raw_html = http_get(result.url, timeout=timeout)
    content = extract_main_text(raw_html)
    return SourceDocument(result.title, result.url, result.snippet, content)


def load_local_documents(paths: list[str]) -> list[SourceDocument]:
    docs: list[SourceDocument] = []
    for path in paths:
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"Local source file not found: {path}")
        raw = p.read_text(encoding="utf-8")
        content = extract_main_text(raw) if "<" in raw and ">" in raw else normalize_whitespace(raw)
        docs.append(SourceDocument(title=p.name, url=f"file://{p.resolve()}", snippet="local file", content=content))
    return docs


def sentence_split(text: str) -> list[str]:
    chunks = re.split(r"(?<=[.!?])\s+", text)
    return [c.strip() for c in chunks if len(c.strip()) > 30]


def keyword_set(query: str) -> set[str]:
    return set(re.findall(r"[a-zA-Z]{3,}", query.lower()))


def score_sentence(sentence: str, terms: set[str]) -> float:
    s = sentence.lower()
    overlap = sum(1 for term in terms if term in s)
    return overlap * 2.0 + min(len(sentence) / 220.0, 1.0)


def top_sentences(text: str, query: str, max_sentences: int = 4) -> list[str]:
    ranked = sorted(sentence_split(text), key=lambda x: score_sentence(x, keyword_set(query)), reverse=True)
    return ranked[:max_sentences]


def synthesize_report(query: str, documents: Iterable[SourceDocument]) -> str:
    docs = list(documents)
    findings: list[str] = []
    for doc in docs:
        for sentence in top_sentences(doc.content, query, max_sentences=2):
            findings.append(f"- {sentence} _(source: {doc.title})_")

    if not findings:
        findings = ["- No high-quality findings extracted. Try broader query or better sources."]

    source_lines = "\n".join(f"- [{d.title}]({d.url})" for d in docs) or "- No sources collected."
    findings_block = "\n".join(findings[:12])

    return (
        f"# Research Brief: {query}\n\n"
        f"## Executive Summary\n"
        f"This brief compiles findings for **{query}** and highlights relevant statements from sources.\n\n"
        f"## Key Findings\n"
        f"{findings_block}\n\n"
        f"## Open Questions\n"
        f"- Which claims are evidence-backed versus opinion?\n"
        f"- Which findings may be outdated?\n"
        f"- What experiments should validate these claims?\n\n"
        f"## Recommended Next Steps\n"
        f"1. Validate top claims using primary technical docs/papers.\n"
        f"2. Build one small prototype from one actionable finding.\n"
        f"3. Measure quality, latency, and cost as you iterate.\n\n"
        f"## Sources\n"
        f"{source_lines}\n"
    )


def run(query: str, max_results: int, output: str | None, local_files: list[str]) -> str:
    docs: list[SourceDocument] = []

    if local_files:
        docs.extend(load_local_documents(local_files))

    if not docs:
        try:
            results = search_web(query, max_results=max_results)
        except URLError as exc:
            raise RuntimeError("Network search failed. Re-run using --local-file with text/html sources.") from exc

        if not results:
            raise RuntimeError("No search results found. Try another query.")

        for result in results:
            try:
                docs.append(fetch_document(result))
            except Exception as exc:
                print(f"[warn] failed to fetch {result.url}: {exc}", file=sys.stderr)

    if not docs:
        raise RuntimeError("Could not load any usable sources.")

    report = synthesize_report(query, docs)
    if output:
        Path(output).write_text(report, encoding="utf-8")
    return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Research AI Agent")
    parser.add_argument("query", help="Research question")
    parser.add_argument("--max-results", type=int, default=5)
    parser.add_argument("--output", help="Optional output markdown file")
    parser.add_argument(
        "--local-file",
        action="append",
        default=[],
        help="Local .txt/.md/.html source file (repeatable). Enables offline research mode.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    print(run(args.query, args.max_results, args.output, args.local_file))


if __name__ == "__main__":
    main()
