# Dodokpo QA Automation — Prompt Snippets

---

## How to Run a New Story (No API Key Needed)

Just tell Claude Code (VS Code):

```
Process ticket DK26-XXX
```

Claude will automatically:
1. Run `python fetch_story.py --issue DK26-XXX`  — fetch ticket from Jira
2. Read the acceptance criteria and generate test cases
3. Save them to `DK26-XXX_tests.json`
4. Run `python upload_xray.py --issue DK26-XXX`  — create everything in Xray

**That's the whole workflow. No Chrome Claude, no API key required.**

For backend tickets:
```
Process ticket DK26-XXX for backend
```

Dry-run (preview only, no writes):
```
Process ticket DK26-XXX dry-run
```

---

Copy-paste any block below directly into Claude Code or any AI agent.
Replace values inside `< >` before sending.

---

## Config & Credentials

| Item | Location |
|---|---|
| Jira base URL | `https://amali-tech.atlassian.net` |
| Project key | `DK26` / Project ID `13358` |
| Jira credentials | `.env.example` → `JIRA_EMAIL` + `JIRA_API_TOKEN` |
| Xray credentials | `.env.example` → `XRAY_CLIENT_ID` + `XRAY_CLIENT_SECRET` |
| Frontend folder path | `Quarter 2 ( April -July )/Frontend/Ebenezer` *(exact spacing matters)* |
| Backend folder path | `Quarter 2 ( April -July )/Backend/Ebenezer` |
| Test Plan | `DK26-118` |
| Test Execution | `DK26-195` |

---

## PROMPT 1 — Format Jira Ticket Description (ADF Table)

> Use when the ticket description has a raw markdown or `||` wiki-markup table that needs to be replaced with a proper native Jira table.

```
Read the credentials from .env.example in the project root.

Fetch Jira ticket <TICKET-KEY> via the REST API (https://amali-tech.atlassian.net/rest/api/3/issue/<TICKET-KEY>)
and replace its description with a properly formatted Atlassian Document Format (ADF) document containing:

1. H2 heading "User Story" with the story text as a paragraph
2. H2 heading "Acceptance Criteria" with a native bullet list
3. H2 heading "Test Cases for QA" with a full-width native ADF table
   Columns: Status | ID | Title | Preconditions | Steps (ordered list inside cell) | Expected Result
   Status default value: "Not Run"
   Test case IDs formatted as inline code
4. H2 heading "Notes" with a bullet list:
   - Status values: Not Run | Pass | Fail | Blocked
   - Update Status as each test is executed
   - Log defects by linking a new Bug issue

Use PUT /rest/api/3/issue/<TICKET-KEY> with Content-Type: application/json.
```

---

## PROMPT 2 — Full Xray Upload (New Story)

> Use when starting a brand-new story. Creates all test cases, folder, test set, steps, and links everything.

```
Read credentials from .env.example in the project root.

For Jira story <TICKET-KEY> (project DK26, project ID 13358):

**Step 1 — Create Jira Test issues**
Create one Jira issue per test case below using POST /rest/api/3/issue with:
  - issuetype: "Test Cases"
  - project key: DK26
  - summary: "[<TC-ID>] <title>"
  - description: ADF with H3 sections for Preconditions, Steps (ordered list), Expected Result

Test cases:
<PASTE TEST CASE TABLE HERE — ID | Title | Preconditions | Steps | Expected Result>

**Step 2 — Xray authenticate**
POST https://xray.cloud.getxray.app/api/v2/authenticate with client_id and client_secret from .env.example.

**Step 3 — Create Xray folder**
GraphQL mutation createFolder:
  projectId: "13358"
  path: "Quarter 2 ( April -July )/Frontend/Ebenezer/<TICKET-KEY> <STORY-SUMMARY>"
  testIssueIds: [<list of numeric Jira IDs from Step 1>]

**Step 4 — Create Test Set**
GraphQL mutation createTestSet:
  jira: { fields: { summary: "Test Set — <TICKET-KEY> <STORY-SUMMARY>", project: {key:"DK26"}, issuetype: {name:"Test Set"} } }
  testIssueIds: [<same numeric IDs>]
Return: testSet { issueId jira(fields:["key","summary"]) }

**Step 5 — Link tests to Test Plan and Test Execution**
Resolve numeric IDs for DK26-118 (Test Plan) and DK26-195 (Test Execution) via GET /rest/api/3/issue/<KEY>.
GraphQL: addTestsToTestPlan(issueId: "<plan numeric id>", testIssueIds: [...])
GraphQL: addTestsToTestExecution(issueId: "<exec numeric id>", testIssueIds: [...])

**Step 6 — Add test steps**
For each test issue created in Step 1, call GraphQL addTestStep(issueId, step:{action, data, result})
for every step. Put the expected result on the final step only. data = precondition text on step 1.

**Step 7 — Link tests to story**
Create Jira issue links (POST /rest/api/3/issueLink) between each test case and <TICKET-KEY>:
  type id: "10006"  (Tests link type)
  inwardIssue: <TICKET-KEY>   (is tested by)
  outwardIssue: <TEST-KEY>    (tests)

Print a summary at the end with all created keys and URLs.
```

