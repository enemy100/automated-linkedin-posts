# n8n Setup – LinkedIn Posting with Optional Image Generation

This guide configures the provided n8n workflow (rob-linkedin.json) that:
- Pulls one item from Notion with flow_status START
- Aggregates the page content
- Rewrites the text for LinkedIn using an LLM
- (Optional) Generates an image from text using Freepik and resizes it
- Publishes on LinkedIn using the built‑in LinkedIn node (OAuth)
- Updates the Notion status to DONE LINKEDIN

## 1) Import the workflow

- In n8n, go to Workflows → Import from File
- Select `../n8n-workflows/rob-linkedin.json`

## 2) Configure credentials

- Notion API: Internal Integration token
- LinkedIn OAuth2: Connect the LinkedIn account you will post from
- (Optional) Freepik API: add header `x-freepik-api-key: <YOUR_KEY>` in the HTTP Request node

## 3) Node overview (matches rob-linkedin.json)

- Schedule Trigger: runs daily at a fixed hour (adjust to your timezone)
- Notion (Get All): databaseId = your content DB, filters: flow_status contains START, limit = 1
- Notion (Get): fetch the full page by URL
- Aggregate: combine Notion blocks into `property_content`
- Code (optional simple formatter): placeholder transformation
- LLM (rewrite article): cleans the text for LinkedIn (no code snippets)
- LinkedIn (Publish on LinkedIn): posts text, or text + image when binary `data` is present
- Notion (Update): sets flow_status → DONE LINKEDIN

Optional image branch:
- LLM (Basic LLM Chain): generate an English image prompt from the content
- HTTP Request (Freepik): text‑to‑image
- Convert to File: convert base64 to binary at `$binary.data`
- Edit Image (info + resize): constrain to ~1200x630 (LinkedIn friendly)
- Merge: merge the image branch with the text branch before LinkedIn publish

## 4) Property mapping and expectations

- Input Notion DB should contain:
  - `Name` (Title)
  - `property_content` (rich text/blocks aggregated by the workflow)
  - `Keywords` (optional)
  - `flow_status` (multi‑select with START / DONE LINKEDIN)
- The LinkedIn node uses:
  - Person (your profile URN) or choose via OAuth credential
  - Text from the rewritten content
  - Binary image at `$binary.data` (when available) → shareMediaCategory IMAGE

## 5) LinkedIn node configuration

- Use LinkedIn OAuth2 credential
- For text‑only posts:
  - `shareMediaCategory: NONE`
- For posts with image:
  - `shareMediaCategory: IMAGE`
  - `binaryPropertyName: data` (matches Convert to File output)

## 6) Notion update

- Final step updates the original page:
  - `flow_status` → `["DONE LINKEDIN"]`

## 7) Testing

- Execute node‑by‑node to validate each step
- Verify Aggregate output has a clean `property_content`
- If Freepik rate limits or fails, disable the image branch and test text‑only
- Re‑auth LinkedIn OAuth2 in n8n if posting fails with 401/403

## 8) Common tweaks

- Adjust the Schedule to your posting window
- Tune the rewrite prompt for tone and length
- Add UTM parameters to links (if you augment content with links)
- Add additional filters in Notion (e.g., tag = LinkedIn)

## 9) Going further

- Add Short.io to shorten links before posting
- Add error paths to set flow_status to ERROR and notify
- Split flows by channel (LinkedIn, X/Twitter, etc.)

