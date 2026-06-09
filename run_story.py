"""
run_story.py — Dodokpo QA Automation (Headed / Verbose Mode)

Usage:
    python run_story.py --issue DK26-XXX
    python run_story.py --issue DK26-XXX --dry-run      # print plan, no writes
    python run_story.py --issue DK26-XXX --skip-format  # skip description reformat
    python run_story.py --issue DK26-XXX --folder backend

Full 7-step workflow, everything printed live:
  1  Fetch Jira ticket & parse acceptance criteria
  2  Generate test cases via Claude AI
  3  Reformat ticket description as ADF table
  4  Create Jira Test Cases issues (one per test case)
  5  Create Xray folder, Test Set, link to Test Plan + Execution
  6  Add test steps to every test case
  7  Link test cases to the story (Xray Tests panel)
"""

import argparse
import base64
import io
import json
import re
import sys
import textwrap
import urllib.error
import urllib.request

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# ── read .env.example ────────────────────────────────────────────────────────
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

JIRA_EMAIL         = ENV.get("JIRA_EMAIL", "")
JIRA_TOKEN         = ENV.get("JIRA_API_TOKEN", "")
XRAY_CLIENT_ID     = ENV.get("XRAY_CLIENT_ID", "").strip()
XRAY_CLIENT_SECRET = ENV.get("XRAY_CLIENT_SECRET", "")
ANTHROPIC_API_KEY  = ENV.get("ANTHROPIC_API_KEY", "")

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

JIRA_CREDS = base64.b64encode(f"{JIRA_EMAIL}:{JIRA_TOKEN}".encode()).decode()
_xray_token = None

# ── terminal output helpers ──────────────────────────────────────────────────
W = 62

def banner(text):
    print("\n" + "=" * W)
    print(f"  {text}")
    print("=" * W)

def step(n, total, text):
    print(f"\n[{n}/{total}] {text}")
    print("-" * W)

def ok(msg):   print(f"  [OK]   {msg}")
def warn(msg): print(f"  [WARN] {msg}")
def info(msg): print(f"         {msg}")
def fail(msg): print(f"  [FAIL] {msg}")

# ── HTTP helpers ─────────────────────────────────────────────────────────────
def jira(method, path, body=None):
    url = f"{JIRA_BASE}{path}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method,
        headers={"Authorization": f"Basic {JIRA_CREDS}",
                 "Content-Type": "application/json", "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            raw = r.read()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Jira {method} {path} -> HTTP {e.code}: {e.read().decode()[:300]}")


