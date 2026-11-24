# DK26-3642: PT-002: Check the anti-cheat device fingerprint on the server

Ticket: https://amali-tech.atlassian.net/browse/DK26-3642
Status: In Progress QA
Parent: DK26-3639 Q4 -- Resolving Identified Vulnerabilities: Client-Side Secrets and Browser Storage
Related: DK26-3640 (PT-001, Done), subtasks DK26-3643 (FE, In Progress Frontend) and DK26-3644 (DevOps, DEV DONE)
Code: dodokpo-backend PR #1344 (candidate side) and PR #1346 (admin side)
Xray folder: `Quarter 4/Ebenezer/Backend/DK26-3642 PT-002: Check the anti-cheat device fingerprint on the server` (not yet created)
Jira test cases: DK26-3658 to DK26-3672 (linked to DK26-3642 as Test)
Test Plan: DK26-3106
Test Execution: DK26-3107

## Review Summary

The browser used to keep the anti-cheat device fingerprint in storage (plain in sessionStorage, and encrypted with a public key in localStorage and IndexedDB). A candidate could therefore copy it to another machine so that a proxy sat the test. The fix moves the check to the server. The server stores an HMAC of the fingerprint with the attempt and checks it on every test-taking route that changes the attempt (start, link-status, autosave, submit, upload URLs). It fails closed when the binding or header is missing, and records a DEVICE_CHANGE proctoring violation on a mismatch. Admin tokens carry the fingerprint HMAC and the gateway checks it. The frontend keeps the fingerprint in memory only.

Points to watch:

- The check starts in flag-only mode. A device change is recorded but never refused until the PO decides on blocking, after the reload checks in TC-08 to TC-10.
- The check stays off until the signing secret (DK26-3644) is set on staging.
- The storage criterion depends on DK26-3643 (Kweku) being deployed with the backend change.
- Until a small frontend change is made, the review screens show the flag as DEVICE_CHANGE.
- TC-05 to TC-07 and TC-15 need Redis, log or config access, or help from Fuad Muhammed or Cletus.

## Acceptance Criteria Coverage

| Acceptance criterion | Covered by |
| --- | --- |
| On staging, sending a different fingerprint on a running attempt is caught by the server and shows on the candidate report. | TC-01, TC-02, TC-03, TC-04, TC-05 |
| A normal attempt with page reloads in Chrome, Firefox and Safari raises no false device-change flags. | TC-08, TC-09, TC-10 |
| During a test on staging, no fingerprint value, plain or encrypted, is readable in localStorage, sessionStorage or IndexedDB. | TC-11, TC-12 |
| Unit and integration tests cover a match, a mismatch and a missing header. | TC-13 |
| Supporting scope from 'What needs to be done' (HMAC storage, no value returned, no bindings for unknown takers, admin sessions, signing secret) | TC-06, TC-07, TC-14, TC-15 |

## Preconditions

### PC-DK26-3642-01: Server-side fingerprint check deployed on staging in flag-only mode

1. Staging runs the backend changes from dodokpo-backend PR #1344 (candidate side) and PR #1346 (admin side).
2. The fingerprint signing secret is set for staging (DK26-3644), so the new check is switched on.
3. The frontend changes from DK26-3643 and PT-001 (DK26-3640) are deployed together, so the fingerprint is no longer cached in browser storage.
4. The check runs in flag-only mode: a device change is recorded as a DEVICE_CHANGE proctoring violation but the request is not refused.
5. A proctored assessment with several questions, including at least one file-upload question, exists. Invite links are available for test candidates.
6. A reviewer account can open the candidate report and its violations list.

### PC-DK26-3642-02: Tools to read and change requests and storage

1. Browser developer tools are available (Network tab and Application/Storage tab).
2. An API client or intercepting proxy (Postman, Burp or similar) can replay a test-taking request with a changed or missing x-device-fingerprint header, using the candidate's own token.
3. The latest Chrome, Firefox and Safari are available, with Safari on macOS.
4. Read access to the backend repository and its CI results, so that unit and integration tests can be checked.
5. Where possible, read access to staging Redis and the attempt record, or a backend developer (Fuad Muhammed) is available to check stored values.

## Test Cases

### TC-DK26-3642-01: A different fingerprint on a running attempt is caught by the server and shown on the candidate report

