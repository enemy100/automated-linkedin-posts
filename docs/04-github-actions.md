# GitHub Actions – Configure, Variables, How to Run

Use Actions to trigger your n8n webhook or run helper scripts on a schedule.

## A) Trigger n8n via webhook (recommended)

1) Add a repo secret:
- Settings → Secrets and variables → Actions → New repository secret
- Name: `N8N_WEBHOOK_URL`
- Value: your production webhook URL

2) Create `.github/workflows/trigger-n8n.yml`:
```yaml
name: Trigger n8n Workflow

on:
  schedule:
    - cron: '0 9,17 * * 1-5'
  workflow_dispatch:

jobs:
  trigger:
    runs-on: ubuntu-latest
    steps:
      - name: Call n8n webhook
        run: |
          curl -fsS -X POST "$${{ secrets.N8N_WEBHOOK_URL }}" || exit 1
```

How to run:
- Manual: Actions → Trigger n8n Workflow → Run workflow
- Scheduled: runs at your cron times

## B) Run helper script (if you need one)

Secrets to set (examples):
- `NOTION_API_TOKEN` (Notion)
- `LINKEDIN_ACCESS_TOKEN` and `LINKEDIN_PROFILE_ID` (only if using a custom script, not needed for n8n node)

Workflow: `.github/workflows/process-posts.yml`
```yaml
name: Process posts

on:
  schedule:
    - cron: '0 * * * *'
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
        run: pip install requests python-dotenv
      - name: Execute
        env:
          NOTION_API_TOKEN: $${{ secrets.NOTION_API_TOKEN }}
        run: |
          python scripts/process_posts.py
```

Notes:
- If you only use n8n, you likely just need option A (webhook)
- Keep all tokens in GitHub Secrets (never commit `.env`)
- Use `workflow_dispatch` for manual runs at any time

