# GitHub Actions – Extraction Only (to Notion)

Use Actions to extract content from external sites and write new items into Notion. n8n will post on its own schedule.

## What are Feed.csv and Config.txt?
- `extractor/Feed.csv`: your sources list. Each line is `URL,Name` and defines where the extractor pulls articles from.
- `extractor/Config.txt`: per‑source checkpoint. It stores the last processed timestamp for each source and is updated automatically on every run.

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
      - name: Install deps
        run: |
          pip install -r extractor/requirements.txt
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

## In 30 seconds: what it does
- Reads sources from `extractor/Feed.csv`
- For each source, fetches recent articles and ignores items older than 14 days
- Uses Groq to rewrite/condense the article (model: `llama-3.1-70b-versatile`, fallback: `llama-3.1-8b-instant`)
- Creates a page in Notion with the rewritten content and metadata
- Updates `extractor/Config.txt` with the latest timestamp to avoid duplicates

  <img width="1907" height="464" alt="image" src="https://github.com/user-attachments/assets/1ab377b9-7abe-425f-afa1-09868da9739c" />


## Why I don’t see new items in Notion?
- Items older than 14 days are skipped by design
- Items already processed (timestamp in `Config.txt` is newer or equal) are ignored
- Verify the `NOTION_API_TOKEN` secret and that the Integration has access to the database
- Check the logs: “Creating Notion page for: <title>” indicates a create attempt

