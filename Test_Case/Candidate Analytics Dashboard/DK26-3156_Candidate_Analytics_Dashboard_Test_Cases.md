# DK26-3156: Story 3.4: Candidate Analytics Dashboard Development

Ticket: https://amali-tech.atlassian.net/browse/DK26-3156
Status: In Progress QA
Parent: DK26-3145 Epic 3: Validate Analytics Readiness for Product Decisions
Developer: Daniel Forson (Data Engineering)
Sources: Confluence 'Training Center Analytics Dashboard: UI Walkthrough for UI/UX', 'Analytics Dashboard Review: Redesign for Cohort-Based Storytelling and Improved User Experience', 'Analytics Data Discrepancies: Findings, Decisions and Fixes' (DK26-3460)
Xray folder: `Quarter 4/Ebenezer/Frontend/DK26-3156 Story 3.4: Candidate Analytics Dashboard Development` (not yet created, Xray key returns 401)
Jira test cases: DK26-3699 to DK26-3720 (linked to DK26-3156 as Test)
Test Plan: DK26-3106
Test Execution: DK26-3107

## Review Summary

The Training Center Analytics dashboard is a separate web app that reads the production gold layer through Athena. According to Daniel Forson's update, development is complete and only stakeholder sign-off remains. It has these pages:

- Portfolio: Overview, Assessments with Assessment detail, and Candidates.
- Item quality: Item bank, Distractors, and Timing & speededness.
- Fairness: Groups & DIF.
- Governance.

Filters: Domain, Category, Assessment, Administration, Group, Completion, Date range and Attempt policy. Access depends on the role: Admin, Org admin, Trainer, Analyst or Viewer, with pseudonyms for some roles.

Points to watch:

- The ticket gives no dashboard URL. Ask Daniel Forson for it and for one account per role.
- There is no candidate cohort filter, because the source data has no cohort records. Group is used instead, as agreed with the Training Center. TC-14 checks this as the agreed substitute.
- Group data is thin (about 3% of records), so the Fairness page will mostly say 'not enough data', which is correct.
- Candidates who never submitted a test do not appear (decision A3). Allow for this when comparing figures in TC-16.
- TC-22 stays open until the pending stakeholder feedback, expected the week of 9 November, is recorded on the ticket.
- Figures in the Confluence pages were measured on test environments or on the 19 October snapshot, so they may differ slightly.

## Acceptance Criteria Coverage

| Acceptance criterion | Covered by |
| --- | --- |
| Deliver dashboard views for agreed candidate analytics metrics such as score distribution, completion rate, pass/fail rate, question performance, and candidate comparison. | TC-01 to TC-10 |
| Support filtering by assessment, date range, candidate cohort, and completion status where data is available. | TC-11 to TC-15 |
| Ensure dashboard data aligns with validated production analytics data sources. | TC-16, TC-17, TC-18 (and TC-03, TC-04) |
| Review the dashboard with stakeholders and capture approval notes or follow-up improvements. | TC-22 |
| Supporting design rules and access (no fake zeros, chart/table, roles, themes, widths) | TC-19, TC-20, TC-21 |

## Preconditions

### PC-DK26-3156-01: Training Center Analytics dashboard reachable on production data, with accounts per role

1. The dashboard URL is known (ask Daniel Forson), and it runs on the production gold layer through Athena. The sidebar does not show the 'Mock data' badge.
2. Accounts are available for at least these roles: Admin (all organisations, real names, export), Org admin (one organisation), and Viewer (pseudonyms, no export). Ask Daniel for them if needed.
3. The tester has read the 'Training Center Analytics Dashboard: UI Walkthrough for UI/UX' page in Confluence, which describes every screen and rule.
4. Latest Chrome, plus Firefox or Safari, with developer tools.

### PC-DK26-3156-02: Reference assessments and figures to compare the dashboard against

