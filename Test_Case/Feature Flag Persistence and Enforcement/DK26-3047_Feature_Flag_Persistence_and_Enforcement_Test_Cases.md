# DK26-3047: Fix feature flag toggles not persisting or taking effect in production

Ticket: https://amali-tech.atlassian.net/browse/DK26-3047
Status: In Progress QA
Parent: DK26-2998 Observability & Operational Excellence
Subtasks: DK26-3048 to DK26-3057, DK26-3472, DK26-3533 (all CODE ON STAGING)
Xray folder: `Quarter 4/Ebenezer/Frontend/DK26-3047 Fix feature flag toggles not persisting or taking effect in production` (not yet created, Xray key returns 401)
Jira test cases: DK26-3673 to DK26-3692 (linked to DK26-3047 as Test)
Test Plan: DK26-3106
Test Execution: DK26-3107

## Review Summary

Flag changes were always saved, but they did not seem to stick or take effect, for several reasons:

- The admin page showed each flag as it applied to the admin viewing it, so a flag targeting other organisations looked OFF after the next live update.
- The app treated a missing flag as ON, and a failed fetch (429 or 503) wiped the whole flag set.
- The live stream gave up after 3 retries.
- test-execution and notification never loaded flags, and they applied other environments' changes.
- No API endpoint was gated by a flag.
- Saving the edit form dropped targeted organisations missing from its dropdown.
- Delete needed an admin key that no client sent.

Fuad Muhammed fixed these in the subtasks above.

Points to watch:

- Production has 19 flags after the removals, all public, with no targeting or rollout (inventory of 29 Oct). Targeting and rollout checks therefore use a test flag on staging.
- Delete is production-only by design. On dev and staging it shows a message instead.
- Fuad noted on 30 Oct that live flag changes did not yet reach the dev and staging backend services. If that is still the case, TC-08, TC-12 and TC-13 fail on the 5-second check.
- Gated endpoints so far: create assessment from file, AI question generation and assessment recall (DK26-3472).
- DK26-3533 must reach production on the frontend first, and sittings in progress should finish before the backend change ships.
- Put back every real flag changed during testing.
- Older feature flag tests (DK26-500 to DK26-513, DK26-371, DK26-600) cover basic create, read and delete. They do not cover these fixes.

## Acceptance Criteria Coverage

| Acceptance criterion | Covered by |
| --- | --- |
| A toggle in the admin UI shows the stored state after a refresh and across sessions, including for targeted and rollout flags. | TC-01, TC-02, TC-03, TC-04 |
| A change takes effect for affected users within 5 seconds without a page reload, and consumers ignore events from other environments. | TC-05, TC-06, TC-07, TC-08 |
| Missing or unknown flags default to OFF, and a failed fetch keeps the last known values. | TC-09, TC-10, TC-11 |
| Backend routes gated by a flag allow or reject requests according to the flag. | TC-12, TC-13, TC-14 (and TC-19 for DK26-3533) |
| Saving a flag never drops its targeting configuration. | TC-15, TC-16 |
| Flag keys used in code match the stored keys, unused flags are removed, and delete works for system admins (or is removed from the UI). | TC-17, TC-18 |
| Unit tests and a staging end-to-end test cover the above, and the behaviour is verified in production after release. | TC-20 |

## Preconditions

### PC-DK26-3047-01: Feature flag fixes deployed on staging and a System Admin signed in

1. Staging runs the code from DK26-3048 to DK26-3057, DK26-3472 and DK26-3533 (all CODE ON STAGING).
2. test-execution and notification have the flag service URL and environment key on staging (DK26-3054) and load their flags at startup.
3. A System Admin can open the Feature Flags admin page on staging.
4. A dedicated test flag can be created and changed freely (for example qa_flag_3047), so that real features are not switched off for others. Any real flag changed during testing is put back to its original value afterwards, and the original values are noted before starting.

### PC-DK26-3047-02: Organisations, users and browsers for targeting and propagation checks

1. Two organisations, Org A and Org B, each with a user who can create assessments. Org A is not on the first page of the organisation dropdown in the flag edit modal (or the list has more organisations than the dropdown loads).
2. A second System Admin session (another browser or a private window) is available.
3. A gated feature visible in the app is known for each check, for example 'Create assessment from file' (gated in the UI and on the API by DK26-3472), AI question generation and assessment recall.
4. Browser developer tools are available to watch the flag stream, block requests and override responses (Network request blocking, Local overrides, or a proxy such as Burp or Charles).
5. An API client such as Postman, with access tokens for users in Org A and Org B.

