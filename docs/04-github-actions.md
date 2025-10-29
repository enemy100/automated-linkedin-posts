# GitHub Actions – Extraction Only (to Notion)

Use Actions to extract content from external sites and write new items into Notion. n8n will post on its own schedule.

## Where to configure Secrets
- In your GitHub repo: Settings → Secrets and variables → Actions → "New repository secret"
- Add at least:
  - `NOTION_API_TOKEN` – your Notion integration token
  - `GROQ_API_KEY` – Groq API key (the extractor uses LLM to rewrite/condense content)
  - (Optional) any other API keys your extractor needs
 
    <img width="805" height="202" alt="image" src="https://github.com/user-attachments/assets/a5d6184c-76b4-4629-9cde-c5a63937e174" />


## How to get a Groq API key (free tier available)
- Create an account at: https://console.groq.com
- Go to API Keys → "Create API Key"
- Copy the key (starts with `gsk_...`) and save it as `GROQ_API_KEY` in GitHub Secrets
- Groq offers a free tier; limits may apply. See their pricing/usage page in the console

  <img width="1849" height="290" alt="image" src="https://github.com/user-attachments/assets/bfc96cbb-4194-4444-acc1-0e227ad3e9fa" />


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
          pip install -r projeto_linkedin/drop-news-main/cybersecurity-daily-feed/requirements.txt
      - name: Extract feeds → Notion (with Groq rewrite)
        env:
          NOTION_API_TOKEN: $${{ secrets.NOTION_API_TOKEN }}
          GROQ_API_KEY: $${{ secrets.GROQ_API_KEY }}
        run: |
          python projeto_linkedin/drop-news-main/cybersecurity-daily-feed/sec-feed-extract.py
```

How it works
- The job runs on the cron schedule or manually with "Run workflow"
- It reads your `Feed.csv`, uses Groq to rewrite/condense posts, and writes items into Notion
- Your n8n workflow (scheduled) will pick up items with `flow_status = START` and post to LinkedIn

Notes
- Keep all tokens in GitHub Secrets
- Logs of each run appear in the Actions tab
- Adjust the cron as needed (e.g., hourly, twice a day)

