#!/usr/bin/env python
"""Upload generated test cases to Jira/Xray.

Adapted from upload_xray.py (origin/testcasegenerator) with three changes:
  - credentials come from jira-xray-config.json, not a .env file
  - the destination folder is a parameter, not a hardcoded Quarter 2 root
  - the story's Jira description is never rewritten

Usage:
    python xray_upload.py --issue DK26-3007 --folder "Quarter 4/Ebenezer/Frontend" --dry-run
    python xray_upload.py --issue DK26-3007 --folder "Quarter 4/Ebenezer/Frontend"
"""
import argparse
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(ROOT, "jira-xray-config.json"), encoding="utf-8") as _h:
    CFG = json.load(_h)

JIRA_BASE = (CFG["jira"].get("base_url") or CFG.get("jira_base_url", "")).rstrip("/")
JIRA_AUTH = base64.b64encode("{}:{}".format(
    CFG["jira"].get("email") or CFG["jira"].get("Email"),
    CFG["jira"]["api_token"]).encode()).decode()
PROJECT_KEY = CFG["jira"].get("project_key", "DK26")
PROJECT_ID = CFG["jira"].get("project_id", "13358")
XRAY_AUTH = CFG["api"]["authentication_endpoint"]
XRAY_GQL = CFG["api"]["graphql_endpoint"]
TEST_PLAN = CFG["folders"].get("test_plan", "DK26-118")
TEST_EXEC = CFG["folders"].get("test_execution", "DK26-195")

W = 66
_token = None


def banner(t):
    print("\n" + "=" * W + "\n  " + t + "\n" + "=" * W)


def step(n, total, t):
    print("\n[{}/{}] {}\n{}".format(n, total, t, "-" * W))


def ok(m):
    print("  [OK]   " + m)


def warn(m):
    print("  [WARN] " + m)


def info(m):
    print("         " + m)


def _send(req, timeout, safe_to_resend, attempts=4):
    """Open `req`, retrying network failures. A failure to connect never reached the
    server, so it is always retried; a timeout after sending is retried only when
    resending cannot create anything twice (`safe_to_resend`)."""
    for attempt in range(1, attempts + 1):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read().decode("utf-8")
        except urllib.error.HTTPError:
            raise
        except urllib.error.URLError as exc:
            if attempt == attempts:
                raise
            warn("network error ({}), retrying".format(exc.reason))
        except (TimeoutError, ConnectionError) as exc:
            if not safe_to_resend or attempt == attempts:
                raise
            warn("network error ({}), retrying".format(exc))
        time.sleep(3 * 2 ** (attempt - 1))


