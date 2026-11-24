# DK26-3173: BE - Story 5.3: Multi-Select Assessments with Archive Action

Ticket: https://amali-tech.atlassian.net/browse/DK26-3173
Status: In Progress QA
Parent: DK26-3147 Epic 5: Improve Question and Test Management
Related: DK26-3164 (FE clone, In Progress Frontend, subtasks DK26-3354 to DK26-3359); DK26-3171 (BE, the same feature for questions, tested at API level)
Xray folder: `Quarter 4/Ebenezer/Backend/DK26-3173 BE - Story 5.3: Multi-Select Assessments with Archive Action`
Test Set: DK26-3441
Test Plan: DK26-3106
Test Execution: DK26-3107

## Review Summary

This is the backend half of a cloned story, so its acceptance criteria are worded for the screen. The FE subtask DK26-3357 shows what the backend is relied on for. There is no bulk archive endpoint and no archive-impact check for assessments: the web app sends one archive request per selected assessment, all in parallel, and restores through a per-assessment restore request. Dispatched assessments can be archived, as single-item archive already allows. The action is gated by the archive permission (canArchiveAssessment) and the organisation's archiving setting (archivingEnabled), and archived assessments are read back with the archived-state filter used by Archives > Assessments (availableArchiveState).

The tests are written at API level, like the question equivalent DK26-3171. They also check two issues QA found there that apply here too: a partly failed selection cannot be rolled back (TC-08), and a wrongly worded archive filter quietly returns the active list (TC-12). TC-14 measures a full page so the team can decide whether a batch endpoint is needed.

Points to confirm with the product owner: what an invited candidate sees when a dispatched assessment is archived (TC-05), and that archived assessments cannot be dispatched or picked elsewhere (TC-13). Neither is defined in the ticket beyond 'the agreed archived-state behavior'.

Upload note: Xray did not register the first TC-14 issue (DK26-3436), so it was replaced by DK26-3438. DK26-3436 is unlinked from the story and marked as a duplicate.

## Acceptance Criteria Coverage

| Acceptance criterion | Covered by |
| --- | --- |
| Add multi-select capability to the assessment list/table view. | TC-02, TC-03 (backend support for acting on a selection) |
| Support selecting individual assessments and selecting all assessments on the current page. | TC-01, TC-02, TC-14 |
| Provide a bulk archive action for selected assessments. | TC-02, TC-05, TC-08, TC-14 |
| Show a confirmation step that includes the number of selected assessments before archiving. | TC-08 (per-item results so the count is correct); the dialog itself is FE (DK26-3164) |
| Confirm archived assessments no longer appear in the default active list and follow the agreed archived-state behavior. | TC-03, TC-04, TC-06, TC-12, TC-13 |
| Security and robustness | TC-07, TC-09, TC-10, TC-11 |

## Preconditions (Xray Precondition issues)

### PC-DK26-3173-01: Org administrator authenticated against the staging API with DK26-3173 deployed

