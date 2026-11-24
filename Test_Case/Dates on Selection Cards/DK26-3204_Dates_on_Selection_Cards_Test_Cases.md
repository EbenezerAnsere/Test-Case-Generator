# DK26-3204: FE - Show date created on the question and test selection cards during test and assessment creation

Ticket: https://amali-tech.atlassian.net/browse/DK26-3204
Status: In Progress QA
Related: DK26-3166 FE - Story 5.5: Absolute Dates on Question, Test, and Assessment Cards
Xray folder: `Quarter 4/Ebenezer/Frontend/DK26-3204 FE - Show date created on the question and test selection cards during test and assessment creation`
Test Set: DK26-3236
Test Plan: DK26-3106
Test Execution: DK26-3107

## Review Summary

This is a follow-up to DK26-3166, raised during QA on staging. The list cards already show absolute dates, but two selection screens did not: Question Selection in test creation and Test Assignment in assessment creation. The fix (commit cd0deb3a2, shipped with DK26-3203 and DK26-3205) reuses `formatAbsoluteDate()`. It puts the date after the score on question cards and after the question count on test cards, and hides it when the API returns no date. Testing covers whether the date is there, that it matches the list cards, its format and timezone, the card layout, the missing-date case, and that selection still works.

## Acceptance Criteria Coverage

| Acceptance criterion | Covered by |
| --- | --- |
| Question selection cards in the test creation flow show the date the question was created. | TC-01, TC-03, TC-06 |
| Test selection cards in the assessment creation flow show the date the test was created. | TC-02, TC-04, TC-06 |
| Both use the same format as the list cards: DD MMM YYYY, H:MM AM/PM. | TC-03, TC-04, TC-05 |
| The date does not crowd out the existing information on the card. | TC-07, TC-08, TC-09 |
| Selection itself still works (regression) | TC-10, TC-11 |

## Preconditions (Xray Precondition issues)

### PC-DK26-3204-01: Org administrator logged in on staging with the DK26-3204 fix deployed

