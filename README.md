# Automated LinkedIn Posts with n8n and Notion

Minimal, production‑ready example to post on LinkedIn using n8n, Notion as content DB, and a GitHub Actions trigger to extract content from external sites.

## Quick start (visual)

| Step | Area | What to do | Where |
|------|------|------------|-------|
| 1 | n8n install | Deploy n8n (Docker/Cloudflare Tunnel) | [n8n setup repo](https://github.com/enemy100/n8n-setup-on-raspberry-with-cloudflare-tunnel)
| 2 | Notion | Create DB and properties (`Edition`, `Content`, `flow_status`, …) | docs/02-notion-setup.md |
| 3 | Credentials | Add Notion token + LinkedIn OAuth2 in n8n | docs/01-linkedin-api.md |
| 4 | Workflow | Import `n8n-workflows/linkedin-notion-posting.json` | n8n → Workflows → Import |
| 5 | Extraction | Configure GitHub Actions to extract content and/or trigger n8n | docs/04-github-actions.md |
| 6 | Test | Put an item with `flow_status = START` in Notion and run once | n8n → Execute Workflow |
| 7 | Schedule | Enable the workflow to post daily | n8n → Toggle On |

## Flow overview (diagram)

```
┌────────────────────────────────────────────────────────────────────┐
│                          Content Extraction                         │
│  GitHub Actions (feeds) → Notion DB item (flow_status = START)      │
└────────────────────────────────────────────────────────────────────┘
                     │
                     ▼ (scheduled or manual run)
┌────────────────────────────────────────────────────────────────────┐
│                              n8n                                    │
│  1) Notion (Get All: 1 item with START)                             │
│  2) Notion (Get: fetch blocks)                                      │
│  3) Aggregate blocks → property_content                              │
│  4) LLM rewrite → clean LinkedIn text                                │
│  5) [Optional] Image branch:                                         │
│     LLM prompt → Freepik → base64→binary → resize (≈1200×630)        │
│  6) LinkedIn node → publish (OAuth2 credential)                      │
│  7) Notion (Update) → flow_status = DONE LINKEDIN                    │
└────────────────────────────────────────────────────────────────────┘
                     │
                     ▼
                 LinkedIn Post
```

## Setup pointers

- n8n install: use your repository here → [n8n setup repo](https://github.com/enemy100/n8n-setup-on-raspberry-with-cloudflare-tunnel)
- LinkedIn OAuth2 in n8n (no Python needed): `docs/01-linkedin-api.md`
- Notion DB schema: `docs/02-notion-setup.md`
- Import + minimal n8n config: `docs/03-n8n-setup.md`
- GitHub Actions for extraction/trigger: `docs/04-github-actions.md`

## Security
- Never commit secrets or `.env`
- Store credentials in n8n and GitHub Secrets
- Ensure the LinkedIn redirect URL matches your n8n callback

## Troubleshooting
- 401/403 on LinkedIn: re‑authorize LinkedIn credential in n8n
- Notion errors: check DB ID, property names, and integration access
- Image errors: disable the image branch and test text‑only first

