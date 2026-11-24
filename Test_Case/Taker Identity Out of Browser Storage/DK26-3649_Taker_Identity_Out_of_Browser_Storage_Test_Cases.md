# DK26-3649: PT-005: Stop keeping test taker identity and session details in browser storage

Ticket: https://amali-tech.atlassian.net/browse/DK26-3649
Status: In Progress QA
Parent: DK26-3639 Q4 -- Resolving Identified Vulnerabilities: Client-Side Secrets and Browser Storage
Subtasks: DK26-3651 (BE attempt session), DK26-3695 (FE send session), DK26-3696 (BE finish session), DK26-3697 (DevOps settings), all Done
Code: dodokpo-backend PR #1345 (builds on PR #1344 from DK26-3642)
Xray folder: `Quarter 4/Ebenezer/Frontend/DK26-3649 PT-005: Stop keeping test taker identity and session details in browser storage` (not yet created, Xray key returns 401)
Jira test cases: DK26-3721 to DK26-3736 (linked to DK26-3649 as Test)
Test Plan: DK26-3106
Test Execution: DK26-3107

## Review Summary

The test-taking app kept the candidate's identity in plain text in the browser:

- takerIdentity in sessionStorage, holding testTakerId, organizationId and themeFlowId.
- typingLogCurrentSessionMeta and typingLogCurrentSessionId in localStorage.

Because the taker id was the only credential the test-taking API asked for, anyone holding it could change the attempt. The story fixes this in two parts:

- **Browser:** the identity and typing session are kept in memory, recovered from the route on reload, and old keys are removed on load.
- **Server:** an HttpOnly attempt session cookie is issued at start and required on every in-test request, controlled by the REQUIRE_ATTEMPT_SESSION setting.

Points to watch:

- Cletus's review of 6 November says this story is the main blocker for a clean retest. The retest will try the API with the taker id alone, so the session must be required in production.
- TC-11 to TC-13 need REQUIRE_ATTEMPT_SESSION set to 'true' on staging. Check the current value with DevOps first.
- TC-14 depends on a PO decision about device changes and browser crashes, which was still open in the subtasks. It fails until the decision is recorded on the story.
- TC-10 and TC-15 need test-execution logs and task definitions, so they need help from Fuad or Cletus.

## Acceptance Criteria Coverage

| Acceptance criterion | Covered by |
| --- | --- |
| During and after a test on staging, sessionStorage has no takerIdentity, and localStorage has no typingLogCurrentSessionMeta or typingLogCurrentSessionId. | TC-01, TC-02, TC-03, TC-04 |
| Reloading mid-test, opening the results page and typing logs still work. | TC-05, TC-06, TC-07, TC-08 |
| Unit tests updated. | TC-16 |
| Supporting scope: server-issued attempt session required on in-test requests (DK26-3651, DK26-3695, DK26-3696, DK26-3697) | TC-09 to TC-15 |

## Preconditions

### PC-DK26-3649-01: PT-005 browser storage change and attempt session deployed on staging

