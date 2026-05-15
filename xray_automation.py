import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional

# Credentials may be provided via environment variables:
# JIRA_EMAIL, JIRA_API_TOKEN, XRAY_CLIENT_ID, XRAY_CLIENT_SECRET
CONFIG_FILE = "jira-xray-config.json"


def load_config(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def format_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True)


class JiraXrayAutomation:
    def __init__(self, config: Dict[str, Any], dry_run: bool = False):
        self.config = config
        self.dry_run = dry_run
        self.jira_config = config.get("jira", {})
        self.xray_config = config.get("xray", {})
        self.jira_base = (
            self.jira_config.get("base_url")
            or config.get("jira_base_url")
            or ""
        )
        self.jira_base = self.jira_base.rstrip("/")
        self.xray_base = (
            self.xray_config.get("base_url")
            or config.get("base_url")
            or ""
        ).rstrip("/")
        self.xray_graphql = (
            self.xray_config.get("graphql_url")
            or config.get("api", {}).get("graphql_endpoint")
            or ""
        ).rstrip("/")
        self.xray_auth_url = (
            self.xray_config.get("auth_url")
            or config.get("api", {}).get("authentication_endpoint")
            or f"{self.xray_base}/authenticate"
        )
        self.jira_email = (
            self.jira_config.get("email")
            or self.jira_config.get("Email")
            or os.environ.get("JIRA_EMAIL")
        )
        self.jira_api_token = self.jira_config.get("api_token") or os.environ.get("JIRA_API_TOKEN")
        self.xray_client_id = self.xray_config.get("client_id") or config.get("client_id") or os.environ.get("XRAY_CLIENT_ID")
        self.xray_client_secret = self.xray_config.get("client_secret") or config.get("client_secret") or os.environ.get("XRAY_CLIENT_SECRET")
        self.xray_token: Optional[str] = None

    def _check_auth(self) -> None:
        if not self.jira_email or not self.jira_api_token:
            raise ValueError(
                "Jira credentials are missing. Set jira.email and jira.api_token in jira-xray-config.json or JIRA_EMAIL/JIRA_API_TOKEN environment variables."
            )
        if not self.xray_client_id or not self.xray_client_secret:
            raise ValueError(
                "Xray credentials are missing. Set xray.client_id and xray.client_secret in jira-xray-config.json or XRAY_CLIENT_ID/XRAY_CLIENT_SECRET environment variables."
            )

    def _request(self, method: str, url: str, body: Optional[bytes] = None, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        request_headers = {"Accept": "application/json"}
        if headers:
            request_headers.update(headers)
        request = urllib.request.Request(url, data=body, headers=request_headers, method=method)
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                raw = response.read().decode("utf-8")
                if not raw:
                    return {}
                return json.loads(raw)
        except urllib.error.HTTPError as exc:
            message = exc.read().decode("utf-8")
            raise RuntimeError(f"HTTP {exc.code} error for {url}: {message}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"Connection error for {url}: {exc.reason}") from exc

    def jira_headers(self) -> Dict[str, str]:
        token = base64.b64encode(f"{self.jira_email}:{self.jira_api_token}".encode("utf-8")).decode("utf-8")
        return {
            "Authorization": f"Basic {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def xray_headers(self) -> Dict[str, str]:
        if not self.xray_token:
            self.authenticate_xray()
        return {"Authorization": f"Bearer {self.xray_token}", "Content-Type": "application/json", "Accept": "application/json"}

    def authenticate_xray(self) -> None:
        if self.dry_run:
            print("[dry-run] would authenticate against Xray to get bearer token")
            self.xray_token = "DRY_RUN_TOKEN"
            return
        self._check_auth()
        auth_url = self.xray_auth_url
        body = json.dumps({
            "client_id": self.xray_client_id,
            "client_secret": self.xray_client_secret,
        }).encode("utf-8")
        response = self._request("POST", auth_url, body=body, headers={"Content-Type": "application/json"})
        if isinstance(response, str):
            self.xray_token = response
        elif isinstance(response, dict) and response.get("token"):
            self.xray_token = response["token"]
        else:
            raise RuntimeError("Unexpected Xray authentication response: {}".format(format_json(response)))

    def jira_request(self, method: str, path: str, body: Optional[dict] = None, params: Optional[dict] = None) -> dict:
        if self.dry_run:
            print(f"[dry-run] Jira {method} {path} params={params} body={body}")
            return {}
        if not self.jira_base:
            raise ValueError("jira.base_url is required in config")
        url = urllib.parse.urljoin(self.jira_base + "/", path.lstrip("/"))
        if params:
            url = f"{url}?{urllib.parse.urlencode(params)}"
        body_bytes = json.dumps(body).encode("utf-8") if body is not None else None
        return self._request(method, url, body=body_bytes, headers=self.jira_headers())

    def xray_request(self, method: str, path: str, body: Optional[dict] = None, params: Optional[dict] = None) -> dict:
        if self.dry_run:
            print(f"[dry-run] Xray {method} {path} params={params} body={body}")
            return {}
        if not self.xray_base:
            raise ValueError("xray.base_url is required in config")
        url = urllib.parse.urljoin(self.xray_base + "/", path.lstrip("/"))
        if params:
            url = f"{url}?{urllib.parse.urlencode(params)}"
        body_bytes = json.dumps(body).encode("utf-8") if body is not None else None
        return self._request(method, url, body=body_bytes, headers=self.xray_headers())

    def get_issue(self, issue_key: str) -> dict:
        if self.dry_run:
            print(f"[dry-run] would fetch Jira issue {issue_key}")
            return {"fields": {"summary": f"[dry-run] {issue_key} summary", "issuelinks": []}}
        return self.jira_request("GET", f"/rest/api/3/issue/{issue_key}")

    def find_linked_test_keys(self, issue_data: dict) -> List[str]:
        tests: List[str] = []
        fields = issue_data.get("fields", {})
        for link in fields.get("issuelinks", []):
            resolved = link.get("outwardIssue") or link.get("inwardIssue")
            if not resolved:
                continue
            issue_type = resolved.get("fields", {}).get("issuetype", {}).get("name", "")
            key = resolved.get("key")
            if issue_type.lower() == "test" and key:
                tests.append(key)
        return sorted(set(tests))

    def find_or_create_xray_subfolder(self, parent_folder_id: str, story_key: str) -> str:
        # Some Xray Cloud GraphQL folder queries vary across versions. To be resilient,
        # attempt to create the folder and return its id. If creation fails because it
        # already exists, the mutation should return an error which will be surfaced.
        print(f"Creating Xray subfolder {story_key} under parent folder {parent_folder_id}")
        return self.create_xray_folder(parent_folder_id, story_key)

    def xray_graphql_request(self, query: str, variables: Optional[dict] = None) -> dict:
        if self.dry_run:
            print(f"[dry-run] Xray GraphQL query: {query} variables={variables}")
            return {}
        if not self.xray_graphql:
            raise RuntimeError("Xray GraphQL endpoint is not configured in the config file")
        payload = {"query": query}
        if variables:
            payload["variables"] = variables
        body_bytes = json.dumps(payload).encode("utf-8")
        return self._request("POST", self.xray_graphql, body=body_bytes, headers=self.xray_headers())

    def _dict_to_graphql_input(self, obj: Any) -> str:
        # Convert Python dict/list/primitive into GraphQL input literal
        if isinstance(obj, dict):
            inner = []
            for k, v in obj.items():
                inner.append(f"{k}: {self._dict_to_graphql_input(v)}")
            return "{" + ", ".join(inner) + "}"
        if isinstance(obj, list):
            return "[" + ", ".join(self._dict_to_graphql_input(x) for x in obj) + "]"
        if obj is None:
            return "null"
        if isinstance(obj, bool):
            return "true" if obj else "false"
        # numbers
        if isinstance(obj, (int, float)):
            return str(obj)
        # strings
        s = str(obj).replace('"', '\\"')
        return f'"{s}"'

    def find_xray_subfolder(self, parent_folder_id: str, folder_name: str) -> Optional[str]:
        # Use GraphQL on Xray Cloud to list children of a folder
        # Build a safe GraphQL query string (Xray Cloud uses getFolder)
        query = f'query {{ getFolder(id:"{parent_folder_id}") {{ id name children {{ id name }} }} }}'
        resp = self.xray_graphql_request(query)
        folder = (resp.get("data") or {}).get("folder") or {}
        for child in folder.get("children", []):
            if child.get("name") == folder_name:
                return child.get("id")
        return None

    def create_xray_folder(self, parent_folder_id: str, folder_name: str) -> str:
        # Use GraphQL mutation to create a folder in Xray Cloud.
        # Different Xray Cloud versions expect different mutation signatures; try multiple.
        safe_name = folder_name.replace('"', '\\"')
        attempts = [
            # common: createFolder(path: "parent", name: "child") returning folder
            f'mutation {{ createFolder(path:"{parent_folder_id}", name:"{safe_name}") {{ folder {{ id name }} }} }}',
            # variant: createFolder(path, name) returning id/name directly
            f'mutation {{ createFolder(path:"{parent_folder_id}", name:"{safe_name}") {{ id name }} }}',
            # variant: createFolder(path, folderName)
            f'mutation {{ createFolder(path:"{parent_folder_id}", folderName:"{safe_name}") {{ folder {{ id name }} }} }}',
            # variant: createFolder(path) where path is parent/child
            f'mutation {{ createFolder(path:"{parent_folder_id}/{safe_name}") {{ folder {{ id name }} }} }}',
        ]
        last_exc = None
        for mut in attempts:
            try:
                resp = self.xray_graphql_request(mut)
            except Exception as exc:
                print(f"GraphQL attempt failed: {exc}")
                last_exc = exc
                continue
            data = (resp.get("data") or {})
            # inspect response for folder id
            # try common shapes
            if "createFolder" in data and isinstance(data["createFolder"], dict):
                cf = data["createFolder"]
                if isinstance(cf.get("folder"), dict):
                    fid = cf["folder"].get("id")
                    if fid:
                        return str(fid)
                if cf.get("id"):
                    return str(cf.get("id"))
            # sometimes top-level key varies
            for val in data.values():
                if isinstance(val, dict):
                    if val.get("id"):
                        return str(val.get("id"))
                    if isinstance(val.get("folder"), dict) and val.get("folder").get("id"):
                        return str(val.get("folder").get("id"))
        raise RuntimeError(f"Could not create Xray folder under {parent_folder_id}; last error: {last_exc}")

    def create_folder_graphql(self, project_id: str, path: str, test_issue_ids: List[str]) -> dict:
        # mutation: createFolder(projectId: "13358", path: "Q1/.../DK26-468", testIssueIds: ["106874"]){ folder { path } warnings }
        safe_path = path.replace('"', '\\"')
        ids_array = json.dumps(test_issue_ids)
        mutation = f'mutation {{ createFolder(projectId: "{project_id}", path: "{safe_path}", testIssueIds: {ids_array}) {{ folder {{ path }} warnings }} }}'
        resp = self.xray_graphql_request(mutation)
        return resp

    def add_tests_to_testplan_graphql(self, testplan_issue_id: str, test_issue_ids: List[str]) -> dict:
        ids_array = json.dumps(test_issue_ids)
        # require a selection set
        mutation = f'mutation {{ addTestsToTestPlan(issueId: "{testplan_issue_id}", testIssueIds: {ids_array}) {{ __typename }} }}'
        resp = self.xray_graphql_request(mutation)
        return resp

    def add_tests_to_testexecution_graphql(self, testexec_issue_id: str, test_issue_ids: List[str]) -> dict:
        ids_array = json.dumps(test_issue_ids)
        mutation = f'mutation {{ addTestsToTestExecution(issueId: "{testexec_issue_id}", testIssueIds: {ids_array}) {{ __typename }} }}'
        resp = self.xray_graphql_request(mutation)
        return resp

    def create_test_set_graphql(self, jira_fields: dict, test_issue_ids: Optional[List[str]] = None) -> dict:
        tests_arg = f", testIssueIds: {json.dumps(test_issue_ids)}" if test_issue_ids else ""
        jira_input = self._dict_to_graphql_input(jira_fields)
        # request a generic selection
        mutation = f'mutation {{ createTestSet(jira: {jira_input}{tests_arg}) {{ __typename ... on CreateTestSetResult {{ issueKey id issueId warnings }} }} }}'
        resp = self.xray_graphql_request(mutation)
        return resp

    def add_tests_to_testset_graphql(self, testset_issue_id: str, test_issue_ids: List[str]) -> dict:
        ids_array = json.dumps(test_issue_ids)
        mutation = f'mutation {{ addTestsToTestSet(issueId: "{testset_issue_id}", testIssueIds: {ids_array}) {{ __typename }} }}'
        resp = self.xray_graphql_request(mutation)
        return resp

    def create_test_set(self, issue_key: str, folder_id: str, summary: str) -> str:
        payload = {
            "projectKey": self.jira_config.get("project_key"),
            "summary": f"Test Set for {issue_key}",
            "folderId": folder_id,
            "description": f"Automated test set for {issue_key} created from issue summary: {summary}",
        }
        response = self.xray_request("POST", "/api/v2/testset", body=payload)
        return str(response.get("key") or response.get("testSetKey") or "")

    def add_tests_to_test_set(self, test_set_key: str, test_keys: List[str]) -> None:
        if not test_keys:
            print("No test keys to add to test set.")
            return
        payload = {"add": test_keys}
        self.xray_request("POST", f"/api/v2/testset/{test_set_key}/test", body=payload)
        print(f"Added {len(test_keys)} test(s) to test set {test_set_key}")

    def add_test_set_to_plan(self, test_plan_key: str, test_set_key: str) -> None:
        if not test_plan_key:
            print("No test plan key configured; skipping plan linkage.")
            return
        payload = {"testSetKey": test_set_key}
        self.xray_request("POST", f"/api/v2/testplan/{test_plan_key}/testset", body=payload)
        print(f"Linked test set {test_set_key} to test plan {test_plan_key}")

    def add_test_set_to_execution(self, test_execution_key: str, test_set_key: str) -> None:
        if not test_execution_key:
            print("No test execution key configured; skipping execution linkage.")
            return
        payload = {"testSetKey": test_set_key}
        self.xray_request("POST", f"/api/v2/testexecution/{test_execution_key}/testset", body=payload)
        print(f"Linked test set {test_set_key} to test execution {test_execution_key}")

    def transition_issue_to_done(self, issue_key: str) -> None:
        # Backwards compatible: attempt transition to 'Done' if available
        return self.transition_issue_by_name(issue_key, "Done")

    def transition_issue_by_name(self, issue_key: str, transition_name: str) -> bool:
        transitions = self.jira_request("GET", f"/rest/api/3/issue/{issue_key}/transitions")
        available = transitions.get("transitions", [])
        # try exact match, then case-insensitive
        candidates = [t for t in available if t.get("name") == transition_name]
        if not candidates:
            candidates = [t for t in available if t.get("name", "").lower() == transition_name.lower()]
        if not candidates:
            print(f"Could not find transition '{transition_name}' for {issue_key}. Available: {[t.get('name') for t in available]}")
            return False
        transition_id = candidates[0].get("id")
        if self.dry_run:
            print(f"[dry-run] would transition {issue_key} to '{transition_name}' using transition id {transition_id}")
            return True
        self.jira_request("POST", f"/rest/api/3/issue/{issue_key}/transitions", body={"transition": {"id": transition_id}})
        print(f"Transitioned issue {issue_key} to '{transition_name}'")
        return True

    def execute(self, issue_key: str, parent_folder_key: Optional[str], test_plan_key: Optional[str], transition_name: Optional[str] = None, preview: bool = False, test_keys: Optional[str] = None, existing_testset: Optional[str] = None, execution_transition: Optional[str] = None, story_transition: Optional[str] = None) -> None:
        issue_data = self.get_issue(issue_key)
        summary = issue_data.get("fields", {}).get("summary", "")
        if not summary:
            raise RuntimeError(f"Could not load issue summary for {issue_key}")

        print(f"Processing story {issue_key}: {summary}")
        folder_id = None

        # Determine parent folder path. parent_folder_key may be an explicit path (contains '/')
        parent_path = None
        if parent_folder_key and ("/" in parent_folder_key or " " in parent_folder_key):
            parent_path = parent_folder_key
        else:
            # Try to use configured folder mapping (if it contains a path instead of id)
            candidate = self.config.get("folders", {}).get(parent_folder_key or self.config.get("default_target_folder", "q1_frontend"))
            if candidate and isinstance(candidate, str) and ("/" in candidate or " " in candidate):
                parent_path = candidate

        if not parent_path:
            raise RuntimeError("Parent folder path is required for Xray Cloud GraphQL operations. Provide --parent-folder with a path like 'Q1 PIP Conclusion/Backend'.")

        full_path = f"{parent_path}/{issue_key} - {summary}"
        print(f"Creating/using Xray folder path: {full_path}")

        linked_tests_keys = self.find_linked_test_keys(issue_data)
        print(f"Linked test cases discovered for {issue_key}: {linked_tests_keys}")

        # Resolve numeric issue IDs required by Xray GraphQL
        linked_tests_ids: List[str] = []
        for tk in linked_tests_keys:
            try:
                tdata = self.get_issue(tk)
                tid = tdata.get("id")
                if tid:
                    linked_tests_ids.append(str(tid))
            except Exception as exc:
                print(f"Warning: could not resolve numeric id for test {tk}: {exc}")

        if preview:
            print("Preview mode enabled; no changes will be written to Jira or Xray.")
            print(f"Would create/find Xray folder path: {full_path}")
            if linked_tests_ids:
                print(f"Would add linked test cases to folder: {linked_tests_keys} (numeric ids: {linked_tests_ids})")
            plan_key = test_plan_key or self.config.get("folders", {}).get("test_plan")
            exec_key = self.config.get("folders", {}).get("test_execution")
            print(f"Would link tests to Test Plan: {plan_key}")
            print(f"Would link tests to Test Execution: {exec_key}")
            print(f"Would transition {issue_key} and linked tests to Done")
            return

        # Create folder (and add tests to it if any)
        project_id = self.jira_config.get("project_id") or self.jira_config.get("projectId")
        try:
            resp = self.create_folder_graphql(project_id, full_path, linked_tests_ids)
            print(f"Created/updated folder: {resp}")
        except Exception as exc:
            print(f"Warning: folder creation failed: {exc}. Continuing to link tests/transition issues.")

        # If explicit test_keys were provided via CLI, override discovered linked tests
        if test_keys:
            provided = [k.strip() for k in test_keys.split(",") if k.strip()]
            linked_tests_keys = provided
            linked_tests_ids = []
            for tk in linked_tests_keys:
                try:
                    tdata = self.get_issue(tk)
                    tid = tdata.get("id")
                    if tid:
                        linked_tests_ids.append(str(tid))
                except Exception as exc:
                    print(f"Warning: could not resolve numeric id for provided test {tk}: {exc}")

        # Create a Test Set and add tests to it
        testset_issue_id = None
        # If user supplied an existing test set, use it (resolve numeric id if needed)
        if existing_testset:
            # if looks like a key (contains '-'), resolve via Jira to numeric id
            if isinstance(existing_testset, str) and '-' in existing_testset:
                try:
                    ej = self.get_issue(existing_testset)
                    testset_issue_id = ej.get('id') or existing_testset
                except Exception:
                    testset_issue_id = existing_testset
            else:
                testset_issue_id = existing_testset
        elif linked_tests_ids:
            jira_fields = {
                "summary": f"Test Set for {issue_key}",
                "project": {"key": self.jira_config.get("project_key")},
                "issuetype": {"name": "Test Set"}
            }
            try:
                cs = self.create_test_set_graphql(jira_fields, linked_tests_ids)
                print(f"Create Test Set response: {cs}")
                testset_issue_id = (cs.get("data") or {}).get("createTestSet", {}).get("issueId")
                if not testset_issue_id:
                    print("Warning: createTestSet did not return issueId")
            except Exception as exc:
                print(f"Warning: createTestSet failed: {exc}")

        # If createTestSet didn't create it, attempt to create a test set without tests
        if not testset_issue_id:
            try:
                cs = self.create_test_set_graphql({"summary": f"Test Set for {issue_key}", "project": {"key": self.jira_config.get("project_key")}, "issuetype": {"name": "Test Set"}}, None)
                # Try common fields: issueId, issueKey, id
                cd = (cs.get("data") or {}).get("createTestSet") or {}
                testset_issue_id = cd.get("issueId") or cd.get("issueKey") or cd.get("id")
                print(f"Created empty Test Set (graphql response): {cs}")
            except Exception as exc:
                print(f"Warning: createTestSet graphql failed: {exc}")
        # If still no testset_issue_id, create via Jira REST as fallback
        if not testset_issue_id:
            try:
                payload = {"fields": {"project": {"key": self.jira_config.get("project_key")}, "summary": f"Test Set for {issue_key}", "issuetype": {"name": "Test Set"}}}
                jr = self.jira_request("POST", "/rest/api/3/issue", body=payload)
                testset_issue_id = jr.get("id") or jr.get("key")
                print(f"Created Test Set via Jira REST: {jr}")
            except Exception as exc:
                print(f"Warning: could not create Test Set via Jira REST: {exc}")

        # If we have testset_issue_id and tests, ensure tests are added to the test set
        if testset_issue_id and linked_tests_ids:
            try:
                at = self.add_tests_to_testset_graphql(testset_issue_id, linked_tests_ids)
                print(f"Added tests to Test Set response: {at}")
            except Exception as exc:
                print(f"Warning: could not add tests to Test Set: {exc}")

        # Link tests to Test Plan and Test Execution (if configured)
        plan_key = test_plan_key or self.config.get("folders", {}).get("test_plan")
        exec_key = self.config.get("folders", {}).get("test_execution")
        # resolve numeric ids for plan/execution if keys provided
        plan_id = None
        exec_id = None
        if plan_key:
            try:
                pd = self.get_issue(plan_key)
                plan_id = pd.get("id")
            except Exception as exc:
                print(f"Warning: could not resolve Test Plan id for {plan_key}: {exc}")
        if exec_key:
            try:
                ed = self.get_issue(exec_key)
                exec_id = ed.get("id")
            except Exception as exc:
                print(f"Warning: could not resolve Test Execution id for {exec_key}: {exc}")

        if linked_tests_ids and plan_id:
            try:
                self.add_tests_to_testplan_graphql(plan_id, linked_tests_ids)
                print(f"Linked {len(linked_tests_ids)} test(s) to Test Plan {plan_key}")
            except Exception as exc:
                print(f"Warning: could not link tests to Test Plan {plan_key}: {exc}")
        if linked_tests_ids and exec_id:
            try:
                self.add_tests_to_testexecution_graphql(exec_id, linked_tests_ids)
                print(f"Linked {len(linked_tests_ids)} test(s) to Test Execution {exec_key}")
            except Exception as exc:
                print(f"Warning: could not link tests to Test Execution {exec_key}: {exc}")

        # Transition story and linked tests using provided transition name (or 'Done' default)
        transition_to = transition_name or "Done"
        # Transition Test Execution issue to requested name (or fallback)
        exec_transition = execution_transition or transition_to
        story_transition = story_transition or transition_to
        if exec_key:
            ok = self.transition_issue_by_name(exec_key, exec_transition)
            if not ok and exec_transition.lower() == "done":
                self.transition_issue_by_name(exec_key, "Completed Test Cases, Test Sets")
        ok_story = self.transition_issue_by_name(issue_key, story_transition)
        if not ok_story and story_transition.lower() == "done":
            self.transition_issue_by_name(issue_key, "Submit for PO Review")
        # Do not transition individual test cases by default
        # for test_key in linked_tests_keys:
        #     self.transition_issue_by_name(test_key, transition_to)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Automate Xray test linkage and Jira transitions for a story.")
    parser.add_argument("--issue", help="Jira issue key to process", default=None)
    parser.add_argument("--parent-folder", help="Folder path in Xray (e.g. 'Q1 PIP Conclusion/Backend')", default=None)
    parser.add_argument("--test-plan-key", help="Test Plan key to link the new Test Set to", default=None)
    parser.add_argument("--test-keys", help="Comma-separated test issue keys to add (e.g. DK26-716,DK26-717)", default=None)
    parser.add_argument("--dry-run", help="Enable dry run mode without modifying Jira/Xray", action="store_true")
    parser.add_argument("--preview", help="Preview the workflow without writing changes", action="store_true")
    parser.add_argument("--transition-name", help="Transition name to apply to issues (default: Done)", default="Done")
    parser.add_argument("--execution-transition", help="Transition name to apply to Test Execution issues (optional)", default=None)
    parser.add_argument("--story-transition", help="Transition name to apply to story issue (optional)", default=None)
    parser.add_argument("--existing-testset", help="Existing Test Set issue key or id to use instead of creating a new one", default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = load_config(CONFIG_FILE)
    automation = JiraXrayAutomation(config=config, dry_run=args.dry_run)
    issue_key = args.issue or config.get("default_issue_key")
    if not issue_key:
        print("No issue key provided. Set --issue or default_issue_key in agent-config.json.")
        return 1
    try:
        automation.execute(issue_key, args.parent_folder, args.test_plan_key, args.transition_name, preview=args.preview or args.dry_run, test_keys=args.test_keys, existing_testset=args.existing_testset, execution_transition=args.execution_transition, story_transition=args.story_transition)
    except Exception as exc:
        print(f"ERROR: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())