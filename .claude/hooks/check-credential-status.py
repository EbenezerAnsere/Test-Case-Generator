#!/usr/bin/env python
"""Report whether credentials are filled in -- never what they are.

Prints one line per field: EMPTY, PLACEHOLDER, or SET (<n> chars). This is the
only sanctioned way for Claude to inspect the credential file; the PreToolUse
guard allowlists exactly this command. It deliberately has no flag that would
print a value.
"""
import json
import os
import re
import sys

CONFIG = os.path.join(os.path.dirname(__file__), "..", "..", "jira-xray-config.json")

FIELDS = [
    ("jira.api_token", ("jira", "api_token")),
    ("client_id", ("client_id",)),
    ("client_secret", ("client_secret",)),
]


def dig(obj, path):
    for key in path:
        if not isinstance(obj, dict):
            return ""
        obj = obj.get(key, "")
    return obj if isinstance(obj, str) else ""


def classify(value):
    if not value:
        return "EMPTY"
    if re.fullmatch(r"<[A-Z_]+>", value) or value.lower().startswith("your-"):
        return "PLACEHOLDER"
    return "SET ({} chars)".format(len(value))


def main():
    try:
        with open(CONFIG, encoding="utf-8") as handle:
            config = json.load(handle)
    except FileNotFoundError:
        print("jira-xray-config.json: NOT FOUND")
        return 1
    except json.JSONDecodeError as exc:
        print("jira-xray-config.json: INVALID JSON ({})".format(exc.msg))
        return 1

    statuses = [(label, classify(dig(config, path))) for label, path in FIELDS]
    for label, status in statuses:
        print("{:<16} {}".format(label, status))

    ready = all(status.startswith("SET") for _, status in statuses)
    print("-" * 34)
    print("READY TO RUN:", "yes" if ready else "no")
    return 0


if __name__ == "__main__":
    sys.exit(main())
