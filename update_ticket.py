import json
import urllib.request
import urllib.error
import base64
import re

def _load_env(path=".env.example"):
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

_ENV = _load_env()
EMAIL    = _ENV.get("JIRA_EMAIL", "")
TOKEN    = _ENV.get("JIRA_API_TOKEN", "")
BASE_URL = "https://amali-tech.atlassian.net"
CREDS    = base64.b64encode(f"{EMAIL}:{TOKEN}".encode()).decode()


def header_row(cols):
    return {
        "type": "tableRow",
        "content": [
            {
                "type": "tableHeader",
                "attrs": {},
                "content": [
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": c, "marks": [{"type": "strong"}]}],
                    }
                ],
            }
            for c in cols
        ],
    }


def bullet_list(items):
    return {
        "type": "bulletList",
        "content": [
            {
                "type": "listItem",
                "content": [
                    {"type": "paragraph", "content": [{"type": "text", "text": item}]}
                ],
            }
            for item in items
        ],
    }


def build_row(tc_id, title, precond, steps, expected):
    steps_lines = [
        re.sub(r"^\d+\.\s*", "", l.strip())
        for l in steps.strip().split("\n")
        if l.strip()
    ]
    return {
        "type": "tableRow",
        "content": [
            {
                "type": "tableCell",
                "attrs": {},
                "content": [
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": "Not Run"}],
                    }
                ],
            },
            {
                "type": "tableCell",
                "attrs": {},
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": tc_id,
                                "marks": [{"type": "code"}],
                            }
                        ],
                    }
                ],
            },
            {
                "type": "tableCell",
                "attrs": {},
                "content": [
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": title}],
                    }
                ],
            },
            {
                "type": "tableCell",
                "attrs": {},
                "content": [
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": precond}],
                    }
                ],
            },
            {
                "type": "tableCell",
                "attrs": {},
                "content": [
                    {
                        "type": "orderedList",
                        "content": [
                            {
                                "type": "listItem",
                                "content": [
                                    {
                                        "type": "paragraph",
                                        "content": [{"type": "text", "text": s}],
                                    }
                                ],
                            }
                            for s in steps_lines
                        ],
                    }
                ],
            },
            {
                "type": "tableCell",
                "attrs": {},
                "content": [
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": expected}],
                    }
                ],
            },
        ],
    }


TEST_CASES = [
    (
        "TC-DM-001",
        "Enable dark mode from profile or header",
        "User is logged in and on any page with the profile/header toggle visible",
        "1. Open the user profile or header menu\n2. Locate the dark mode toggle\n3. Turn on dark mode",
        "Dark mode activates immediately; UI switches to dark theme without page reload",
    ),
    (
        "TC-DM-002",
        "Verify dark mode on Dashboard",
        "Dark mode is enabled",
        "1. Navigate to the Dashboard",
        "Dashboard renders fully in dark theme with no light-mode elements",
    ),
    (
        "TC-DM-003",
        "Verify dark mode on Assessment screens",
        "Dark mode is enabled",
        "1. Navigate to an assessment screen",
        "Assessment screen renders fully in dark theme",
    ),
    (
        "TC-DM-004",
        "Verify dark mode on Admin pages",
        "Dark mode is enabled",
        "1. Navigate to an admin page",
        "Admin page renders fully in dark theme",
    ),
    (
        "TC-DM-005",
        "Verify dark mode on modals and dialogs",
        "Dark mode is enabled",
        "1. Open a modal or dialog from any page",
        "Modal or dialog renders in dark theme; no light-mode bleed",
    ),
    (
        "TC-DM-006",
        "Verify accessibility contrast in dark mode",
        "Dark mode is enabled",
        "1. Inspect text, icons, buttons, and interactive elements across dark theme pages\n2. Run a contrast-ratio check on key UI elements",
        "All UI elements meet WCAG AA contrast ratio >= 4.5:1",
    ),
    (
        "TC-DM-007",
        "Persist dark mode after page refresh",
        "Dark mode is enabled",
        "1. Refresh the browser page",
        "Dark mode remains active after refresh; preference is retained",
    ),
    (
        "TC-DM-008",
        "Persist dark mode across sessions",
        "Dark mode is enabled",
        "1. Sign out of the application\n2. Sign back in",
        "Dark mode preference is retained after sign-in",
    ),
    (
        "TC-DM-009",
        "Disable dark mode",
        "Dark mode is enabled",
        "1. Open the profile or header menu\n2. Turn off the dark mode toggle",
        "UI switches back to light theme immediately; toggle reflects off state",
    ),
]

adf_doc = {
    "type": "doc",
    "version": 1,
    "content": [
        {
            "type": "heading",
            "attrs": {"level": 2},
            "content": [{"type": "text", "text": "User Story"}],
        },
        {
            "type": "paragraph",
            "content": [
                {
                    "type": "text",
                    "text": "As a User, I want to switch to dark mode so that I can use the platform comfortably in low-light environments.",
                }
            ],
        },
        {
            "type": "heading",
            "attrs": {"level": 2},
            "content": [{"type": "text", "text": "Acceptance Criteria"}],
        },
        bullet_list(
            [
                "Toggle available in the user profile or header.",
                "Dark mode applies to: Dashboard, Assessment screens, Admin pages, Modals and dialogs.",
                "Dark mode respects accessibility standards (contrast ratio >= 4.5:1).",
                "User preference is stored and persists across sessions.",
                "Dark mode applies instantly without page reload.",
            ]
        ),
        {
            "type": "heading",
            "attrs": {"level": 2},
            "content": [{"type": "text", "text": "Test Cases for QA"}],
        },
        {
            "type": "table",
            "attrs": {"isNumberColumnEnabled": False, "layout": "full-width"},
            "content": [
                header_row(
                    ["Status", "ID", "Title", "Preconditions", "Steps", "Expected Result"]
                )
            ]
            + [build_row(*tc) for tc in TEST_CASES],
        },
        {
            "type": "heading",
            "attrs": {"level": 2},
            "content": [{"type": "text", "text": "Notes"}],
        },
        bullet_list(
            [
                "Status values: Not Run | Pass | Fail | Blocked",
                "Update the Status column as each test is executed.",
                "Log defects by linking a new bug issue to this ticket.",
            ]
        ),
    ],
}

payload = json.dumps({"fields": {"description": adf_doc}}).encode()
req = urllib.request.Request(
    f"{BASE_URL}/rest/api/3/issue/DK26-139",
    data=payload,
    method="PUT",
    headers={
        "Authorization": f"Basic {CREDS}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    },
)
try:
    resp = urllib.request.urlopen(req)
    print("SUCCESS - HTTP", resp.status)
    print("Ticket updated: https://amali-tech.atlassian.net/browse/DK26-139")
except urllib.error.HTTPError as e:
    body = e.read().decode()
    print("Error:", e.code, body[:600])
