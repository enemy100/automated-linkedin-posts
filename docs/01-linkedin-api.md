# LinkedIn OAuth2 in n8n – Quick Setup

You don’t need Python to authenticate. Use n8n’s built‑in LinkedIn OAuth2 credential and the LinkedIn node.

This follows the standard steps described in guides like this article: [LinkedIn Developer API](https://medium.com/@j622amilah/linkedin-developer-api-799f84e159ea).

## 1) Create a LinkedIn App (once)
- Go to: https://www.linkedin.com/developers/apps → Create app
- App name, logo, and company/page (if applicable)
- Products: enable Marketing Developer Platform (for posting)
- Note your Client ID and Client Secret
- Add an OAuth Redirect URL: `https://<your-n8n-host>/rest/oauth2-credential/callback`
  - Example (local dev): `http://localhost:5678/rest/oauth2-credential/callback`

## 2) Add the credential in n8n
- In n8n: Settings → Credentials → New → "LinkedIn OAuth2 API"
- Fill:
  - Client ID: from your LinkedIn App
  - Client Secret: from your LinkedIn App
  - OAuth Redirect URL: must match what you configured in LinkedIn (see above)
- Click "Connect" and complete the LinkedIn consent screen

That’s it. n8n stores the token and refreshes it when needed.

## 3) Use the LinkedIn node
- In your workflow (`n8n-workflows/linkedin-notion-posting.json`), open the "Publish on LinkedIn" node
- Select the LinkedIn credential you just created
- For text‑only posts: set `shareMediaCategory` to NONE
- For posts with image: set `shareMediaCategory` to IMAGE and `binaryPropertyName` to `data`

## Common issues
- 401/403: Re‑open the credential in n8n and re‑authorize
- Redirect URL mismatch: ensure the n8n callback URL exactly matches the one in your LinkedIn App
- Missing scope: ensure your app has Marketing Developer Platform and scope to post (`w_member_social`)

Links
- LinkedIn Developers: https://www.linkedin.com/developers
- n8n LinkedIn node: https://docs.n8n.io/integrations/builtin/app-nodes/n8n-nodes-base.linkedIn/
- Medium reference: [LinkedIn Developer API](https://medium.com/@j622amilah/linkedin-developer-api-799f84e159ea)

