---
name: n8n-workflow-generator
description: Generate a valid, importable n8n workflow JSON from a plain-English description of an automation. Use when the user describes something they want automated ("when X happens, do Y"), asks for an n8n workflow/flow, or wants to import a ready-made automation into n8n. Not for Zapier/Make-specific formats (different export schema) — use this skill's structure only for n8n.
---

# n8n Workflow Generator

Turn a plain-English automation request into a complete, structurally valid n8n workflow JSON file the user can import directly (Editor → ⋯ → Import from File, or paste via Import from Clipboard).

## When to use

- "I want an n8n workflow that does X when Y happens"
- "Automate [task] for me" where the user has (or plans to get) n8n
- "Turn this into an n8n flow"
- User pastes an existing n8n workflow and asks to extend, fix, or explain it

## Not for

- Zapier or Make.com native export formats — those use a different JSON/schema entirely. If the user wants one of those, say so and offer to describe the equivalent automation in plain steps instead, or build the n8n version.
- A generic "explain what n8n is" question — just answer it, no workflow needed.

## Input

Gather (ask only what's actually missing, don't interrogate for things you can reasonably infer):

1. **Trigger** — what starts it? A schedule, an incoming webhook/form, a new email, a manual run?
2. **The steps** — what should happen, in order? Where are branches/conditions?
3. **The systems involved** — Slack, Gmail, Google Sheets, a REST API, a database? (Determines which nodes are available — check `../../references/node-reference.md` before assuming a service has a node.)
4. **Any conditions** — does it only fire in some cases (severity, amount threshold, day of week)?

If the user's description leaves the trigger or the target system genuinely ambiguous (e.g. "notify me" — Slack? Email? Telegram?), ask one direct question rather than guessing. If it's a minor gap (exact webhook path name, exact cron time), make a sensible default and say what you defaulted to.

## Steps

1. **Read the reference docs first.** Before writing any JSON: read `../../references/node-reference.md` (the only node `type` strings you're allowed to use), `../../references/workflow-json-schema.md` (the exact structure), and `../../references/expressions-guide.md` (expression syntax) if the workflow needs any dynamic values.

2. **Sketch the node list on paper first, then wire it.** Decide: one trigger node, then each processing/action step as its own node, then any branches. Don't try to write the final JSON in one pass — get the node list and flow right first (even as a short bullet list to the user, "Trigger → Check severity → branch: critical→Slack, else→stop"), then translate to JSON.

3. **Assign positions.** Start the trigger at `[0, 0]`. Space each downstream node `+220` on the x-axis. When a node branches, offset the branches on the y-axis (e.g. `-80` for the "true"/primary path, `+80` or more for the alternate), per the convention in `workflow-json-schema.md`.

4. **Write the JSON.** Follow `workflow-json-schema.md` exactly for the top-level shape, node shape, and connections shape. Every `type` string must come from `node-reference.md` — if the automation needs an integration not on that list, tell the user plainly ("n8n's core Notion node isn't in my verified list — I'll use an HTTP Request node against Notion's API instead, or you can swap in n8n's Notion node yourself since the exact parameters for it aren't something I want to guess") rather than fabricating a node type or parameter shape.

5. **Handle credentials correctly.** Never invent or embed API keys, tokens, or credential objects. Leave credential-needing nodes without a `credentials` block and call out, in your explanation, exactly which node(s) need which credential type added inside n8n after import.

6. **Validate before handing it over.** Run the workflow JSON through `../../lib/validate_workflow.py` (or reproduce its checks manually if the tool isn't runnable in context) and fix anything it flags — a workflow that fails structural validation is not a finished deliverable.

7. **Ship it as a `.json` file**, not pasted inline as a giant code block in the chat — n8n imports files directly, and a file is easier for the user to actually use. Accompany it with:
   - A short plain-English walkthrough of what each node does, in order.
   - Exactly which credentials to add where, before activating.
   - Any assumption you made (field names guessed, a default schedule time, etc.) stated explicitly — never silently assumed.

## Hard rules

- Only use `type` strings verified in `node-reference.md`. Never invent a plausible-sounding node type or guess at one from a SaaS product's name.
- Every workflow must pass `lib/validate_workflow.py` before being handed to the user.
- Never embed real or placeholder credentials, tokens, or secrets in the JSON.
- Ship `"active": false` — let the user activate it themselves once credentials are wired up.
- Never invent a specific field name for incoming data (a webhook payload field, a spreadsheet column) that the user didn't state and that isn't a reasonable, clearly-flagged default — say when you're guessing.
- Don't pad a simple automation with unnecessary nodes to look more sophisticated. A two-node workflow (trigger + action) that correctly does what was asked beats a seven-node workflow with decorative branches.

## Anti-patterns (skill will refuse / avoid)

- A `type` string not in `node-reference.md`, invented from pattern-matching a service name.
- Connections wired by node `id` instead of `name`.
- A workflow with no trigger node and no note explaining it's meant to be manual-only.
- Hardcoded values (names, emails, amounts) where an expression referencing `$json` is clearly what's meant.
- A credentials object with fake/placeholder key values baked into the JSON.
- Handing over JSON that hasn't been checked against `validate_workflow.py`'s rules.

## Output shape

1. One-paragraph summary of the automation being built.
2. The workflow JSON as a `.json` file (not a giant inline block).
3. A numbered walkthrough: trigger → each node → what it does.
4. A short "Before you activate this" checklist: credentials to add, any placeholder values to replace (sheet IDs, channel names, webhook paths), and any assumptions made.

## Resources

- `../../references/node-reference.md` — the only allowed node `type` strings, with `typeVersion` and key parameters
- `../../references/workflow-json-schema.md` — exact top-level/node/connections structure, with the reasoning behind each field
- `../../references/expressions-guide.md` — `{{ }}` expression syntax and common variables
- `../../lib/validate_workflow.py` — structural validator; run it on every workflow before delivery
- `../../examples/webhook-to-slack-alert.json` — worked example: webhook trigger, IF branch, Set, Slack
- `../../examples/scheduled-invoice-reminder.json` — worked example: schedule trigger, Google Sheets read, Filter, Set, Gmail send

