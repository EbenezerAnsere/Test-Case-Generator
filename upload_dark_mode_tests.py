"""
Full Xray upload for DK26-139 Dark Mode:
  1. Create 9 Jira Test issues
  2. Xray-authenticate
  3. Create folder Quarter 2/Frontend/Ebenezer/DK26-139 SP3: Q1-3. Dark Mode
  4. Create Test Set and add all tests
  5. Link tests + Test Set to Test Plan DK26-118
  6. Link tests + Test Set to Test Execution DK26-195
"""

import base64
import io
import json
import sys
import urllib.error
import urllib.parse
import urllib.request

# force UTF-8 output on Windows so Unicode chars don't crash
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

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

# ── credentials ────────────────────────────────────────────────────────────────
JIRA_EMAIL         = _ENV.get("JIRA_EMAIL", "")
JIRA_TOKEN         = _ENV.get("JIRA_API_TOKEN", "")
XRAY_CLIENT_ID     = _ENV.get("XRAY_CLIENT_ID", "")
XRAY_CLIENT_SECRET = _ENV.get("XRAY_CLIENT_SECRET", "")

# ── project constants ───────────────────────────────────────────────────────────
JIRA_BASE      = "https://amali-tech.atlassian.net"
XRAY_AUTH_URL  = "https://xray.cloud.getxray.app/api/v2/authenticate"
XRAY_GRAPHQL   = "https://xray.cloud.getxray.app/api/v2/graphql"
PROJECT_KEY    = "DK26"
PROJECT_ID     = "13358"
STORY_KEY      = "DK26-139"
STORY_SUMMARY  = "SP3: Q1-3. Dark Mode"
PARENT_PATH    = "Quarter 2/Frontend/Ebenezer"
FOLDER_NAME    = f"{STORY_KEY} {STORY_SUMMARY}"
FOLDER_PATH    = f"{PARENT_PATH}/{FOLDER_NAME}"
TEST_PLAN_KEY  = "DK26-118"
TEST_EXEC_KEY  = "DK26-195"

# ── test case definitions ───────────────────────────────────────────────────────
TEST_CASES = [
    {
        "id":           "TC-DM-001",
        "summary":      "Enable dark mode from profile or header",
        "preconditions":"User is logged in and on any page with the profile/header toggle visible",
        "steps":        ["Open the user profile or header menu", "Locate the dark mode toggle", "Turn on dark mode"],
        "expected":     "Dark mode activates immediately; UI switches to dark theme without page reload",
    },
    {
        "id":           "TC-DM-002",
        "summary":      "Verify dark mode on Dashboard",
        "preconditions":"Dark mode is enabled",
        "steps":        ["Navigate to the Dashboard"],
        "expected":     "Dashboard renders fully in dark theme with no light-mode elements",
    },
    {
        "id":           "TC-DM-003",
        "summary":      "Verify dark mode on Assessment screens",
        "preconditions":"Dark mode is enabled",
        "steps":        ["Navigate to an assessment screen"],
        "expected":     "Assessment screen renders fully in dark theme",
    },
    {
        "id":           "TC-DM-004",
        "summary":      "Verify dark mode on Admin pages",
        "preconditions":"Dark mode is enabled",
        "steps":        ["Navigate to an admin page"],
        "expected":     "Admin page renders fully in dark theme",
    },
    {
        "id":           "TC-DM-005",
        "summary":      "Verify dark mode on modals and dialogs",
        "preconditions":"Dark mode is enabled",
        "steps":        ["Open a modal or dialog from any page"],
        "expected":     "Modal or dialog renders in dark theme; no light-mode bleed",
    },
    {
        "id":           "TC-DM-006",
        "summary":      "Verify accessibility contrast in dark mode",
        "preconditions":"Dark mode is enabled",
        "steps":        [
            "Inspect text, icons, buttons, and interactive elements across dark theme pages",
            "Run a contrast-ratio check on key UI elements",
        ],
        "expected":     "All UI elements meet WCAG AA contrast ratio >= 4.5:1",
    },
    {
        "id":           "TC-DM-007",
        "summary":      "Persist dark mode after page refresh",
        "preconditions":"Dark mode is enabled",
        "steps":        ["Refresh the browser page"],
        "expected":     "Dark mode remains active after refresh; preference is retained",
    },
    {
        "id":           "TC-DM-008",
        "summary":      "Persist dark mode across sessions",
        "preconditions":"Dark mode is enabled",
        "steps":        ["Sign out of the application", "Sign back in"],
        "expected":     "Dark mode preference is retained after sign-in",
    },
    {
        "id":           "TC-DM-009",
        "summary":      "Disable dark mode",
        "preconditions":"Dark mode is enabled",
        "steps":        ["Open the profile or header menu", "Turn off the dark mode toggle"],
        "expected":     "UI switches back to light theme immediately; toggle reflects off state",
    },
]

# ── helpers ─────────────────────────────────────────────────────────────────────
JIRA_CREDS = base64.b64encode(f"{JIRA_EMAIL}:{JIRA_TOKEN}".encode()).decode()
_xray_token = None


