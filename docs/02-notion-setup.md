# Notion Setup – Content Database

Use Notion as the source of truth for articles and drafts that will be posted to LinkedIn.

## Required properties

| Property       | Type         | Purpose                                  |
|----------------|--------------|------------------------------------------|
| `Edition`      | Title        | Article/post title                        |
| `Created time` | Date         | Creation/publish date                     |
| `Source`       | Select       | Content source (feed/tag)                 |
| `Content`      | Rich text    | Full post content                         |
| `Tags`         | Multi‑select | Labels for channels/workflow              |
| `Keywords`     | Rich text    | Optional keywords/hashtags                |
| `flow_status`  | Multi‑select | Workflow status control                   |
| `Link`         | URL          | Original article link (optional)          |

Recommended values:
- Tags: include `LinkedIn` for channel selection
- flow_status: `NOT STARTED`, `START`, `DONE LINKEDIN`, `ERROR`

## Create the database

1) Create a new full‑page database in Notion (Table view)
2) Add the properties listed above
3) Share the database with your integration (Settings → Connections)

## API access (explicit steps)

- Create integration: https://www.notion.so/my-integrations → New integration → copy the token (`secret_...`)
- Share database with integration: open the DB → ••• (top right) → Connections → add your integration
- Get Database ID: open the DB and copy from the URL (or via “Copy link to view”); it’s the long ID in the URL
- Store both in n8n credentials (Notion API)

  <img width="1727" height="531" alt="image" src="https://github.com/user-attachments/assets/f97e4164-ec5a-4716-bbb7-f5c959fa63ee" />


## Example: create a page via API (Python)

```python
import requests, os
from datetime import datetime

NOTION_TOKEN = os.getenv('NOTION_API_TOKEN')
DATABASE_ID = os.getenv('NOTION_DATABASE_ID')

headers = {
  'Authorization': f'Bearer {NOTION_TOKEN}',
  'Notion-Version': '2022-06-28',
  'Content-Type': 'application/json',
}

data = {
  'parent': {'database_id': DATABASE_ID},
  'properties': {
    'Edition': {'title': [{'text': {'content': 'Sample article'}}]},
    'Created time': {'date': {'start': datetime.now().isoformat()}},
    'Source': {'select': {'name': 'GitHub Blog'}},
    'Content': {'rich_text': [{'text': {'content': 'Body...'}}]},
    'Tags': {'multi_select': [{'name': 'LinkedIn'}]},
    'flow_status': {'multi_select': [{'name': 'START'}]},
  }
}

r = requests.post('https://api.notion.com/v1/pages', headers=headers, json=data)
print(r.status_code, r.text)
```

## Query with filters

```python
query = {
  'filter': {
    'and': [
      {'property': 'Tags', 'multi_select': {'contains': 'LinkedIn'}},
      {'property': 'flow_status', 'multi_select': {'contains': 'START'}},
    ]
  },
  'page_size': 1
}

r = requests.post(
  f'https://api.notion.com/v1/databases/{DATABASE_ID}/query',
  headers=headers,
  json=query
)
print(r.status_code, len(r.json().get('results', [])))
```

## Status flow

```
NOT STARTED → START → DONE LINKEDIN
                └─(on error)→ ERROR
```

## Checklist

- [ ] Database created and shared with the integration
- [ ] Properties match the names used in the workflow
- [ ] Notion token stored in n8n credentials
- [ ] Database ID set in workflow/node configuration
- [ ] Test create/query/update calls succeed

