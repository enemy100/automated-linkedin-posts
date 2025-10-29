# LinkedIn API – Authentication and Posting

This repo primarily uses the n8n LinkedIn node (OAuth2) to publish. This document provides:
- A quick overview of LinkedIn OAuth2
- A minimal Python example for reference/testing
- Notes to align with the n8n LinkedIn node

## OAuth2 overview

Basic flow:
1) User visits LinkedIn authorization URL (scopes include `w_member_social`)
2) After consent, LinkedIn redirects with a one‑time `code`
3) Exchange `code` for an `access_token`
4) Use Bearer token to call LinkedIn APIs

In n8n, this is handled for you by the LinkedIn OAuth2 credential. Open the credential, complete the consent flow, and n8n stores the token.

## Python reference (optional)

```python
import requests

CLIENT_ID = '...'
CLIENT_SECRET = '...'
REDIRECT_URI = 'https://yourapp.com/callback'

# Authorization URL to open in a browser
auth_url = (
  'https://www.linkedin.com/oauth/v2/authorization?'
  f'response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}'
  '&state=xyz&scope=r_liteprofile%20w_member_social'
)
print(auth_url)

# After getting ?code=..., exchange for token
r = requests.post('https://www.linkedin.com/oauth/v2/accessToken', data={
  'grant_type': 'authorization_code',
  'code': 'CODE_FROM_CALLBACK',
  'redirect_uri': REDIRECT_URI,
  'client_id': CLIENT_ID,
  'client_secret': CLIENT_SECRET,
})
print(r.status_code, r.json())
```

## Posting UGC (reference)

n8n’s LinkedIn node abstracts this, but for reference:

```python
import requests

def post_text(access_token, person_id, text):
  url = 'https://api.linkedin.com/v2/ugcPosts'
  headers = {
    'Authorization': f'Bearer {access_token}',
    'Content-Type': 'application/json',
    'X-Restli-Protocol-Version': '2.0.0',
  }
  body = {
    'author': f'urn:li:person:{person_id}',
    'lifecycleState': 'PUBLISHED',
    'specificContent': {
      'com.linkedin.ugc.ShareContent': {
        'shareCommentary': {'text': text},
        'shareMediaCategory': 'NONE',
      }
    },
    'visibility': {'com.linkedin.ugc.MemberNetworkVisibility': 'PUBLIC'}
  }
  r = requests.post(url, headers=headers, json=body)
  print(r.status_code, r.text)
```

## Using n8n’s LinkedIn node

- Add credential: LinkedIn OAuth2 → connect the account
- For text‑only posts:
  - `shareMediaCategory`: NONE
- For posts with image:
  - `shareMediaCategory`: IMAGE
  - `binaryPropertyName`: data (ensure a `$binary.data` exists upstream)
- Person/Page selection: choose the identity you’re posting as (your profile or a page)

## Scopes and limits

- Scopes: `w_member_social` required for posting to a member profile
- Rate limits: expect standard LinkedIn API rate limiting; handle retries or backoff in your workflow

## Links

- LinkedIn API docs: https://learn.microsoft.com/en-us/linkedin/
- UGC Post API: https://learn.microsoft.com/en-us/linkedin/marketing/integrations/community-management/shares/ugc-post-api
- n8n LinkedIn node: https://docs.n8n.io/integrations/builtin/app-nodes/n8n-nodes-base.linkedIn/

