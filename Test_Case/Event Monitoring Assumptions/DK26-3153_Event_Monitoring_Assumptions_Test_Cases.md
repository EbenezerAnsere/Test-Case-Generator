# DK26-3153: Story 3.1: Validate Event Monitoring Assumptions

Ticket: https://amali-tech.atlassian.net/browse/DK26-3153
Status: In Progress QA
Parent: DK26-3145 Epic 3: Validate Analytics Readiness for Product Decisions
Related: DK26-3293 (analytics platform cleanup, tracked separately); DK26-3167 and DK26-3168 (overlap with backlog item B3)
Findings: Confluence 'Event Monitoring Assumptions: Validation Against Production Records' (https://amali-tech.atlassian.net/wiki/x/AwCmw), Daniel Forson, 2026-10-19
Xray folder: `Quarter 4/Ebenezer/Backend/DK26-3153 Story 3.1: Validate Event Monitoring Assumptions`
Test Set: DK26-3388
Test Plan: DK26-3106
Test Execution: DK26-3107

## Review Summary

This is an analysis story, not a feature build, so the tests check the outcome of the study rather than application behaviour. The Confluence findings page tests 16 event monitoring assumptions against the 2026-10-19 production snapshot in Athena (dodokpo_prod_bronze). It covers 10,749 journeys, a 30-day volume window and a 12-journey end-to-end sample. The results are 9 valid, 5 partially valid, 1 invalid and 1 that cannot be validated, with eight findings (F1 to F8) and nine proposed backlog items (B1 to B9).

The tests check that the journey mapping is complete, that the sample size and traces hold up, and that the volume comparison, gaps, duplicates, sequencing issues and missing identifiers all reproduce in Athena. They also check that every verdict is supported, that the readiness conclusions and reproducibility hold, and that the limitations and privacy points are covered.

Known blocker: the page says backlog items B1 to B9 are 'to be raised in Jira after this page is reviewed'. As of 2026-10-20 none exist, so TC-09 (acceptance criterion 5) fails until they are created.

## Acceptance Criteria Coverage

| Acceptance criterion | Covered by |
| --- | --- |
| Review production event capture for the core assessment journey from assessment start to submission. | TC-01 |
| Compare expected events against actual captured events for at least 10 completed assessment journeys or the agreed sample size. | TC-02, TC-03 |
| Identify event gaps, duplicate events, sequencing issues, and missing identifiers. | TC-04, TC-05, TC-06, TC-07 |
| Document which assumptions are valid, partially valid, or invalid. | TC-08, TC-10 |
| Create follow-up backlog items for any event capture gaps that block analytics readiness. | TC-09 |
| Quality checks: reproducibility, limitations, privacy | TC-11, TC-12 |

## Preconditions (Xray Precondition issues)

### PC-DK26-3153-01: Findings page and the source assumption pages are available

- Jira: [DK26-3385](https://amali-tech.atlassian.net/browse/DK26-3385)

1. The Confluence page 'Event Monitoring Assumptions: Validation Against Production Records' (https://amali-tech.atlassian.net/wiki/x/AwCmw) is accessible.
2. The source pages it tests against are accessible: 'Lifecycle Events and Observability Cost' (catalogue dated 2026-10-16) and 'Activity Tracking & Audit Logging' sections 7.14 and 7.15.
3. The tester has read the page's summary, assumption register, findings, sample, population checks, limitations and backlog sections.

### PC-DK26-3153-02: Athena access to the production snapshot used in the study

- Jira: [DK26-3386](https://amali-tech.atlassian.net/browse/DK26-3386)

1. The tester can run queries in Athena in the dodokpo-prod-workgroup workgroup.
2. The dodokpo_prod_bronze database with load_date = '2026-10-19' is available, covering the 6 PostgreSQL databases and the reporting DynamoDB table.
3. The study's query pack (profile, volumes, journey checks, duplicates, reconciliation, sample, retakes) is available from the dodokpo-data-analytics repository, or from the author (Daniel Forson) if it has not been committed yet.
4. Results are compared with the page using the same windows: all journeys 2024-02-12 to 2026-10-19, recent journeys created on or after 2026-09-16, and volumes over 2026-09-16 to 2026-10-15.

### PC-DK26-3153-03: Jira access to the DK26 backlog and related stories

- Jira: [DK26-3387](https://amali-tech.atlassian.net/browse/DK26-3387)

1. The tester can search and open issues in the DK26 project.
2. The related stories DK26-3167 (Authoritative Assessment Lifecycle Events) and DK26-3168 (Assessment Journey Traceability) are accessible.
3. The parent epic DK26-3145 (Validate Analytics Readiness for Product Decisions) is accessible.

## Test Cases

### TC-DK26-3153-01: Core assessment journey from start to submission is fully mapped to production records

- Jira: [DK26-3373](https://amali-tech.atlassian.net/browse/DK26-3373)
- Linked preconditions: PC-DK26-3153-01 (DK26-3385), PC-DK26-3153-02 (DK26-3386)
- Preconditions: Findings page available; Athena access to dodokpo_prod_bronze load_date 2026-10-19.
- Steps:
  1. Open the 'Where each journey step is recorded' table on the findings page.
  2. Check that it covers every step from invite to result: invited, link viewed, compatibility check, consent, ID capture, assessment started, test submitted, violation recorded, assessment submitted and result in reporting.
  3. For each step, run a query in Athena that confirms the named table and action exist and can be joined on the stated key (assessmentTakerId, testId, clientEventKey or candidateId).
  4. Check that the 'since' dates given for newer tables (CompatibilityCheckLog 2026-05-17, ProctoringConsent 2026-09-09, ProctoringViolationEvent 2026-07-25) match the earliest record in each table.
- Expected:
  - Every step of the core journey from assessment start to submission is mapped to a real production table or action, with a join key that works in Athena. No step is left unmapped, and the start date given for each newer table matches its earliest record.

### TC-DK26-3153-02: Sample meets the agreed size and every sampled journey is traced end to end

- Jira: [DK26-3374](https://amali-tech.atlassian.net/browse/DK26-3374)
- Linked preconditions: PC-DK26-3153-01 (DK26-3385), PC-DK26-3153-02 (DK26-3386)
- Preconditions: Findings page available; Athena access to the 2026-10-19 snapshot.
- Steps:
  1. Open the 'Sample: 12 completed journeys' table and count the journeys and categories.
  2. Check that every sampled journey is a completed journey from the recent window (created on or after 2026-09-16).
  3. Pick at least 3 sampled journeys from different categories, for example dcca81d7 (clean), 7b88c167 (multi-test) and 8e7797fd (retake).
  4. For each one, query the v, s, ts, d, tr, pve and rep counts in Athena and compare them with the table.
  5. Compare the 'Observed' note for each with the records.
- Expected:
  - The sample has at least 10 completed journeys (12 are reported), two from each of the six categories, all from the recent window. For every journey re-checked, the counts in Athena match the table exactly and the 'Observed' note is true of the records, for example 7b88c167's completion log being about 1 second before its last test submission.

### TC-DK26-3153-03: Expected event volumes are compared with actual captured volumes and reproduce

- Jira: [DK26-3375](https://amali-tech.atlassian.net/browse/DK26-3375)
- Linked preconditions: PC-DK26-3153-01 (DK26-3385), PC-DK26-3153-02 (DK26-3386)
- Preconditions: Findings page and the Lifecycle Events and Observability Cost catalogue available; Athena access to the 2026-10-19 snapshot.
- Steps:
  1. List each volume assumption A1 to A11 with the catalogue's expected daily rate.
  2. Re-run the volume queries for the window 2026-09-16 to 2026-10-15.
  3. Compare the recomputed daily rates with those on the page, for example A1 8.1 starts a day, A4 8.3 link views a day, A6 9.1 test submissions a day and A10 8.0 results ingested a day.
  4. Check the summary claim that 9 of the 11 volume figures are within about 1 event a day of the catalogue, and that the exceptions are assessment.started and the email events.
- Expected:
  - Every volume assumption has an expected and an actual figure side by side. The recomputed daily rates match the page to one decimal place. The summary's '9 of 11 within about 1 a day' claim holds, with A5 (8.1 a day against 6 expected) and A11 (emails, not usable) as the only exceptions.

### TC-DK26-3153-04: Event capture gaps are identified with counts that reproduce

- Jira: [DK26-3376](https://amali-tech.atlassian.net/browse/DK26-3376)
- Linked preconditions: PC-DK26-3153-01 (DK26-3385), PC-DK26-3153-02 (DK26-3386)
- Preconditions: Findings page available; Athena access to the 2026-10-19 snapshot.
- Steps:
  1. For F5, count the reporting EVENT items and find the latest timestamp. Count ProctoringViolationEvent rows overall, and those for recent journeys after 2026-09-08.
  2. For F6, count violations since 2026-07-25 that have a copy in WindowViolation or Idletime, linked by sourceEventId, and break the misses down by type.
  3. For F8, count AssessmentTaker rows where resultEmailSentAt has a value, and check what the values hold.
  4. For A8, count recent completed journeys with no consent record and with no compatibility check.
  5. Compare each result with the page.
- Expected:
  - Each gap is reproduced. The reporting store holds 430 events, none after 2026-09-08 20:07 UTC (430 of 1,797, 24%, with no WINDOW_MINIMIZED events). 1,702 of 1,777 violations have a legacy copy, and UNREADABLE_ID is never copied. 96 resultEmailSentAt values, all email addresses. 9 recent completed journeys with no consent and 9 with no compatibility check. Each gap is stated with its scope and impact.

### TC-DK26-3153-05: Duplicate events are identified and told apart from retakes

- Jira: [DK26-3377](https://amali-tech.atlassian.net/browse/DK26-3377)
- Linked preconditions: PC-DK26-3153-01 (DK26-3385), PC-DK26-3153-02 (DK26-3386)
- Preconditions: Findings page available; Athena access to the 2026-10-19 snapshot.
- Steps:
  1. Count duplicate clientEventKey values in ProctoringViolationEvent.
  2. Group AssessmentTakingLog start, completion and test-submission rows by taker (and testId for submissions) and find groups with more than one row.
  3. Split the groups into those less than a minute apart, less than a day apart, and more than a day apart (retakes).
  4. Compare the counts with A15 and F2 on the page.
- Expected:
  - There are 0 duplicate clientEventKey values in 1,797 violation rows. The journey log counts match the page: within a minute, 9 start, 13 completion and 24 test-submission groups. Under a day apart, 21, 25 and 38 groups. 341 groups more than a day apart are retakes. The page clearly says that retakes and real duplicates can only be told apart by the time gap.

### TC-DK26-3153-06: Sequencing issues in the journey are identified with counts that reproduce

- Jira: [DK26-3378](https://amali-tech.atlassian.net/browse/DK26-3378)
- Linked preconditions: PC-DK26-3153-01 (DK26-3385), PC-DK26-3153-02 (DK26-3386)
- Preconditions: Findings page available; Athena access to the 2026-10-19 snapshot.
- Steps:
  1. For each journey with a completion log, compare the ASSESSMENT_COMPLETION timestamp with the last test submission timestamp.
  2. Count the cases where completion comes first, split into under a second, under a minute and more than an hour, for all journeys and for recent ones.
  3. Run the ordering checks from 'Population checks': started before link viewed, completion before start, and test submission before start.
  4. For F7, compare AssessmentTaker.endTime with the completion log for auto-submitted journeys, and count those more than a minute apart.
- Expected:
  - The counts match the page. Completion comes before the last test submission in 1,247 journeys within a minute (644 under a second, 603 under a minute), and in 43 of 289 recent completed journeys. 0 journeys start before the link is viewed, 0 complete before they start, and 97 (8 recent) have a test submission before the start. 404 journeys have endTime and completion more than a minute apart. The page explains the effect on event-ordered funnels.

### TC-DK26-3153-07: Missing and unreliable identifiers are identified

- Jira: [DK26-3379](https://amali-tech.atlassian.net/browse/DK26-3379)
- Linked preconditions: PC-DK26-3153-01 (DK26-3385), PC-DK26-3153-02 (DK26-3386)
- Preconditions: Findings page available; Athena access to the 2026-10-19 snapshot.
- Steps:
  1. Check what share of journeys have organisation, assessment, dispatch and taker IDs, for all journeys and for recent ones.
  2. Count violation rows with no test ID and break them down by violation type.
  3. Check the attemptNumber values in TestResult and ProctoringViolationEvent for journeys with an attempt count of 2 or 3.
  4. Check every journey table for a session or correlation ID column.
  5. Compare the results with A12, A13 and A14 on the page.
- Expected:
  - Organisation, assessment and taker IDs are present on 100% of journeys. Dispatch ID is on 100% of recent journeys but missing on about 95% of older ones. 26 violation rows have no test ID, mostly UNREADABLE_ID. attemptNumber is always 1 in TestResult and ProctoringViolationEvent, including for the 1,517 retake journeys. No journey table has a session or correlation ID. All of these are reported as findings.

### TC-DK26-3153-08: Every assumption is given a supported verdict of valid, partially valid or invalid

- Jira: [DK26-3380](https://amali-tech.atlassian.net/browse/DK26-3380)
- Linked preconditions: PC-DK26-3153-01 (DK26-3385)
- Preconditions: Findings page and source assumption pages available.
- Steps:
  1. Open the assumption register and list A1 to A16 with their source, verdict and evidence.
  2. Check that each assumption traces to a real statement in the catalogue or in Activity Tracking §1, §7.14 or §7.15.
  3. Count the verdicts and compare them with the summary.
  4. For each Partially valid, Invalid and Cannot be validated verdict, check that the evidence says what holds, what does not, and links to a finding where one applies.
- Expected:
  - All 16 assumptions have a source, a verdict and evidence. Every verdict is Valid, Partially valid, Invalid or Cannot be validated from the database. The counts match the summary: 9 valid, 5 partially valid, 1 invalid (A13) and 1 cannot be validated (A11). No verdict goes against its own evidence.

### TC-DK26-3153-09: Follow-up backlog items exist in Jira for every gap that blocks analytics readiness

- Jira: [DK26-3381](https://amali-tech.atlassian.net/browse/DK26-3381)
- Linked preconditions: PC-DK26-3153-01 (DK26-3385), PC-DK26-3153-03 (DK26-3387)
- Preconditions: Findings page available; Jira access to DK26, including DK26-3167, DK26-3168 and epic DK26-3145.
- Steps:
  1. List the proposed backlog items B1 to B9 and note which ones block analytics ('Yes' or 'Partly').
  2. Search DK26 for a Jira issue matching each of B1, B2, B4 and B7, and for each 'Partly' item (B5, B6, B8).
  3. Check that B3 is linked to DK26-3167 or DK26-3168, not raised as a duplicate.
  4. Check that each backlog issue links back to DK26-3153 or to epic DK26-3145, names an owning team and describes the gap and its evidence.
- Expected:
  - Every blocking item (B1, B2, B3, B4 and B7) and every partly blocking item (B5, B6 and B8) has a Jira issue. B3 is linked to DK26-3167 or DK26-3168 instead of being duplicated. Each issue links to DK26-3153 or DK26-3145 and states the gap, its evidence and the owning team. As of 2026-10-20 the page says these are still 'to be raised', so this test fails until they exist.

### TC-DK26-3153-10: Analytics readiness conclusions match the findings

- Jira: [DK26-3382](https://amali-tech.atlassian.net/browse/DK26-3382)
- Linked preconditions: PC-DK26-3153-01 (DK26-3385)
- Preconditions: Findings page available.
- Steps:
  1. Open the 'Impact on analytics readiness' table.
  2. For each use marked Yes or Yes, with care, check that the condition given deals with the related findings (F3, F4, F5, F6, F7).
  3. For each use marked No, check that it is backed by a finding and a backlog item.
  4. Compare the table with the readiness statement in the summary.
- Expected:
  - Every readiness verdict follows from the findings. Uses marked Yes or Yes, with care name a condition that avoids the known gaps, for example taking status from test-creation, timing from the last test submission, and violations from ProctoringViolationEvent. Uses marked No (session sequencing, retake analytics, email metrics) point to F1, F3, F8 and A13 and to backlog items. The summary agrees with the table.

### TC-DK26-3153-11: Results can be reproduced from the documented queries and source

- Jira: [DK26-3383](https://amali-tech.atlassian.net/browse/DK26-3383)
- Linked preconditions: PC-DK26-3153-01 (DK26-3385), PC-DK26-3153-02 (DK26-3386)
- Preconditions: Findings page available; Athena access; the dodokpo-data-analytics repository available.
- Steps:
  1. Check that the query pack is committed to the dodokpo-data-analytics repository and is linked to DK26-3153.
  2. Run the population-check queries in the dodokpo-prod-workgroup workgroup on dodokpo_prod_bronze with load_date = '2026-10-19'.
  3. Compare every row of the 'Population checks' table, for all and recent journeys, with the results.
  4. Note the data scanned by the full query pack.
- Expected:
  - The query pack is in the repository and linked to the ticket. Every population check reproduces exactly: for example 1,782 and 43 completions before the last test submission, 89 and 4 TestResults dated 1970, 1,991 and 39 status mismatches. The full pack scans under 100 MB as stated.

### TC-DK26-3153-12: Limitations are stated and the findings contain no personal data

- Jira: [DK26-3384](https://amali-tech.atlassian.net/browse/DK26-3384)
- Linked preconditions: PC-DK26-3153-01 (DK26-3385)
- Preconditions: Findings page available.
- Steps:
  1. Read the Limitations section and check that it covers the snapshot-only view, the lack of log-side access, the tables not exported, the timestamp and timezone handling, pseudonymised emails and the late start of newer tables.
  2. Check that findings which depend on a limitation say so, for example that the cause of the A5 gap is unconfirmed and that gaps under a second may be clock differences.
  3. Search the page and its tables for candidate names, real email addresses, full candidate IDs or other personal data.
- Expected:
  - Every known limitation is stated, and each finding it affects is qualified. The page has no candidate names, real email addresses or full IDs: journeys appear only by shortened taker ID and emails only as pseudonyms.
