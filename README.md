# Automated LinkedIn Posts with n8n and Notion

Minimal, production‑ready example to post on LinkedIn using n8n, Notion as content DB, and an optional GitHub Actions trigger.

## Quick start

1) Notion database
- Create a table with properties: `Edition` (Title), `Content` (Rich text), `flow_status` (Multi‑select: NOT STARTED, START, DONE LINKEDIN), and optional `Tags`, `Keywords`, `Link`.
- Add at least one item with `flow_status = START` for testing.

2) n8n
- Install n8n using your existing setup guide (you already have a working guide in your environment: `~/Downloads/GUIA_INICIO.md` and `n8n.yaml`).
- Import the workflow: `n8n-workflows/rob-linkedin.json`.
- Configure credentials:
  - Notion (Internal Integration token)
  - LinkedIn OAuth2 (see docs/01-linkedin-api.md; no Python needed)
  - (Optional) Freepik API for image generation
- Run once manually to test, then enable the schedule.

3) (Optional) GitHub Actions
- Use a webhook trigger to tell n8n to run on a schedule (docs/04-github-actions.md).

## Flow (rob-linkedin.json)
- Schedule Trigger → Notion (Get All, 1 page, `START`) → Notion (Get) → Aggregate blocks
- LLM rewrite (clean text for LinkedIn)
- Optional image: LLM prompt → Freepik → convert base64 → resize → merge
- LinkedIn node publishes using your OAuth2 credential
- Notion status set to `DONE LINKEDIN`

## Docs
- LinkedIn OAuth2 in n8n: `docs/01-linkedin-api.md`
- Notion setup: `docs/02-notion-setup.md`
- n8n setup (import + minimal config): `docs/03-n8n-setup.md`
- GitHub Actions (optional): `docs/04-github-actions.md`

## Security
- Never commit secrets or `.env`
- Store credentials in n8n and GitHub Secrets
- Ensure the LinkedIn redirect URL matches your n8n callback

## Troubleshooting
- 401/403 on LinkedIn: re‑authorize LinkedIn credential in n8n
- Notion errors: check DB ID, property names, and integration access
- Image errors: disable the image branch and test text‑only first

