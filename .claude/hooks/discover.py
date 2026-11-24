#!/usr/bin/env python
"""Read-only discovery: fetch a Jira story and map the Xray folder tree.

Writes nothing to Jira or Xray. Loads credentials from jira-xray-config.json
and never prints them.

Usage: python .claude/hooks/discover.py DK26-3007
"""
import base64
import json
import os
import sys
import urllib.error
import urllib.request

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
CONFIG = os.path.join(ROOT, "jira-xray-config.json")

with open(CONFIG, encoding="utf-8") as handle:
    CFG = json.load(handle)

JIRA_BASE = (CFG.get("jira", {}).get("base_url") or CFG.get("jira_base_url", "")).rstrip("/")
JIRA_EMAIL = CFG["jira"].get("email") or CFG["jira"].get("Email")
JIRA_TOKEN = CFG["jira"]["api_token"]
PROJECT_ID = CFG["jira"].get("project_id", "13358")
XRAY_AUTH = CFG["api"]["authentication_endpoint"]
XRAY_GQL = CFG["api"]["graphql_endpoint"]

JIRA_AUTH = base64.b64encode("{}:{}".format(JIRA_EMAIL, JIRA_TOKEN).encode()).decode()


def request(url, data=None, headers=None, method="GET"):
    req = urllib.request.Request(url, data=data, headers=headers or {}, method=method)
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            return json.loads(resp.read().decode("utf-8") or "{}")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", "replace")[:400]
        raise SystemExit("HTTP {} for {}\n{}".format(exc.code, url, body))


def adf_to_text(node, depth=0):
    """Flatten an Atlassian Document Format tree into readable text."""
    if not isinstance(node, dict):
        return ""
    out = []
    ntype = node.get("type")
    if ntype == "text":
        return node.get("text", "")
    content = node.get("content") or []
    inner = "".join(adf_to_text(c, depth + 1) for c in content)
    if ntype in ("paragraph", "heading"):
        prefix = "#" * node.get("attrs", {}).get("level", 0) + " " if ntype == "heading" else ""
        return prefix + inner + "\n"
    if ntype == "listItem":
        return "  " * max(depth - 1, 0) + "- " + inner.strip() + "\n"
    if ntype in ("bulletList", "orderedList"):
        return inner
    if ntype in ("tableRow",):
        cells = [adf_to_text(c, depth).strip().replace("\n", " ") for c in content]
        return "| " + " | ".join(cells) + " |\n"
    if ntype == "codeBlock":
        return "```\n" + inner + "\n```\n"
    if ntype == "hardBreak":
        return "\n"
    out.append(inner)
    return "".join(out)


def fetch_issue(key):
    url = "{}/rest/api/3/issue/{}".format(JIRA_BASE, key)
    return request(url, headers={
        "Authorization": "Basic " + JIRA_AUTH,
        "Accept": "application/json",
    })


def xray_token():
    body = json.dumps({
        "client_id": CFG["client_id"],
        "client_secret": CFG["client_secret"],
    }).encode()
    req = urllib.request.Request(XRAY_AUTH, data=body,
                                 headers={"Content-Type": "application/json"},
                                 method="POST")
    with urllib.request.urlopen(req, timeout=45) as resp:
        return resp.read().decode("utf-8").strip().strip('"')


def gql(query, token):
    body = json.dumps({"query": query}).encode()
    return request(XRAY_GQL, data=body, method="POST", headers={
        "Authorization": "Bearer " + token,
        "Content-Type": "application/json",
    })


def print_tree(node, indent=0):
    name = node.get("name", "?")
    count = node.get("testsCount")
    label = name if count is None else "{}  [{} tests]".format(name, count)
    print("   " * indent + ("- " if indent else "") + label)
    for child in node.get("folders") or []:
        print_tree(child, indent + 1)


def main():
    key = sys.argv[1] if len(sys.argv) > 1 else "DK26-3007"

    print("=" * 70)
    print("JIRA STORY:", key)
    print("=" * 70)
    issue = fetch_issue(key)
    fields = issue.get("fields", {})
    print("Summary     :", fields.get("summary"))
    print("Type        :", (fields.get("issuetype") or {}).get("name"))
    print("Status      :", (fields.get("status") or {}).get("name"))
    print("Issue id    :", issue.get("id"))
    parent = fields.get("parent")
    if parent:
        print("Parent      : {} - {}".format(
            parent.get("key"), (parent.get("fields") or {}).get("summary")))
    labels = fields.get("labels")
    if labels:
        print("Labels      :", ", ".join(labels))

    print("\n--- DESCRIPTION " + "-" * 54)
    desc = fields.get("description")
    print(adf_to_text(desc).strip() if desc else "(empty)")

    # Acceptance criteria often lives in a custom field; surface any that match.
    print("\n--- OTHER TEXT FIELDS " + "-" * 48)
    for fid, value in fields.items():
        if not fid.startswith("customfield_") or not value:
            continue
        text = adf_to_text(value).strip() if isinstance(value, dict) else (
            value.strip() if isinstance(value, str) else "")
        if len(text) > 25:
            print("[{}]\n{}\n".format(fid, text))

    print("=" * 70)
    print("XRAY FOLDER TREE (project {})".format(PROJECT_ID))
    print("=" * 70)
    token = xray_token()
    query = ('{ getFolder(projectId: "%s", path: "/") '
             '{ name path testsCount folders } }' % PROJECT_ID)
    resp = gql(query, token)
    if resp.get("errors"):
        print("GraphQL errors:", json.dumps(resp["errors"])[:500])
        return 1
    root = (resp.get("data") or {}).get("getFolder")
    if not root:
        print("No folder data returned.")
        return 1
    print_tree(root)
    return 0


if __name__ == "__main__":
    sys.exit(main())
