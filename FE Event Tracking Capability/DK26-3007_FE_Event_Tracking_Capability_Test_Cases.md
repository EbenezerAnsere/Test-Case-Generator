# DK26-3007: FE - Assess and Refine FE Event Tracking Capability

Ticket: https://amali-tech.atlassian.net/browse/DK26-3007
Status: In Progress QA
Parent: DK26-2998 Observability & Operational Excellence
Xray folder: `Quarter 4/Ebenezer/Frontend/DK26-3007 FE - Assess and Refine FE Event Tracking Capability`
Test Set: DK26-3218

## Review Summary

This story is a gap analysis rather than a feature build: the FE events already sent to Grafana are reviewed for completeness, optimized where needed, and documented. Testing therefore verifies the *outcome* of the analysis - that the inventory matches the code, that every tracked event actually reaches Grafana and is referenced there, that identified gaps are logged, and that the refinement broke nothing that previously worked.

## Test Plan

- Goal: Confirm FE event tracking is complete, correctly delivered to Grafana, and documented.
- Scope: Event inventory accuracy, instrumentation firing, Grafana delivery and dashboard reference, payload schema, gap tracking, documentation, regression and privacy.
- Environment: QA or staging with event tracking enabled, plus Grafana access to the FE event data source.
- Preconditions:
  - The gap analysis output and event inventory are available.
  - Grafana permissions allow querying the FE event data source and viewing dashboards.
  - A build containing the refinement changes is deployed.

## Acceptance Criteria Coverage

| Acceptance criterion | Covered by |
| --- | --- |
| The current events are re-analysed and optimized if necessary. | TC-01, TC-08, TC-09 |
| Any identified gap is tracked and accounted for. | TC-05 |
| All tracked events are referenced on Grafana. | TC-03, TC-07 |
| All tracked events are documented. | TC-06 |
| Cross-cutting quality checks | TC-02, TC-04, TC-10, TC-11 |

## Test Cases

### TC-DK26-3007-01: FE Event Inventory Matches Codebase

