# n8n workflow JSON — structure reference

This is the shape n8n expects when you import a workflow (Editor → ⋯ → Import from File/URL, or paste into "Import from Clipboard"). Get this structure wrong and the import either fails outright or silently produces a broken workflow (nodes stacked on top of each other, connections that go nowhere).

## Top-level object

```json
{
  "name": "My Workflow",
  "nodes": [ /* array of node objects, see below */ ],
  "connections": { /* object, see below */ },
  "active": false,
  "settings": { "executionOrder": "v1" },
  "meta": { "notes": "optional, freeform, n8n ignores unknown keys here" }
}
```

- `name` — required, string. Shown in the n8n UI.
- `nodes` — required, array. Order in the array does not matter (position on canvas does, see below); execution order is driven by `connections`, not array order.
- `connections` — required, object. See "Connections" below.
- `active` — boolean. Always ship `false` for a template someone is about to import — importing with `active: true` on a workflow with a missing credential will fail to activate and can confuse the user. Let them activate it manually after wiring credentials.
- `settings.executionOrder` — set `"v1"` unless you have a specific reason not to (this is n8n's current default execution model).
- `id` — omit it in templates you hand to someone else. n8n assigns a new id on import; a hardcoded id can collide.

## Node object

```json
{
  "id": "e3b0c442-98fc-1c14-9afb-000000000001",
  "name": "Get Unpaid Invoices",
  "type": "n8n-nodes-base.googleSheets",
  "typeVersion": 4.5,
  "position": [220, 0],
  "parameters": { /* node-specific, see node-reference.md */ }
}
```

- `id` — a string, conventionally a UUID. n8n doesn't strictly validate the format, but keep it unique within the workflow. When generating a workflow, invent stable-looking UUIDs (don't reuse the same id twice).
- `name` — required, and **this is what connections reference, not `id`**. Must be unique within the workflow. Make it human-readable ("Post to Slack", not "Slack1") — the person importing the workflow reads these names in the canvas.
- `type` — the fully-qualified node type string, e.g. `n8n-nodes-base.webhook`. Get this wrong (typo, wrong casing, a node type that doesn't exist) and n8n shows the node as an unrecognized/red node on import. Only use types you actually know — see `node-reference.md` for a verified list. Never invent a plausible-sounding type string.
- `typeVersion` — a number (sometimes decimal, e.g. `3.4`). Each node type has its own version history; using an old version isn't fatal (n8n will run it) but using a version number that never existed for that node type can break the parameter schema. When unsure, use the version listed in `node-reference.md`.
- `position` — required, `[x, y]` pixel coordinates on the canvas. Missing this stacks every node at `[0,0]`, which still imports and runs but is unusable to look at. Convention used in this repo's examples: start the trigger at `[0, 0]` and space downstream nodes `~220px` apart on the x-axis; branch vertically (±80 to ±200 on y) for parallel paths.
- `parameters` — required, object. Shape is entirely node-type-specific (a Webhook node's parameters look nothing like a Slack node's). See `node-reference.md` for the common ones.

## Connections

Connections are keyed by the **source node's `name`** (not `id`), and describe where each output goes:

```json
"connections": {
  "Webhook": {
    "main": [
      [
        { "node": "Check Severity", "type": "main", "index": 0 }
      ]
    ]
  },
  "Check Severity": {
    "main": [
      [ { "node": "Format Slack Message", "type": "main", "index": 0 } ],
      [ { "node": "No Action Needed", "type": "main", "index": 0 } ]
    ]
  }
}
```

Reading this shape from the outside in:

1. `connections["Webhook"]` — everything wired to the Webhook node's outputs.
2. `"main"` — the connection type. Almost every node only has a `main` output. (A few nodes, like AI/LangChain-style nodes, have other types such as `ai_tool` or `ai_languageModel` — out of scope for this skill's default cases; flag it to the user rather than guessing.)
3. The array under `"main"` is **one entry per output socket** the node has. A Set node has one output socket → one array. An IF node has two output sockets (true branch, false branch) → two arrays, in that order. A Switch node has one array per case, in the order the cases are defined.
4. Each of those entries is itself an array of `{ "node", "type", "index" }` objects — this lets one output fan out to multiple downstream nodes (an array with more than one object), or go nowhere (an empty array `[]`, which is valid for e.g. a "false" branch you don't need to wire up).
5. `"index"` is almost always `0` — it's the **target's input index**, relevant only for nodes with multiple inputs (like Merge, which has 2).

### Common mistakes this causes if you get it wrong

- Using the node's `id` instead of `name` as the connections key or target → n8n shows the workflow with the node floating, disconnected.
- Wiring an IF node's two branches into a single one-item array instead of two separate arrays → both downstream nodes fire on the same branch.
- Forgetting a downstream node exists in `nodes` while still connecting to it → n8n rejects the import or shows a broken link (this is exactly what `lib/validate_workflow.py` in this repo catches automatically).

## Multi-input nodes (Merge)

A Merge node takes two inputs. Wire node A into its `index: 0` and node B into its `index: 1`:

```json
"connections": {
  "Fetch From API": {
    "main": [[ { "node": "Merge", "type": "main", "index": 0 } ]]
  },
  "Fetch From Sheet": {
    "main": [[ { "node": "Merge", "type": "main", "index": 1 } ]]
  }
}
```

## Credentials

Never embed real or fake credential values, tokens, or API keys in a workflow JSON you hand to someone. n8n workflows reference a credential **by name/id from the user's own n8n credential store** — it is not part of the portable JSON at all in any usable form. The correct pattern in a node's parameters is to leave credential-requiring fields either absent or referencing a placeholder, and tell the user in the accompanying explanation: "add your \[Slack / Gmail / Google Sheets] credential to this node after importing." See Hard rules in the skill's `SKILL.md`.

