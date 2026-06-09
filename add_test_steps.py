"""
Add Xray test steps to DK26-1710..DK26-1718 (Dark Mode test cases).
Each step uses addTestStep(issueId, step: {action, data, result}).
Expected result is placed on the final step of each test.
"""
import io, sys, json, urllib.request, urllib.error
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
XRAY_AUTH = "https://xray.cloud.getxray.app/api/v2/authenticate"
XRAY_GQL  = "https://xray.cloud.getxray.app/api/v2/graphql"
CLIENT_ID  = _ENV.get("XRAY_CLIENT_ID", "")
CLIENT_SEC = _ENV.get("XRAY_CLIENT_SECRET", "")

# Authenticate
r = urllib.request.urlopen(
    urllib.request.Request(XRAY_AUTH,
        data=json.dumps({"client_id": CLIENT_ID, "client_secret": CLIENT_SEC}).encode(),
        method="POST", headers={"Content-Type": "application/json"}),
    timeout=30)
TOKEN = r.read().decode().strip().strip('"')


def gql(query, variables=None):
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    body = json.dumps(payload).encode()
    req = urllib.request.Request(XRAY_GQL, data=body, method="POST",
        headers={"Authorization": f"Bearer {TOKEN}",
                 "Content-Type": "application/json", "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r2:
            return json.loads(r2.read())
    except urllib.error.HTTPError as e:
        return {"httpError": e.code, "body": e.read().decode()[:400]}


# issueId (Xray numeric), tc_id, list of (action, data, result) tuples
# Only the LAST step of a test carries the expected result; others have result=""
TESTS = [
    {
        "issueId": "120311",
        "key":     "DK26-1710",
        "tc_id":   "TC-DM-001",
        "steps": [
            ("Open the user profile or header menu",                         "",                                                    ""),
            ("Locate the dark mode toggle",                                  "",                                                    ""),
            ("Turn on dark mode",                                            "",                                                    "Dark mode activates immediately; UI switches to dark theme without page reload"),
        ],
    },
    {
        "issueId": "120312",
        "key":     "DK26-1711",
        "tc_id":   "TC-DM-002",
        "steps": [
            ("Navigate to the Dashboard",                                    "Dark mode is enabled",                                "Dashboard renders fully in dark theme with no light-mode elements"),
        ],
    },
    {
        "issueId": "120314",
        "key":     "DK26-1712",
        "tc_id":   "TC-DM-003",
        "steps": [
            ("Navigate to an assessment screen",                             "Dark mode is enabled",                                "Assessment screen renders fully in dark theme"),
        ],
    },
    {
        "issueId": "120315",
        "key":     "DK26-1713",
        "tc_id":   "TC-DM-004",
        "steps": [
            ("Navigate to an admin page",                                    "Dark mode is enabled",                                "Admin page renders fully in dark theme"),
        ],
    },
    {
        "issueId": "120316",
        "key":     "DK26-1714",
        "tc_id":   "TC-DM-005",
        "steps": [
            ("Open a modal or dialog from any page",                         "Dark mode is enabled",                                "Modal or dialog renders in dark theme; no light-mode bleed"),
        ],
    },
    {
        "issueId": "120317",
        "key":     "DK26-1715",
        "tc_id":   "TC-DM-006",
        "steps": [
            ("Inspect text, icons, buttons, and interactive elements across dark theme pages", "Dark mode is enabled",             ""),
            ("Run a contrast-ratio check on key UI elements",               "",                                                    "All UI elements meet WCAG AA contrast ratio >= 4.5:1"),
        ],
    },
    {
        "issueId": "120318",
        "key":     "DK26-1716",
        "tc_id":   "TC-DM-007",
        "steps": [
            ("Refresh the browser page",                                     "Dark mode is enabled",                                "Dark mode remains active after refresh; preference is retained"),
        ],
    },
    {
        "issueId": "120319",
        "key":     "DK26-1717",
        "tc_id":   "TC-DM-008",
        "steps": [
            ("Sign out of the application",                                  "Dark mode is enabled",                                ""),
            ("Sign back in",                                                 "",                                                    "Dark mode preference is retained after sign-in"),
        ],
    },
    {
        "issueId": "120320",
        "key":     "DK26-1718",
        "tc_id":   "TC-DM-009",
        "steps": [
            ("Open the profile or header menu",                              "Dark mode is enabled",                                ""),
            ("Turn off the dark mode toggle",                                "",                                                    "UI switches back to light theme immediately; toggle reflects off state"),
        ],
    },
]

ADD_STEP_MUTATION = """
mutation AddStep($issueId: String!, $step: CreateStepInput!) {
  addTestStep(issueId: $issueId, step: $step) {
    id
    action
    data
    result
  }
}
"""

total_steps = 0
total_ok    = 0

for tc in TESTS:
    issue_id = tc["issueId"]
    key      = tc["key"]
    tc_id    = tc["tc_id"]
    print(f"\n{key} ({tc_id})")

    for i, (action, data, result) in enumerate(tc["steps"], 1):
        resp = gql(ADD_STEP_MUTATION, {
            "issueId": issue_id,
            "step": {"action": action, "data": data, "result": result},
        })
        total_steps += 1
        errs = resp.get("errors")
        if errs or "httpError" in resp:
            msg = errs or resp.get("body", "")
            print(f"  WARN step {i}: {msg}")
        else:
            step_data = (resp.get("data") or {}).get("addTestStep") or {}
            print(f"  OK   step {i}: {action[:60]}")
            total_ok += 1

print(f"\n{'='*50}")
print(f"Done: {total_ok}/{total_steps} steps added across {len(TESTS)} test cases.")
print("Verify at: https://amali-tech.atlassian.net/browse/DK26-1710")
