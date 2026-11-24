# DK26-3750: Add audit to user activities in the system (Example: Activating and Deactivating users)

Ticket: https://amali-tech.atlassian.net/browse/DK26-3750
Status: In Progress QA
Subtasks: DK26-3755 to DK26-3765 and DK26-3886 (one per service; CODE ON STAGING, DK26-3762 in DK26 REVIEW)
Related: DK26-3798 UI/UX - Audit Logs design (Done, no screen built yet)
Xray folder: `Quarter 4/Ebenezer/Backend/DK26-3750 Add audit to user activities in the system (Example: Activating and Deactivating users)` (not yet created, Xray key returns 401)
Jira test cases: DK26-3916 to DK26-3935 (linked to DK26-3750 as Test)
Test Plan: DK26-3106
Test Execution: DK26-3107

## Review Summary

Before this story, the platform could not reliably say who did what, to whom, and when. Durable audit rows were written only for system-org admins. Targets were not named, and before and after states were hardcoded. Authentication recorded nothing, history was deleted with the admin who wrote it, and org admins could not read any of it.

The fix gives every service one shared record format (packages/audit) with these fields:

- actor, resource and outcome
- changes
- context: request id, IP, user agent and auth method
- IDs only, no personal data

Each service writes a flat audit_event line to Loki and publishes to the audit-events Kafka topic. user-management stores every record in an append-only audit_logs table and serves it through an org-scoped, paginated GET /audit-logs. The gateway sets the request context and marks calls made with an API key.

Points to watch:

- There is no Audit Logs screen yet, only the design (DK26-3798), so every test calls the API.
- Several tests need database, Loki or Kafka access, or help from Fuad Muhammed: TC-08, TC-09, TC-10 and TC-19.
- The story lists five decisions to make before build: storage, retention, read access, personal data and auditing reads. TC-20 checks that they are recorded.
- Your earlier activity-log tests (DK26-272 to DK26-298, DK26-510) cover the old activity log, not this audit trail.

## Acceptance Criteria Coverage

| Acceptance criterion | Covered by |
| --- | --- |
| AC1: One durable record per affected user for activate, deactivate, reactivate, block, unblock, delete and role change, with actor, target, before and after state and timestamp. Deactivating an org writes one for the org plus one per member. | TC-01, TC-02, TC-03, TC-04, TC-05 |
| AC2: Records are written for every organisation, not only the system org. | TC-06 |
| AC3: Records survive deletion of both actor and target. The store is append-only. | TC-07, TC-08, TC-09 |
| AC4: A committed change always gets its record, and a rolled-back change never does. | TC-10 |
| AC5: Org admins list their org's records with filters and pagination. System admins query any org. Others are refused. | TC-11, TC-12, TC-13 |
| AC6: A refused attempt (401/403) on an audited operation writes a failure record. | TC-14 |
| AC7: Every record carries request id, client IP, user agent and auth method, so API keys and people can be told apart. | TC-15, TC-16 |
| AC8: Records contain no personal data beyond IDs. | TC-17 |
| End-to-end check (org admin A deactivates user B) | TC-01 (step 1), TC-18 (step 2), TC-11 (step 3), TC-07 (step 4) |
| Shared rules across services, tests and documentation | TC-19, TC-20 |

## Preconditions

### PC-DK26-3750-01: Audit trail subtasks deployed on staging, with accounts and an API client

1. Staging runs the audit work from DK26-3755 to DK26-3765 and DK26-3886 (CODE ON STAGING), including the audit_logs table, the audit-events consumer and GET /audit-logs in user-management.
2. An API client such as Postman, calling through the api-gateway on staging.
3. Accounts and tokens for: Org admin A in org X; users B, C and D in org X (B active, C with a role that can be changed, D with no permission to manage users); Org admin E in org Y; a System admin; and an organisation admin F in a test org Z with at least three members, which can be deactivated.
4. An API key for org X, issued through external-api-integration, and its key id.
5. The ids of every account above are noted.

### PC-DK26-3750-02: Read access to the audit store, Loki and Kafka, or developer support

1. Read-only access to the staging audit_logs table, or Fuad Muhammed available to run queries.
2. Access to Loki (Grafana) for staging service logs, to query log_type="audit_event".
3. Developer support to replay the audit-events-staging topic, to look at its dead-letter queue, and to force a failure inside a user-management transaction (or a known input that makes it roll back).
4. Read access to the dodokpo-backend repository, CI runs and OBSERVABILITY.md.