def xray_token():
    global _xray_token
    if _xray_token:
        return _xray_token
    body = json.dumps({"client_id": XRAY_CLIENT_ID, "client_secret": XRAY_CLIENT_SECRET}).encode()
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
    req = urllib.request.Request(XRAY_GQL, data=body, method="POST",
        headers={"Authorization": f"Bearer {xray_token()}",
                 "Content-Type": "application/json", "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Xray GQL HTTP {e.code}: {e.read().decode()[:300]}")


def gql_check(resp, label):
    errs = resp.get("errors")
    if errs:
        warn(f"{label}: {[e['message'] for e in errs]}")
        return False
    ok(label)
    return True

# ── ADF builders ─────────────────────────────────────────────────────────────
def adf_text(t, bold=False):
    node = {"type": "text", "text": t}
    if bold:
        node["marks"] = [{"type": "strong"}]
    return node

def adf_para(text, bold=False):
    return {"type": "paragraph", "content": [adf_text(text, bold)]}

def adf_heading(level, text):
    return {"type": "heading", "attrs": {"level": level},
            "content": [adf_text(text)]}

def adf_bullet(items):
    return {"type": "bulletList", "content": [
        {"type": "listItem", "content": [adf_para(i)]} for i in items]}

def adf_ordered(items):
    return {"type": "orderedList", "content": [
        {"type": "listItem", "content": [adf_para(i)]} for i in items]}

def adf_table_header(cols):
    return {"type": "tableRow", "content": [
        {"type": "tableHeader", "attrs": {},
         "content": [{"type": "paragraph", "content": [adf_text(c, bold=True)]}]}
        for c in cols]}

def adf_table_row(cells):
    content = []
    for cell in cells:
        if isinstance(cell, list):
            # ordered list inside cell (steps)
            content.append({"type": "tableCell", "attrs": {},
                "content": [adf_ordered(cell)]})
        else:
            content.append({"type": "tableCell", "attrs": {},
                "content": [adf_para(str(cell))]})
    return {"type": "tableRow", "content": content}

def adf_table(header_cols, rows):
    return {"type": "table",
            "attrs": {"isNumberColumnEnabled": False, "layout": "full-width"},
            "content": [adf_table_header(header_cols)] + [adf_table_row(r) for r in rows]}

def build_description_adf(story_text, ac_items, test_cases):
    rows = []
    for tc in test_cases:
        rows.append([
            "Not Run",
            tc["id"],
            tc["title"],
            tc["preconditions"],
            tc["steps"],          # list -> ordered list cell
            tc["expected"],
        ])
    return {
        "type": "doc", "version": 1,
        "content": [
            adf_heading(2, "User Story"),
            adf_para(story_text),
            adf_heading(2, "Acceptance Criteria"),
            adf_bullet(ac_items),
            adf_heading(2, "Test Cases for QA"),
            adf_table(
                ["Status", "ID", "Title", "Preconditions", "Steps", "Expected Result"],
                rows,
            ),
            adf_heading(2, "Notes"),
            adf_bullet([
                "Status values: Not Run | Pass | Fail | Blocked",
                "Update Status column as each test is executed.",
                "Log defects by linking a new Bug issue to this ticket.",
            ]),
        ],
    }

def build_test_adf(preconditions, steps, expected):
    return {
        "type": "doc", "version": 1,
        "content": [
            adf_heading(3, "Preconditions"),
            adf_para(preconditions),
            adf_heading(3, "Steps"),
            adf_ordered(steps),
            adf_heading(3, "Expected Result"),
            adf_para(expected),
        ],
    }

# ── ADF parser: extract plain text from content blocks ───────────────────────
def adf_to_text(node):
    if not node:
        return ""
    t = node.get("type", "")
    if t == "text":
        return node.get("text", "")
    content = node.get("content", [])
    parts = [adf_to_text(c) for c in content]
    sep = "\n" if t in ("paragraph", "heading", "listItem", "bulletList", "orderedList") else ""
    return sep.join(p for p in parts if p)

def extract_acceptance_criteria(description_adf):
    """Pull bullet list items that follow an 'Acceptance Criteria' heading."""
    if not description_adf:
        return []
    content = description_adf.get("content", [])
    capture = False
    items = []
    for node in content:
        t = node.get("type", "")
        if t == "heading":
            text = adf_to_text(node).strip().lower()
            capture = "acceptance" in text
            continue
        if capture:
            if t in ("bulletList", "orderedList"):
                for li in node.get("content", []):
                    txt = adf_to_text(li).strip()
                    if txt:
                        items.append(txt)
                break
            elif t == "heading":
                break
    return items

def extract_user_story(description_adf):
    if not description_adf:
        return ""
    content = description_adf.get("content", [])
    capture = False
    for node in content:
        t = node.get("type", "")
        if t == "heading":
            text = adf_to_text(node).strip().lower()
            capture = "user story" in text or "story" in text
            continue
        if capture and t == "paragraph":
            return adf_to_text(node).strip()
    # fallback: first paragraph
    for node in content:
        if node.get("type") == "paragraph":
            return adf_to_text(node).strip()
    return ""

# ── Claude AI: generate test cases ──────────────────────────────────────────
def generate_test_cases(story_key, story_summary, user_story, ac_items):
    """Call Claude to generate structured test cases."""
    import anthropic

    api_key = ANTHROPIC_API_KEY
    if not api_key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY not set in .env.example. "
            "Add it to use AI test case generation."
        )

    ac_text = "\n".join(f"- {a}" for a in ac_items) if ac_items else "(none found)"
    prompt = textwrap.dedent(f"""
        You are a QA engineer. Generate test cases for this Jira story.

        Story: {story_key} — {story_summary}
        User Story: {user_story}
        Acceptance Criteria:
        {ac_text}

        Rules:
        - One test case per acceptance criterion (minimum). Add edge/negative cases where useful.
        - IDs: TC-{story_key.replace('-','')}-001, TC-{story_key.replace('-','')}-002, ...
        - Steps must be short, imperative sentences (no numbering, I will add that).
        - Expected result is a single sentence.
        - Preconditions state what must already be true before the test.

        Return ONLY a JSON array, no markdown fences, no extra text:
        [
          {{
            "id": "TC-...-001",
            "title": "...",
            "preconditions": "...",
            "steps": ["step 1", "step 2"],
            "expected": "..."
          }}
        ]
    """).strip()

    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = message.content[0].text.strip()
    # strip possible markdown fences
    raw = re.sub(r"^```[a-z]*\n?", "", raw)
    raw = re.sub(r"\n?```$", "", raw)
    return json.loads(raw)

