# GitHub Actions – Extraction Only (to Notion)

Use Actions to extract content from external sites and write new items into Notion. n8n will post on its own schedule.

## Where to configure Secrets
- In your GitHub repo: Settings → Secrets and variables → Actions → "New repository secret"
- Add at least:
  - `NOTION_API_TOKEN` – your Notion integration token
  - `GROQ_API_KEY` – Groq API key (the extractor uses LLM to rewrite/condense content)
  - (Optional) any other API keys your extractor needs

## How to get a Groq API key (free tier available)
- Create an account at: https://console.groq.com
- Go to API Keys → "Create API Key"
- Copy the key (starts with `gsk_...`) and save it as `GROQ_API_KEY` in GitHub Secrets
- Groq offers a free tier; limits may apply. See their pricing/usage page in the console

## Bring the extractor into this repo
Choose ONE:
- Copy the folder `cybersecurity-daily-feed/` from your other project into this repo as `extractor/`
  - Expected files: `extractor/sec-feed-extract.py`, `extractor/requirements.txt`, `extractor/Feed.csv`, `extractor/Config.txt`
- Or add the other project as a submodule and adjust paths accordingly

Example to copy (local):
```bash
# from your machine, in the repo root
mkdir -p extractor
# copy the four key files into extractor/
```

## Example workflow: `.github/workflows/extract-content.yml`
```yaml
name: Extract content to Notion

on:
  schedule:
    - cron: '0 */2 * * *'   # every 2 hours
  workflow_dispatch:

jobs:
  run:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install deps (requirements or fallback)
        run: |
          if [ -f extractor/requirements.txt ]; then
            pip install -r extractor/requirements.txt
          else
            # Fallback minimal set used by the extractor
            pip install feedparser groq requests python-dotenv sgmllib3k httpx pydantic
          fi
      - name: Extract feeds → Notion (with Groq rewrite)
        env:
          NOTION_API_TOKEN: $${{ secrets.NOTION_API_TOKEN }}
          GROQ_API_KEY: $${{ secrets.GROQ_API_KEY }}
        run: |
          python extractor/sec-feed-extract.py
```

## Create and run from the GitHub UI

- Create via UI:
  1) Go to your repo → Actions tab
  2) Click "set up a workflow yourself" (or "New workflow" → "set up a workflow yourself")
  3) Paste the example YAML above and save as `.github/workflows/extract-content.yml`
  4) Commit the new file to `main`

- Run manually:
  1) Actions tab → select "Extract content to Notion"
  2) Click "Run workflow" → choose branch `main` → Run

- Run on schedule:
  - The job runs automatically at the cron you set (e.g., every 2 hours)

- View runs and logs:
  - Actions tab → click the workflow run → view job logs and outputs

How it works
- The job runs on the cron schedule or manually with "Run workflow"
- It reads your `Feed.csv`, uses Groq to rewrite/condense posts, and writes items into Notion
- Your n8n workflow (scheduled) will pick up items with `flow_status = START` and post to LinkedIn

Notes
- Keep all tokens in GitHub Secrets
- Logs of each run appear in the Actions tab
- Adjust the cron as needed (e.g., hourly, twice a day)