1. Staging runs the PT-005 frontend change (identity and typing log session kept in memory, old keys removed on load) and DK26-3695 (credentials sent on every in-test request).
2. The backend attempt session from DK26-3651 and DK26-3696 is deployed on staging (dodokpo-backend PR #1345).
3. The value of REQUIRE_ATTEMPT_SESSION on staging is known from DevOps (DK26-3697): 'log' or 'true'. Tests that need refusals run when it is 'true'.
4. A proctored assessment exists with several sections and questions, including a coding question (test cases and code runs), an essay or free-text question (typing logs) and a file-upload question.
5. At least three candidate invite links are available, and two of them can be opened in the same browser.

### PC-DK26-3649-02: Tools and access for storage, cookie and API checks

1. Browser developer tools in the latest Chrome, Firefox and Safari (Application/Storage and Network tabs).
2. An API client or intercepting proxy (Postman, Burp or similar) to replay in-test requests with and without the attempt session cookie.
3. A reviewer account to open the candidate report, including typing activity and violations.
4. Read access to the frontend and backend repositories and their CI runs, and to test-execution logs (Grafana) or help from Fuad Muhammed or Cletus Nehinlalei Mangu.

## Test Cases

### TC-DK26-3649-01: No taker identity or typing log session is in browser storage during a test

- Jira: [DK26-3721](https://amali-tech.atlassian.net/browse/DK26-3721)
- Linked preconditions: PC-DK26-3649-01, PC-DK26-3649-02
- Preconditions: PT-005 deployed on staging; a fresh Chrome profile; a candidate invite link; developer tools open.
- Steps:
  1. Open the invite link and note the taker id and organisation id in the URL.
  2. Start the test and answer questions in each section, including typing in the essay and coding questions.
  3. At each section, open Application > Storage and list every sessionStorage and localStorage entry for the site.
  4. Check for takerIdentity, typingLogCurrentSessionMeta and typingLogCurrentSessionId.
  5. Search every stored value for the taker id, the organisation id and themeFlowId.
- Expected result: sessionStorage has no takerIdentity, and localStorage has no typingLogCurrentSessionMeta or typingLogCurrentSessionId at any point. No other key holds the taker id, organisation id or themeFlowId in plain text or base64. Any typing log id that remains is an opaque value that is useless without the server session.

### TC-DK26-3649-02: No taker identity or typing log session is left in storage after the test

- Jira: [DK26-3722](https://amali-tech.atlassian.net/browse/DK26-3722)
- Linked preconditions: PC-DK26-3649-01, PC-DK26-3649-02
- Preconditions: PT-005 deployed on staging; a candidate who has just submitted a test.
- Steps:
  1. Submit the test and wait for the results page.
  2. Check sessionStorage, localStorage and IndexedDB for the three keys and for the taker id.
  3. Close the tab, reopen the invite link and check again.
  4. Leave a test unfinished (close the tab mid-test), then check storage.
- Expected result: After submitting, on the results page, after reopening the link and after leaving mid-test, none of the three keys exist and the taker id is not stored anywhere.

### TC-DK26-3649-03: Keys left by an older version are removed on load

- Jira: [DK26-3723](https://amali-tech.atlassian.net/browse/DK26-3723)
- Linked preconditions: PC-DK26-3649-01, PC-DK26-3649-02
- Preconditions: PT-005 deployed on staging; developer tools available.
- Steps:
  1. Before opening a link, add takerIdentity to sessionStorage, and typingLogCurrentSessionMeta and typingLogCurrentSessionId to localStorage, with values like the old ones.
  2. Open a candidate invite link and start or continue the test.
  3. Check both storage areas.
  4. Continue the test and confirm it works.
- Expected result: All three old keys are removed when the app loads, and they do not come back. The test starts and continues normally, using the identity from the link, not from the old keys.

### TC-DK26-3649-04: Storage stays clean in Firefox and Safari

- Jira: [DK26-3724](https://amali-tech.atlassian.net/browse/DK26-3724)
- Linked preconditions: PC-DK26-3649-01, PC-DK26-3649-02
- Preconditions: PT-005 deployed on staging; the latest Firefox and Safari; two candidate invite links.
- Steps:
  1. In Firefox, take a test with a reload mid-test and submit it.
  2. Check sessionStorage and localStorage during and after the test.
  3. Repeat in Safari.
- Expected result: In both browsers, the three keys never appear, the taker id is not stored, and the test, reload and submit work as in Chrome.

### TC-DK26-3649-05: Reloading mid-test restores the candidate's place, answers and timer

- Jira: [DK26-3725](https://amali-tech.atlassian.net/browse/DK26-3725)
- Linked preconditions: PC-DK26-3649-01
- Preconditions: PT-005 deployed on staging; a candidate invite link.
- Steps:
  1. Start the test and answer several questions, including a multiple-choice, an essay and a coding question.
  2. Reload the page on a question in the middle of a section.
  3. Do a hard reload (Ctrl+Shift+R) in another section, and reload once on the instructions or code-of-conduct page.
  4. After each reload, check the identity, current section and question, saved answers and timer.
  5. Finish and submit.
- Expected result: After every reload the candidate stays on the same test as the same person, with no error or 'link invalid' message. The current section, saved answers and remaining time are restored. Submit succeeds and every answer is recorded.

### TC-DK26-3649-06: The results page opens after submitting and after a reload

- Jira: [DK26-3726](https://amali-tech.atlassian.net/browse/DK26-3726)
- Linked preconditions: PC-DK26-3649-01
- Preconditions: PT-005 deployed on staging; an assessment that shows results to candidates.
- Steps:
  1. Take and submit a test.
  2. Read the results page.
  3. Reload the results page.
  4. Close the tab and open the results again from the link or email the candidate received.
- Expected result: The results page shows the right candidate's results after submitting, after a reload and when reopened. No other candidate's data appears, and no identity is read from storage.

### TC-DK26-3649-07: Typing logs are still recorded, including across a reload

- Jira: [DK26-3727](https://amali-tech.atlassian.net/browse/DK26-3727)
- Linked preconditions: PC-DK26-3649-01, PC-DK26-3649-02
- Preconditions: PT-005 deployed on staging; an assessment with essay and coding questions and typing tracking (suspicious typing) on; a reviewer account.
- Steps:
  1. Type an answer to the essay question, including a paste.
  2. Reload mid-typing and continue typing.
  3. Type in the coding question, then submit the test.
  4. As a reviewer, open the candidate report and its typing activity.
- Expected result: Typing activity is recorded for both questions, including the typing before and after the reload, in one continuous session or clearly linked sessions. The paste is detected as before. No typing log request fails in the Network tab.

### TC-DK26-3649-08: Two attempts in the same browser keep their own identity and session

- Jira: [DK26-3728](https://amali-tech.atlassian.net/browse/DK26-3728)
- Linked preconditions: PC-DK26-3649-01, PC-DK26-3649-02
- Preconditions: PT-005 and DK26-3696 deployed on staging; two invite links for different candidates.
- Steps:
  1. Open invite link 1 in a tab and start the test.
  2. Open invite link 2 in another tab of the same browser and start that test.
  3. Answer questions and reload in each tab in turn.
  4. Submit both, then check each candidate's answers in the reports.
- Expected result: Each tab keeps its own candidate: answers saved in one tab never appear on the other attempt. Neither attempt is refused as the wrong taker, because each attempt session cookie is scoped to its own taker path. Both submits succeed.

### TC-DK26-3649-09: An HttpOnly attempt session cookie is issued when the test starts

- Jira: [DK26-3729](https://amali-tech.atlassian.net/browse/DK26-3729)
- Linked preconditions: PC-DK26-3649-01, PC-DK26-3649-02
- Preconditions: Attempt session deployed on staging; developer tools open on the Network and Application tabs.
- Steps:
  1. Open a candidate invite link and start the test.
  2. In the assessment-in-progress response, find the Set-Cookie header.
  3. Read the cookie's attributes in Application > Cookies.
  4. In the console, run document.cookie and check whether the session appears.
- Expected result: Starting the test sets an attempt session cookie that is HttpOnly, Secure and SameSite=Strict, with a path scoped to this taker's test-taking path. It is not visible to scripts through document.cookie.

### TC-DK26-3649-10: Every in-test request carries the attempt session

- Jira: [DK26-3730](https://amali-tech.atlassian.net/browse/DK26-3730)
- Linked preconditions: PC-DK26-3649-01, PC-DK26-3649-02
- Preconditions: Attempt session deployed on staging with REQUIRE_ATTEMPT_SESSION set to 'log' or 'true'; access to test-execution logs.
- Steps:
  1. Take a full test with reloads, including autosave, section submit, a file upload, test cases and code runs on the coding question, and final submit.
  2. In the Network tab, check that each of these requests, and link-status, sends the attempt session cookie.
  3. Check the test-execution logs for that sitting for missing-session entries.
- Expected result: Every in-test request sends the attempt session cookie, including after reloads. The logs show no missing-session entries for the sitting.

### TC-DK26-3649-11: In-test requests with only the taker id are refused

- Jira: [DK26-3731](https://amali-tech.atlassian.net/browse/DK26-3731)
- Linked preconditions: PC-DK26-3649-01, PC-DK26-3649-02
- Preconditions: REQUIRE_ATTEMPT_SESSION is 'true' on staging; an attempt in progress; an API client.
- Steps:
  1. Capture the autosave, upload URL, test cases, code run and submit requests of a running attempt.
  2. Replay each one with the taker id but without the attempt session cookie.
  3. Check the attempt's answers and status afterwards.
- Expected result: Each request is refused with 401. No answer is changed, no file upload URL is returned, no code runs, and the attempt is not submitted. The candidate's own attempt in the browser continues normally.

### TC-DK26-3649-12: Expired sessions and sessions for another taker are refused with 401

- Jira: [DK26-3732](https://amali-tech.atlassian.net/browse/DK26-3732)
- Linked preconditions: PC-DK26-3649-01, PC-DK26-3649-02
- Preconditions: REQUIRE_ATTEMPT_SESSION is 'true' on staging; two attempts in progress for different candidates; an API client; developer help to expire a session if needed.
- Steps:
  1. Send candidate A's autosave request with candidate B's attempt session cookie.
  2. Send candidate A's autosave request with an altered (invalid) cookie value.
  3. Send it with an expired session (wait for expiry or ask a developer).
  4. Check both attempts.
- Expected result: Each request is refused with 401, not 403 or 500. Neither attempt is changed.

### TC-DK26-3649-13: A candidate whose session is refused can carry on through the link without losing answers

- Jira: [DK26-3733](https://amali-tech.atlassian.net/browse/DK26-3733)
- Linked preconditions: PC-DK26-3649-01, PC-DK26-3649-02
- Preconditions: REQUIRE_ATTEMPT_SESSION is 'true' on staging; an attempt in progress in Chrome.
- Steps:
  1. Answer several questions.
  2. Delete the attempt session cookie in Application > Cookies.
  3. Answer another question, so that autosave gets 401.
  4. Follow what the page shows, returning through the invite link.
  5. Check the saved answers and submit.
- Expected result: The page does not freeze or show a raw error. The candidate is sent back through the link, a new session is issued, and the test continues. No answer is lost, including the one typed when the 401 happened. The attempt is not auto-submitted with empty answers.

### TC-DK26-3649-14: Continuing on another device follows the PO decision

- Jira: [DK26-3734](https://amali-tech.atlassian.net/browse/DK26-3734)
- Linked preconditions: PC-DK26-3649-01, PC-DK26-3649-02
- Preconditions: REQUIRE_ATTEMPT_SESSION is 'true' on staging; the PO decision on device changes and browser crashes is recorded on the story.
- Steps:
  1. Start an attempt in Chrome and answer some questions.
  2. Open the same invite link in Firefox (as if Chrome crashed) and try to continue.
  3. If the decision includes an admin reset, ask an admin to reset the attempt and try again.
  4. Check the candidate report for a device-change flag.
- Expected result: The behaviour matches the PO decision recorded on the story: either the candidate is blocked with a clear message and can continue after an admin reset, or they continue and a device change is flagged. Answers already saved are kept. If no decision is recorded, this test fails.

### TC-DK26-3649-15: The attempt session settings are set in every environment

- Jira: [DK26-3735](https://amali-tech.atlassian.net/browse/DK26-3735)
- Linked preconditions: PC-DK26-3649-02
- Preconditions: Help from DevOps (Cletus Nehinlalei Mangu) to read the running task definitions.
- Steps:
  1. Check the running test-execution task definition on dev, staging and production for REQUIRE_ATTEMPT_SESSION and ATTEMPT_SESSION_COOKIE_PATH.
  2. Note each environment's value.
  3. Check that production was switched on only after the frontend change was live there.
- Expected result: Both settings appear on the running task definitions in all three environments. Staging is 'true' when the refusal tests run. Production follows the release, and was never 'true' before the frontend sent the session.

### TC-DK26-3649-16: Unit tests cover storage removal and the attempt session

- Jira: [DK26-3736](https://amali-tech.atlassian.net/browse/DK26-3736)
- Linked preconditions: PC-DK26-3649-02
- Preconditions: Read access to the frontend and backend repositories and CI.
- Steps:
  1. Open the frontend tests for test-taking.service.ts and typing-log.service.ts.
  2. Check that they cover: identity kept in memory and recovered from the route, typing session not stored, old keys removed on load, credentials sent on in-test requests and 401 handling.
  3. Open the backend tests from PR #1345 and DK26-3696 for missing, expired and wrong-taker sessions.
  4. Open the latest CI runs.
- Expected result: The tests exist for each case listed, and all of them pass in CI.