# ── main workflow ─────────────────────────────────────────────────────────────
def run(issue_key, folder_key="frontend", dry_run=False, skip_format=False):
    TOTAL = 7
    banner(f"Dodokpo QA Automation — {issue_key}  {'[DRY RUN]' if dry_run else ''}")

    # ── STEP 1: fetch ticket ─────────────────────────────────────────────────
    step(1, TOTAL, "Fetch Jira ticket")
    ticket = jira("GET", f"/rest/api/3/issue/{issue_key}")
    fields      = ticket.get("fields", {})
    summary     = fields.get("summary", "")
    description = fields.get("description")
    story_id    = ticket.get("id")
    ok(f"{issue_key}: {summary}")
    info(f"Jira numeric id: {story_id}")

    user_story = extract_user_story(description)
    ac_items   = extract_acceptance_criteria(description)
    info(f"User story: {user_story[:80] or '(not found in description)'}")
    info(f"Acceptance criteria found: {len(ac_items)}")
    for a in ac_items:
        info(f"  • {a[:75]}")

    # ── STEP 2: generate test cases ──────────────────────────────────────────
    step(2, TOTAL, "Generate test cases via Claude AI")
    if dry_run:
        info("[dry-run] skipping Claude API call — using placeholder")
        test_cases = [{"id": "TC-SAMPLE-001", "title": "Sample test", "preconditions": "Logged in",
                       "steps": ["Do step 1"], "expected": "Expected outcome"}]
    else:
        info("Calling Claude (claude-sonnet-4-6)...")
        test_cases = generate_test_cases(issue_key, summary, user_story, ac_items)
    ok(f"Generated {len(test_cases)} test cases")
    for tc in test_cases:
        info(f"  {tc['id']}  {tc['title']}")

    # ── STEP 3: reformat ticket description ──────────────────────────────────
    step(3, TOTAL, "Reformat ticket description (ADF table)")
    if skip_format or dry_run:
        info("Skipping description update.")
    else:
        new_desc = build_description_adf(user_story or summary, ac_items, test_cases)
        jira("PUT", f"/rest/api/3/issue/{issue_key}", {"fields": {"description": new_desc}})
        ok(f"Description updated on {issue_key}")

    # ── STEP 4: create Jira Test Cases issues ────────────────────────────────
    step(4, TOTAL, "Create Jira Test Cases issues")
    created = []   # {key, id, tc}
    for tc in test_cases:
        issue_summary = f"[{tc['id']}] {tc['title']}"
        payload = {"fields": {
            "project":     {"key": PROJECT_KEY},
            "summary":     issue_summary,
            "issuetype":   {"name": "Test Cases"},
            "description": build_test_adf(tc["preconditions"], tc["steps"], tc["expected"]),
        }}
        if dry_run:
            info(f"[dry-run] would create: {issue_summary}")
            created.append({"key": f"DK26-DRYRUN", "id": "000000", "tc": tc})
        else:
            resp = jira("POST", "/rest/api/3/issue", payload)
            key  = resp.get("key", "")
            iid  = resp.get("id", "")
            created.append({"key": key, "id": iid, "tc": tc})
            ok(f"{key}  ({tc['id']}) {tc['title'][:50]}")

    test_ids  = [c["id"]  for c in created]
    test_keys = [c["key"] for c in created]
    ids_json  = json.dumps(test_ids)
    info(f"Total created: {len(created)}")

    # ── STEP 5: Xray folder + Test Set + Plan/Execution linkage ─────────────
    step(5, TOTAL, "Xray: folder, Test Set, Test Plan & Execution")

    parent_path = FOLDER_ROOTS.get(folder_key, FOLDER_ROOTS["frontend"])
    folder_path = f"{parent_path}/{issue_key} {summary}"
    info(f"Folder: {folder_path}")

    if not dry_run:
        # auth
        tok = xray_token()
        info(f"Xray token obtained (len={len(tok)})")

        # folder
        safe = folder_path.replace('"', '\\"')
        r = gql(f'mutation {{ createFolder(projectId:"{PROJECT_ID}", path:"{safe}", testIssueIds:{ids_json}) '
                f'{{ folder {{ path }} warnings }} }}')
        gql_check(r, f"createFolder")
        fp = ((r.get("data") or {}).get("createFolder") or {})
        warnings = fp.get("warnings") or []
        if warnings:
            warn(f"Folder warnings: {warnings}")

        # Test Set
        ts_summary = f"Test Set — {issue_key} {summary}"
        r2 = gql(f'''mutation {{
          createTestSet(
            jira: {{ fields: {{ summary:"{ts_summary}", project:{{key:"{PROJECT_KEY}"}}, issuetype:{{name:"Test Set"}} }} }},
            testIssueIds: {ids_json}
          ) {{ testSet {{ issueId jira(fields:["key","summary"]) }} warnings }}
        }}''')
        gql_check(r2, "createTestSet")
        ts = ((r2.get("data") or {}).get("createTestSet") or {}).get("testSet") or {}
        testset_id  = ts.get("issueId")
        testset_key = (ts.get("jira") or {}).get("key")
        info(f"Test Set: {testset_key}  (id {testset_id})")

        # plan + execution numeric IDs
        plan_id = jira("GET", f"/rest/api/3/issue/{TEST_PLAN}").get("id")
        exec_id = jira("GET", f"/rest/api/3/issue/{TEST_EXEC}").get("id")
        info(f"Test Plan {TEST_PLAN} id={plan_id}  |  Test Exec {TEST_EXEC} id={exec_id}")

        gql_check(
            gql(f'mutation {{ addTestsToTestPlan(issueId:"{plan_id}", testIssueIds:{ids_json}) {{ __typename }} }}'),
            f"addTestsToTestPlan ({TEST_PLAN})")
        gql_check(
            gql(f'mutation {{ addTestsToTestExecution(issueId:"{exec_id}", testIssueIds:{ids_json}) {{ __typename }} }}'),
            f"addTestsToTestExecution ({TEST_EXEC})")

        # link Test Set via Jira Relates
        for target in [testset_key, TEST_PLAN, TEST_EXEC]:
            if testset_key and target != testset_key:
                try:
                    jira("POST", "/rest/api/3/issueLink", {
                        "type": {"id": "10003"},
                        "inwardIssue":  {"key": testset_key},
                        "outwardIssue": {"key": target},
                    })
                    ok(f"Relates link: {testset_key} <-> {target}")
                except Exception as e:
                    warn(f"Relates link {testset_key}<->{target}: {e}")
    else:
        info("[dry-run] skipping Xray calls")
        testset_key = "DK26-DRYRUN-TS"

    # ── STEP 6: add test steps ───────────────────────────────────────────────
    step(6, TOTAL, "Add Xray test steps")
    ADD_STEP = """
    mutation AddStep($issueId: String!, $step: CreateStepInput!) {
      addTestStep(issueId: $issueId, step: $step) { id action data result }
    }
    """
    steps_ok = 0
    for c in created:
        tc = c["tc"]
        info(f"{c['key']} ({tc['id']})")
        steps_list = tc["steps"]
        for i, action in enumerate(steps_list):
            is_last = (i == len(steps_list) - 1)
            data_val   = tc["preconditions"] if i == 0 else ""
            result_val = tc["expected"] if is_last else ""
            if dry_run:
                info(f"  [dry-run] step {i+1}: {action[:55]}")
                steps_ok += 1
                continue
            r = gql(ADD_STEP, {"issueId": c["id"],
                                "step": {"action": action, "data": data_val, "result": result_val}})
            if r.get("errors"):
                warn(f"  step {i+1} error: {r['errors']}")
            else:
                info(f"  step {i+1}: {action[:55]}")
                steps_ok += 1
    ok(f"{steps_ok} steps added")

    # ── STEP 7: link tests -> story ──────────────────────────────────────────
    step(7, TOTAL, f"Link test cases to story {issue_key} (Xray Tests panel)")
    links_ok = 0
    for c in created:
        if dry_run:
            info(f"[dry-run] link {c['key']} tests {issue_key}")
            links_ok += 1
            continue
        try:
            jira("POST", "/rest/api/3/issueLink", {
                "type": {"id": "10006"},
                "inwardIssue":  {"key": issue_key},
                "outwardIssue": {"key": c["key"]},
            })
            ok(f"{c['key']} tests {issue_key}")
            links_ok += 1
        except RuntimeError as e:
            if "already exists" in str(e).lower():
                ok(f"{c['key']} (link already existed)")
                links_ok += 1
            else:
                warn(str(e))

    # ── summary ──────────────────────────────────────────────────────────────
    banner("COMPLETE")
    print(f"  Story       : {JIRA_BASE}/browse/{issue_key}")
    print(f"  Summary     : {summary}")
    print(f"  Folder      : {folder_path}")
    print(f"  Test cases  : {', '.join(test_keys)}")
    print(f"  Test Set    : {testset_key}  -> {JIRA_BASE}/browse/{testset_key}" if testset_key else "  Test Set    : (dry-run)")
    print(f"  Test Plan   : {JIRA_BASE}/browse/{TEST_PLAN}")
    print(f"  Test Exec   : {JIRA_BASE}/browse/{TEST_EXEC}")
    print()


# ── CLI ───────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Dodokpo QA Automation — full Xray workflow for a Jira story")
    parser.add_argument("--issue",       required=True, help="Jira story key, e.g. DK26-200")
    parser.add_argument("--folder",      default="frontend", choices=["frontend", "backend"],
                        help="Target Xray folder (default: frontend)")
    parser.add_argument("--dry-run",     action="store_true",
                        help="Print what would happen without writing anything")
    parser.add_argument("--skip-format", action="store_true",
                        help="Skip rewriting the ticket description")
    args = parser.parse_args()
    run(args.issue, folder_key=args.folder, dry_run=args.dry_run, skip_format=args.skip_format)


if __name__ == "__main__":
    main()
