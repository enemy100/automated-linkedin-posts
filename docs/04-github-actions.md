# GitHub Actions – Extraction and Triggers

Use Actions for two things:
- Extract content from external sites and write into Notion
- Trigger n8n via webhook to run the posting workflow

## A) Extraction workflow (example)

Secrets to set:
- `NOTION_API_TOKEN` – Notion integration token
- (Optional) Other API keys your extractor uses

Example `.github/workflows/extract-content.yml`:
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

This job reads your `Feed.csv` and updates Notion with new items.

## B) Trigger n8n webhook

1) In n8n, add a Webhook Trigger node to either:
   - the main posting workflow, or
   - a tiny workflow that calls "Execute Workflow" for your posting flow.

2) Copy the Production URL from the Webhook node panel (the URL looks like:
   `https://<your-n8n-host>/webhook/<id>` or with path you set).

3) Save it as a secret: `N8N_WEBHOOK_URL`.

Workflow `.github/workflows/trigger-n8n.yml`:
```yaml
name: Trigger n8n Posting

on:
  schedule:
    - cron: '30 9,17 * * 1-5'
  workflow_dispatch:

jobs:
  trigger:
    runs-on: ubuntu-latest
    steps:
      - name: Call n8n webhook
        run: |
          curl -fsS -X POST "$${{ secrets.N8N_WEBHOOK_URL }}" || exit 1
```

Notes:
- Keep all tokens in GitHub Secrets
- If your n8n is behind Cloudflare Tunnel/Traefik, ensure the webhook URL is reachable publicly
- You can combine A) extraction + B) trigger in the same workflow file (two jobs)