- Jira: [DK26-3207](https://amali-tech.atlassian.net/browse/DK26-3207)
- Preconditions: Access to the FE codebase and to the event tracking documentation produced by the gap analysis.
- Steps:
  1. Open the FE event tracking inventory produced by the gap analysis.
  2. Extract the full list of documented event names and their trigger points.
  3. Search the FE codebase for every tracking/analytics dispatch call.
  4. Compare the code-derived event list against the documented inventory in both directions.
- Expected:
  - Every event emitted by FE code appears in the documented inventory, and every documented event exists in the code. No undocumented events and no stale entries remain. Any discrepancy found is recorded as a tracked gap rather than left unlogged.

### TC-DK26-3007-02: Tracked Events Fire on Their User Actions

- Jira: [DK26-3208](https://amali-tech.atlassian.net/browse/DK26-3208)
- Preconditions: QA or staging build with event tracking enabled; browser developer tools open on the Network tab.
- Steps:
  1. Log in to the application on the QA environment.
  2. Perform each user action listed in the documented event inventory, covering navigation, create, update, delete and submit flows.
  3. Observe the outgoing tracking requests produced by each action.
  4. Record which actions emit an event and which emit nothing.
- Expected:
  - Each documented user action emits exactly its mapped event, once per action. No inventory action fails to emit, and no action emits unintended duplicate events.

### TC-DK26-3007-03: Tracked Events Are Delivered to Grafana

- Jira: [DK26-3209](https://amali-tech.atlassian.net/browse/DK26-3209)
- Preconditions: QA or staging environment; Grafana access with permission to query the FE event data source.
- Steps:
  1. Note the current timestamp, then perform a known set of instrumented FE actions.
  2. Open Grafana and query the FE event data source for that time window.
  3. Verify each triggered event appears in the results.
  4. Confirm the event name, timestamp and source attributes match what was triggered.
- Expected:
  - Every event triggered in the FE appears in Grafana within the expected ingestion delay, with matching name, timestamp and attributes. No triggered event is missing from the data source.

### TC-DK26-3007-04: Event Payload Schema Is Consistent and Complete

- Jira: [DK26-3210](https://amali-tech.atlassian.net/browse/DK26-3210)
- Preconditions: QA or staging environment; documented event schema defining required properties per event.
- Steps:
  1. Trigger a representative event from each event category in the inventory.
  2. Capture the full payload of each emitted event.
  3. Compare each payload against the documented required properties for that event.
  4. Check that shared properties such as user id, session id, timestamp and app version use consistent names and types across all events.
- Expected:
  - Every event payload contains all required properties with correct types. Shared properties are named and typed identically across events. No event emits a malformed, empty or partially populated payload.

### TC-DK26-3007-05: Identified Tracking Gaps Are Tracked and Accounted For

- Jira: [DK26-3211](https://amali-tech.atlassian.net/browse/DK26-3211)
- Preconditions: Gap analysis complete; access to the Jira backlog used to record findings.
- Steps:
  1. Open the gap analysis output and list every gap identified.
  2. For each gap, locate the corresponding Jira issue or backlog entry.
  3. Confirm each entry describes the missing or incorrect event and its impact.
  4. Verify no gap from the analysis is left without a tracked entry.
- Expected:
  - Every identified gap has a corresponding tracked Jira issue describing the missing or incorrect event. No gap is closed, dismissed or left untracked without a recorded justification.

### TC-DK26-3007-06: All Tracked Events Are Documented and Accessible

- Jira: [DK26-3212](https://amali-tech.atlassian.net/browse/DK26-3212)
- Preconditions: Access to the agreed documentation location for FE event tracking.
- Steps:
  1. Open the FE event tracking documentation at its agreed location.
  2. Confirm each tracked event has an entry covering its name, trigger, payload properties and purpose.
  3. Verify the documentation states where the event is surfaced in Grafana.
  4. Confirm the document is reachable by the wider team and carries a last-updated reference.
- Expected:
  - Documentation exists at the agreed location and covers every tracked event with name, trigger, payload and purpose. It is accessible to the team and reflects the current state of the code after the refinement.

### TC-DK26-3007-07: All Tracked Events Are Referenced on Grafana Dashboards

- Jira: [DK26-3213](https://amali-tech.atlassian.net/browse/DK26-3213)
- Preconditions: Grafana access with permission to view the FE observability dashboards and their panel queries.
- Steps:
  1. Open the FE observability dashboards in Grafana.
  2. List every event name referenced by the dashboard panels and queries.
  3. Compare that list against the documented event inventory.
  4. Identify any tracked event that no panel or query references.
- Expected:
  - Every tracked event is referenced by at least one Grafana panel, query or alert. Any event collected but not surfaced anywhere is either given a reference or recorded as a deliberate, documented exception.

### TC-DK26-3007-08: Redundant and Duplicate Events Are Removed

- Jira: [DK26-3214](https://amali-tech.atlassian.net/browse/DK26-3214)
- Preconditions: Access to the pre-refinement event list and the optimized post-refinement inventory.
- Steps:
  1. Compare the pre-refinement event list against the optimized inventory.
  2. Identify events that were merged, renamed or removed during optimization.
  3. Trigger the affected user flows in the QA environment.
  4. Observe the emitted events for duplicates or events that should no longer fire.
- Expected:
  - Removed events no longer fire, merged events emit a single consolidated event, and renamed events emit only under the new name. No user action produces redundant duplicate events.

### TC-DK26-3007-09: No Regression in Previously Working Events

- Jira: [DK26-3215](https://amali-tech.atlassian.net/browse/DK26-3215)
- Preconditions: QA or staging build containing the refinement changes; list of events that were working before the change.
- Steps:
  1. Take the list of events confirmed working before the refinement.
  2. Trigger each corresponding user action on the updated build.
  3. Confirm each event still fires with its expected payload.
  4. Query Grafana to confirm each event still arrives at the data source.
- Expected:
  - Every event that worked before the refinement still fires and still reaches Grafana. The optimization introduces no loss of existing tracking coverage.

### TC-DK26-3007-10: Event Tracking Degrades Safely on Network Failure

- Jira: [DK26-3216](https://amali-tech.atlassian.net/browse/DK26-3216)
- Preconditions: QA or staging environment; ability to simulate offline conditions or block the tracking endpoint in developer tools.
- Steps:
  1. Simulate an offline state or block the tracking endpoint in developer tools.
  2. Perform several instrumented user actions.
  3. Confirm the application remains usable and surfaces no tracking-related error to the user.
  4. Restore connectivity and observe whether queued events are retried or dropped as designed.
- Expected:
  - Tracking failures never block or degrade the user-facing experience and never surface an error to the user. Event loss or retry behaviour on reconnect matches the documented design.

### TC-DK26-3007-11: Event Payloads Contain No Sensitive Data

- Jira: [DK26-3217](https://amali-tech.atlassian.net/browse/DK26-3217)
- Preconditions: QA or staging environment; organisation guidance on what may not be sent to observability tooling.
- Steps:
  1. Trigger events across authentication, profile, assessment and administrative flows.
  2. Capture the full payload of each emitted event.
  3. Inspect every property for personal or sensitive values such as passwords, tokens, full email addresses or candidate answer content.
  4. Confirm user identifiers are sent in the agreed non-identifying form.
- Expected:
  - No event payload carries passwords, tokens, candidate answer content or other sensitive data. User identifiers appear only in the agreed non-identifying form, consistent with organisation guidance.

## Critical Edge Cases

- EC-1: An event fires correctly in the FE but never arrives in Grafana.
  - Expected: Treated as a tracked gap with a logged issue, not silently accepted.
- EC-2: An event is collected and delivered but referenced by no dashboard or alert.
  - Expected: Either given a Grafana reference or recorded as a deliberate documented exception.
- EC-3: Documentation drifts after a later code change.
  - Expected: The inventory carries a last-updated reference so drift is detectable.
