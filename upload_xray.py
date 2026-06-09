"""
upload_xray.py — Full Xray upload from a test cases JSON file (no AI API needed).

Usage:
    python upload_xray.py --issue DK26-XXX
    python upload_xray.py --issue DK26-XXX --folder backend
    python upload_xray.py --issue DK26-XXX --dry-run
    python upload_xray.py --issue DK26-XXX --skip-format

Reads:  DK26-XXX_story.json   (from fetch_story.py)
        DK26-XXX_tests.json   (written by Claude in the chat)

Runs 6 steps with live output:
  1  Reformat ticket description as ADF table
  2  Create Jira Test Cases issues
  3  Create Xray folder
  4  Create Test Set + link to Test Plan & Test Execution
  5  Add test steps
  6  Link test cases to story (Xray Tests panel)
"""

import argparse
import base64
import io
import json
import sys
import urllib.error
import urllib.request

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

ENV = load_env()
JIRA_BASE    = "https://amali-tech.atlassian.net"
XRAY_AUTH    = "https://xray.cloud.getxray.app/api/v2/authenticate"
XRAY_GQL     = "https://xray.cloud.getxray.app/api/v2/graphql"
PROJECT_KEY  = "DK26"
PROJECT_ID   = "13358"
TEST_PLAN    = "DK26-118"
TEST_EXEC    = "DK26-195"
FOLDER_ROOTS = {
    "frontend": "Quarter 2 ( April -July )/Frontend/Ebenezer",
    "backend":  "Quarter 2 ( April -July )/Backend/Ebenezer",
}
JIRA_CREDS = base64.b64encode(
    f"{ENV.get('JIRA_EMAIL','')}:{ENV.get('JIRA_API_TOKEN','')}".encode()
).decode()
_xray_token = None

W = 62

# ── output helpers ────────────────────────────────────────────────────────────
def banner(t): print(f"\n{'='*W}\n  {t}\n{'='*W}")
def step(n, total, t): print(f"\n[{n}/{total}] {t}\n{'-'*W}")
def ok(m):   print(f"  [OK]   {m}")
def warn(m): print(f"  [WARN] {m}")
def info(m): print(f"         {m}")

