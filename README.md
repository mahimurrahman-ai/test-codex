# Research AI Agent

This repository contains a working Python **research AI agent**.

## Features
- Web research pipeline: search -> fetch -> extract -> synthesize.
- Markdown research brief generation with findings and sources.
- Offline mode with local files (`--local-file`) for restricted environments.
- Dependency-free runtime (Python standard library only).

## Quick start

```bash
python3 research_agent.py "AI agent evaluation metrics" --max-results 5 --output report.md
```

## Offline mode

```bash
python3 research_agent.py "RAG architecture tradeoffs" \
  --local-file notes1.txt \
  --local-file notes2.md \
  --output report.md
```

## CLI

```bash
python3 research_agent.py "query" \
  [--max-results 5] \
  [--output report.md] \
  [--local-file file1 --local-file file2]
```

## Run tests

```bash
python3 -m unittest discover -s tests -v
```

## Notes
- In environments that block outbound HTTP/proxy access, use offline mode.
- Missing local files are reported as explicit errors.
