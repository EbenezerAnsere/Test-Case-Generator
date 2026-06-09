"""
Xray steps only (tests already created in Jira):
  DK26-1710..DK26-1718  ->  Xray IDs 120311..120320
  1. Create folder  Quarter 2/Frontend/Ebenezer/DK26-139 SP3: Q1-3. Dark Mode
  2. Create Test Set and add all tests
  3. Link tests to Test Plan DK26-118
  4. Link tests to Test Execution DK26-195
  5. Link Test Set to Test Plan + Test Execution
"""

import base64
import io
import json
import sys
import urllib.error
import urllib.request

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

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

_ENV = load_env()

# ── credentials ─────────────────────────────────────────────────────────────────
XRAY_CLIENT_ID     = _ENV.get("XRAY_CLIENT_ID", "")
XRAY_CLIENT_SECRET = _ENV.get("XRAY_CLIENT_SECRET", "")
XRAY_AUTH_URL      = "https://xray.cloud.getxray.app/api/v2/authenticate"
XRAY_GRAPHQL       = "https://xray.cloud.getxray.app/api/v2/graphql"

# ── constants ───────────────────────────────────────────────────────────────────
PROJECT_KEY   = "DK26"
PROJECT_ID    = "13358"
STORY_KEY     = "DK26-139"
FOLDER_PATH   = "Quarter 2/Frontend/Ebenezer/DK26-139 SP3: Q1-3. Dark Mode"
TEST_PLAN_KEY = "DK26-118"
TEST_EXEC_KEY = "DK26-195"

# Jira key -> Xray issueId (resolved in previous run)
TESTS = {
    "DK26-1710": "120311",
    "DK26-1711": "120312",
    "DK26-1712": "120314",
    "DK26-1713": "120315",
    "DK26-1714": "120316",
    "DK26-1715": "120317",
    "DK26-1716": "120318",
    "DK26-1717": "120319",
    "DK26-1718": "120320",
}

JIRA_BASE  = "https://amali-tech.atlassian.net"
JIRA_EMAIL = _ENV.get("JIRA_EMAIL", "")
JIRA_TOKEN = _ENV.get("JIRA_API_TOKEN", "")
JIRA_CREDS = base64.b64encode(f"{JIRA_EMAIL}:{JIRA_TOKEN}".encode()).decode()