- Jira: [DK26-3439](https://amali-tech.atlassian.net/browse/DK26-3439)

1. The staging API runs a build that contains DK26-3173.
2. An organisation administrator account with the archive permission (canArchiveAssessment) is signed in, and its access token is available to an API client (Postman, curl or the browser's developer tools).
3. Archiving is enabled for the organisation (archivingEnabled is on).
4. The archive, restore and assessment list requests are known, from the API documentation or from the requests the web app sends when archiving a single assessment, opening the Assessments list and opening Archives > Assessments (/dashboard/archives/assessments). This includes the archived-state filter (availableArchiveState).

### PC-DK26-3173-02: Disposable assessments exist for archiving, including a dispatched one

- Jira: [DK26-3440](https://amali-tech.atlassian.net/browse/DK26-3440)

1. At least 30 fresh, non-dispatched assessments have been created in the organisation for this test run, with names that are easy to find (for example 'QA-ARCH-3173-01' to 'QA-ARCH-3173-30'), so a full page and more can be archived.
2. At least one disposable assessment has been dispatched, with at least one invited candidate who has not finished it.
3. The IDs of all these assessments are recorded.
4. The total number of active assessments shown by the list request has been noted before any archiving.

### PC-DK26-3173-03: Users and organisations for permission and isolation checks

- Jira: [DK26-3437](https://amali-tech.atlassian.net/browse/DK26-3437)

1. User B belongs to the same organisation but their role does not include the permission to archive assessments, and their access token is available.
2. An administrator of a different organisation is available, with at least one assessment in their own organisation and its ID recorded.
3. The tester, or an administrator, can switch the organisation's archiving setting (archivingEnabled) off and back on.

## Test Cases

### TC-DK26-3173-01: An assessment is archived, and the response names what was archived

- Jira: [DK26-3423](https://amali-tech.atlassian.net/browse/DK26-3423)
- Linked preconditions: PC-DK26-3173-01 (DK26-3439), PC-DK26-3173-02 (DK26-3440)
- Preconditions: Org administrator authenticated on the staging API with DK26-3173 deployed; disposable non-dispatched assessments exist.
- Steps:
  1. Pick one disposable non-dispatched assessment and note its ID.
  2. Send the archive request for it as the org administrator.
  3. Read the status code and the response body.
  4. Request that assessment by ID and check its state.
- Expected:
  - The request succeeds with a success status. The response identifies the assessment that was archived, with its ID and organisation, and its state is now archived. No other assessment changes.

### TC-DK26-3173-02: Every assessment in a multi-selection is archived when the requests are sent together

- Jira: [DK26-3424](https://amali-tech.atlassian.net/browse/DK26-3424)
- Linked preconditions: PC-DK26-3173-01 (DK26-3439), PC-DK26-3173-02 (DK26-3440)
- Preconditions: Org administrator authenticated; at least 5 disposable non-dispatched assessments available.
- Steps:
  1. Pick 5 disposable assessments and note their IDs.
  2. Send the archive request for all 5 at the same time (in parallel), as the web app does for a bulk selection.
  3. Check the status code of each of the 5 responses.
  4. Request each of the 5 assessments by ID and check its state.
- Expected:
  - All 5 requests succeed, and all 5 assessments are archived, not just the first or last. Requests sent at the same time do not interfere with each other: there are no 409, 500 or timeout errors and no assessment is left half-updated.

### TC-DK26-3173-03: Archived assessments are excluded from the default active list and its count

- Jira: [DK26-3425](https://amali-tech.atlassian.net/browse/DK26-3425)
- Linked preconditions: PC-DK26-3173-01 (DK26-3439), PC-DK26-3173-02 (DK26-3440)
- Preconditions: Org administrator authenticated; the active assessment total was noted before archiving; the assessments archived in TC-01 and TC-02 are known.
- Steps:
  1. Request the default assessment list (no archive filter), going through every page.
  2. Search the results for each archived assessment by ID and by name.
  3. Compare the total count in the response with the total noted before archiving.
  4. Search the list by the name of one archived assessment.
- Expected:
  - None of the archived assessments appear in the default list on any page or in search results. The total count is lower by exactly the number archived, and the paging totals are consistent with the items returned.

### TC-DK26-3173-04: Archived assessments are returned by the archived-state filter and stay readable

- Jira: [DK26-3426](https://amali-tech.atlassian.net/browse/DK26-3426)
- Linked preconditions: PC-DK26-3173-01 (DK26-3439), PC-DK26-3173-02 (DK26-3440)
- Preconditions: Org administrator authenticated; the assessments archived in TC-01 and TC-02 are known; the archived-state filter (availableArchiveState) is known.
- Steps:
  1. Request the assessment list with the archived-state filter, as Archives > Assessments does.
  2. Check that every assessment archived earlier is returned.
  3. Check that no active assessment is returned.
  4. Open one archived assessment by ID and read its details, tests and settings.
- Expected:
  - The archived-state list returns all archived assessments and only archived ones, each marked as archived. An archived assessment can still be read by ID with its tests and settings intact, so nothing is lost by archiving.

### TC-DK26-3173-05: A dispatched assessment can be archived and its candidate data is kept

- Jira: [DK26-3427](https://amali-tech.atlassian.net/browse/DK26-3427)
- Linked preconditions: PC-DK26-3173-01 (DK26-3439), PC-DK26-3173-02 (DK26-3440)
- Preconditions: Org administrator authenticated; a disposable dispatched assessment exists with at least one invited candidate.
- Steps:
  1. Note the dispatched assessment's ID, its candidates and any results or report data.
  2. Send the archive request for it.
  3. Check that it has left the active list and appears in the archived list.
  4. Request its candidate, result and report data again.
  5. Try to open the invited candidate's assessment link and record what happens.
- Expected:
  - Archiving a dispatched assessment is allowed, matching the existing single-item behaviour. It leaves the active list and appears in the archive. Its candidates, results and report data are still returned unchanged. What happens to the invited candidate's link is recorded and checked against the agreed archived-state behaviour; if that is not defined, it is raised with the product owner.

### TC-DK26-3173-06: An archived assessment can be restored to the active list

- Jira: [DK26-3428](https://amali-tech.atlassian.net/browse/DK26-3428)
- Linked preconditions: PC-DK26-3173-01 (DK26-3439), PC-DK26-3173-02 (DK26-3440)
- Preconditions: Org administrator authenticated; at least one archived disposable assessment from an earlier test.
- Steps:
  1. Send the restore request for one archived assessment.
  2. Read the status code and response.
  3. Check that it appears in the default active list again and no longer appears in the archived list.
  4. Open it by ID and compare its details with those before archiving.
- Expected:
  - The restore succeeds and the assessment returns to the active list with all its details, tests and settings unchanged. It no longer appears in the archived list, and the active total goes up by one.

### TC-DK26-3173-07: Archiving an already-archived, missing or malformed assessment ID fails cleanly

- Jira: [DK26-3429](https://amali-tech.atlassian.net/browse/DK26-3429)
- Linked preconditions: PC-DK26-3173-01 (DK26-3439), PC-DK26-3173-02 (DK26-3440)
- Preconditions: Org administrator authenticated; one archived disposable assessment ID is known.
- Steps:
  1. Send the archive request again for an assessment that is already archived.
  2. Send the archive request for a well-formed ID that does not exist.
  3. Send the archive request for a malformed ID (for example 'abc' or an empty value).
  4. Read the status code and message for each, and check that no assessment changed.
- Expected:
  - Re-archiving an archived assessment either succeeds without changing anything or is refused with a clear 'already archived' message, never a 500. A missing ID returns 404 and a malformed ID returns 400, each with a clear message. No other assessment is affected.

### TC-DK26-3173-08: A selection with one failing item archives the rest and reports the failure

- Jira: [DK26-3430](https://amali-tech.atlassian.net/browse/DK26-3430)
- Linked preconditions: PC-DK26-3173-01 (DK26-3439), PC-DK26-3173-02 (DK26-3440)
- Preconditions: Org administrator authenticated; at least 4 disposable non-dispatched assessments available.
- Steps:
  1. Prepare a selection of 4 valid disposable assessment IDs plus 1 ID that does not exist.
  2. Send the 5 archive requests at the same time.
  3. Check each response's status code and message.
  4. Check the state of each of the 4 valid assessments.
- Expected:
  - The 4 valid assessments are archived and the missing one is refused with a clear error, so the web app can report the correct count (4 archived, 1 failed). One failure does not stop or undo the others. Because there is no bulk endpoint, there is no rollback; this is recorded as known behaviour, as it was for questions in DK26-3171.

### TC-DK26-3173-09: Archiving and restoring without authentication are rejected

- Jira: [DK26-3431](https://amali-tech.atlassian.net/browse/DK26-3431)
- Linked preconditions: PC-DK26-3173-01 (DK26-3439), PC-DK26-3173-02 (DK26-3440)
- Preconditions: The archive and restore requests are known; disposable active and archived assessment IDs are recorded.
- Steps:
  1. Send the archive request for an active disposable assessment with no access token.
  2. Send it again with an invalid or expired token.
  3. Send the restore request for an archived assessment with no access token.
  4. Check the state of both assessments as the org administrator.
- Expected:
  - Each request is rejected with 401 Unauthorized and no assessment data in the response. The active assessment stays active and the archived one stays archived.

### TC-DK26-3173-10: Archiving is refused without the archive permission or when archiving is switched off

- Jira: [DK26-3432](https://amali-tech.atlassian.net/browse/DK26-3432)
- Linked preconditions: PC-DK26-3173-01 (DK26-3439), PC-DK26-3173-02 (DK26-3440), PC-DK26-3173-03 (DK26-3437)
- Preconditions: User B (no archive permission) is authenticated; the org administrator is authenticated; the archiving setting can be switched off and on.
- Steps:
  1. As User B, send the archive request for an active disposable assessment.
  2. As User B, send the restore request for an archived assessment.
  3. Switch the organisation's archiving setting (archivingEnabled) off. As the org administrator, send the archive request for an active disposable assessment.
  4. Switch archiving back on and check the state of every assessment used.
- Expected:
  - User B's requests are refused with 403 Forbidden and a clear message, and nothing changes. With archiving switched off, the administrator's archive request is also refused, so the backend enforces both gates and not only the hidden UI button. After switching archiving back on, every assessment is in the state it was in before the test.

### TC-DK26-3173-11: An administrator cannot archive or restore another organisation's assessment

- Jira: [DK26-3433](https://amali-tech.atlassian.net/browse/DK26-3433)
- Linked preconditions: PC-DK26-3173-01 (DK26-3439), PC-DK26-3173-03 (DK26-3437)
- Preconditions: Org administrator of organisation A authenticated; the ID of an assessment in organisation B is recorded; organisation B's administrator is available to check it.
- Steps:
  1. As organisation A's administrator, send the archive request for organisation B's assessment ID.
  2. Send the restore request for it too.
  3. Request organisation A's archived list and check for the other organisation's assessment.
  4. As organisation B's administrator, check the state of that assessment.
- Expected:
  - Both requests are refused with 403 or 404, and the response reveals nothing about organisation B's assessment. Organisation B's assessment is unchanged and never appears in organisation A's lists.

### TC-DK26-3173-12: An unrecognised archive filter is not silently treated as the active list

- Jira: [DK26-3434](https://amali-tech.atlassian.net/browse/DK26-3434)
- Linked preconditions: PC-DK26-3173-01 (DK26-3439), PC-DK26-3173-02 (DK26-3440)
- Preconditions: Org administrator authenticated; at least one archived assessment exists; the correct archived-state filter is known.
- Steps:
  1. Request the assessment list with the correct archived-state filter and note the result.
  2. Request it again with two plausible but incorrect filter values or parameter names (for example a misspelled parameter or the value 'archive' instead of the expected one).
  3. Compare what each request returns.
- Expected:
  - The correct filter returns archived assessments. An incorrect filter is either refused with 400 and a clear message, or still returns archived assessments. It must not quietly return the active list as though the filter had been understood, the issue found for questions in DK26-3171.

### TC-DK26-3173-13: Archived assessments cannot be dispatched or picked elsewhere in the platform

- Jira: [DK26-3435](https://amali-tech.atlassian.net/browse/DK26-3435)
- Linked preconditions: PC-DK26-3173-01 (DK26-3439), PC-DK26-3173-02 (DK26-3440)
- Preconditions: Org administrator authenticated; at least one archived non-dispatched disposable assessment exists.
- Steps:
  1. Send the dispatch request for an archived assessment.
  2. Request the assessment list used by skill creation, Step 2: Assessment Assignment, and search for the archived assessment.
  3. Request any other list that offers assessments for selection, such as reports filters, and search for it.
  4. Restore the assessment and repeat the skill list check.
- Expected:
  - Dispatching an archived assessment is refused with a clear message. The archived assessment does not appear in the skill creation list or other selection lists. After it is restored, it appears in them again.

### TC-DK26-3173-14: Archiving a full page of assessments completes in a reasonable time

- Jira: [DK26-3438](https://amali-tech.atlassian.net/browse/DK26-3438)
- Linked preconditions: PC-DK26-3173-01 (DK26-3439), PC-DK26-3173-02 (DK26-3440)
- Preconditions: Org administrator authenticated; at least 25 disposable non-dispatched assessments available (one page).
- Steps:
  1. Take 25 disposable assessment IDs, a full page at the default page size.
  2. Send the 25 archive requests at the same time and time the whole batch from the first request to the last response.
  3. Check that all 25 succeed and are archived.
  4. Record the total time, the slowest single request and any throttling (429) or error responses.
- Expected:
  - All 25 assessments are archived with no 429, 500 or timeout responses, and the batch finishes within a few seconds. The timing is recorded on the ticket so the team can decide whether a batch endpoint is needed, as with DK26-3171. A slow result is reported, not treated as a failure of the acceptance criteria.
