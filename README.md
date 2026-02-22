# Research AI Agent

This repository now contains a fully working **research AI agent** built in Python.

## What it does
- Searches DuckDuckGo HTML results for your research query.
- Fetches and reads source pages.
- Extracts useful text from each source.
- Produces a structured Markdown research brief with findings and sources.
- Supports **offline mode** using local files when network search is unavailable.

## Quick start

```bash
python3 research_agent.py "AI agent evaluation metrics" --max-results 5 --output report.md
```

## Offline mode (works without internet)

```bash
python3 research_agent.py "RAG architecture tradeoffs" \
  --local-file notes1.txt \
  --local-file notes2.md \
  --output report.md
```

## CLI options

```bash
python3 research_agent.py "query" [--max-results 5] [--output report.md] [--local-file file1 --local-file file2]
```

## Run tests

```bash
python3 -m unittest discover -s tests -v
```

## File structure
- `research_agent.py`: core agent logic (search, parse, summarize, report generation).
- `tests/test_agent.py`: unit tests for parsing and summarization behavior.
