"""
fetch_story.py — Pull a Jira story and dump what's needed for test case generation.

Usage:
    python fetch_story.py --issue DK26-XXX

Outputs:
    DK26-XXX_story.json   — story summary, user story text, acceptance criteria
    (printed to console as well so you can review immediately)
"""

import argparse
import base64
import io
import json
import sys
import urllib.request
import urllib.error

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# ── credentials ──────────────────────────────────────────────────────────────
def load_env(path=".env.example"):
    env = {}
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, _, v = line.partition("=")
                    env[k.strip()] = v.strip()
    except FileNotFoundError:
        pass
    return env

ENV        = load_env()
JIRA_BASE  = "https://amali-tech.atlassian.net"
JIRA_CREDS = base64.b64encode(
    f"{ENV.get('JIRA_EMAIL','')}:{ENV.get('JIRA_API_TOKEN','')}".encode()
).decode()


def jira_get(path):
    req = urllib.request.Request(
        f"{JIRA_BASE}{path}",
        headers={"Authorization": f"Basic {JIRA_CREDS}", "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


# ── ADF helpers ───────────────────────────────────────────────────────────────
def adf_to_text(node):
    if not node:
        return ""
    t = node.get("type", "")
    if t == "text":
        return node.get("text", "")
    sep = "\n" if t in ("paragraph","heading","listItem","bulletList","orderedList") else " "
    return sep.join(adf_to_text(c) for c in node.get("content", []) if adf_to_text(c))


def extract_section(content_blocks, heading_keyword):
    """Return text blocks that follow a heading containing heading_keyword."""
    capture = False
    results = []
    for node in content_blocks:
        t = node.get("type", "")
        if t == "heading":
            capture = heading_keyword.lower() in adf_to_text(node).lower()
            continue
        if capture:
            if t == "heading":
                break
            txt = adf_to_text(node).strip()
            if txt:
                results.append(txt)
    return results


def extract_list_items(content_blocks, heading_keyword):
    """Return individual bullet/ordered list items under a heading."""
    capture = False
    items = []
    for node in content_blocks:
        t = node.get("type", "")
        if t == "heading":
            capture = heading_keyword.lower() in adf_to_text(node).lower()
            continue
        if capture:
            if t == "heading":
                break
            if t in ("bulletList", "orderedList"):
                for li in node.get("content", []):
                    txt = adf_to_text(li).strip()
                    if txt:
                        items.append(txt)
    return items


# ── main ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--issue", required=True, help="Jira story key e.g. DK26-200")
    args = parser.parse_args()
    key = args.issue.upper()

    print(f"Fetching {key} from Jira...")
    ticket  = jira_get(f"/rest/api/3/issue/{key}")
    fields  = ticket.get("fields", {})
    summary = fields.get("summary", "")
    desc    = fields.get("description") or {}
    blocks  = desc.get("content", [])

    user_story = " ".join(extract_section(blocks, "user story")) or summary
    ac_items   = extract_list_items(blocks, "acceptance criteria")

    # fallback: if no structured AC found, grab all bullet items
    if not ac_items:
        for node in blocks:
            if node.get("type") in ("bulletList", "orderedList"):
                for li in node.get("content", []):
                    txt = adf_to_text(li).strip()
                    if txt:
                        ac_items.append(txt)

    output = {
        "issue_key": key,
        "summary":   summary,
        "jira_id":   ticket.get("id"),
        "user_story": user_story,
        "acceptance_criteria": ac_items,
        "testcases_file": f"{key}_tests.json",
    }

    out_file = f"{key}_story.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    # ── pretty print for review ───────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"  {key}: {summary}")
    print(f"{'='*60}")
    print(f"\nUser Story:\n  {user_story}")
    print(f"\nAcceptance Criteria ({len(ac_items)} items):")
    for i, a in enumerate(ac_items, 1):
        print(f"  {i}. {a}")
    print(f"\nSaved to: {out_file}")
    print(f"\nNext step — Claude will read this file and generate {key}_tests.json")
    print(f"Then run:  python upload_xray.py --issue {key}")


if __name__ == "__main__":
    main()
