#!/usr/bin/env python
"""PreToolUse guard: stop shell commands from reading credential files.

permissions.deny Read(...) rules cover the Read/Grep/Glob tools, but they do
not inspect shell commands -- `cat jira-xray-config.json` would sail straight
through. This hook closes that gap for the Bash/PowerShell tools.

Contract: reads the hook payload on stdin, denies the call when the command
names a credential file, unless the command is a vetted metadata-only probe.
Exit 0 always; the decision travels in the JSON on stdout.
"""
import json
import re
import sys

# Files whose CONTENTS must never reach the model.
CREDENTIAL_PATHS = [
    r"jira-xray-config\.json",
    r"agent-config\.json",
    r"\.env(?![A-Za-z0-9_-])",          # .env, .env.local, .env.example ...
    r"credentials?\.(json|ya?ml|ini|txt)",
    r"\.netrc",
    r"id_(rsa|ed25519|ecdsa)",
]

# Commands that may still mention those paths: they reveal existence and
# ignore-status only, never content. Anchored at the start of the command.
METADATA_ONLY = [
    r"^\s*ls(\s+-[A-Za-z]+)*\s",
    r"^\s*test\s+-[efrw]\s",
    r"^\s*stat\s",
    r"^\s*git\s+check-ignore\b",
    r"^\s*git\s+status\b",
    r"^\s*git\s+ls-files\b",
    # The vetted status probe: reports PLACEHOLDER/SET, never a value.
    r"^\s*python\s+(-I\s+)?[\"']?\.claude/hooks/check-credential-status\.py",
]

# Broad secret-harvesting shapes, regardless of filename.
HARVEST = [
    r"ATATT[A-Za-z0-9_=-]{8,}",
    r"rev-list\s+--all.*cat-file",
    r"(api[_-]?token|client[_-]?secret|password)\s*[:=]\s*[\"'][^\"'<]{12,}",
]


def deny(reason):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }))
    sys.exit(0)


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)  # Unparseable payload: stay out of the way.

    tool_input = payload.get("tool_input") or {}
    command = tool_input.get("command") or ""
    if not command:
        sys.exit(0)

    for pattern in HARVEST:
        if re.search(pattern, command, re.I):
            deny(
                "Blocked: this command matches a credential-harvesting shape. "
                "Ask the user to run it themselves if it is genuinely needed."
            )

    for pattern in CREDENTIAL_PATHS:
        if not re.search(pattern, command, re.I):
            continue
        if any(re.search(safe, command, re.I) for safe in METADATA_ONLY):
            sys.exit(0)  # Metadata probe: existence only, no content.
        deny(
            "Blocked by .claude/hooks/block-credential-reads.py: this command "
            "references a credential file. Claude must not read API keys or "
            "secrets. Automation scripts may still READ these files "
            "themselves -- just don't pipe their contents into the "
            "conversation. To check whether credentials are filled in, run: "
            "python .claude/hooks/check-credential-status.py"
        )

    sys.exit(0)


if __name__ == "__main__":
    main()
