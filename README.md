# Automated LinkedIn Posts with n8n, GitHub Actions, and Notion

A complete, end-to-end example of automating LinkedIn posting using n8n, Notion as a content database, optional image generation, and CI automation with GitHub Actions.

## What you’ll build

- A Notion database to store articles and post drafts
- An n8n workflow that:
  - Fetches one item per run from Notion with status START
  - Aggregates page content and formats it
  - Optionally generates an image prompt (LLM) and an image (Freepik), resizes it, and attaches it
  - Publishes to LinkedIn via n8n’s LinkedIn node (OAuth)
  - Updates the Notion page status to DONE LINKEDIN
- Optional: a GitHub Actions workflow to trigger or run supporting scripts on a schedule

## Repository structure

```
automated-linkedin-posts/
├── README.md
├── docs/
│   ├── 01-linkedin-api.md            # LinkedIn API overview and posting
│   ├── 02-notion-setup.md            # Notion database schema and setup
│   ├── 03-n8n-setup.md               # n8n workflow setup (LinkedIn node + image)
│   ├── 04-github-actions.md          # Optional CI automation
│   └── 05-architecture.md            # High-level architecture (optional)
├── examples/
│   └── linkedin_poster.py            # Standalone Python example (optional)
├── n8n-workflows/
│   └── rob-linkedin.json             # Working n8n workflow you provided
└── config/
    ├── env.example                   # Example environment variables
    └── notion-schema.json            # Notion DB properties reference
```

## End-to-end flow

1. Source articles are inserted into Notion (manually or by a feeder script).
2. n8n (rob-linkedin.json) runs on a schedule:
   - Notion (Get All) → fetch 1 page filtered by flow_status contains START
   - Notion (Get) → fetch page content (blocks)
   - Aggregate → combine blocks into a single field (property_content)
   - LLM (rewrite) → clean up the text for LinkedIn
   - Optional branch for image:
     - LLM → generate image prompt
     - HTTP Request (Freepik) → text-to-image
     - Convert to File → base64 to binary
     - Edit Image → resize to LinkedIn-friendly size
     - Merge → join text and image branches
   - LinkedIn (Publish) → post using OAuth credentials
   - Notion (Update) → set flow_status to DONE LINKEDIN

## Prerequisites

- n8n instance (Docker or Cloud)
- A Notion workspace and an internal integration token
- A LinkedIn developer application and OAuth credentials (used by the n8n LinkedIn node)
- (Optional) Freepik API key for AI image generation
- (Optional) GitHub repository for CI/CD

## Setup (quick start)

1) Notion
- Create a database with the properties described in docs/02-notion-setup.md
- Share the database with your integration token

2) n8n
- Import n8n-workflows/rob-linkedin.json
- Configure credentials:
  - Notion API (internal token)
  - LinkedIn OAuth2 (account where you’ll post)
  - (Optional) Freepik API key for image generation
- Adjust database IDs, property names and any prompts as needed
- Enable the Schedule Trigger

3) LinkedIn
- The LinkedIn node in n8n uses OAuth2; complete the credential setup in n8n
- For manual or programmatic posting examples, see docs/01-linkedin-api.md

4) GitHub Actions (optional)
- See docs/04-github-actions.md if you want to trigger the n8n webhook or run helper scripts on a cron schedule

## Security

- Never commit secrets. Use env vars, n8n credentials, or GitHub Actions secrets
- Rotate tokens regularly
- Limit scopes to the minimum required (e.g., w_member_social for posting)

## Troubleshooting

- If LinkedIn posting fails in n8n: re-auth the LinkedIn OAuth credential in n8n
- If Notion nodes fail: verify integration access to the target database and property keys
- If image generation fails: temporarily disable the image branch and post text-only

## Credits

- Base flow inspired by your working n8n workflow (rob-linkedin.json)
- Image generation via Freepik API is optional and can be removed if you just want text posts

