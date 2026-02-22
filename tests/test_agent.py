import tempfile
import unittest
from pathlib import Path

from research_agent import (
    extract_ddg_redirect_url,
    load_local_documents,
    parse_duckduckgo_results,
    run,
    top_sentences,
)


class AgentTests(unittest.TestCase):
    def test_extract_ddg_redirect_url(self):
        wrapped = "/l/?uddg=https%3A%2F%2Fexample.com%2Fpaper"
        self.assertEqual(extract_ddg_redirect_url(wrapped), "https://example.com/paper")

    def test_parse_duckduckgo_results(self):
        html = """
        <div class='result'>
          <a class='result__a' href='https://example.com/a'>Title A</a>
          <span class='result__snippet'>Snippet A</span>
        </div>
        <div class='result'>
          <a class='result__a' href='/l/?uddg=https%3A%2F%2Fexample.com%2Fb'>Title B</a>
          <div class='result__snippet'>Snippet B</div>
        </div>
        """
        results = parse_duckduckgo_results(html, limit=5)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[1].url, "https://example.com/b")
        self.assertIn("Snippet", results[0].snippet)

    def test_top_sentences_prefers_relevant(self):
        text = (
            "Cooking recipes are fun for beginners. "
            "AI research agents combine retrieval with summarization for faster analysis. "
            "Some systems use tools, planning, and memory for complex tasks."
        )
        picked = top_sentences(text, query="AI research agent tools", max_sentences=2)
        joined = " ".join(picked).lower()
        self.assertIn("research", joined)
        self.assertIn("tools", joined)

    def test_load_local_documents(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "sample.txt"
            p.write_text("Agents use retrieval and ranking to improve research quality.", encoding="utf-8")
            docs = load_local_documents([str(p)])
            self.assertEqual(len(docs), 1)
            self.assertIn("retrieval", docs[0].content.lower())

    def test_run_with_local_files_generates_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "source.md"
            p.write_text(
                "RAG systems improve reliability by grounding outputs in retrieved evidence.",
                encoding="utf-8",
            )
            report = run("RAG reliability", max_results=2, output=None, local_files=[str(p)])
            self.assertIn("Research Brief", report)
            self.assertIn("Sources", report)


if __name__ == "__main__":
    unittest.main()