---

## PROMPT 3 — Add Test Steps Only

> Use when test cases already exist in Xray but have no steps in the Test Details panel.

```
Read credentials from .env.example.
Authenticate with Xray: POST https://xray.cloud.getxray.app/api/v2/authenticate

For each test case below, call GraphQL addTestStep for every step:

mutation AddStep($issueId: String!, $step: CreateStepInput!) {
  addTestStep(issueId: $issueId, step: $step) { id action data result }
}

CreateStepInput fields: action (step text), data (test data / precondition), result (expected — last step only).

Test cases and Xray issueIds:
<TICKET-KEY>  Xray issueId: <NUMERIC-ID>
  Step 1 | action: "<text>" | data: "<precondition>" | result: ""
  Step 2 | action: "<text>" | data: "" | result: "<expected result>"

Repeat for all test cases. Print OK/WARN per step.
```

---

## PROMPT 4 — Link Existing Tests to a Story (Xray "Tests" panel)

> Use when tests exist in Xray but don't appear under the story's "Tests and Preconditions" section.

```
Read credentials from .env.example.

Create Jira issue links to make test cases appear in the Xray "Tests and Preconditions" panel
of story <TICKET-KEY>.

For each test key in [<DK26-XXXX>, <DK26-XXXX>, ...]:
  POST https://amali-tech.atlassian.net/rest/api/3/issueLink
  Body:
  {
    "type": { "id": "10006" },
    "inwardIssue":  { "key": "<TICKET-KEY>" },
    "outwardIssue": { "key": "<TEST-KEY>" }
  }

Auth: Basic base64(email:api_token) from .env.example.
Print OK/SKIP(already exists)/FAIL per link.
```

---

## PROMPT 5 — Move Tests to Correct Xray Folder

> Use when tests were placed in the wrong folder and need to be relocated.

```
Read credentials from .env.example.
Authenticate with Xray: POST https://xray.cloud.getxray.app/api/v2/authenticate

For each test Xray issueId in [<ID1>, <ID2>, ...], call:

mutation {
  updateTestFolder(issueId: "<ID>", folderPath: "Quarter 2 ( April -July )/Frontend/Ebenezer/<TICKET-KEY> <STORY-SUMMARY>")
}

After moving, verify with:
query { getFolder(projectId:"13358", path:"<FULL-PATH>") { path testsCount } }

Then delete the wrong folder:
mutation { deleteFolder(projectId:"13358", path:"<WRONG-PATH>") }
Only delete the specific subfolder we created — never delete shared parent folders like Frontend or Ebenezer.

NOTE: The correct existing folder is "Quarter 2 ( April -July )" — exact name with spaces ( April -July ).
Do NOT create a new folder with a similar name — use the existing one.
```

---

## PROMPT 6 — Format + Full Upload (Combined, One Shot)