### PC-DK26-3047-03: Developer and DevOps support for service, log and production checks

1. Read access to the flag service and backend service logs (Grafana), or Fuad Muhammed is available to check them.
2. A way to make the flag service unreachable for a backend service on staging, or developer help to do so.
3. Read access to the CI runs of the flag service, frontend and backend repositories.
4. For the production checks: the release is live, a System Admin login on production is available, and the production flag values were recorded before the release (inventory of 29 Oct: 21 flags, then 19 after the removals).

## Test Cases

### TC-DK26-3047-01: A global flag toggle shows the stored state after a refresh and in a new session

- Jira: [DK26-3673](https://amali-tech.atlassian.net/browse/DK26-3673)
- Linked preconditions: PC-DK26-3047-01, PC-DK26-3047-02
- Preconditions: System Admin on the Feature Flags page on staging; the test flag exists and applies to everyone; a second admin session is available.
- Steps:
  1. Turn the test flag ON and wait a few seconds.
  2. Refresh the page and read the toggle.
  3. Sign out and sign back in, then read the toggle.
  4. Open the page in the second admin session and read the toggle.
  5. Turn the flag OFF and repeat steps 2 to 4.
- Expected result: After each refresh, new sign-in and in the other session, the toggle shows the value last saved (ON, then OFF). It never flips back by itself. The flag's API record (GET the flag) has the same value as the page.

### TC-DK26-3047-02: A flag targeted at other organisations stays ON after a refresh and after other flags change

- Jira: [DK26-3674](https://amali-tech.atlassian.net/browse/DK26-3674)
- Linked preconditions: PC-DK26-3047-01, PC-DK26-3047-02
- Preconditions: System Admin on the Feature Flags page on staging; the test flag targets Org B only, and the admin's own organisation is not Org B.
- Steps:
  1. Turn the targeted test flag ON.
  2. Change another test flag, and wait for the live update to arrive.
  3. Refresh the page and read the targeted flag's toggle.
  4. Sign out and back in, then read it again.
  5. Open the page as the second admin and read it.
- Expected result: The targeted flag stays ON in every case, even though the viewing admin is not in Org B. The page shows the stored setting, not what the flag means for the person viewing it. This is the main bug of the story: before the fix, the toggle went back to OFF on the next live update.

### TC-DK26-3047-03: A flag with a percentage rollout keeps its stored state on the admin page

- Jira: [DK26-3675](https://amali-tech.atlassian.net/browse/DK26-3675)
- Linked preconditions: PC-DK26-3047-01
- Preconditions: System Admin on the Feature Flags page on staging; a test flag with a percentage rollout (for example 10%) can be set up.
- Steps:
  1. Set a test flag to a 10% rollout and turn it ON.
  2. Change another flag to trigger a live update.
  3. Refresh the page, sign out and back in, and open it as the second admin.
  4. Read the toggle and the rollout percentage each time.
- Expected result: The flag shows ON with a 10% rollout every time, whether or not the viewing admin falls inside the rollout. The percentage is not changed or lost.

### TC-DK26-3047-04: The admin page updates live when another admin changes a flag

- Jira: [DK26-3676](https://amali-tech.atlassian.net/browse/DK26-3676)
- Linked preconditions: PC-DK26-3047-01, PC-DK26-3047-02
- Preconditions: Two System Admin sessions on the Feature Flags page on staging.
- Steps:
  1. In session 1, turn a test flag ON.
  2. Watch session 2 without refreshing, and note how long the change takes to appear.
  3. In session 2, turn a targeted test flag OFF and watch session 1.
- Expected result: Each session shows the other's change within 5 seconds without a refresh, with the stored value (a targeted flag shows its stored ON or OFF, not the viewer's evaluation).

### TC-DK26-3047-05: Turning a global flag off and on reaches signed-in users within 5 seconds without a reload

- Jira: [DK26-3677](https://amali-tech.atlassian.net/browse/DK26-3677)
- Linked preconditions: PC-DK26-3047-01, PC-DK26-3047-02
- Preconditions: System Admin on the Feature Flags page; an Org A user signed in, in another browser, on a page showing a gated feature (for example 'Create from file' on Create Assessment).
- Steps:
  1. With the user's page open, turn the feature's flag OFF and start a timer.
  2. Watch the user's page without reloading and note when the feature disappears.
  3. Turn the flag back ON and note when the feature returns.
  4. Put the flag back to its original value.
- Expected result: The feature disappears within 5 seconds of turning the flag OFF and comes back within 5 seconds of turning it ON, with no page reload. No error appears on the user's page.

### TC-DK26-3047-06: A targeted flag change reaches only the targeted organisation

- Jira: [DK26-3678](https://amali-tech.atlassian.net/browse/DK26-3678)
- Linked preconditions: PC-DK26-3047-01, PC-DK26-3047-02
- Preconditions: Users from Org A and Org B signed in, in separate browsers, on a page with a gated feature; the feature's flag can be targeted.
- Steps:
  1. Set the feature's flag to target Org A only, and turn it ON.
  2. Watch both users' pages without reloading.
  3. Remove Org A from the targeting and add Org B, then save.
  4. Watch both pages again, then restore the flag.
- Expected result: Within 5 seconds, the feature appears for the Org A user only, and the Org B user does not see it. After the targeting is switched, it disappears for Org A and appears for Org B within 5 seconds. No reload is needed.

### TC-DK26-3047-07: The flag stream reconnects after a drop and picks up changes made meanwhile

- Jira: [DK26-3679](https://amali-tech.atlassian.net/browse/DK26-3679)
- Linked preconditions: PC-DK26-3047-01, PC-DK26-3047-02
- Preconditions: An Org A user signed in on a page with a gated feature, with developer tools open on the Network tab; a System Admin in another browser.
- Steps:
  1. In the user's browser, set the network to Offline (or block the flag stream request) for about a minute, so that the stream fails more than 3 times.
  2. While the user is offline, the admin changes the feature's flag.
  3. Put the user's network back online and watch the stream and the page without reloading.
  4. Leave the page idle until the server closes the stream (idle timeout), or ask a developer to restart the flag service, then change the flag again.
- Expected result: The stream keeps retrying with growing waits and no limit, and reconnects once the network is back. After reconnecting, the full flag set is fetched again, so the change made while offline shows without a reload. It also reconnects after a normal close or service restart, and the later change arrives. The user is not logged out.

### TC-DK26-3047-08: Backend services load flags at startup and ignore changes from other environments

- Jira: [DK26-3680](https://amali-tech.atlassian.net/browse/DK26-3680)
- Linked preconditions: PC-DK26-3047-01, PC-DK26-3047-03
- Preconditions: Staging and dev with DK26-3053 and DK26-3054 deployed; access to service logs, or help from Fuad Muhammed.
- Steps:
  1. Check the test-execution and notification logs on staging after their last restart for the flags they loaded.
  2. On dev, change a backend-checked flag (or the test flag) and note the flag service log entry and its environment.
  3. Check that staging's backend services did not apply the dev change, and that staging behaviour is unchanged.
  4. Change the same flag on staging and check that staging's services apply it within 5 seconds.
- Expected result: Both services load their flags at startup without errors (the object response is read correctly). Flag service logs show which environment each request served. A change on dev is ignored by staging's services, and a change on staging is applied there within 5 seconds.

### TC-DK26-3047-09: A missing or unknown flag counts as OFF

- Jira: [DK26-3681](https://amali-tech.atlassian.net/browse/DK26-3681)
- Linked preconditions: PC-DK26-3047-01, PC-DK26-3047-02
- Preconditions: An Org A user signed in; developer tools able to override the flags response (Local overrides or a proxy).
- Steps:
  1. Override the flags response so that a gated feature's flag is missing, then reload the page.
  2. Check whether the feature is shown.
  3. Send a live update that lacks that flag's value, or an update for an unknown key, and check the page again.
  4. Remove the override and reload.
- Expected result: A feature whose flag is missing is hidden (OFF), on load and after a live update. An unknown key changes nothing else. Every place in the app follows the same rule, with no feature shown because its flag is absent. After removing the override, the feature returns according to its real value.

### TC-DK26-3047-10: A failed flag fetch keeps the last known values

- Jira: [DK26-3682](https://amali-tech.atlassian.net/browse/DK26-3682)
- Linked preconditions: PC-DK26-3047-01, PC-DK26-3047-02
- Preconditions: An Org A user signed in, with some gated features ON and some OFF; developer tools able to return 429 and 503 for the flags request.
- Steps:
  1. Note which gated features the user sees.
  2. Make the flags request return 429, then trigger a re-fetch (reconnect the stream, or navigate in the app).
  3. Check the gated features.
  4. Repeat with a 503 response and with the request blocked entirely.
  5. Restore the request and change a flag as admin.
- Expected result: After a failed fetch the user sees exactly the same features as before: nothing switches on, and nothing switches off. No error page appears. Once the request works again, flag changes apply normally.

### TC-DK26-3047-11: A flag removed from the service is removed in the app on the next update

- Jira: [DK26-3683](https://amali-tech.atlassian.net/browse/DK26-3683)
- Linked preconditions: PC-DK26-3047-01, PC-DK26-3047-02
- Preconditions: A test flag that is ON and read by a test page or visible in the flag state of the app; a user signed in.
- Steps:
  1. Check the app's flag state in developer tools (the flags response) and note the test flag as ON.
  2. Remove the test flag from the service (on staging use the method the team agreed, since delete is production-only), or override the response to leave it out.
  3. Trigger a live update or re-fetch, and check the app's flag state.
- Expected result: After the update, the removed flag is no longer in the app's flag state and counts as OFF. Other flags keep their values: the update merges changes rather than replacing everything.

### TC-DK26-3047-12: Create assessment from file is allowed or refused on the API according to its flag

- Jira: [DK26-3684](https://amali-tech.atlassian.net/browse/DK26-3684)
- Linked preconditions: PC-DK26-3047-01, PC-DK26-3047-02
- Preconditions: An API client with tokens for Org A and Org B users; the 'Create assessment from file' flag can be targeted; its original value noted.
- Steps:
  1. Target the flag at Org A only and turn it ON.
  2. Call the create-from-file upload endpoint as Org A, then as Org B.
  3. Turn the flag OFF and call it as both organisations again.
  4. Turn it ON for everyone and call it as both.
  5. Restore the flag's original setting.
- Expected result: With Org A targeted, Org A's request succeeds and Org B's is refused with a clear 'feature not available' error (403 or the agreed code). With the flag OFF, both are refused. With it ON for everyone, both succeed. Each change takes effect within 5 seconds, matching what the UI shows.

### TC-DK26-3047-13: AI question generation and assessment recall are refused on the API when their flags are off

- Jira: [DK26-3685](https://amali-tech.atlassian.net/browse/DK26-3685)
- Linked preconditions: PC-DK26-3047-01, PC-DK26-3047-02
- Preconditions: An API client with an Org A token; the AI question generation and assessment recall flags, with their original values noted.
- Steps:
  1. With both flags ON for Org A, call the AI question generation and assessment recall endpoints.
  2. Turn the AI question generation flag OFF and call it again.
  3. Turn the assessment recall flag OFF and call it again.
  4. Restore both flags.
- Expected result: With a flag ON, its endpoint works. With it OFF, the endpoint refuses the request with the same clear error as create from file, and no AI cost is incurred and no recall happens. Endpoints not tied to a flag keep working.

### TC-DK26-3047-14: The backend keeps the last known flag values when the flag service is unreachable

- Jira: [DK26-3686](https://amali-tech.atlassian.net/browse/DK26-3686)
- Linked preconditions: PC-DK26-3047-01, PC-DK26-3047-03
- Preconditions: Developer help to make the flag service unreachable for the backend on staging; an API client with an Org A token.
- Steps:
  1. Note the current value of the create-from-file flag for Org A (for example ON), and of one flag that is OFF.
  2. Make the flag service unreachable from the backend.
  3. Call the gated endpoints for both flags.
  4. Restore access and check the logs.
- Expected result: While the flag service is down, the endpoint whose flag was ON still works, and the one that was OFF is still refused. Nothing switches on or off because of the outage. Logs record the failed fetches, and normal updates resume once access is back.

### TC-DK26-3047-15: Editing a flag keeps its targeted organisations, including ones not loaded in the dropdown

- Jira: [DK26-3687](https://amali-tech.atlassian.net/browse/DK26-3687)
- Linked preconditions: PC-DK26-3047-01, PC-DK26-3047-02
- Preconditions: System Admin on staging; a test flag targeting Org A (not on the dropdown's first page) and Org B.
- Steps:
  1. Note the flag's targeted organisation IDs from the API (GET the flag).
  2. Open the edit modal, change only the description and save.
  3. Open the edit modal again and save without changes.
  4. Read the flag from the API and compare the targeted organisations.
- Expected result: Both Org A and Org B are still targeted after each save, and the list from the API is identical to the one noted at the start. The modal shows both organisations even though Org A is not in the loaded dropdown list.

### TC-DK26-3047-16: Targeting survives switching a flag off and on, and a failed details load cannot wipe it

- Jira: [DK26-3688](https://amali-tech.atlassian.net/browse/DK26-3688)
- Linked preconditions: PC-DK26-3047-01, PC-DK26-3047-02
- Preconditions: System Admin on staging; a test flag targeting Org A and Org B; developer tools able to block or fail the flag details request.
- Steps:
  1. Turn the targeted flag OFF, then ON again, and read its targeting from the API.
  2. Block the flag details request and open the edit modal.
  3. Try to change the description and save.
  4. Unblock the request and read the flag from the API.
- Expected result: Switching off and on keeps both organisations. When the details fail to load, the modal shows an error and does not let the user save with empty targeting, or saving keeps the stored targeting. Afterwards the API still lists both organisations.

### TC-DK26-3047-17: Flag keys in code match the stored keys, and the unused flags are gone

- Jira: [DK26-3689](https://amali-tech.atlassian.net/browse/DK26-3689)
- Linked preconditions: PC-DK26-3047-01, PC-DK26-3047-03
- Preconditions: System Admin on staging; read access to the frontend and backend repositories, or help from Fuad Muhammed.
- Steps:
  1. List all flags on the Feature Flags page (or from the API) on staging.
  2. Search for flagged_candidate_768210 and theme_service_test_taker_317250.
  3. Check every stored key against the naming rule (lower case with underscores, no camelCase or hyphens).
  4. Compare the list of keys read in the code with the stored keys, including that proctoring-require-violation-type is no longer read anywhere.
- Expected result: The two unused flags no longer exist. All 19 remaining keys follow the naming rule. Every key the code reads exists in the store with exactly the same spelling, and no stored flag is unused.

### TC-DK26-3047-18: Delete gives a clear message on staging and works for System Admins on production

- Jira: [DK26-3690](https://amali-tech.atlassian.net/browse/DK26-3690)
- Linked preconditions: PC-DK26-3047-01, PC-DK26-3047-03
- Preconditions: System Admin on staging; for the production step, a System Admin on production and a throwaway flag created there for this check, agreed with the team.
- Steps:
  1. On staging, try to delete the test flag from the admin page.
  2. Read the message, and check that the flag still exists.
  3. As a user who is not a System Admin, call the delete endpoint through the gateway.
  4. On production, after the release, delete the throwaway flag as a System Admin and check that it is gone from every environment.
- Expected result: On staging (and dev), delete is not carried out and a clear message says that deleting is done from production because it affects every environment. A non-System-Admin is refused. On production, a System Admin can delete the flag, it disappears from all environments, and no request fails with a missing admin key.

### TC-DK26-3047-19: Proctoring violations always carry a type, and one without a type is rejected

- Jira: [DK26-3691](https://amali-tech.atlassian.net/browse/DK26-3691)
- Linked preconditions: PC-DK26-3047-01, PC-DK26-3047-02
- Preconditions: DK26-3533 frontend and backend changes on staging; a proctored assessment with screen and camera capture; an API client.
- Steps:
  1. Sit the proctored assessment with screen capture on, and move the mouse out of the test window several times, switch tabs and trigger other violations.
  2. Save and submit, then check the stored violations on the candidate report.
  3. Send a violation request without a type field using the API client.
- Expected result: The sitting saves and submits normally, and every stored violation has a type, including mouse-leave with screen capture on. The request without a type is rejected with a clear validation error, whatever any flag says, since the rollout flag no longer exists.

### TC-DK26-3047-20: Unit and staging end-to-end tests pass, and the behaviour is confirmed in production

- Jira: [DK26-3692](https://amali-tech.atlassian.net/browse/DK26-3692)
- Linked preconditions: PC-DK26-3047-03
- Preconditions: Read access to CI; after the release, a System Admin on production and the flag values recorded before the release.
- Steps:
  1. Open the latest CI runs of the flag service, frontend and backend, and find the tests for stored state, defaults, merging, targeting on save and endpoint enforcement.
  2. Check the staging end-to-end results from DK26-3057.
  3. After the release, compare every production flag's value with the values recorded before.
  4. On production, repeat TC-01, TC-05 and TC-12 with a flag agreed with the team, and put it back afterwards.
- Expected result: All the tests are present and pass in CI, including the frontend flag tests that now run there. The staging end-to-end test passes. In production no flag value has changed because of the release, a toggle keeps its stored state, a change reaches users within 5 seconds, and a gated endpoint follows its flag.
