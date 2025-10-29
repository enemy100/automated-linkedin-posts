# GitHub Actions – Optional Automation

Use GitHub Actions to trigger your n8n workflow on a schedule or to run helper scripts.

## Option A: Trigger n8n webhook

```yaml
name: Trigger n8n Workflow

on:
  schedule:
    - cron: '0 9,17 * * 1-5'  # 09:00 and 17:00 UTC on weekdays
  workflow_dispatch:

jobs:
  trigger:
    runs-on: ubuntu-latest
    steps:
      - name: Call n8n webhook
        run: |
          curl -fsS -X POST "${{ secrets.N8N_WEBHOOK_URL }}" || exit 1
```

Set `N8N_WEBHOOK_URL` in repo secrets.

## Option B: Run helper script

```yaml
name: Process posts

on:
  schedule:
    - cron: '0 * * * *'  # hourly
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
          NOTION_API_TOKEN: ${{ secrets.NOTION_API_TOKEN }}
          LINKEDIN_ACCESS_TOKEN: ${{ secrets.LINKEDIN_ACCESS_TOKEN }}
          LINKEDIN_PROFILE_ID: ${{ secrets.LINKEDIN_PROFILE_ID }}
        run: |
          python scripts/process_posts.py
```

## Tips

- Prefer n8n’s Scheduler inside the workflow unless you specifically need CI
- Keep all secrets in GitHub → Settings → Secrets and variables → Actions
- Add notifications on failure (Slack, email) if the pipeline is critical