- Jira: [DK26-3658](https://amali-tech.atlassian.net/browse/DK26-3658)
- Linked preconditions: PC-DK26-3642-01, PC-DK26-3642-02
- Preconditions: Server check deployed on staging in flag-only mode; a candidate invite link; an API client or proxy to replay requests.
- Steps:
  1. Open the invite link in Chrome, start the attempt and answer one question.
  2. In the Network tab, note the x-device-fingerprint header sent on the link-status and assessment-in-progress requests.
  3. Replay the assessment-in-progress request with the candidate's token but a different x-device-fingerprint value.
  4. Continue and submit the attempt in Chrome.
  5. As a reviewer, open the candidate report and its proctoring violations.
- Expected result: The request with the changed fingerprint is detected by the server and a device-change violation is recorded on the attempt. The candidate report shows the violation with the time it happened, under a readable name such as 'Device change' (or DEVICE_CHANGE until the frontend label change is deployed). In flag-only mode the request is not refused, and the candidate can continue and submit.

### TC-DK26-3642-02: Continuing a running attempt from a second browser is flagged once and not blocked

- Jira: [DK26-3659](https://amali-tech.atlassian.net/browse/DK26-3659)
- Linked preconditions: PC-DK26-3642-01
- Preconditions: Server check deployed on staging in flag-only mode; a candidate invite link.
- Steps:
  1. Start the attempt in Chrome and answer one question.
  2. Open the same invite link in Firefox (or a Chrome private window) and continue the same attempt there.
  3. Answer another question in the second browser and submit.
  4. As a reviewer, open the candidate report and count the device-change violations.
- Expected result: Exactly one device-change violation is recorded for the switch to the second browser, not one per request. The candidate is not blocked, and the answers from both browsers are saved. This is the attack in the report: a proxy taking over the attempt on another machine is now visible to the reviewer.

### TC-DK26-3642-03: Autosave, submit and upload URL routes check the fingerprint

- Jira: [DK26-3660](https://amali-tech.atlassian.net/browse/DK26-3660)
- Linked preconditions: PC-DK26-3642-01, PC-DK26-3642-02
- Preconditions: Server check deployed on staging in flag-only mode; an assessment with a file-upload question; an API client or proxy.
- Steps:
  1. Start an attempt in Chrome and capture the autosave request, the upload URL request (from the file-upload question) and the submit request.
  2. Replay the autosave request with a different x-device-fingerprint and check the report.
  3. Start a new attempt and replay the upload URL request with a different fingerprint, then check the report.
  4. Start a new attempt and send the submit request with a different fingerprint, then check the report.
- Expected result: Each of the three routes compares the fingerprint, not only link-status and assessment-in-progress. A mismatch on autosave, on the upload URL request and on submit is each recorded as a device-change violation on that attempt. In flag-only mode the answer is still saved, the upload URL is still returned and the submit still succeeds.

### TC-DK26-3642-04: A request with no fingerprint header during a running attempt is not skipped

- Jira: [DK26-3661](https://amali-tech.atlassian.net/browse/DK26-3661)
- Linked preconditions: PC-DK26-3642-01, PC-DK26-3642-02
- Preconditions: Server check deployed on staging in flag-only mode; an API client or proxy.
- Steps:
  1. Start an attempt in Chrome and answer one question.
  2. Replay the autosave request with the x-device-fingerprint header removed.
  3. Replay the assessment-in-progress request with the header present but empty.
  4. Open the candidate report as a reviewer.
- Expected result: A missing or empty header is treated as a failed check, not as a pass: each request is recorded as a device-change (or missing-fingerprint) violation on the attempt. No error page or 500 response is shown, and in flag-only mode the requests still succeed.

### TC-DK26-3642-05: A lost device binding is re-created from the attempt record, and checks continue

- Jira: [DK26-3662](https://amali-tech.atlassian.net/browse/DK26-3662)
- Linked preconditions: PC-DK26-3642-01, PC-DK26-3642-02
- Preconditions: Server check deployed on staging; Redis access, or a backend developer who can remove the binding key.
- Steps:
  1. Start an attempt in Chrome and answer one question.
  2. Delete the attempt's fingerprint binding from Redis (or wait for it to expire), as if Redis had restarted.
  3. Continue answering in Chrome.
  4. Replay an autosave request with a different fingerprint.
  5. Open the candidate report.
- Expected result: After the binding is lost, the check is not skipped. The binding is restored from the value saved with the attempt, so continuing in Chrome raises no violation, while the request with a different fingerprint is still recorded as a device change. If the binding cannot be restored, the attempt is flagged rather than passed.

### TC-DK26-3642-06: The server stores only an HMAC of the fingerprint and never sends it back

- Jira: [DK26-3663](https://amali-tech.atlassian.net/browse/DK26-3663)
- Linked preconditions: PC-DK26-3642-01, PC-DK26-3642-02
- Preconditions: Server check deployed on staging; read access to Redis and the attempt record, or help from a backend developer.
- Steps:
  1. Start an attempt and note the x-device-fingerprint value sent by the browser.
  2. Read the binding stored in Redis and the value saved with the attempt.
  3. Compare the stored value with the raw fingerprint.
  4. Search every test-taking response body and header in the Network tab, and the candidate report API response, for the raw fingerprint and the stored value.
- Expected result: The stored value is an HMAC made with the server-held secret, not the raw fingerprint, and it is saved with the attempt as well as in Redis. Neither the raw fingerprint nor the stored HMAC appears in any API response to the browser. The violation details shown to reviewers do not contain either value.

### TC-DK26-3642-07: No binding is created for a test taker that does not exist

- Jira: [DK26-3664](https://amali-tech.atlassian.net/browse/DK26-3664)
- Linked preconditions: PC-DK26-3642-01, PC-DK26-3642-02
- Preconditions: Server check deployed on staging; an API client; Redis access or help from a backend developer.
- Steps:
  1. Send a link-status request with a made-up taker id and a fingerprint header.
  2. Send it again with several other random taker ids.
  3. Check Redis for fingerprint bindings for those ids.
- Expected result: Requests for a taker that does not exist are refused with a not-found or unauthorised response. No fingerprint binding is created in Redis or elsewhere for any made-up id.

### TC-DK26-3642-08: A normal attempt with reloads in Chrome raises no device-change flag

- Jira: [DK26-3665](https://amali-tech.atlassian.net/browse/DK26-3665)
- Linked preconditions: PC-DK26-3642-01
- Preconditions: Server check deployed on staging; the latest Chrome; a new candidate invite link.
- Steps:
  1. Open the invite link in Chrome and start the attempt.
  2. During the attempt, reload the page 10 times, including hard reloads (Ctrl+Shift+R), on different questions.
  3. Duplicate the tab once and continue in the duplicate.
  4. Close the browser, reopen it on the same machine and resume the attempt with the same link.
  5. Submit, then open the candidate report as a reviewer.
- Expected result: The x-device-fingerprint value is the same on every request after each reload, duplicate tab and browser restart. The candidate is never logged out or blocked, and the candidate report shows no device-change violation.

### TC-DK26-3642-09: A normal attempt with reloads in Firefox raises no device-change flag

- Jira: [DK26-3666](https://amali-tech.atlassian.net/browse/DK26-3666)
- Linked preconditions: PC-DK26-3642-01
- Preconditions: Server check deployed on staging; the latest Firefox; a new candidate invite link.
- Steps:
  1. Open the invite link in Firefox and start the attempt.
  2. During the attempt, reload the page 10 times, including hard reloads (Ctrl+Shift+R), on different questions.
  3. Close the browser, reopen it on the same machine and resume the attempt.
  4. Submit, then open the candidate report as a reviewer.
- Expected result: The fingerprint stays the same on every request, including with Firefox's default tracking protection on. The candidate is never logged out or blocked, and the candidate report shows no device-change violation.

### TC-DK26-3642-10: A normal attempt with reloads in Safari raises no device-change flag

- Jira: [DK26-3667](https://amali-tech.atlassian.net/browse/DK26-3667)
- Linked preconditions: PC-DK26-3642-01
- Preconditions: Server check deployed on staging; the latest Safari on macOS; a new candidate invite link.
- Steps:
  1. Open the invite link in Safari and start the attempt.
  2. During the attempt, reload the page 10 times, including reloads from origin (Cmd+Option+R), on different questions.
  3. Quit Safari, reopen it and resume the attempt.
  4. Submit, then open the candidate report as a reviewer.
- Expected result: The fingerprint stays the same on every request, despite Safari's fingerprinting protections. The candidate is never logged out or blocked, and the candidate report shows no device-change violation. Any false flag is reported before blocking mode is discussed with the PO.

### TC-DK26-3642-11: No fingerprint value, plain or encrypted, is in browser storage during a test

- Jira: [DK26-3668](https://amali-tech.atlassian.net/browse/DK26-3668)
- Linked preconditions: PC-DK26-3642-01, PC-DK26-3642-02
- Preconditions: Server and frontend changes deployed on staging; a fresh browser profile; a candidate invite link.
- Steps:
  1. Start an attempt and note the x-device-fingerprint header value from the Network tab.
  2. Open Application/Storage and list every entry in localStorage, sessionStorage and IndexedDB for the site.
  3. Check for the keys fp_cached_plain, fp_refresh_once, fp_persistent and the BrowserTagDB store.
  4. Search every value, including base64-decoded values and the access token entry, for the fingerprint.
  5. Repeat after a reload and after submitting the attempt, in Chrome, Firefox and Safari.
- Expected result: None of the old fingerprint keys or the BrowserTagDB store exist. The fingerprint does not appear in any storage, plain, base64-encoded or encrypted, and the token entry no longer contains it. The header is still sent on every request, because the value is kept only in memory.

### TC-DK26-3642-12: Fingerprint copies left by an older version are removed on load

- Jira: [DK26-3669](https://amali-tech.atlassian.net/browse/DK26-3669)
- Linked preconditions: PC-DK26-3642-01, PC-DK26-3642-02
- Preconditions: Server and frontend changes deployed on staging; developer tools available.
- Steps:
  1. In the browser, manually add the old keys: fp_cached_plain and fp_refresh_once in sessionStorage, fp_persistent in localStorage, and a BrowserTagDB IndexedDB store with a value.
  2. Reload the page.
  3. Check all three storage areas.
  4. Sign in, or open a candidate invite link, and start an attempt.
- Expected result: After the reload, all the old keys and the BrowserTagDB store are removed. The user is sent to the login page or stays signed in, as described in DK26-3643. Starting an attempt works, and none of the old values comes back.

### TC-DK26-3642-13: Unit and integration tests cover a match, a mismatch and a missing header

- Jira: [DK26-3670](https://amali-tech.atlassian.net/browse/DK26-3670)
- Linked preconditions: PC-DK26-3642-02
- Preconditions: Read access to dodokpo-backend PRs #1344 and #1346 and their CI runs.
- Steps:
  1. Open the test files changed in PR #1344 and find the tests for the fingerprint check in test-execution.
  2. Confirm there are tests for a matching fingerprint, a different fingerprint and a missing header, on start or link-status and on autosave, submit and the upload URL routes.
  3. Do the same for PR #1346 (gateway check on admin tokens).
  4. Open the latest CI run of each PR.
- Expected result: Both PRs have unit and integration tests for the three cases: a match passes with no violation, a mismatch records a device-change violation, and a missing header is not treated as a pass. The tests also check that the stored value is an HMAC. All tests pass in CI.

### TC-DK26-3642-14: Admin sessions carry a fingerprint HMAC and a device change is recorded

- Jira: [DK26-3671](https://amali-tech.atlassian.net/browse/DK26-3671)
- Linked preconditions: PC-DK26-3642-01, PC-DK26-3642-02
- Preconditions: PR #1346 deployed on staging; an organisation admin account; an API client.
- Steps:
  1. Sign in as an admin in Chrome and decode the access token (for example at jwt.io, using a non-production token).
  2. Check what the token holds for the fingerprint.
  3. Call an admin API with the same token but a different x-device-fingerprint header, then with no header.
  4. Ask a backend developer, or check the logs, whether the gateway recorded the mismatch.
- Expected result: The token holds an HMAC of the fingerprint, never the raw value. The gateway compares it on each request. For now a mismatch or missing header is only recorded and the request succeeds, as stated in the ticket comment. The browser-side fingerprint compare in auth.service.ts is no longer used.

### TC-DK26-3642-15: The check stays off without the signing secret and logs no secret

- Jira: [DK26-3672](https://amali-tech.atlassian.net/browse/DK26-3672)
- Linked preconditions: PC-DK26-3642-02
- Preconditions: Access to the dev or staging environment config and service logs, with help from DevOps (Cletus) if needed.
- Steps:
  1. Confirm the signing secret is set for staging (DK26-3644) and that test-execution and api-gateway start without errors.
  2. Search the service logs from a test attempt, including one with a device change, for the secret, the raw fingerprint and the HMAC.
  3. On a dev environment with the secret removed, start an attempt and check the result (only if DevOps agrees).
- Expected result: With the secret set, both services start and the check runs. No log contains the secret or the raw fingerprint. Without the secret, the check is switched off as described in the ticket comment, and test taking still works; it does not crash or block candidates.
