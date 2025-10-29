# n8n Setup – Minimal Steps

Already have n8n running? Skip to Import Workflow.

If you need installation, use your existing guide (Docker/Cloudflare/Traefik). For reference in this environment you have a full guide at `~/Downloads/GUIA_INICIO.md` and `n8n.yaml`.

## Import Workflow
- In n8n, go to Workflows → Import from File
- Select `../n8n-workflows/rob-linkedin.json`
- Save

## Credentials to configure
- Notion API → Internal Integration token
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