def jira(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(JIRA_BASE + path, data=data, method=method, headers={
        "Authorization": "Basic " + JIRA_AUTH,
        "Content-Type": "application/json",
        "Accept": "application/json",
    })
    try:
        raw = _send(req, 45, safe_to_resend=method in ("GET", "PUT", "DELETE"))
        return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        raise RuntimeError("Jira {} {} HTTP {}: {}".format(
            method, path, exc.code, exc.read().decode("utf-8", "replace")[:300]))


def xray_token():
    global _token
    if _token:
        return _token
    body = json.dumps({"client_id": CFG["client_id"],
                       "client_secret": CFG["client_secret"]}).encode()
    req = urllib.request.Request(XRAY_AUTH, data=body, method="POST",
                                 headers={"Content-Type": "application/json"})
    _token = _send(req, 45, safe_to_resend=True).strip().strip('"')
    return _token


def gql(query, variables=None):
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    req = urllib.request.Request(XRAY_GQL, data=json.dumps(payload).encode(), method="POST",
                                 headers={"Authorization": "Bearer " + xray_token(),
                                          "Content-Type": "application/json"})
    try:
        raw = _send(req, 60, safe_to_resend=not query.lstrip().startswith("mutation"))
        return json.loads(raw or "{}")
    except urllib.error.HTTPError as exc:
        raise RuntimeError("Xray GraphQL HTTP {}: {}".format(
            exc.code, exc.read().decode("utf-8", "replace")[:300]))


def gql_ok(resp, label):
    if resp.get("errors"):
        warn("{}: {}".format(label, json.dumps(resp["errors"])[:300]))
        return False
    ok(label)
    return True


# ── ADF helpers ───────────────────────────────────────────────────────────────
def _t(text):
    return {"type": "text", "text": text}


def para(text):
    return {"type": "paragraph", "content": [_t(text)]}


def heading(level, text):
    return {"type": "heading", "attrs": {"level": level}, "content": [_t(text)]}


def ordered(items):
    return {"type": "orderedList", "content": [
        {"type": "listItem", "content": [para(i)]} for i in items]}


def build_test_adf(preconditions, steps, expected):
    return {"type": "doc", "version": 1, "content": [
        heading(3, "Preconditions"), para(preconditions),
        heading(3, "Steps"), ordered(steps),
        heading(3, "Expected Result"), para(expected),
    ]}


def find_issue(issuetype, summary_prefix):
    """The existing issue of this type whose summary starts with `summary_prefix`, or None.
    Lets a rerun after an interruption reuse what was already created."""
    jql = 'project = {} AND issuetype = "{}" AND summary ~ "\\"{}\\""'.format(
        PROJECT_KEY, issuetype, summary_prefix.strip("[]"))
    resp = jira("GET", "/rest/api/3/search/jql?fields=summary&maxResults=20&jql="
                + urllib.parse.quote(jql))
    for issue in resp.get("issues", []):
        if issue["fields"]["summary"].startswith(summary_prefix):
            return {"key": issue["key"], "id": issue["id"]}
    return None


def linked_keys(issue_key):
    links = jira("GET", "/rest/api/3/issue/{}?fields=issuelinks".format(issue_key))["fields"]["issuelinks"]
    return {(l.get("inwardIssue") or l.get("outwardIssue"))["key"] for l in links}


def wait_for_xray(created, timeout=180, interval=6):
    """Return the keys Xray still has not registered as tests after `timeout` seconds."""
    pending = {c["id"]: c["key"] for c in created}
    deadline = time.time() + timeout
    while pending:
        for issue_id in list(pending):
            resp = gql('{{ getTest(issueId:"{}") {{ issueId }} }}'.format(issue_id))
            if (resp.get("data") or {}).get("getTest"):
                del pending[issue_id]
        if not pending or time.time() > deadline:
            break
        time.sleep(interval)
    return sorted(pending.values())


def run(issue_key, folder_root, dry_run):
    tests_file = os.path.join(ROOT, "{}_tests.json".format(issue_key))
    with open(tests_file, encoding="utf-8") as handle:
        data = json.load(handle)
    # Either a plain list of tests, or {"preconditions": [...], "tests": [...]}
    if isinstance(data, dict):
        test_cases, preconditions = data["tests"], data.get("preconditions", [])
    else:
        test_cases, preconditions = data, []

    story = jira("GET", "/rest/api/3/issue/{}".format(issue_key))
    summary = story["fields"]["summary"]

    TOTAL = 6
    banner("Xray Upload - {} {}".format(issue_key, "[DRY RUN]" if dry_run else ""))
    info("Story  : {}".format(summary))
    info("Tests  : {} test cases, {} preconditions".format(len(test_cases), len(preconditions)))
    info("Folder : {}/{} {}".format(folder_root, issue_key, summary))

    # ── STEP 1: create Jira test case issues ──────────────────────────────────
    step(1, TOTAL, "Create Jira Test Case issues")
    created = []
    for tc in test_cases:
        title = "[{}] {}".format(tc["id"], tc["title"])
        if dry_run:
            info("[dry-run] " + title)
            created.append({"key": "DK26-DRY", "id": "000000", "tc": tc})
            continue
        existing = find_issue("Test Cases", "[{}]".format(tc["id"]))
        if existing:
            created.append(dict(existing, tc=tc))
            ok("{}  {} (already exists)".format(existing["key"], title[:40]))
            continue
        resp = jira("POST", "/rest/api/3/issue", {"fields": {
            "project": {"key": PROJECT_KEY},
            "summary": title,
            "issuetype": {"name": "Test Cases"},
            "description": build_test_adf(tc["preconditions"], tc["steps"], tc["expected"]),
        }})
        created.append({"key": resp.get("key", ""), "id": resp.get("id", ""), "tc": tc})
        ok("{}  {}".format(resp.get("key"), title[:50]))

    test_ids = [c["id"] for c in created]
    ids_json = json.dumps(test_ids)

    # Xray registers new Jira issues asynchronously, and rejects a whole call if
    # any id in it is unknown, so wait until every test is registered first.
    if not dry_run:
        missing = wait_for_xray(created)
        if missing:
            warn("Xray has not registered: {}. Stopping before any Xray step so nothing "
                 "is half-done. Recreate these through Xray createTest, then rerun the "
                 "remaining steps.".format(", ".join(missing)))
            return 1
        ok("Xray has registered all {} tests".format(len(created)))

    # ── STEP 2: Xray folder ───────────────────────────────────────────────────
    step(2, TOTAL, "Create Xray folder")
    folder_path = "{}/{} {}".format(folder_root, issue_key, summary)
    info("Path: " + folder_path)
    if dry_run:
        info("[dry-run] skipped")
    else:
        path = "/" + folder_path.lstrip("/")
        exists = (gql('query($p:String!){{ getFolder(projectId:"{}", path:$p) {{ path }} }}'
                      .format(PROJECT_ID), {"p": path}).get("data") or {}).get("getFolder")
        if exists:
            resp = gql('mutation($p:String!,$i:[String]!){{ addIssuesToFolder(projectId:"{}", path:$p, '
                       'issueIds:$i) {{ folder {{ path }} warnings }} }}'.format(PROJECT_ID),
                       {"p": path, "i": test_ids})
            gql_ok(resp, "addIssuesToFolder (folder already exists)")
            warnings = ((resp.get("data") or {}).get("addIssuesToFolder") or {}).get("warnings") or []
        else:
            resp = gql('mutation($p:String!,$t:[String]){{ createFolder(projectId:"{}", path:$p, '
                       'testIssueIds:$t) {{ folder {{ path }} warnings }} }}'.format(PROJECT_ID),
                       {"p": path, "t": test_ids})
            gql_ok(resp, "createFolder")
            warnings = ((resp.get("data") or {}).get("createFolder") or {}).get("warnings") or []
        if warnings:
            warn("Folder warnings: {}".format(warnings))

    # ── STEP 3: Xray Preconditions, linked to their tests ─────────────────────
    step(3, TOTAL, "Create Xray Preconditions")
    pc_keys = {}
    CREATE_PC = ("mutation CreatePC($def:String!,$tests:[String],$folder:String,$jira:JSON!)"
                 "{createPrecondition(preconditionType:{name:\"Manual\"},definition:$def,"
                 "testIssueIds:$tests,folderPath:$folder,jira:$jira)"
                 "{precondition{issueId jira(fields:[\"key\"])} warnings}}")
    for pc in preconditions:
        linked_ids = [c["id"] for c in created if pc["id"] in c["tc"].get("precondition_ids", [])]
        title = "[{}] {}".format(pc["id"], pc["title"])
        if dry_run:
            info("[dry-run] {}  -> {} tests".format(title, len(linked_ids)))
            continue
        existing = find_issue("Precondition", "[{}]".format(pc["id"]))
        if existing:
            pc_keys[pc["id"]] = existing["key"]
            gql_ok(gql('mutation($p:String!,$t:[String]!){ addTestsToPrecondition(issueId:$p, '
                       'testIssueIds:$t) { addedTests warning } }',
                       {"p": existing["id"], "t": linked_ids}),
                   "{} already exists; linked to {} tests".format(existing["key"], len(linked_ids)))
            continue
        resp = gql(CREATE_PC, {"def": pc["definition"], "tests": linked_ids,
                               "folder": "/" + folder_path.lstrip("/"),
                               "jira": {"fields": {"summary": title,
                                                   "project": {"key": PROJECT_KEY}}}})
        if gql_ok(resp, "createPrecondition {}".format(pc["id"])):
            result = resp["data"]["createPrecondition"]
            pc_keys[pc["id"]] = (result["precondition"]["jira"] or {}).get("key")
            info("{} -> {} tests".format(pc_keys[pc["id"]], len(linked_ids)))
            if result.get("warnings"):
                warn("Precondition warnings: {}".format(result["warnings"]))

    # ── STEP 4: add test steps (before the execution, so runs include them) ──
    step(4, TOTAL, "Add Xray test steps")
    ADD_STEP = ("mutation AddStep($issueId:String!,$step:CreateStepInput!)"
                "{addTestStep(issueId:$issueId,step:$step){id}}")
    steps_added = 0
    for c in created:
        tc = c["tc"]
        if not dry_run:
            have = ((gql('{{ getTest(issueId:"{}") {{ steps {{ id }} }} }}'.format(c["id"]))
                     .get("data") or {}).get("getTest") or {}).get("steps") or []
            if have:
                info("{}: already has {} steps".format(c["key"], len(have)))
                continue
        for i, action in enumerate(tc["steps"]):
            last = i == len(tc["steps"]) - 1
            if dry_run:
                steps_added += 1
                continue
            resp = gql(ADD_STEP, {"issueId": c["id"], "step": {
                "action": action,
                "data": tc["preconditions"] if i == 0 else "",
                "result": tc["expected"] if last else "",
            }})
            if resp.get("errors"):
                warn("{} step {}: {}".format(c["key"], i + 1, json.dumps(resp["errors"])[:160]))
            else:
                steps_added += 1
        if not dry_run:
            info("{}: {} steps".format(c["key"], len(tc["steps"])))
    ok("{} steps added".format(steps_added))

    # ── STEP 5: Test Set + link to Plan / Execution ───────────────────────────
    step(5, TOTAL, "Create Test Set, link to Test Plan & Test Execution")
    testset_key = None
    if dry_run:
        info("[dry-run] skipped")
    else:
        ts_name = "Test Set - {} {}".format(issue_key, summary)
        existing = find_issue("Test Set", "Test Set - {} ".format(issue_key))
        if existing:
            testset_key = existing["key"]
            gql_ok(gql('mutation{{addTestsToTestSet(issueId:"{}",testIssueIds:{}){{addedTests warning}}}}'
                       .format(existing["id"], ids_json)), "Test Set {} already exists; tests added".format(testset_key))
        else:
            resp = gql('mutation($s:String!,$t:[String]){{ createTestSet(jira:{{fields:{{summary:$s, '
                       'project:{{key:"{}"}}, issuetype:{{name:"Test Set"}}}}}}, testIssueIds:$t) '
                       '{{ testSet {{ issueId jira(fields:["key"]) }} warnings }} }}'.format(PROJECT_KEY),
                       {"s": ts_name, "t": test_ids})
            gql_ok(resp, "createTestSet")
            ts = ((resp.get("data") or {}).get("createTestSet") or {}).get("testSet") or {}
            testset_key = (ts.get("jira") or {}).get("key")
        info("Test Set: {}".format(testset_key))

        plan_id = jira("GET", "/rest/api/3/issue/{}".format(TEST_PLAN)).get("id")
        exec_id = jira("GET", "/rest/api/3/issue/{}".format(TEST_EXEC)).get("id")
        gql_ok(gql('mutation{{addTestsToTestPlan(issueId:"{}",testIssueIds:{}){{__typename}}}}'
                   .format(plan_id, ids_json)), "addTestsToTestPlan ({})".format(TEST_PLAN))
        gql_ok(gql('mutation{{addTestsToTestExecution(issueId:"{}",testIssueIds:{}){{__typename}}}}'
                   .format(exec_id, ids_json)), "addTestsToTestExecution ({})".format(TEST_EXEC))

        already = linked_keys(testset_key) if testset_key else set()
        for target in (TEST_PLAN, TEST_EXEC):
            if not testset_key or target in already:
                continue
            try:
                jira("POST", "/rest/api/3/issueLink", {
                    "type": {"id": "10003"},
                    "inwardIssue": {"key": testset_key},
                    "outwardIssue": {"key": target},
                })
                ok("Relates: {} <-> {}".format(testset_key, target))
            except Exception as exc:
                warn(str(exc))

    # ── STEP 6: link test cases to the story ──────────────────────────────────
    step(6, TOTAL, "Link test cases to story {}".format(issue_key))
    linked = 0
    already = set() if dry_run else linked_keys(issue_key)
    for c in created:
        if dry_run or c["key"] in already:
            linked += 1
            continue
        try:
            jira("POST", "/rest/api/3/issueLink", {
                "type": {"id": "10006"},
                "inwardIssue": {"key": issue_key},
                "outwardIssue": {"key": c["key"]},
            })
            linked += 1
        except Exception as exc:
            warn("{}: {}".format(c["key"], str(exc)[:160]))
    ok("{} test cases linked".format(linked))

    banner("SUMMARY")
    print("  Story      : {} {}".format(issue_key, summary))
    print("  Folder     : {}".format(folder_path))
    print("  Test Set   : {}".format(testset_key or "(dry run)"))
    for pc_id, key in pc_keys.items():
        print("  Precond.   : {}  {}".format(key, pc_id))
    print("  Test cases : {}".format(len(created)))
    for c in created:
        print("     {}  {}".format(c["key"], c["tc"]["id"]))
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--issue", required=True)
    ap.add_argument("--folder", required=True, help="Xray parent folder path")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    return run(args.issue, args.folder.rstrip("/"), args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
