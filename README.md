# AI/AGI Engineer 5-Month Roadmap Site

This repo contains a complete static website designed for GitHub Pages.

## What this site includes
- 5-month practical roadmap (web → JS/API → Python → backend API → AI agents)
- "Learn now" vs "skip for now" guidance for each month
- Monthly completion tracker with local persistence
- Focus filter (Web/API/Python/AI)
- Light/dark theme toggle

## Run locally
```bash
python3 -m http.server 8000
```
Open <http://127.0.0.1:8000>.

## Deploy to GitHub Pages
### Option A: automatic via GitHub Actions (recommended)
1. Push the repo to GitHub.
2. In GitHub: **Settings → Pages → Build and deployment → Source = GitHub Actions**.
3. The included workflow (`.github/workflows/pages.yml`) deploys on every push to `main`.

### Option B: branch deploy
1. In GitHub: **Settings → Pages**.
2. Choose **Deploy from a branch**.
3. Select branch `main` and folder `/ (root)`.