def jira_get(path):
    req = urllib.request.Request(
        f"{JIRA_BASE}{path}",
        headers={"Authorization": f"Basic {JIRA_CREDS}", "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


# ── Xray auth ────────────────────────────────────────────────────────────────────
print("Authenticating with Xray Cloud...")
r = urllib.request.urlopen(
    urllib.request.Request(
        XRAY_AUTH_URL,
        data=json.dumps({"client_id": XRAY_CLIENT_ID, "client_secret": XRAY_CLIENT_SECRET}).encode(),
        method="POST",
        headers={"Content-Type": "application/json"},
    ),
    timeout=30,
)
XRAY_TOKEN = r.read().decode().strip().strip('"')
print(f"  Token obtained (len={len(XRAY_TOKEN)})\n")


def gql(query):
    body = json.dumps({"query": query}).encode()
    req = urllib.request.Request(
        XRAY_GRAPHQL, data=body, method="POST",
        headers={"Authorization": f"Bearer {XRAY_TOKEN}",
                 "Content-Type": "application/json",
                 "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r2:
            return json.loads(r2.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Xray GraphQL HTTP {e.code}: {e.read().decode()[:500]}")


def check(resp, label):
    errs = resp.get("errors")
    if errs:
        print(f"  WARN {label}: {errs}")
        return False
    print(f"  OK   {label}")
    return True


# ── build test ID list ───────────────────────────────────────────────────────────
test_ids    = list(TESTS.values())
test_ids_j  = json.dumps(test_ids)

# ── resolve plan & exec numeric IDs ─────────────────────────────────────────────
plan_id = jira_get(f"/rest/api/3/issue/{TEST_PLAN_KEY}").get("id")
exec_id = jira_get(f"/rest/api/3/issue/{TEST_EXEC_KEY}").get("id")
print(f"Test Plan {TEST_PLAN_KEY} -> Jira id {plan_id}")
print(f"Test Exec {TEST_EXEC_KEY} -> Jira id {exec_id}\n")

# ── STEP 1: create folder ────────────────────────────────────────────────────────
print("=" * 60)
print(f"STEP 1 — Create folder: {FOLDER_PATH}")
print("=" * 60)
safe = FOLDER_PATH.replace('"', '\\"')
r1 = gql(f'''
mutation {{
  createFolder(projectId: "{PROJECT_ID}", path: "{safe}", testIssueIds: {test_ids_j}) {{
    folder {{ path }}
    warnings
  }}
}}
''')
if check(r1, "createFolder"):
    fd = (r1.get("data") or {}).get("createFolder", {})
    print(f"       path: {(fd.get('folder') or {}).get('path', FOLDER_PATH)}")
    if fd.get("warnings"):
        print(f"       warnings: {fd['warnings']}")
print()

# ── STEP 2: create Test Set ──────────────────────────────────────────────────────
print("=" * 60)
print("STEP 2 — Create Test Set")
print("=" * 60)
ts_summary = f"Test Set — {STORY_KEY} SP3: Q1-3. Dark Mode"
r2 = gql(f'''
mutation {{
  createTestSet(
    jira: {{
      summary: "{ts_summary}",
      project: {{key: "{PROJECT_KEY}"}},
      issuetype: {{name: "Test Set"}}
    }},
    testIssueIds: {test_ids_j}
  ) {{
    testSet {{ issueId jira(fields: ["key","summary"]) }}
    warnings
  }}
}}
''')
testset_id  = None
testset_key = None
if check(r2, "createTestSet"):
    ts = ((r2.get("data") or {}).get("createTestSet") or {}).get("testSet") or {}
    testset_id  = ts.get("issueId")
    testset_key = (ts.get("jira") or {}).get("key")
    print(f"       Test Set: {testset_key}  (issueId={testset_id})")
    warnings = ((r2.get("data") or {}).get("createTestSet") or {}).get("warnings", [])
    if warnings:
        print(f"       warnings: {warnings}")
print()

# ── STEP 3: link tests -> Test Plan ─────────────────────────────────────────────
print("=" * 60)
print(f"STEP 3 — Link {len(test_ids)} tests to Test Plan {TEST_PLAN_KEY}")
print("=" * 60)
r3 = gql(f'mutation {{ addTestsToTestPlan(issueId: "{plan_id}", testIssueIds: {test_ids_j}) {{ __typename }} }}')
check(r3, f"addTestsToTestPlan({TEST_PLAN_KEY})")
print()

# ── STEP 4: link tests -> Test Execution ────────────────────────────────────────
print("=" * 60)
print(f"STEP 4 — Link {len(test_ids)} tests to Test Execution {TEST_EXEC_KEY}")
print("=" * 60)
r4 = gql(f'mutation {{ addTestsToTestExecution(issueId: "{exec_id}", testIssueIds: {test_ids_j}) {{ __typename }} }}')
check(r4, f"addTestsToTestExecution({TEST_EXEC_KEY})")
print()

# ── STEP 5: link Test Set -> Test Plan & Test Execution ──────────────────────────
if testset_id:
    ts_ids_j = json.dumps([testset_id])

    print("=" * 60)
    print(f"STEP 5 — Link Test Set {testset_key} to Test Plan + Test Execution")
    print("=" * 60)

    r5a = gql(f'mutation {{ addTestSetsToTestPlan(issueId: "{plan_id}", testSetIssueIds: {ts_ids_j}) {{ __typename }} }}')
    check(r5a, f"addTestSetsToTestPlan({TEST_PLAN_KEY})")

    r5b = gql(f'mutation {{ addTestSetsToTestExecution(issueId: "{exec_id}", testSetIssueIds: {ts_ids_j}) {{ __typename }} }}')
    check(r5b, f"addTestSetsToTestExecution({TEST_EXEC_KEY})")
    print()

# ── summary ──────────────────────────────────────────────────────────────────────
print("=" * 60)
print("DONE")
print("=" * 60)
print(f"  Story         : {STORY_KEY} SP3: Q1-3. Dark Mode")
print(f"  Folder        : {FOLDER_PATH}")
print(f"  Tests created : {', '.join(TESTS.keys())}")
print(f"  Test Set      : {testset_key}  (id {testset_id})")
print(f"  Test Plan     : {TEST_PLAN_KEY}  (Jira id {plan_id})")
print(f"  Test Exec     : {TEST_EXEC_KEY}  (Jira id {exec_id})")
print()
print(f"  View story : {JIRA_BASE}/browse/{STORY_KEY}")
print(f"  View plan  : {JIRA_BASE}/browse/{TEST_PLAN_KEY}")
print(f"  View exec  : {JIRA_BASE}/browse/{TEST_EXEC_KEY}")
if testset_key:
    print(f"  View set   : {JIRA_BASE}/browse/{testset_key}")
