# n8n Setup – Minimal Steps

Already have n8n running? Skip to Import Workflow.

If you need installation, use your repository (no inline docs here):
- n8n install repo: https://github.com/enemy100/n8n-setup-on-raspberry-with-cloudflare-tunnel

## Import Workflow
- In n8n: Workflows → Import from File
- Select: `n8n-workflows/linkedin-notion-posting.json`
- Save the workflow

## Credentials to configure
- Notion API → Internal Integration token (connect your DB)
- LinkedIn OAuth2 → Follow docs/01-linkedin-api.md (no Python needed)
- (Optional) Freepik API → add header `x-freepik-api-key` to the HTTP Request node

## What the workflow does
- Schedule Trigger (daily by default)
- Notion (Get All) → fetch 1 page with `flow_status` contains `START`
- Notion (Get) → fetch content blocks
- Aggregate → combine into `property_content`
- LLM (rewrite) → clean text for LinkedIn
- Optional image branch → generate + resize image
- LinkedIn (Publish) → post using your OAuth2 credential
- Notion (Update) → set `flow_status` to `DONE LINKEDIN`

## Before running
- Ensure your Notion DB has items with `flow_status = START`
- Map the correct Database ID and property names if they differ
- Link the LinkedIn credential in the "Publish on LinkedIn" node

## Run
- Manual: open the workflow → "Execute Workflow"
- Scheduled: enable the workflow toggle to run at the configured time

