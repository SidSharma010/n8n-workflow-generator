# n8n expression syntax reference

n8n expressions let a parameter value be computed from data flowing through the workflow instead of being a hardcoded string. Any parameter field with the little "expression" (fx) toggle can hold one.

## Syntax

Wrap the expression in double curly braces, and prefix the *whole field value* with `=` when the field is otherwise a plain string field being set to an expression (this is how it appears in the raw JSON — see below):

```
{{ <expression> }}
```

In the **raw JSON**, a field that is "using an expression" is stored as a string starting with `=`:

```json
"value": "=Hi {{ $json.client_name }}, your invoice is due."
```

A field that is a **literal, non-expression** string has no leading `=`:

```json
"value": "Hi there, your invoice is due."
```

This distinction matters when generating JSON by hand — forgetting the leading `=` means n8n treats `{{ $json.client_name }}` as literal text to send, not something to evaluate.

## Core variables

| Expression | Refers to |
|---|---|
| `$json` | The current item's JSON data (from the immediately preceding node) |
| `$json.fieldName` | A specific field on the current item |
| `$node["Node Name"].json` | Data from a specific earlier node by name, not just the immediately previous one |
| `$now` | Current date/time (a Luxon DateTime object — e.g. `$now.toISODate()`) |
| `$today` | Today at midnight |
| `$workflow.id` / `$workflow.name` | Metadata about the running workflow |
| `$execution.id` | The current execution's id |
| `$itemIndex` | Index of the current item in the current batch |
| `$input.all()` | All items available to the current node |

## Common patterns

Interpolating a field into a string:
```
=Hello {{ $json.first_name }}, your order #{{ $json.order_id }} shipped.
```

Referencing an earlier node explicitly (needed once a workflow branches and merges, since `$json` only sees the immediately preceding node):
```
={{ $node["Webhook"].json.body.email }}
```

Conditional value inline (ternary):
```
={{ $json.amount > 1000 ? "high-value" : "standard" }}
```

Date formatting:
```
={{ $now.toFormat("dd LLL yyyy") }}
```

Default/fallback if a field might be missing:
```
={{ $json.nickname || $json.first_name }}
```

## Hard rules for generating expressions

- Never hardcode a value that should clearly come from the trigger/input data (an email, a name, an amount) — use `$json.<field>` for it instead of inventing a placeholder string.
- Don't guess a field name that wasn't given by the user or implied by the node before it. If the exact incoming field name is unknown (e.g. what a webhook's payload will actually contain), say so plainly in the explanation that ships with the workflow, and use a clearly-named placeholder like `$json.body.YOUR_FIELD_NAME_HERE` with a note, rather than silently inventing a specific name that will just be wrong.
- Always add the leading `=` on any field carrying an expression.
- Keep expressions readable — prefer several Set-node fields with simple expressions over one field with deeply nested ternaries.

