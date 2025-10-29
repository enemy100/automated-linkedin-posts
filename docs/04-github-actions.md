# GitHub Actions – Extraction Only (to Notion)

Use Actions to extract content from external sites and write new items into Notion. n8n will post on its own schedule.

## Secrets to set
- `NOTION_API_TOKEN` – Notion integration token
- (Optional) Any API keys your extractor needs

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
      - name: Extract feeds → Notion
        env:
          NOTION_API_TOKEN: $${{ secrets.NOTION_API_TOKEN }}
        run: |
          python projeto_linkedin/drop-news-main/cybersecurity-daily-feed/sec-feed-extract.py
```

How it works
- The job runs on the cron schedule or manually with "Run workflow"
- It reads your `Feed.csv` and writes items into Notion
- Your n8n workflow (scheduled) will pick up items with `flow_status = START` and post to LinkedIn

Notes
- Keep all tokens in GitHub Secrets
- Logs of each run appear in the Actions tab
- Adjust the cron as needed (e.g., hourly, twice a day)