def jira_request(method, path, body=None):
    url = f"{JIRA_BASE}{path}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        url, data=data, method=method,
        headers={"Authorization": f"Basic {JIRA_CREDS}",
                 "Content-Type": "application/json",
                 "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            raw = r.read().decode()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Jira {method} {path} -> HTTP {e.code}: {e.read().decode()[:400]}")


def xray_token():
    global _xray_token
    if _xray_token:
        return _xray_token
    body = json.dumps({"client_id": XRAY_CLIENT_ID, "client_secret": XRAY_CLIENT_SECRET}).encode()
    req = urllib.request.Request(
        XRAY_AUTH_URL, data=body, method="POST",
        headers={"Content-Type": "application/json", "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        raw = r.read().decode().strip().strip('"')
    _xray_token = raw
    return _xray_token


def gql(query):
    body = json.dumps({"query": query}).encode()
    req = urllib.request.Request(
        XRAY_GRAPHQL, data=body, method="POST",
        headers={"Authorization": f"Bearer {xray_token()}",
                 "Content-Type": "application/json",
                 "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Xray GraphQL error: HTTP {e.code}: {e.read().decode()[:400]}")


def adf_description(preconditions, steps, expected):
    return {
        "type": "doc", "version": 1,
        "content": [
            {"type": "heading", "attrs": {"level": 3},
             "content": [{"type": "text", "text": "Preconditions"}]},
            {"type": "paragraph",
             "content": [{"type": "text", "text": preconditions}]},
            {"type": "heading", "attrs": {"level": 3},
             "content": [{"type": "text", "text": "Steps"}]},
            {"type": "orderedList", "content": [
                {"type": "listItem",
                 "content": [{"type": "paragraph",
                              "content": [{"type": "text", "text": s}]}]}
                for s in steps
            ]},
            {"type": "heading", "attrs": {"level": 3},
             "content": [{"type": "text", "text": "Expected Result"}]},
            {"type": "paragraph",
             "content": [{"type": "text", "text": expected}]},
        ],
    }


# ── step 1: create Jira Test issues ─────────────────────────────────────────────
print("=" * 60)
print("STEP 1 — Creating Jira Test issues")
print("=" * 60)

created_issues = []  # {key, id, tc_id}

for tc in TEST_CASES:
    issue_summary = f"[{tc['id']}] {tc['summary']}"
    payload = {
        "fields": {
            "project":     {"key": PROJECT_KEY},
            "summary":     issue_summary,
            "issuetype":   {"name": "Test Cases"},
            "description": adf_description(tc["preconditions"], tc["steps"], tc["expected"]),
        }
    }
    try:
        resp = jira_request("POST", "/rest/api/3/issue", body=payload)
        key = resp.get("key", "")
        iid = resp.get("id", "")
        created_issues.append({"key": key, "id": iid, "tc_id": tc["id"]})
        print(f"  ✓ Created {key}  ({tc['id']})")
    except RuntimeError as e:
        print(f"  ✗ Failed {tc['id']}: {e}")

if not created_issues:
    print("No test issues created — aborting Xray steps.")
    raise SystemExit(1)

test_issue_ids  = [i["id"]  for i in created_issues]
test_issue_keys = [i["key"] for i in created_issues]
print(f"\nCreated {len(created_issues)} test issues: {test_issue_keys}\n")

# ── step 2: Xray authenticate ────────────────────────────────────────────────────
print("=" * 60)
print("STEP 2 — Authenticating with Xray Cloud")
print("=" * 60)
tok = xray_token()
print(f"  ✓ Xray token obtained (length {len(tok)})\n")

# ── step 3: create folder ────────────────────────────────────────────────────────
print("=" * 60)
print(f"STEP 3 — Creating folder: {FOLDER_PATH}")
print("=" * 60)

safe_path = FOLDER_PATH.replace('"', '\\"')
ids_json  = json.dumps(test_issue_ids)
folder_mutation = f'''
mutation {{
  createFolder(projectId: "{PROJECT_ID}", path: "{safe_path}", testIssueIds: {ids_json}) {{
    folder {{ path }}
    warnings
  }}
}}
'''
resp = gql(folder_mutation)
errors = resp.get("errors")
if errors:
    print(f"  ⚠ Folder GraphQL errors: {errors}")
else:
    folder_data = (resp.get("data") or {}).get("createFolder", {})
    folder_path = (folder_data.get("folder") or {}).get("path", "")
    warnings    = folder_data.get("warnings", [])
    print(f"  ✓ Folder created/updated: {folder_path or FOLDER_PATH}")
    if warnings:
        print(f"  ⚠ Warnings: {warnings}")
print()

# ── step 4: create Test Set ──────────────────────────────────────────────────────
print("=" * 60)
print("STEP 4 — Creating Test Set")
print("=" * 60)

ts_summary  = f"Test Set — {STORY_KEY} {STORY_SUMMARY}"
ts_mutation = f'''
mutation {{
  createTestSet(
    jira: {{
      summary: "{ts_summary}",
      project: {{key: "{PROJECT_KEY}"}},
      issuetype: {{name: "Test Set"}}
    }},
    testIssueIds: {ids_json}
  ) {{
    issueKey
    issueId
    warnings
  }}
}}
'''
resp = gql(ts_mutation)
errors = resp.get("errors")
testset_id  = None
testset_key = None
if errors:
    print(f"  ⚠ createTestSet GraphQL errors: {errors}")
    # fallback: create via Jira REST
    try:
        payload = {"fields": {"project": {"key": PROJECT_KEY},
                              "summary": ts_summary,
                              "issuetype": {"name": "Test Set"}}}
        jr = jira_request("POST", "/rest/api/3/issue", body=payload)
        testset_key = jr.get("key")
        testset_id  = jr.get("id")
        print(f"  ✓ Test Set created via Jira REST: {testset_key} (id {testset_id})")
    except RuntimeError as e:
        print(f"  ✗ Jira REST fallback also failed: {e}")
else:
    cd = (resp.get("data") or {}).get("createTestSet", {})
    testset_key = cd.get("issueKey")
    testset_id  = cd.get("issueId")
    warnings    = cd.get("warnings", [])
    print(f"  ✓ Test Set created: {testset_key} (id {testset_id})")
    if warnings:
        print(f"  ⚠ Warnings: {warnings}")
print()

# ── step 4b: ensure tests are in the test set (if it was REST-created) ───────────
if testset_id and errors:
    print("STEP 4b — Adding tests to Test Set via GraphQL")
    at_mutation = f'''
    mutation {{
      addTestsToTestSet(issueId: "{testset_id}", testIssueIds: {ids_json}) {{
        __typename
      }}
    }}
    '''
    r2 = gql(at_mutation)
    if r2.get("errors"):
        print(f"  ⚠ addTestsToTestSet errors: {r2['errors']}")
    else:
        print(f"  ✓ Added {len(test_issue_ids)} tests to Test Set {testset_key}")
    print()

# ── step 5: resolve numeric IDs for plan & execution ────────────────────────────
print("=" * 60)
print("STEP 5 — Linking to Test Plan and Test Execution")
print("=" * 60)

plan_id = jira_request("GET", f"/rest/api/3/issue/{TEST_PLAN_KEY}").get("id")
exec_id = jira_request("GET", f"/rest/api/3/issue/{TEST_EXEC_KEY}").get("id")
print(f"  Test Plan  {TEST_PLAN_KEY} → id {plan_id}")
print(f"  Test Exec  {TEST_EXEC_KEY} → id {exec_id}")

# add tests to plan
r = gql(f'mutation {{ addTestsToTestPlan(issueId: "{plan_id}", testIssueIds: {ids_json}) {{ __typename }} }}')
if r.get("errors"):
    print(f"  ⚠ addTestsToTestPlan errors: {r['errors']}")
else:
    print(f"  ✓ Added {len(test_issue_ids)} tests to Test Plan {TEST_PLAN_KEY}")

# add tests to execution
r = gql(f'mutation {{ addTestsToTestExecution(issueId: "{exec_id}", testIssueIds: {ids_json}) {{ __typename }} }}')
if r.get("errors"):
    print(f"  ⚠ addTestsToTestExecution errors: {r['errors']}")
else:
    print(f"  ✓ Added {len(test_issue_ids)} tests to Test Execution {TEST_EXEC_KEY}")

# link test set to plan
if testset_id and plan_id:
    ts_ids_json = json.dumps([testset_id])
    r = gql(f'mutation {{ addTestSetsToTestPlan(issueId: "{plan_id}", testSetIssueIds: {ts_ids_json}) {{ __typename }} }}')
    if r.get("errors"):
        print(f"  ⚠ addTestSetsToTestPlan errors: {r['errors']}")
    else:
        print(f"  ✓ Linked Test Set {testset_key} to Test Plan {TEST_PLAN_KEY}")

# link test set to execution
if testset_id and exec_id:
    ts_ids_json = json.dumps([testset_id])
    r = gql(f'mutation {{ addTestSetsToTestExecution(issueId: "{exec_id}", testSetIssueIds: {ts_ids_json}) {{ __typename }} }}')
    if r.get("errors"):
        print(f"  ⚠ addTestSetsToTestExecution errors: {r['errors']}")
    else:
        print(f"  ✓ Linked Test Set {testset_key} to Test Execution {TEST_EXEC_KEY}")

# ── summary ──────────────────────────────────────────────────────────────────────
print()
print("=" * 60)
print("DONE")
print("=" * 60)
print(f"  Story       : {STORY_KEY} — {STORY_SUMMARY}")
print(f"  Folder path : {FOLDER_PATH}")
print(f"  Test issues : {', '.join(test_issue_keys)}")
print(f"  Test Set    : {testset_key}")
print(f"  Test Plan   : {TEST_PLAN_KEY}")
print(f"  Test Exec   : {TEST_EXEC_KEY}")
print()
print(f"  View ticket : {JIRA_BASE}/browse/{STORY_KEY}")
print(f"  View plan   : {JIRA_BASE}/browse/{TEST_PLAN_KEY}")
print(f"  View exec   : {JIRA_BASE}/browse/{TEST_EXEC_KEY}")