> Use when you have a new ticket and want to do everything in one go.

```
Read credentials from .env.example in this project:
  JIRA_EMAIL, JIRA_API_TOKEN, XRAY_CLIENT_ID, XRAY_CLIENT_SECRET

Project config:
  Jira base: https://amali-tech.atlassian.net
  Project key: DK26  |  Project ID: 13358
  Frontend folder: Quarter 2 ( April -July )/Frontend/Ebenezer
  Test Plan: DK26-118  |  Test Execution: DK26-195

Story to process: <TICKET-KEY>

Run these steps in order, printing progress at each step:

1. Fetch the ticket and reformat its description as a proper ADF document
   (H2 User Story, H2 Acceptance Criteria bullet list, H2 Test Cases full-width table, H2 Notes)

2. Create 1 Jira Test issue (issuetype "Test Cases") per test case row in the table.
   Summary format: "[TC-<STORY>-NNN] <title>"
   Description: ADF with Preconditions / Steps / Expected Result sections.

3. Xray-authenticate and create the folder:
   path = "Quarter 2 ( April -July )/Frontend/Ebenezer/<TICKET-KEY> <summary>"
   Include all new test issue IDs.

4. Create a Test Set (jira fields format, not plain fields):
   jira: { fields: { summary: "Test Set — <TICKET-KEY>...", project:{key:"DK26"}, issuetype:{name:"Test Set"} } }

5. Add tests to Test Plan DK26-118 and Test Execution DK26-195 via addTestsToTestPlan / addTestsToTestExecution.

6. Add Xray test steps to every test case via addTestStep mutations.
   action = step text, data = precondition on step 1, result = expected result on last step.

7. Create Jira "Tests" issue links (link type id 10006) from each test to <TICKET-KEY>.

Print a final summary table: Ticket | Folder | Test Keys | Test Set | Plan | Execution.
```

---

## Quick Reference — Key GraphQL Mutations

```graphql
# Create folder with tests
mutation {
  createFolder(projectId:"13358", path:"<PATH>", testIssueIds:["<ID>",...]) {
    folder { path }  warnings
  }
}

# Create Test Set (MUST use fields wrapper)
mutation {
  createTestSet(
    jira: { fields: { summary:"<NAME>", project:{key:"DK26"}, issuetype:{name:"Test Set"} } },
    testIssueIds: ["<ID>",...]
  ) { testSet { issueId jira(fields:["key","summary"]) }  warnings }
}

# Add test step
mutation {
  addTestStep(issueId:"<ID>", step:{action:"<text>", data:"<data>", result:"<expected>"}) {
    id action data result
  }
}

# Link tests to plan / execution
mutation { addTestsToTestPlan(issueId:"<PLAN-NUM-ID>", testIssueIds:["<ID>",...]) { __typename } }
mutation { addTestsToTestExecution(issueId:"<EXEC-NUM-ID>", testIssueIds:["<ID>",...]) { __typename } }

# Move test to correct folder
mutation { updateTestFolder(issueId:"<ID>", folderPath:"<FULL-PATH>") }

# Delete a specific subfolder (never delete shared parent folders)
mutation { deleteFolder(projectId:"13358", path:"<EXACT-SUBFOLDER-PATH>") }
```

---

## Common Gotchas

- **Xray createTestSet** — must use `jira: { fields: { ... } }` not `jira: { summary: ... }` directly.
- **Folder path spacing** — the correct folder is `Quarter 2 ( April -July )` with a space after `(` and no space before `July`. Do NOT create a new folder — use the existing one.
- **Issue type name** — in DK26 the Xray test type is called `"Test Cases"` not `"Test"`.
- **Jira numeric IDs** — Xray GraphQL requires numeric `issueId` (from Jira REST `id` field), not the `DK26-XXXX` key.
- **Tests panel on story** — tests only appear in the Xray "Tests and Preconditions" panel when a Jira link of type `10006` (Tests / is tested by) exists between the test and the story.
- **Python on Windows** — use `python` not `python3`. Force UTF-8 output with `sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")`.