- Jira: [DK26-3233](https://amali-tech.atlassian.net/browse/DK26-3233)

1. Staging (amap-staging.amalitech-dev.net) runs a build that contains the DK26-3204 fix (branch feature/DK26-3203-absolute-dates-previews-and-selection-cards, commit cd0deb3a2).
2. The tester is logged in as an organisation administrator who can create tests and assessments.
3. The browser cache has been cleared after the deployment, or a hard refresh has been done.

### PC-DK26-3204-02: Question bank holds questions with known created dates

- Jira: [DK26-3234](https://amali-tech.atlassian.net/browse/DK26-3234)

1. The organisation has at least 10 active questions across several types (Multiple Choice, Essay, Code, Fill In The Blanks, Matrix) and difficulty levels.
2. The created date and time of at least 3 questions has been noted from the Questions list cards.
3. At least one question has a long question text that wraps or is cut off on the card.
4. If possible, one question was created on day 1-9 of a month and one at an hour of 12 (noon or midnight).

### PC-DK26-3204-03: Test library holds active tests with known created dates

- Jira: [DK26-3235](https://amali-tech.atlassian.net/browse/DK26-3235)

1. The organisation has more than 25 active tests, so Test Assignment shows more than one page.
2. The created date and time of at least 3 tests has been noted from the Tests list cards.
3. At least one test has a long title and a long domain name.

## Test Cases

### TC-DK26-3204-01: Question selection cards show the question's created date

- Jira: [DK26-3222](https://amali-tech.atlassian.net/browse/DK26-3222)
- Linked preconditions: PC-DK26-3204-01 (DK26-3233), PC-DK26-3204-02 (DK26-3234)
- Preconditions: Org administrator logged in on staging with the fix deployed; the question bank holds questions with known created dates.
- Steps:
  1. Go to Test Management > Tests and start creating a regular test.
  2. Fill in the test details and continue to the Question Selection step (/dashboard/test-management/tests/create-test/regular/questions-assignment).
  3. Look at the metadata line of each question card on the first page.
  4. Scroll through the list and check the cards further down.
- Expected:
  - Every question card shows a created date in its metadata line, after the score, for example 'Score: 10 • 06 May 2025, 12:00 PM'. The question text, domain, difficulty, score and type badge are still shown.

### TC-DK26-3204-02: Test selection cards show the test's created date

- Jira: [DK26-3223](https://amali-tech.atlassian.net/browse/DK26-3223)
- Linked preconditions: PC-DK26-3204-01 (DK26-3233), PC-DK26-3204-03 (DK26-3235)
- Preconditions: Org administrator logged in on staging with the fix deployed; the test library holds active tests with known created dates.
- Steps:
  1. Go to Test Management > Assessments and start creating an assessment.
  2. Fill in the assessment details and continue to the Test Assignment step (/dashboard/test-management/assessments/create-assessments/Assign-Test-To-Assessment).
  3. Look at the metadata line of each test card on the first page.
  4. Scroll through the list and check the cards further down.
- Expected:
  - Every test card shows a created date after the question count, for example '15 Questions • 01 Jul 2026, 4:22 PM'. The title, status badge, domain, duration and question count are still shown.

### TC-DK26-3204-03: Question selection date matches the Questions list card for the same question

- Jira: [DK26-3224](https://amali-tech.atlassian.net/browse/DK26-3224)
- Linked preconditions: PC-DK26-3204-01 (DK26-3233), PC-DK26-3204-02 (DK26-3234)
- Preconditions: Org administrator logged in on staging with the fix deployed; the created dates of at least 3 questions have been noted from the Questions list cards.
- Steps:
  1. Open Test Management > Questions and write down the date shown on the cards of 3 chosen questions.
  2. Start creating a regular test and go to the Question Selection step.
  3. Find the same 3 questions, using search or scrolling.
  4. Compare the date on each selection card with the date written down from the list card.
- Expected:
  - For each question, the selection card shows exactly the same date and time as its Questions list card, character for character, in the format DD MMM YYYY, H:MM AM/PM (for example 16 Oct 2026, 7:57 AM). No relative label such as '3 days ago' appears.

### TC-DK26-3204-04: Test selection date matches the Tests list card for the same test

- Jira: [DK26-3225](https://amali-tech.atlassian.net/browse/DK26-3225)
- Linked preconditions: PC-DK26-3204-01 (DK26-3233), PC-DK26-3204-03 (DK26-3235)
- Preconditions: Org administrator logged in on staging with the fix deployed; the created dates of at least 3 tests have been noted from the Tests list cards.
- Steps:
  1. Open Test Management > Tests and write down the date shown on the cards of 3 chosen tests.
  2. Start creating an assessment and go to the Test Assignment step.
  3. Find the same 3 tests using the Search test field.
  4. Compare the date on each selection card with the date written down from the list card.
- Expected:
  - For each test, the selection card shows exactly the same date and time as its Tests list card, in the format DD MMM YYYY, H:MM AM/PM. No relative label such as '3 days ago' appears.

### TC-DK26-3204-05: Created date follows the DD MMM YYYY, H:MM AM/PM rules on both screens

- Jira: [DK26-3226](https://amali-tech.atlassian.net/browse/DK26-3226)
- Linked preconditions: PC-DK26-3204-01 (DK26-3233), PC-DK26-3204-02 (DK26-3234), PC-DK26-3204-03 (DK26-3235)
- Preconditions: Org administrator logged in on staging with the fix deployed; questions and tests exist with varied created dates, ideally including a day from 1-9 and an hour of 12.
- Steps:
  1. Go to the Question Selection step of test creation and check the dates on several cards.
  2. Go to the Test Assignment step of assessment creation and check the dates on several cards.
  3. For each date, check the day, month, year, hour, minutes and AM/PM parts.
  4. Look in particular for a date with a day from 1 to 9 and a time at the 12 o'clock hour.
- Expected:
  - Every date has a two-digit day (06, not 6), a three-letter English month (May, Oct), a four-digit year, a comma, an hour from 1 to 12 with no leading zero, two-digit minutes and AM or PM. Noon shows as 12:xx PM and midnight as 12:xx AM, never 0:xx. Both screens use the same format.

### TC-DK26-3204-06: Created date shows the correct moment in the viewer's local timezone

- Jira: [DK26-3227](https://amali-tech.atlassian.net/browse/DK26-3227)
- Linked preconditions: PC-DK26-3204-01 (DK26-3233), PC-DK26-3204-02 (DK26-3234), PC-DK26-3204-03 (DK26-3235)
- Preconditions: Org administrator logged in on staging with the fix deployed; browser developer tools available to read the API response and override the timezone.
- Steps:
  1. Open the Question Selection step with developer tools open on the Network tab.
  2. In the questions API response, find the created timestamp of one question and convert it to the local timezone.
  3. Compare it with the date on that question's selection card.
  4. Repeat steps 1-3 for one test on the Test Assignment step.
  5. In developer tools, change the timezone (Sensors > Location, for example America/New_York), reload both screens and check the same two cards again.
- Expected:
  - The date on each card matches the API timestamp converted to the viewer's local time. After the timezone change, the cards show the same moment in New York time, still as an absolute date in the same format. The values match the Questions and Tests list cards under the same timezone.

### TC-DK26-3204-07: Created date does not crowd out question selection card content

- Jira: [DK26-3228](https://amali-tech.atlassian.net/browse/DK26-3228)
- Linked preconditions: PC-DK26-3204-01 (DK26-3233), PC-DK26-3204-02 (DK26-3234)
- Preconditions: Org administrator logged in on staging with the fix deployed; at least one question has long question text.
- Steps:
  1. Open the Question Selection step at a desktop width of 1440 px or more.
  2. Check a card with long question text and a card with short question text.
  3. Resize the browser to about 1024 px and then to a narrow width of about 768 px, and check the same cards again.
  4. Turn on dark mode with the moon icon and check the cards again.
- Expected:
  - At every width, the domain, difficulty, score, type badge and created date are all readable. Nothing overlaps, is clipped or is pushed off the card, and the checkbox stays lined up with its card. If the line wraps, the date moves down as a whole and is not split mid-value. The date is legible in both light and dark mode.

### TC-DK26-3204-08: Created date does not crowd out test selection card content

- Jira: [DK26-3229](https://amali-tech.atlassian.net/browse/DK26-3229)
- Linked preconditions: PC-DK26-3204-01 (DK26-3233), PC-DK26-3204-03 (DK26-3235)
- Preconditions: Org administrator logged in on staging with the fix deployed; at least one test has a long title and long domain name.
- Steps:
  1. Open the Test Assignment step at a desktop width of 1440 px or more.
  2. Check the card of a test with a long title and domain, and a card with short values.
  3. Resize the browser to about 1024 px and then to a narrow width of about 768 px, and check the same cards again.
  4. Turn on dark mode with the moon icon and check the cards again.
- Expected:
  - At every width, the title, status badge, domain, duration, question count and created date are all readable. The date does not overlap the Active status badge and does not push the duration or question count off the card. The date is legible in both light and dark mode.

### TC-DK26-3204-09: Card shows no date or broken text when the API returns no created date

- Jira: [DK26-3230](https://amali-tech.atlassian.net/browse/DK26-3230)
- Linked preconditions: PC-DK26-3204-01 (DK26-3233)
- Preconditions: Org administrator logged in on staging with the fix deployed; browser developer tools with response override (Network > Override content) available.
- Steps:
  1. In developer tools, override the questions API response for Question Selection so one question has its created date set to null and another has the field removed.
  2. Reload the Question Selection step and look at those two cards.
  3. Do the same for one test in the tests API response used by Test Assignment, then reload and look at that card.
  4. Remove the overrides and reload.
- Expected:
  - Cards with no created date show their other information as normal, with no date and no stray bullet separator. No text such as 'Invalid Date', 'NaN', 'null', 'undefined' or '01 Jan 1970' appears, and there are no console errors. Other cards still show their dates. After the overrides are removed, every card shows its date again.

### TC-DK26-3204-10: Question selection still works with the created date shown

- Jira: [DK26-3231](https://amali-tech.atlassian.net/browse/DK26-3231)
- Linked preconditions: PC-DK26-3204-01 (DK26-3233), PC-DK26-3204-02 (DK26-3234)
- Preconditions: Org administrator logged in on staging with the fix deployed; the question bank holds at least 10 active questions.
- Steps:
  1. Start creating a regular test and go to the Question Selection step.
  2. Select 3 questions by clicking their checkboxes, then clear one.
  3. Use search or filters to narrow the list, then clear them, and check that the selections are kept.
  4. Check that cards brought up by search, filtering or a new page also show the created date.
  5. Continue to the next step and finish creating the test.
  6. Open the new test and check its questions.
- Expected:
  - Selecting and clearing questions works as it did before the fix, the selected count is correct and selections survive search and filtering. Every card shows the created date, including cards loaded later. The saved test contains exactly the 2 questions left selected.

### TC-DK26-3204-11: Test assignment still works with the created date shown

- Jira: [DK26-3232](https://amali-tech.atlassian.net/browse/DK26-3232)
- Linked preconditions: PC-DK26-3204-01 (DK26-3233), PC-DK26-3204-03 (DK26-3235)
- Preconditions: Org administrator logged in on staging with the fix deployed; more than 25 active tests exist, so the list has more than one page.
- Steps:
  1. Start creating an assessment and go to the Test Assignment step.
  2. Select 2 tests by clicking their checkboxes.
  3. Use 'Select all 25 tests on this page', then clear it.
  4. Use Search test and Filter By, then go to the next page, and check that every card shown still has a created date.
  5. Select 2 tests, continue and finish creating the assessment.
  6. Open the new assessment and check its tests.
- Expected:
  - Single selection, 'Select all on this page', search, filter and paging work as they did before the fix. Every card shown, including on the second page and in search results, has a created date. The saved assessment contains exactly the 2 tests selected.