### PC-DK26-3750-03: Open decisions from the story are recorded

1. The decisions listed under 'Decisions needed before build' are recorded on DK26-3750 or OBSERVABILITY.md: where records are stored (one central store in user-management is assumed), the retention period, which records org admins can read, whether the actor's name is copied into records, and whether audits of reads stay in this story.
2. Where a decision is not recorded, the tests that depend on it note it as a finding.

## Test Cases

### TC-DK26-3750-01: Deactivating a user writes one record with actor, target, before and after state, and context

- Jira: [DK26-3916](https://amali-tech.atlassian.net/browse/DK26-3916)
- Linked preconditions: PC-DK26-3750-01, PC-DK26-3750-02
- Preconditions: Staging with the audit work deployed; Org admin A and active user B in org X; access to audit_logs or GET /audit-logs.
- Steps:
  1. As Org admin A, deactivate user B through the gateway, sending a known User-Agent, and note the time and the response's x-request-id.
  2. Call GET /audit-logs as A, filtered by target B and event user.deactivated.
  3. Read every field of the record.
  4. Check audit_logs (or ask a developer) for any other record for this action.
- Expected result: Exactly one user.deactivated record exists, with: a UUID event_id; event_category; occurred_at in UTC ISO-8601 within seconds of the action; actor {type: user, id: A, org_id: X, role: A's role}; resource {type: user, id: B, org_id: X}; outcome success; changes with the status going from active to deactivated, read from the database and not hardcoded; context with the request id, client IP, user agent and auth_method user; service user-management.

### TC-DK26-3750-02: Activation, reactivation and unblocking are recorded as different events with the real before state

- Jira: [DK26-3917](https://amali-tech.atlassian.net/browse/DK26-3917)
- Linked preconditions: PC-DK26-3750-01, PC-DK26-3750-02
- Preconditions: Org admin A in org X; user B deactivated by TC-01; a user blocked by the platform (ask a developer, or trigger the lockout block).
- Steps:
  1. As A, reactivate user B.
  2. Have the platform block a user, then lift the block (as a System admin, or by the bulk unblock).
  3. Invite a new user and accept the invite with create-password, so they become active.
  4. Read the records for each user from GET /audit-logs.
- Expected result: B's reactivation writes user.activated (or the documented reactivation event) with changes from deactivated to active. Lifting a platform block writes user.unblocked with the blocked state as the before value, not an ordinary reactivation. The block itself writes user.blocked with a system actor. Accepting the invite records the activation. Each change writes exactly one record per affected user.

### TC-DK26-3750-03: A role change records the old and new role, and a role update records the permission changes

- Jira: [DK26-3918](https://amali-tech.atlassian.net/browse/DK26-3918)
- Linked preconditions: PC-DK26-3750-01, PC-DK26-3750-02
- Preconditions: Org admin A in org X; user C with a known role; a custom role in org X that A can edit.
- Steps:
  1. As A, change user C's role from role R1 to role R2.
  2. Edit the custom role, adding one permission and removing another.
  3. Read the records for C and for the role from GET /audit-logs.
- Expected result: One user.role_changed record names actor A and resource C, with changes [{field: role, old: R1, new: R2}]. One role.permissions_changed record names the role as the resource and lists the added and removed permissions. No secret or personal data is in the changes.

### TC-DK26-3750-04: Deleting a user writes a record that keeps the deleted user's ids and key fields

- Jira: [DK26-3919](https://amali-tech.atlassian.net/browse/DK26-3919)
- Linked preconditions: PC-DK26-3750-01, PC-DK26-3750-02
- Preconditions: Org admin A in org X; a throwaway user in org X created for this test.
- Steps:
  1. Note the throwaway user's id, organisation, role and status.
  2. As A (or a System admin), delete the user.
  3. Read the user.deleted record from GET /audit-logs and from audit_logs.
- Expected result: One user.deleted record exists with actor A, resource {type: user, id, org_id: X}, and the key fields of the deleted user (status, role, organisation) captured before the hard delete, as ids and values without email or name. The record is still readable after the user is gone. If the delete also removes an org with the same email, that deletion is recorded too.

### TC-DK26-3750-05: Deactivating an organisation writes one record for the org and one for each member

- Jira: [DK26-3920](https://amali-tech.atlassian.net/browse/DK26-3920)
- Linked preconditions: PC-DK26-3750-01, PC-DK26-3750-02
- Preconditions: System admin; org Z with admin F and at least three members, with their ids noted.
- Steps:
  1. As the System admin, deactivate org admin F, which deactivates the whole org Z.
  2. Read all records for org Z with that request id.
  3. Reactivate org Z and read the records again.
- Expected result: One organization.deactivated record names org Z, and there is one user.deactivated record for every member, including F. Each names the System admin as actor, and all share the same request id. Reactivation writes organization.reactivated plus one record per member. No member is missing and none is recorded twice.

### TC-DK26-3750-06: Records are written for organisation admins of every organisation, not only the system org

- Jira: [DK26-3921](https://amali-tech.atlassian.net/browse/DK26-3921)
- Linked preconditions: PC-DK26-3750-01, PC-DK26-3750-02
- Preconditions: Org admin A in org X and Org admin E in org Y, neither in the system org.
- Steps:
  1. As A, deactivate and reactivate a user in org X.
  2. As E, change the role of a user in org Y.
  3. Check audit_logs and GET /audit-logs for each action.
- Expected result: Each action has a durable record in audit_logs with the right organization_id (X or Y), not only a Loki line. Before this change, only system-org admins got database records.

### TC-DK26-3750-07: Records survive deletion of the actor and the target

- Jira: [DK26-3922](https://amali-tech.atlassian.net/browse/DK26-3922)
- Linked preconditions: PC-DK26-3750-01, PC-DK26-3750-02
- Preconditions: A throwaway org admin (actor) and a throwaway user (target) in the same org, created for this test; a System admin.
- Steps:
  1. As the throwaway admin, deactivate the throwaway user, and note the record's event_id.
  2. As the System admin, delete the throwaway user, then delete the throwaway admin.
  3. Read the record by event_id from GET /audit-logs (as the System admin) and from audit_logs.
- Expected result: The original record is unchanged, with the same actor id, resource id, changes and context. Deleting either account removes nothing from audit_logs, because the table has no foreign key that cascades. Deletion records exist for both accounts.

### TC-DK26-3750-08: The audit store cannot be changed or deleted

- Jira: [DK26-3923](https://amali-tech.atlassian.net/browse/DK26-3923)
- Linked preconditions: PC-DK26-3750-01, PC-DK26-3750-02
- Preconditions: A System admin token; an existing record's event_id; developer support for the database check.
- Steps:
  1. As the System admin, send PUT, PATCH and DELETE to /audit-logs and to /audit-logs/{id}.
  2. Ask a developer to try an UPDATE and a DELETE on one audit_logs row with the service's database user on staging.
  3. Read the record again.
- Expected result: There is no API to change or delete records: the calls return 404 or 405. The database refuses UPDATE and DELETE on audit_logs. The record is unchanged.

### TC-DK26-3750-09: Replaying the audit-events topic creates no duplicates, and bad messages go to a dead-letter queue

- Jira: [DK26-3924](https://amali-tech.atlassian.net/browse/DK26-3924)
- Linked preconditions: PC-DK26-3750-02
- Preconditions: Developer support to replay audit-events-staging and to read its dead-letter queue.
- Steps:
  1. Count the audit_logs rows for a known window of events published by other services (for example test-creation and external-api-integration).
  2. Replay the topic over that window.
  3. Count the rows again, and check for event_ids that appear more than once.
  4. Publish one malformed message and check where it goes.
- Expected result: The count is the same after the replay, and no event_id appears twice, because inserts are idempotent on event_id. The malformed message goes to the dead-letter queue with an error logged. It is not silently dropped, and it does not stop the consumer.

### TC-DK26-3750-10: A committed change always has its record, and a rolled-back change never does

- Jira: [DK26-3925](https://amali-tech.atlassian.net/browse/DK26-3925)
- Linked preconditions: PC-DK26-3750-01, PC-DK26-3750-02
- Preconditions: Org admin A in org X; developer support to force a failure inside a user-management change (or an input that makes the transaction roll back).
- Steps:
  1. Make a normal change (deactivate a user) and check that the change and its record both exist.
  2. Force a failure after the change is written but before the transaction commits (or send a change that is rejected partway), and check the user's state and the records.
  3. With the audit-events publisher unable to reach Kafka (developer help), make a change in another service, such as creating an assessment in test-creation.
  4. Restore Kafka and check the records.
- Expected result: The committed change has exactly one record. The rolled-back change leaves the user unchanged and has no record. In user-management the record is written in the same transaction as the change. When publishing fails, the user's action still succeeds, the publish is retried, and either the record arrives or an audit.publish_failed error is logged. The action is never rolled back because of the audit.

### TC-DK26-3750-11: An org admin can list their org's records with filters

- Jira: [DK26-3926](https://amali-tech.atlassian.net/browse/DK26-3926)
- Linked preconditions: PC-DK26-3750-01
- Preconditions: Org admin A in org X; the records created by TC-01 to TC-03 exist.
- Steps:
  1. As A, call GET /audit-logs with no filters.
  2. Filter by actor A, then by target B, then by event user.role_changed, then by a date range covering only today.
  3. Combine two filters (actor and event).
  4. Send a date range with the start after the end, and an unknown event name.
- Expected result: Only org X's records are returned, newest first. Each filter returns only matching records, and combined filters apply together. An invalid date range returns 400 with a clear message. An unknown event returns an empty list or a 400, not an error page or a 500.

### TC-DK26-3750-12: The audit list pages through results without gaps or duplicates

- Jira: [DK26-3927](https://amali-tech.atlassian.net/browse/DK26-3927)
- Linked preconditions: PC-DK26-3750-01
- Preconditions: Org admin A in org X; at least 30 records in org X (generate them with repeated changes if needed).
- Steps:
  1. Call GET /audit-logs with a page size of 10.
  2. Follow the next cursor until the last page.
  3. Make a new change while paging, then continue.
  4. Send a tampered or invalid cursor.
- Expected result: Pages follow on from each other with no record repeated or skipped. The last page has no next cursor. A record created while paging does not cause duplicates in later pages. An invalid cursor returns 400, not a 500 or another org's data.

### TC-DK26-3750-13: Only org admins (for their own org) and system admins can read audit records

- Jira: [DK26-3928](https://amali-tech.atlassian.net/browse/DK26-3928)
- Linked preconditions: PC-DK26-3750-01
- Preconditions: Tokens for Org admin A (org X), Org admin E (org Y), user D (org X, no admin rights) and a System admin.
- Steps:
  1. As A, request org Y's records (by organisation parameter or header).
  2. As D, request org X's records.
  3. As the System admin, request org X's records, then org Y's.
  4. Call GET /audit-logs with no token and with an expired token.
- Expected result: A gets 403 for org Y. D gets 403 for org X. The System admin can read any org. The calls without a valid token get 401. No refused call returns any record.

### TC-DK26-3750-14: A refused attempt on an audited action writes a failure record

- Jira: [DK26-3929](https://amali-tech.atlassian.net/browse/DK26-3929)
- Linked preconditions: PC-DK26-3750-01, PC-DK26-3750-02
- Preconditions: User D in org X without permission to manage users; Org admin E in org Y; access to audit_logs or Loki.
- Steps:
  1. As D, try to deactivate user B (expect 403).
  2. As E, try to change the role of a user in org X (expect 403).
  3. Call the deactivate endpoint with an invalid token and with an expired token (expect 401).
  4. Look for the matching records.
- Expected result: Each refusal writes a record with outcome failure and a reason, naming the actor (D or E, or null for the invalid token) and the resource that was attempted. The gateway writes gateway.auth.denied for the invalid and expired tokens. The target user is unchanged.

### TC-DK26-3750-15: Every record carries the request id, real client IP, user agent and auth method

- Jira: [DK26-3930](https://amali-tech.atlassian.net/browse/DK26-3930)
- Linked preconditions: PC-DK26-3750-01, PC-DK26-3750-02
- Preconditions: Org admin A in org X; an API client.
- Steps:
  1. As A, deactivate and reactivate a user, sending a custom User-Agent and a fake X-Forwarded-For header such as 1.2.3.4.
  2. Read the response's x-request-id.
  3. Read the records' context.
  4. Check the records written by authentication for the same action.
- Expected result: Each record's context has the gateway's request id (matching the response), the real client IP and not 1.2.3.4, the custom user agent, and auth_method user. The records from authentication carry the same request id.

### TC-DK26-3750-16: Actions taken with an API key are recorded as the key, not as a person

- Jira: [DK26-3931](https://amali-tech.atlassian.net/browse/DK26-3931)
- Linked preconditions: PC-DK26-3750-01, PC-DK26-3750-02
- Preconditions: An API key for org X and its key id; an audited action the API key can perform (for example dispatching an assessment through the external API).
- Steps:
  1. Perform the audited action with the API key.
  2. Perform a similar action as Org admin A.
  3. Read both records.
  4. Revoke the API key and read the api_key.revoked record.
- Expected result: The API key record has actor {type: api_key, id: the key id, org_id: X} and auth_method api_key, not a made-up Org Admin user. A's record has actor type user and auth_method user, so the two can be told apart. The revoke is recorded with the person who revoked it as actor and the key as resource.

### TC-DK26-3750-17: Records hold no personal data beyond IDs and no secrets

- Jira: [DK26-3932](https://amali-tech.atlassian.net/browse/DK26-3932)
- Linked preconditions: PC-DK26-3750-01, PC-DK26-3750-02
- Preconditions: Records from TC-01 to TC-16 exist; access to audit_logs and Loki.
- Steps:
  1. Try to log in with a wrong password for a known email.
  2. Change a user's password and request a password reset.
  3. Search the audit_logs rows and the Loki audit_event lines from these tests for emails, names, tokens, reset links, passwords and question text.
  4. Read the changes field of the password and profile records.
- Expected result: No record contains an email, name, token, link, password or question text: people and things appear only as ids. The failed login record masks or hashes the identifier. Password changes are recorded without old or new values. Any decision to copy the actor's name into records is documented on the story.

### TC-DK26-3750-18: End to end: authentication records the sessions it ended, with the admin as actor and the same request id

- Jira: [DK26-3933](https://amali-tech.atlassian.net/browse/DK26-3933)
- Linked preconditions: PC-DK26-3750-01, PC-DK26-3750-02
- Preconditions: User B in org X signed in on another browser; Org admin A in org X.
- Steps:
  1. As A, deactivate user B and note the request id.
  2. Check that B's session ends (B's next request is refused).
  3. Read the records written by authentication for B.
  4. Read the user-management record for the same action.
- Expected result: authentication writes user.deactivation_applied and records the ended sessions, with actor A (not B) and the same request id as the user-management user.deactivated record. A can see the user-management record in the org's audit list. This is step 2 of the story's end-to-end check.

### TC-DK26-3750-19: Other services publish records in the shared format, and system actions name the job or topic

- Jira: [DK26-3934](https://amali-tech.atlassian.net/browse/DK26-3934)
- Linked preconditions: PC-DK26-3750-01, PC-DK26-3750-02
- Preconditions: Org admin A in org X; access to Loki and audit_logs.
- Steps:
  1. Create, edit and dispatch an assessment, recall a dispatch, change a notification setting, and create and revoke an API key.
  2. Query Loki for log_type="audit_event" over that time.
  3. Find the matching records in audit_logs.
  4. Find a record written by a cron job or Kafka consumer (for example a scheduled dispatch or a lockout unblock).
- Expected result: Each action writes one flat JSON line with log_type audit_event in Loki (none nested under an audit_event key), and the same record reaches audit_logs, with the service field set to the right service. Event names follow resource.past_tense_verb and appear in the OBSERVABILITY.md catalog. Cron and consumer records have actor {type: system, id: job or topic name}. A missing upstream value is null, and never makes the request fail.

### TC-DK26-3750-20: Tests and documentation cover the record format, the store and its retention

- Jira: [DK26-3935](https://amali-tech.atlassian.net/browse/DK26-3935)
- Linked preconditions: PC-DK26-3750-02, PC-DK26-3750-03
- Preconditions: Read access to dodokpo-backend, its CI and OBSERVABILITY.md.
- Steps:
  1. Check that each service has a test asserting the record shape, and that packages/audit holds the shared format, publisher and actor helpers.
  2. Open the latest CI runs.
  3. Read OBSERVABILITY.md for the record format, the event catalog, the store, the shared publisher and the retention period.
  4. Check DK26-3750 for the decisions listed under 'Decisions needed before build'.
- Expected result: Every service has a passing record-shape test, and no service keeps its own copy of the publisher or actor helpers. OBSERVABILITY.md documents the format, events, store and retention period, and corrects the two wrong claims. Each open decision (storage, retention, read access, personal data, auditing reads) is recorded, or the gap is reported.
