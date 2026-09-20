# n8n-workflow-generator

A Claude skill that turns a plain-English description of an automation into a valid, importable [n8n](https://n8n.io) workflow JSON file — not a static template library, an actual generator that follows n8n's real node schema.

Describe what you want automated. Get back a `.json` file you can import straight into n8n, a plain-English walkthrough of what each node does, and a clear checklist of what credentials to add before you activate it.

## Why this is different from a template pack

Most "n8n templates" repos are a folder of pre-built JSON files for specific use cases — useful, but rigid. This repo ships a **skill**: Claude reads a verified reference of real n8n node types, the exact JSON structure n8n expects, and expression syntax, then builds a workflow shaped to what *you* actually described — instead of you searching for the closest pre-made template and hacking it to fit.

It also ships a real validator (`lib/validate_workflow.py`) so every generated workflow is checked for structural correctness (valid JSON, real node references, no dangling connections, a trigger present) before it's handed to you.

## Install

**Claude Code / Codex** (as a plugin):
```
/plugin marketplace add SidSharma010/n8n-workflow-generator
/plugin install n8n-workflow-generator
```

**claude.ai / Claude Desktop** (as a plugin marketplace): add this repo's URL as a marketplace source, then install `n8n-workflow-generator`.

**Any agent that reads SKILL.md files**: point it at `skills/n8n-workflow-generator/SKILL.md` directly.

## Usage

```
"Build me an n8n workflow: when a webhook receives an alert with
severity=critical, post it to #alerts on Slack. Otherwise do nothing."

"I need an n8n automation that checks a Google Sheet every morning
for unpaid invoices, and emails a reminder for anything overdue."

"Here's my existing n8n workflow JSON — add a step that also
logs each event to a Postgres table."
```

The skill will ask one direct question if something essential is genuinely ambiguous (which chat app for a notification, for example) — otherwise it builds, validates, and explains.

## Validating a workflow yourself

You don't need Claude to use the validator — it's a plain script:

```bash
python lib/validate_workflow.py path/to/workflow.json
```

```json
{
  "node_count": 5,
  "has_trigger": true,
  "issues": [],
  "passed": true
}
```

It checks: valid JSON, required top-level keys, every node has the required fields, node names are unique (connections are wired by name, not id), every connection points at a node that actually exists, at least one trigger node is present, and every node has a real `[x, y]` position.

It does **not** check whether your credentials are valid, whether an API field name is correct, or whether a referenced integration node is installed on your n8n instance — those need n8n itself.

## Repo structure

```
n8n-workflow-generator/
├── skills/
│   └── n8n-workflow-generator/
│       └── SKILL.md              # the skill Claude reads
├── references/
│   ├── node-reference.md         # verified list of real n8n node types + params
│   ├── workflow-json-schema.md   # exact JSON structure n8n expects
│   └── expressions-guide.md      # {{ }} expression syntax reference
├── lib/
│   └── validate_workflow.py      # structural validator, dependency-free
├── examples/
│   ├── webhook-to-slack-alert.json
│   └── scheduled-invoice-reminder.json
└── README.md
```

## Why this exists

Built after shipping [freelance-gig-skills](https://github.com/SidSharma010/freelance-gig-skills) and a fork of [linkedin-skills](https://github.com/SidSharma010/linkedin-skills) — same principle applied to a different problem: don't guess, don't fabricate, verify against a real reference before generating anything the user is going to actually run. A wrong node type or a broken connection in a workflow someone imports into their real n8n instance is a worse failure than a bland LinkedIn post, so this skill leans harder on validation than either of those two.

## Status

New, not yet used against a real n8n instance at volume. The two example workflows in `examples/` pass the validator and were checked by hand against n8n's actual node parameter shapes, but "does this import cleanly on every n8n version" hasn't been tested against a live instance. If you try it and something doesn't import right, that's useful signal — the reference docs are meant to be corrected, not treated as gospel.

## License

MIT — see [LICENSE](LICENSE).