# ── HTTP helpers ──────────────────────────────────────────────────────────────
def jira(method, path, body=None):
    url  = f"{JIRA_BASE}{path}"
    data = json.dumps(body).encode() if body is not None else None
    req  = urllib.request.Request(url, data=data, method=method,
        headers={"Authorization": f"Basic {JIRA_CREDS}",
                 "Content-Type": "application/json", "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            raw = r.read()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Jira {method} {path} HTTP {e.code}: {e.read().decode()[:300]}")


def xray_token():
    global _xray_token
    if _xray_token:
        return _xray_token
    body = json.dumps({"client_id": ENV.get("XRAY_CLIENT_ID","").strip(),
                       "client_secret": ENV.get("XRAY_CLIENT_SECRET","")}).encode()
    req = urllib.request.Request(XRAY_AUTH, data=body, method="POST",
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        _xray_token = r.read().decode().strip().strip('"')
    return _xray_token


def gql(query, variables=None):
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    body = json.dumps(payload).encode()
    req  = urllib.request.Request(XRAY_GQL, data=body, method="POST",
        headers={"Authorization": f"Bearer {xray_token()}",
                 "Content-Type": "application/json", "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Xray GQL HTTP {e.code}: {e.read().decode()[:300]}")


def gql_ok(resp, label):
    errs = resp.get("errors")
    if errs:
        warn(f"{label}: {[e['message'] for e in errs]}")
        return False
    ok(label)
    return True

# ── ADF builders ──────────────────────────────────────────────────────────────
def _t(text, bold=False):
    n = {"type": "text", "text": text}
    if bold: n["marks"] = [{"type": "strong"}]
    return n

def para(text, bold=False):
    return {"type": "paragraph", "content": [_t(text, bold)]}

def heading(level, text):
    return {"type": "heading", "attrs": {"level": level}, "content": [_t(text)]}

def bullet(items):
    return {"type": "bulletList", "content": [
        {"type": "listItem", "content": [para(i)]} for i in items]}

def ordered(items):
    return {"type": "orderedList", "content": [
        {"type": "listItem", "content": [para(i)]} for i in items]}

def table_header(cols):
    return {"type": "tableRow", "content": [
        {"type": "tableHeader", "attrs": {},
         "content": [{"type": "paragraph", "content": [_t(c, bold=True)]}]}
        for c in cols]}

def table_row(cells):
    row = []
    for cell in cells:
        if isinstance(cell, list):
            row.append({"type": "tableCell", "attrs": {}, "content": [ordered(cell)]})
        else:
            row.append({"type": "tableCell", "attrs": {}, "content": [para(str(cell))]})
    return {"type": "tableRow", "content": row}

def build_desc_adf(user_story, ac_items, test_cases):
    rows = [[
        "Not Run", tc["id"], tc["title"],
        tc["preconditions"], tc["steps"], tc["expected"],
    ] for tc in test_cases]
    return {"type": "doc", "version": 1, "content": [
        heading(2, "User Story"), para(user_story),
        heading(2, "Acceptance Criteria"), bullet(ac_items),
        heading(2, "Test Cases for QA"),
        {"type": "table",
         "attrs": {"isNumberColumnEnabled": False, "layout": "full-width"},
         "content": [table_header(["Status","ID","Title","Preconditions","Steps","Expected Result"])]
                    + [table_row(r) for r in rows]},
        heading(2, "Notes"),
        bullet(["Status values: Not Run | Pass | Fail | Blocked",
                "Update Status column as each test is executed.",
                "Log defects by linking a new Bug issue to this ticket."]),
    ]}

def build_test_adf(preconditions, steps, expected):
    return {"type": "doc", "version": 1, "content": [
        heading(3, "Preconditions"), para(preconditions),
        heading(3, "Steps"),        ordered(steps),
        heading(3, "Expected Result"), para(expected),
    ]}

# ── main workflow ─────────────────────────────────────────────────────────────
def run(issue_key, folder_key="frontend", dry_run=False, skip_format=False):
    story_file = f"{issue_key}_story.json"
    tests_file = f"{issue_key}_tests.json"

    # load story metadata
    try:
        with open(story_file, encoding="utf-8") as f:
            story = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: {story_file} not found. Run: python fetch_story.py --issue {issue_key}")
        sys.exit(1)

    # load test cases
    try:
        with open(tests_file, encoding="utf-8") as f:
            test_cases = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: {tests_file} not found.")
        print(f"  Ask Claude to generate it by saying:")
        print(f'  "Read {story_file} and generate test cases to {tests_file}"')
        sys.exit(1)

    summary    = story["summary"]
    user_story = story.get("user_story", summary)
    ac_items   = story.get("acceptance_criteria", [])
    TOTAL = 6

    banner(f"Dodokpo QA Upload — {issue_key}  {'[DRY RUN]' if dry_run else ''}")
    info(f"Story   : {summary}")
    info(f"Tests   : {len(test_cases)} test cases from {tests_file}")

    # ── STEP 1: reformat ticket description ───────────────────────────────────
    step(1, TOTAL, "Reformat Jira ticket description")
    if skip_format or dry_run:
        info("Skipped.")
    else:
        new_desc = build_desc_adf(user_story, ac_items, test_cases)
        jira("PUT", f"/rest/api/3/issue/{issue_key}", {"fields": {"description": new_desc}})
        ok(f"Description updated on {issue_key}")

    # ── STEP 2: create Jira Test Cases issues ─────────────────────────────────
    step(2, TOTAL, "Create Jira Test Cases issues")
    created = []
    for tc in test_cases:
        s = f"[{tc['id']}] {tc['title']}"
        if dry_run:
            info(f"[dry-run] {s}")
            created.append({"key": "DK26-DRY", "id": "000000", "tc": tc})
        else:
            resp = jira("POST", "/rest/api/3/issue", {"fields": {
                "project":     {"key": PROJECT_KEY},
                "summary":     s,
                "issuetype":   {"name": "Test Cases"},
                "description": build_test_adf(tc["preconditions"], tc["steps"], tc["expected"]),
            }})
            created.append({"key": resp.get("key",""), "id": resp.get("id",""), "tc": tc})
            ok(f"{resp.get('key')}  {s[:55]}")
    info(f"Total: {len(created)}")

    test_ids  = [c["id"]  for c in created]
    test_keys = [c["key"] for c in created]
    ids_json  = json.dumps(test_ids)

    # ── STEP 3: Xray folder ───────────────────────────────────────────────────
    step(3, TOTAL, "Create Xray folder")
    parent      = FOLDER_ROOTS.get(folder_key, FOLDER_ROOTS["frontend"])
    folder_path = f"{parent}/{issue_key} {summary}"
    info(f"Path: {folder_path}")
    if not dry_run:
        tok = xray_token()
        info(f"Xray authenticated (token len={len(tok)})")
        safe = folder_path.replace('"', '\\"')
        r = gql(f'mutation {{ createFolder(projectId:"{PROJECT_ID}",path:"{safe}",testIssueIds:{ids_json}) '
                f'{{ folder {{ path }} warnings }} }}')
        gql_ok(r, "createFolder")
        w = ((r.get("data") or {}).get("createFolder") or {}).get("warnings") or []
        if w: warn(f"Folder warnings: {w}")
    else:
        info("[dry-run] skipped")

    # ── STEP 4: Test Set + link to Plan/Execution ─────────────────────────────
    step(4, TOTAL, "Create Test Set, link to Test Plan & Test Execution")
    testset_key = None
    if not dry_run:
        ts_name = f"Test Set — {issue_key} {summary}"
        r2 = gql(f'''mutation {{
          createTestSet(
            jira:{{fields:{{summary:"{ts_name}",project:{{key:"{PROJECT_KEY}"}},issuetype:{{name:"Test Set"}}}}}},
            testIssueIds:{ids_json}
          ) {{ testSet {{ issueId jira(fields:["key","summary"]) }} warnings }}
        }}''')
        gql_ok(r2, "createTestSet")
        ts = ((r2.get("data") or {}).get("createTestSet") or {}).get("testSet") or {}
        testset_key = (ts.get("jira") or {}).get("key")
        testset_id  = ts.get("issueId")
        info(f"Test Set: {testset_key} (id {testset_id})")

        plan_id = jira("GET", f"/rest/api/3/issue/{TEST_PLAN}").get("id")
        exec_id = jira("GET", f"/rest/api/3/issue/{TEST_EXEC}").get("id")

        gql_ok(gql(f'mutation{{addTestsToTestPlan(issueId:"{plan_id}",testIssueIds:{ids_json}){{__typename}}}}'),
               f"addTestsToTestPlan ({TEST_PLAN})")
        gql_ok(gql(f'mutation{{addTestsToTestExecution(issueId:"{exec_id}",testIssueIds:{ids_json}){{__typename}}}}'),
               f"addTestsToTestExecution ({TEST_EXEC})")

        for target in [TEST_PLAN, TEST_EXEC]:
            if testset_key:
                try:
                    jira("POST", "/rest/api/3/issueLink", {
                        "type": {"id": "10003"},
                        "inwardIssue":  {"key": testset_key},
                        "outwardIssue": {"key": target},
                    })
                    ok(f"Relates: {testset_key} <-> {target}")
                except Exception as e:
                    warn(str(e))
    else:
        info("[dry-run] skipped")

    # ── STEP 5: add test steps ────────────────────────────────────────────────
    step(5, TOTAL, "Add Xray test steps")
    ADD_STEP = "mutation AddStep($issueId:String!,$step:CreateStepInput!){addTestStep(issueId:$issueId,step:$step){id action data result}}"
    steps_ok = 0
    for c in created:
        tc = c["tc"]
        info(f"{c['key']} ({tc['id']})")
        for i, action in enumerate(tc["steps"]):
            is_last    = i == len(tc["steps"]) - 1
            data_val   = tc["preconditions"] if i == 0 else ""
            result_val = tc["expected"] if is_last else ""
            if dry_run:
                info(f"  step {i+1}: {action[:55]}")
                steps_ok += 1
            else:
                r = gql(ADD_STEP, {"issueId": c["id"],
                                   "step": {"action": action, "data": data_val, "result": result_val}})
                if r.get("errors"):
                    warn(f"  step {i+1}: {r['errors']}")
                else:
                    info(f"  step {i+1}: {action[:55]}")
                    steps_ok += 1
    ok(f"{steps_ok} steps added")

    # ── STEP 6: link tests -> story ───────────────────────────────────────────
    step(6, TOTAL, f"Link test cases to story {issue_key}")
    links_ok = 0
    for c in created:
        if dry_run:
            info(f"[dry-run] {c['key']} tests {issue_key}")
            links_ok += 1
        else:
            try:
                jira("POST", "/rest/api/3/issueLink", {
                    "type": {"id": "10006"},
                    "inwardIssue":  {"key": issue_key},
                    "outwardIssue": {"key": c["key"]},
                })
                ok(f"{c['key']} tests {issue_key}")
                links_ok += 1
            except RuntimeError as e:
                if "already" in str(e).lower():
                    ok(f"{c['key']} (already linked)")
                    links_ok += 1
                else:
                    warn(str(e))

    # ── summary ───────────────────────────────────────────────────────────────
    banner("COMPLETE")
    print(f"  Story      : {JIRA_BASE}/browse/{issue_key}")
    print(f"  Folder     : {folder_path}")
    print(f"  Tests      : {', '.join(test_keys)}")
    if testset_key:
        print(f"  Test Set   : {JIRA_BASE}/browse/{testset_key}")
    print(f"  Test Plan  : {JIRA_BASE}/browse/{TEST_PLAN}")
    print(f"  Test Exec  : {JIRA_BASE}/browse/{TEST_EXEC}")
    print()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--issue",       required=True)
    parser.add_argument("--folder",      default="frontend", choices=["frontend","backend"])
    parser.add_argument("--dry-run",     action="store_true")
    parser.add_argument("--skip-format", action="store_true")
    args = parser.parse_args()
    run(args.issue, folder_key=args.folder, dry_run=args.dry_run, skip_format=args.skip_format)


if __name__ == "__main__":
    main()
