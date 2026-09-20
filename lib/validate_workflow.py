#!/usr/bin/env python3
"""
validate_workflow.py

Dependency-free structural validator for n8n workflow JSON exports.

This does NOT guarantee a workflow will run correctly inside n8n (it can't
check credentials, whether an API field name is right, or whether your
n8n instance has the referenced node type installed). What it DOES check
is the stuff that silently breaks an import or a run:

  - The file is valid JSON
  - Required top-level keys exist
  - Every node has the required fields (id, name, type, typeVersion,
    position, parameters)
  - Node names are unique (n8n uses names, not ids, to wire connections)
  - Every connection references a node name that actually exists in the
    workflow
  - At least one trigger-type node exists (a workflow with no trigger
    can only ever be run manually, which is fine for testing but is
    usually a sign a trigger node was forgotten)
  - Node positions are present and are 2-element [x, y] pairs (n8n's
    editor will silently stack nodes at 0,0 otherwise)

Usage:
    python validate_workflow.py path/to/workflow.json
    cat workflow.json | python validate_workflow.py
"""

import json
import sys

TRIGGER_TYPE_SUFFIXES = (
    "trigger",
    "webhook",
    "cron",
    "manualTrigger",
    "formTrigger",
    "errorTrigger",
)

REQUIRED_TOP_LEVEL_KEYS = ["name", "nodes", "connections"]
REQUIRED_NODE_KEYS = ["id", "name", "type", "typeVersion", "position", "parameters"]


def is_trigger_node(node_type: str) -> bool:
    lowered = node_type.lower()
    return any(suffix.lower() in lowered for suffix in TRIGGER_TYPE_SUFFIXES)


def check(data: dict) -> dict:
    issues = []

    # --- Top-level structure ---
    for key in REQUIRED_TOP_LEVEL_KEYS:
        if key not in data:
            issues.append(f"Missing required top-level key: '{key}'")

    nodes = data.get("nodes", [])
    connections = data.get("connections", {})

    if not isinstance(nodes, list):
        issues.append("'nodes' must be a list")
        nodes = []

    if not isinstance(connections, dict):
        issues.append("'connections' must be an object")
        connections = {}

    if not nodes:
        issues.append("Workflow has zero nodes")

    # --- Per-node checks ---
    seen_names = set()
    node_names = set()
    has_trigger = False

    for i, node in enumerate(nodes):
        label = node.get("name", f"<node at index {i}, no name>")

        if not isinstance(node, dict):
            issues.append(f"Node at index {i} is not an object")
            continue

        for key in REQUIRED_NODE_KEYS:
            if key not in node:
                issues.append(f"Node '{label}': missing required key '{key}'")

        name = node.get("name")
        if name:
            if name in seen_names:
                issues.append(f"Duplicate node name: '{name}' (connections are wired by name, so duplicates break routing)")
            seen_names.add(name)
            node_names.add(name)

        pos = node.get("position")
        if pos is not None:
            if not (isinstance(pos, list) and len(pos) == 2):
                issues.append(f"Node '{label}': 'position' must be a [x, y] pair, got {pos!r}")

        node_type = node.get("type", "")
        if node_type and is_trigger_node(node_type):
            has_trigger = True

        params = node.get("parameters")
        if params is not None and not isinstance(params, dict):
            issues.append(f"Node '{label}': 'parameters' must be an object")

    if not has_trigger:
        issues.append(
            "No trigger-type node found (webhook / schedule / manual / form / error trigger). "
            "The workflow can only be run manually from the editor."
        )

    # --- Connection checks ---
    for source_name, outputs in connections.items():
        if source_name not in node_names:
            issues.append(f"Connections reference unknown source node: '{source_name}'")
        if not isinstance(outputs, dict):
            issues.append(f"Connections for '{source_name}' must be an object keyed by output type (usually 'main')")
            continue
        for output_type, branches in outputs.items():
            if not isinstance(branches, list):
                continue
            for branch in branches:
                if not isinstance(branch, list):
                    continue
                for target in branch:
                    target_name = target.get("node") if isinstance(target, dict) else None
                    if target_name and target_name not in node_names:
                        issues.append(
                            f"Connection from '{source_name}' targets unknown node: '{target_name}'"
                        )

    return {
        "node_count": len(nodes),
        "has_trigger": has_trigger,
        "issues": issues,
        "passed": len(issues) == 0,
    }


def main():
    if len(sys.argv) > 1:
        with open(sys.argv[1], "r", encoding="utf-8") as f:
            raw = f.read()
    else:
        raw = sys.stdin.read()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        print(json.dumps({"passed": False, "issues": [f"Invalid JSON: {e}"]}, indent=2))
        sys.exit(1)

    result = check(data)
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()

