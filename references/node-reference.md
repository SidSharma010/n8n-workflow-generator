# n8n node reference — the "safe list"

Only use node `type` strings from this list when generating a workflow. If the automation needs a node not covered here (a specific SaaS integration like HubSpot, Notion, Stripe, etc.), say so explicitly to the user instead of guessing a plausible-looking type string — n8n has hundreds of integration nodes and a wrong guess produces a workflow that looks right and fails on import. The user can also always swap in a **Code** or **HTTP Request** node to call any API directly, which covers the gap for almost anything.

Every entry below is a real, current n8n core node. `typeVersion` is the latest stable version as of this reference — use it unless the user's n8n instance is known to be older.

## Triggers (a workflow needs exactly one, usually)

| Node | `type` | `typeVersion` | What it's for |
|---|---|---|---|
| Manual Trigger | `n8n-nodes-base.manualTrigger` | 1 | "Click to run" — testing, or workflows only ever run by hand |
| Webhook | `n8n-nodes-base.webhook` | 2 | Fires when an HTTP request hits n8n's URL for this node. Key params: `path`, `httpMethod`, `responseMode` |
| Schedule Trigger | `n8n-nodes-base.scheduleTrigger` | 1.2 | Cron-style recurring runs. Params: `rule.interval[].field` (`cronExpression`, `days`, `hours`, etc.) |
| Form Trigger | `n8n-nodes-base.formTrigger` | 2.2 | Generates a hosted web form; fires on submit |
| Email Trigger (IMAP) | `n8n-nodes-base.emailReadImap` | 2.1 | Fires on new email in an inbox |
| Error Trigger | `n8n-nodes-base.errorTrigger` | 1 | Fires when another workflow in the same instance fails — used to build an alerting workflow |

## Flow control / logic

| Node | `type` | `typeVersion` | What it's for |
|---|---|---|---|
| IF | `n8n-nodes-base.if` | 2 | Two-way branch (true/false) on a condition. Params: `conditions.conditions[]` with `leftValue`, `rightValue`, `operator` |
| Switch | `n8n-nodes-base.switch` | 3 | Multi-way branch by matching a value against several cases |
| Filter | `n8n-nodes-base.filter` | 2.2 | Drops items that don't match a condition (single output, unlike IF) |
| Merge | `n8n-nodes-base.merge` | 3 | Combines two input branches (append, or match by field) |
| Wait | `n8n-nodes-base.wait` | 1.1 | Pauses the workflow for a duration or until a webhook resumes it |
| No Operation (NoOp) | `n8n-nodes-base.noOp` | 1 | Does nothing — useful as an explicit "end of branch" node so a diagram reads cleanly |
| Split In Batches (Loop) | `n8n-nodes-base.splitInBatches` | 3 | Iterates over items in chunks |

## Data shaping

| Node | `type` | `typeVersion` | What it's for |
|---|---|---|---|
| Edit Fields (Set) | `n8n-nodes-base.set` | 3.4 | Add/rename/transform fields on each item. Params: `assignments.assignments[]` with `name`, `type`, `value` |
| Code | `n8n-nodes-base.code` | 2 | Arbitrary JavaScript (or Python, on n8n Cloud/certain setups) for logic the built-in nodes can't express. Params: `jsCode`, `mode` (`runOnceForAllItems` / `runOnceForEachItem`) |
| Item Lists | `n8n-nodes-base.itemLists` | 3.1 | Sort, dedupe, split/aggregate arrays |
| Aggregate | `n8n-nodes-base.aggregate` | 1 | Combine many items into one item with an array field |
| Date & Time | `n8n-nodes-base.dateTime` | 2 | Format/parse/shift dates |

## HTTP / generic

| Node | `type` | `typeVersion` | What it's for |
|---|---|---|---|
| HTTP Request | `n8n-nodes-base.httpRequest` | 4.2 | Call any REST API. Params: `method`, `url`, `sendHeaders`/`headerParameters`, `sendBody`/`bodyParameters` or `jsonBody`, `authentication` |

## Common integrations (verified core-node names — use only these; anything else, flag to the user)

| Node | `type` | `typeVersion` | Notes |
|---|---|---|---|
| Slack | `n8n-nodes-base.slack` | 2.2 | `resource: message`, `operation: post` is the common case |
| Gmail | `n8n-nodes-base.gmail` | 2.1 | `resource: message`, `operation: send` |
| Google Sheets | `n8n-nodes-base.googleSheets` | 4.5 | `operation`: `read` / `append` / `update` / `delete` |
| Google Drive | `n8n-nodes-base.googleDrive` | 3 | File operations |
| Google Calendar | `n8n-nodes-base.googleCalendar` | 1.3 | Event CRUD |
| Telegram | `n8n-nodes-base.telegram` | 1.2 | `resource: message`, `operation: sendMessage` |
| Discord | `n8n-nodes-base.discord` | 2 | `resource: message`, `operation: send` |
| Airtable | `n8n-nodes-base.airtable` | 2.1 | `operation`: `search` / `create` / `update` / `delete` |
| Postgres | `n8n-nodes-base.postgres` | 2.5 | `operation: executeQuery` for raw SQL |
| MySQL | `n8n-nodes-base.mySql` | 2.4 | Same pattern as Postgres |
| Notion | `n8n-nodes-base.notion` | 2.2 | Resource-based (`page`, `database`, `block`) |
| Twilio | `n8n-nodes-base.twilio` | 1 | SMS/WhatsApp send |

## What NOT to do

- Do not invent a `type` string for an integration not listed here (e.g. don't guess `n8n-nodes-base.hubspot` or `n8n-nodes-base.stripe` from pattern-matching — verify first, or substitute an **HTTP Request** node against that service's REST API and say so).
- Do not use a `typeVersion` you're not confident is real for that node — when unsure, use the version in this table.
- Do not fabricate node `parameters` for a real node type you're unsure about — check this table's "notes" and the workflow-json-schema.md conventions first; if a parameter's exact key name isn't known, prefer a Set/Code node for that piece of logic instead of guessing a parameter name that silently gets ignored by n8n.