1. One assessment with many sittings is chosen. Its candidates, sittings, pass rate and completion figures are noted from the Dodokpo platform (assessment report and candidate list) or from an Athena query on the gold views (with Daniel's help), for a fixed date range.
2. One assessment where some candidates retook the test, with the candidates and number of attempts noted.
3. One assessment with partial-credit answers (for example multiple-answer questions).
4. One small assessment or administration with fewer than 20 answers per question, and one group with fewer than 5 candidates, to check the 'not enough data' and 'suppressed' states.
5. The expected figures from 'Analytics Data Discrepancies: Findings, Decisions and Fixes' (DK26-3460) are available.

### PC-DK26-3156-03: Stakeholder review status known

1. The reviews held in early November with the Training Center are documented (Confluence 'Analytics Dashboard Review' page and the DK26-3156 comment of Daniel Forson).
2. The latest stakeholder's feedback is expected the week of 9 November 2026. Approval notes or follow-up improvements should be added to DK26-3156 once received.

## Test Cases

### TC-DK26-3156-01: Overview shows candidates, sittings, pass rate and completion rate with honest change arrows

- Jira: [DK26-3699](https://amali-tech.atlassian.net/browse/DK26-3699)
- Linked preconditions: PC-DK26-3156-01
- Preconditions: Signed in as Admin on the dashboard running on production data.
- Steps:
  1. Open Portfolio > Overview with no filters.
  2. Read the four headline numbers and the smaller assessment and domain counts.
  3. Hover each change arrow and open the (i) 'What the colours mean'.
  4. Check the Needs attention, What changed, Pass rate by month and Sittings by month cards, and the By domain table (top 8, show all).
- Expected result: The Overview shows Candidates (distinct people), Sittings, Pass rate and Completion rate, each with a change since the previous period. Count arrows are grey. Rate arrows are coloured only when the change is real and big enough, otherwise they say 'within noise' or 'too small to act on'. Pass rate and sittings by month are two separate charts with one scale each. Needs attention is never empty. By domain shows 8 rows and expands to all.

### TC-DK26-3156-02: Score distribution is shown per assessment against its pass mark

- Jira: [DK26-3700](https://amali-tech.atlassian.net/browse/DK26-3700)
- Linked preconditions: PC-DK26-3156-01, PC-DK26-3156-02
- Preconditions: Admin signed in; the reference assessment chosen.
- Steps:
  1. Open Portfolio > Assessments and open the reference assessment.
  2. On the Overview tab, read the Score distribution card.
  3. Switch the card between Chart and Table.
  4. Compare the number of sittings in the distribution with the 'In statistics' tile.
- Expected result: The score distribution is shown for this test, with its pass mark marked. The table view shows the same values as the chart. The total behind the distribution matches the 'In statistics' count. Score distribution is not on the Overview page, because mixing different tests is not meaningful.

### TC-DK26-3156-03: Pass and fail rate are correct for an assessment and over time

- Jira: [DK26-3701](https://amali-tech.atlassian.net/browse/DK26-3701)
- Linked preconditions: PC-DK26-3156-01, PC-DK26-3156-02
- Preconditions: Admin signed in; the reference assessment's pass and fail counts noted from the platform for a fixed date range.
- Steps:
  1. Set the date range to the noted range and open the reference assessment.
  2. Read its pass rate (and pass and fail counts in the table view).
  3. On Overview, filter to the same assessment and read the Pass rate by month chart in table view.
  4. Compare with the noted figures.
- Expected result: The pass rate matches the platform figures for the same range: each sitting is judged against its own test's pass mark. Pass plus fail adds up to the sittings counted. The monthly table matches the chart, and each month's rate is consistent with the overall rate.

### TC-DK26-3156-04: Completion rate and completion statuses are shown and follow the agreed source of truth

- Jira: [DK26-3702](https://amali-tech.atlassian.net/browse/DK26-3702)
- Linked preconditions: PC-DK26-3156-01, PC-DK26-3156-02
- Preconditions: Admin signed in; the reference assessment's completion statuses noted from test-execution data (with Daniel's help).
- Steps:
  1. Open the reference assessment and read the Completion tile and the Completion status card.
  2. Open Item quality > Timing & speededness and read Time taken next to Completion states.
  3. Compare each status count with the noted figures.
  4. Open Governance and find the data-quality checks for services disagreeing on status.
- Expected result: The completion rate and the status breakdown (completed, time expired, did not finish and so on) match the noted figures. Statuses come from test-execution first, as agreed in A1, and an 'in progress' status never overrides an end state. Governance counts sittings where the services disagree.

### TC-DK26-3156-05: Item bank shows question performance with Replace, Review, Keep and Insufficient evidence verdicts

- Jira: [DK26-3703](https://amali-tech.atlassian.net/browse/DK26-3703)
- Linked preconditions: PC-DK26-3156-01
- Preconditions: Admin signed in.
- Steps:
  1. Open Item quality > Item bank.
  2. Note which verdicts are shown on opening, and the counts on each verdict chip.
  3. Click each chip in turn, and switch the view between Chart and Table.
  4. Sort the table by difficulty and by quality, and open the fold-out list of questions with incomplete statistics.
- Expected result: The page opens showing only Replace and Review. The chips appear in the order Replace, Review, Keep, Insufficient evidence, each with an icon and a word as well as a colour. Their counts cover the whole bank and do not change as chips are clicked. Questions with fewer than 20 answers are 'Insufficient evidence', not Keep. Sorting applies to the whole list. Questions without statistics are listed with grouped reasons.

### TC-DK26-3156-06: Question panel explains each question's verdict and counts partial answers separately

- Jira: [DK26-3704](https://amali-tech.atlassian.net/browse/DK26-3704)
- Linked preconditions: PC-DK26-3156-01, PC-DK26-3156-02
- Preconditions: Admin signed in; an assessment with partial-credit answers.
- Steps:
  1. Open a Replace or Review question from the Item bank.
  2. Read 'Why this verdict', the statistics and the answer options.
  3. Open a question from the partial-credit assessment and read its counts.
  4. Copy the page link, open it in a new tab and check that the same question panel opens.
- Expected result: The panel states the rule that gave the verdict in plain words, and shows difficulty, quality and the counts of correct, partial, wrong and skipped answers. Partial answers are counted as Partial, not as wrong (decision A2). The correct option is marked. The link reopens the same question.

### TC-DK26-3156-07: Distractors page shows how often each wrong option is chosen

- Jira: [DK26-3705](https://amali-tech.atlassian.net/browse/DK26-3705)
- Linked preconditions: PC-DK26-3156-01
- Preconditions: Admin signed in.
- Steps:
  1. Open Item quality > Distractors.
  2. Read the tiles, including the threshold in use.
  3. Click a question in 'Questions needing attention' and read each option's pick rate.
  4. Check how questions without a title are labelled.
- Expected result: Tiles show questions analysed, total distractors, non-working ones, questions with no working distractor, possible wrong answer keys and the threshold ('at least 5% of people pick it'). Each option shows how often it was picked, and the pick rates of a question add up to 100%. Questions without a title are shown by their text.

### TC-DK26-3156-08: Candidate roster compares candidates by mean score, best score, pass rate and attempts

- Jira: [DK26-3706](https://amali-tech.atlassian.net/browse/DK26-3706)
- Linked preconditions: PC-DK26-3156-01
- Preconditions: Admin signed in; the roster has more than one page of candidates.
- Steps:
  1. Open Portfolio > Candidates.
  2. Sort by mean score, then best score, then pass rate, then attempts, in both directions.
  3. Go to page 2 after each sort and check the order continues.
  4. Check what the note says about sittings and candidates.
- Expected result: There is one row per person. Each column sorts the whole roster, not only the visible page, so page 2 continues the order of page 1. Values are consistent: the best score is never below the mean score, and attempts count all sittings of that person.

### TC-DK26-3156-09: Candidate profile shows retake progression, all sittings and each sitting's answers

- Jira: [DK26-3707](https://amali-tech.atlassian.net/browse/DK26-3707)
- Linked preconditions: PC-DK26-3156-01, PC-DK26-3156-02
- Preconditions: Admin signed in; a candidate who retook an assessment, with the number and dates of attempts noted.
- Steps:
  1. Open the candidate from the roster to show the person panel.
  2. Read Retake progression and All sittings.
  3. Open one sitting and read each question's answer, correctness and pause time.
  4. Compare the attempts with the noted figures.
- Expected result: The person panel shows every sitting in date order with its score, and the retake progression matches the noted attempts. The sitting panel shows each question with the answer, Correct, Partial, Wrong or Skipped, and the pause time. A pause that was not measured is blank, not 0. The on-screen notes explain that attempt order comes from timestamps.

### TC-DK26-3156-10: Group comparison shows group performance and hides groups that are too small

- Jira: [DK26-3708](https://amali-tech.atlassian.net/browse/DK26-3708)
- Linked preconditions: PC-DK26-3156-01, PC-DK26-3156-02
- Preconditions: Admin signed in; a group with fewer than 5 candidates and one with 5 to 9 are known, if available.
- Steps:
  1. Open Fairness > Groups & DIF, Group performance tab.
  2. Group by candidate group, then by organisation and by month.
  3. Find the small groups.
  4. Open the DIF tab, pick two groups and run the comparison.
- Expected result: Each group shows its average, spread and pass rate. Groups under 10 are marked 'too small to compare' with how many more are needed. Groups under 5 show 'Suppressed (n < 5)' and no figures. DIF lists questions graded A, B or C, never labelled 'biased', and lists questions that could not be tested. Where data is thin the page explains why instead of showing empty boxes.

### TC-DK26-3156-11: Assessment filter narrows from domain to category, assessment and administration

- Jira: [DK26-3709](https://amali-tech.atlassian.net/browse/DK26-3709)
- Linked preconditions: PC-DK26-3156-01
- Preconditions: Admin signed in.
- Steps:
  1. Open the filter bar and choose a Domain, then a Category, an Assessment and an Administration.
  2. Check the lists offered at each level.
  3. Change the Domain and check the lower levels.
  4. Search the Assessment list by part of a name, and search the Domain list for 'Backend Engineering'.
- Expected result: Each list only offers what exists under the level above, so no empty combination can be built. Changing a higher level clears the levels below it. Long lists (domains, assessments) can be searched. Domains with the same name appear once, and hover text explains the merge. Every figure on the page updates to the selection.

### TC-DK26-3156-12: Date range filter changes every figure and is shown in the scope line

- Jira: [DK26-3710](https://amali-tech.atlassian.net/browse/DK26-3710)
- Linked preconditions: PC-DK26-3156-01, PC-DK26-3156-02
- Preconditions: Admin signed in; the reference assessment's figures noted for two different date ranges.
- Steps:
  1. On Overview, set a date range and note the headline numbers.
  2. Set the second date range and note them again.
  3. Read the scope line, then remove the date range with its ✕.
  4. Set a range in which nothing happened.
- Expected result: The figures change with the date range and match the noted figures for each range. The scope line names the date range and the amount of data behind it, and ✕ removes it. A range with no data shows a sentence explaining that there is no data, not zeros or empty boxes.

### TC-DK26-3156-13: Completion status filter narrows figures to the chosen statuses

- Jira: [DK26-3711](https://amali-tech.atlassian.net/browse/DK26-3711)
- Linked preconditions: PC-DK26-3156-01, PC-DK26-3156-02
- Preconditions: Admin signed in; the reference assessment's status counts noted.
- Steps:
  1. Open the reference assessment and set the Completion filter to completed only.
  2. Read the sittings, score distribution and completion card.
  3. Change the filter to a non-completed status (for example time expired).
  4. Clear the filter.
- Expected result: With a completion filter, only sittings in that status are counted, and the counts match the noted figures. The scope line and collapsed filter summary name the filter. Clearing it restores the original figures.

### TC-DK26-3156-14: Candidate cohort is replaced by Group, with a warning about how little data has groups

- Jira: [DK26-3712](https://amali-tech.atlassian.net/browse/DK26-3712)
- Linked preconditions: PC-DK26-3156-01
- Preconditions: Admin signed in.
- Steps:
  1. Open the filter bar and look for a cohort filter.
  2. Filter by a Group and read any banner.
  3. Open 'Not available here (n)' at the bottom of the menu.
  4. Visit a page where Group has no effect and check whether the banner is shown.
- Expected result: There is no cohort filter, because the source data has no cohort records (agreed with the Training Center). Group is offered instead, and filtering by group shows a banner that only a small share of records (about 3%) have a group. The banner appears only where groups affect the numbers. 'Not available here' lists cohort and country views with the reason.

### TC-DK26-3156-15: Filters carry across pages and are kept in a shareable link

- Jira: [DK26-3713](https://amali-tech.atlassian.net/browse/DK26-3713)
- Linked preconditions: PC-DK26-3156-01
- Preconditions: Admin signed in.
- Steps:
  1. Set an organisation, domain, assessment, date range and completion status.
  2. Move between Overview, Item bank, Timing and Governance.
  3. Collapse the filter bar and read its summary.
  4. Copy the link and open it in a private window after signing in.
- Expected result: The filters stay applied on every page, and each page's scope line states them. The collapsed summary names every active filter, not just a count. Pages where Category cannot narrow the numbers say so next to the filter. The copied link opens the same page with the same filters.

### TC-DK26-3156-16: Dashboard figures match the production data for a reference assessment

- Jira: [DK26-3714](https://amali-tech.atlassian.net/browse/DK26-3714)
- Linked preconditions: PC-DK26-3156-01, PC-DK26-3156-02
- Preconditions: Admin signed in; the reference assessment's figures noted from the Dodokpo platform or an Athena query on the gold views, for a fixed date range.
- Steps:
  1. Filter the dashboard to the reference assessment and the same date range.
  2. Compare candidates, sittings, pass rate, completion rate and mean score with the noted figures.
  3. Open the Assessment detail 'Comparison with the platform's own figures' card.
  4. Note every difference and its explanation.
- Expected result: Candidates, sittings, pass rate and completion rate match the production figures. Any difference is explained on screen (for example attempt policy, candidates who never submitted, or status taken from test-execution), and the platform comparison card shows both values side by side.

### TC-DK26-3156-17: Data discrepancy fixes are visible on the dashboard

- Jira: [DK26-3715](https://amali-tech.atlassian.net/browse/DK26-3715)
- Linked preconditions: PC-DK26-3156-01, PC-DK26-3156-02
- Preconditions: Admin signed in; the expected figures from the 'Analytics Data Discrepancies' page (DK26-3460).
- Steps:
  1. Filter to the review window used on that page and open Governance.
  2. Read the checks for responses whose correctness is derived from the score, for records that fell back from test-execution, and for status disagreements.
  3. Open a partial-credit question and check its Partial count.
  4. Look up a candidate record known to have been deleted at the source, if one is available.
- Expected result: Responses whose correctness is derived from the score are 0 in the window. Partial answers are counted as Partial (217 in the window). Status disagreements are counted (about 64 candidates), and the value shown is the higher-priority one. Records deleted at the source no longer appear.

### TC-DK26-3156-18: Governance shows data-quality checks, data freshness, definitions and the draft rule set

- Jira: [DK26-3716](https://amali-tech.atlassian.net/browse/DK26-3716)
- Linked preconditions: PC-DK26-3156-01
- Preconditions: Admin signed in.
- Steps:
  1. Open Governance with no filters, then with an assessment filter.
  2. Read the data-quality checks, data freshness dates, metric definitions and the rule set.
  3. Hover the 'Draft thresholds' badge on Overview.
  4. Check the sidebar for the 'Mock data' badge.
- Expected result: Governance lists the 17 data-quality checks as counts, which change with the filters. Data freshness shows when each source was last updated, and the dates are recent (within the weekly load). Each metric has a plain definition. The rule set shows its version, draft status and thresholds in order. No 'Mock data' badge is shown, confirming production data is used.

### TC-DK26-3156-19: No empty boxes or fake zeros, and every chart can be read as a table

- Jira: [DK26-3717](https://amali-tech.atlassian.net/browse/DK26-3717)
- Linked preconditions: PC-DK26-3156-01, PC-DK26-3156-02
- Preconditions: Admin signed in; a small assessment with fewer than 20 answers per question.
- Steps:
  1. Open the small assessment's detail page and its Item quality tab.
  2. Read each card, including Reliability.
  3. On each page, use the Chart / Table switch on every chart card.
  4. Look for blank cards, '0' values that should be 'not measured', and charts with two vertical scales.
- Expected result: Where there is not enough data, a short sentence explains why (for example 'Needs at least 20 answers; this question has 12'). No box is empty and no missing value is shown as 0. Every chart has a working table view with the same values, and no chart has two vertical scales.

### TC-DK26-3156-20: Each role sees only its allowed data, names and export

- Jira: [DK26-3718](https://amali-tech.atlassian.net/browse/DK26-3718)
- Linked preconditions: PC-DK26-3156-01
- Preconditions: Accounts for Admin, Org admin and Viewer.
- Steps:
  1. As Admin, check the organisation picker, candidate names and export buttons.
  2. As Org admin, check the picker, the organisations whose data appears, and names.
  3. As Viewer, check names, the pseudonym notice in the profile menu, and export buttons.
  4. As Org admin, change the organisation in the page link to another organisation and reload.
- Expected result: Admin sees all organisations, real names and export. Org admin sees only their own organisation, with no full picker. Viewer sees consistent pseudonyms, a notice explaining them and no export buttons. Changing the link to another organisation shows no data from it, because access is decided by the server.

### TC-DK26-3156-21: The dashboard is usable in dark mode, at narrow widths and by keyboard

- Jira: [DK26-3719](https://amali-tech.atlassian.net/browse/DK26-3719)
- Linked preconditions: PC-DK26-3156-01
- Preconditions: Admin signed in.
- Steps:
  1. Switch between light and dark with the theme button, and choose 'Match the system theme'.
  2. View Overview, Item bank and Groups & DIF at 1440 px, about 900 px and about 720 px wide.
  3. Using only the keyboard, open filters, choose values, switch Chart / Table and open a question panel.
  4. Time how long Overview and the Item bank take to load.
- Expected result: Text, chart colours and status chips are readable in both themes, and status is never shown by colour alone. Under 900 px the sidebar starts collapsed, and under 720 px layouts become one column without overlap (wide tables scroll inside their card). Everything can be reached by keyboard with visible focus. Pages load in an acceptable time; slow loading was a known issue.

### TC-DK26-3156-22: Stakeholder review is recorded with approval notes or follow-up improvements

- Jira: [DK26-3720](https://amali-tech.atlassian.net/browse/DK26-3720)
- Linked preconditions: PC-DK26-3156-03
- Preconditions: The stakeholder reviews of early November and the pending feedback are known.
- Steps:
  1. Read the DK26-3156 comments and the linked Confluence review pages.
  2. Check that each review lists who attended, what was agreed and what changed.
  3. Check that the latest stakeholder's feedback has been added as approval notes or follow-up items.
  4. Check that each follow-up improvement is raised as a Jira ticket or explicitly declined.
- Expected result: The ticket or Confluence holds approval notes from the stakeholders, or a list of follow-up improvements with tickets. The early-November reviews are documented, and the changes made from them are visible (separate assessment and candidate views, every chart says why it is there). Until the pending feedback is recorded, this test stays open.
