# DK26-3203: FE - Show absolute dates on the cards inside the test preview and assessment preview

Ticket: https://amali-tech.atlassian.net/browse/DK26-3203
Status: In Progress QA
Related: DK26-3166 FE - Story 5.5: Absolute Dates on Question, Test, and Assessment Cards
Xray folder: `Quarter 4/Ebenezer/Frontend/DK26-3203 FE - Show absolute dates on the cards inside the test preview and assessment preview`
Test Set: DK26-3263
Test Plan: DK26-3106
Test Execution: DK26-3107

## Review Summary

This is a follow-up to DK26-3166, which fixed the dates on the main list cards but not on the preview screens. Before the fix, test preview question cards showed relative labels such as 'Added 30 minutes ago', and assessment preview test cards showed no date at all. The fix (commit 37cc5ed97) reuses `formatAbsoluteDate()`. Question cards now show 'Added 01 Jul 2026, 4:22 PM' with the Archived and Unpublished labels unchanged, and test cards show their created date, hidden when the API returns none.

Point to confirm: 'Added' on the test preview could mean the question's created date or the date it was added to the test. TC-03 checks against the API timestamp and records any difference from the Questions list card, so it can be confirmed with the developer.

## Acceptance Criteria Coverage

| Acceptance criterion | Covered by |
| --- | --- |
| Question cards inside the test preview show an absolute date instead of 'Added X ago'. | TC-01, TC-03, TC-07 |
| Test cards inside the assessment preview show the created date. | TC-02, TC-04 |
| Both use the same format as the list cards: DD MMM YYYY, H:MM AM/PM. | TC-03, TC-04, TC-05 |
| The date shown is correct for the viewer's timezone, consistent with the list cards. | TC-03, TC-06 |
| Quality checks: missing date, layout, regression | TC-08, TC-09, TC-10 |

## Preconditions (Xray Precondition issues)

### PC-DK26-3203-01: Org administrator logged in on staging with the DK26-3203 fix deployed

- Jira: [DK26-3260](https://amali-tech.atlassian.net/browse/DK26-3260)

1. Staging (amap-staging.amalitech-dev.net) runs a build that contains the DK26-3203 fix (branch feature/DK26-3203-absolute-dates-previews-and-selection-cards, commit 37cc5ed97).
2. The tester is logged in as an organisation administrator who can view tests and assessments.
3. The browser cache has been cleared after the deployment, or a hard refresh has been done.

### PC-DK26-3203-02: A test with many questions and known dates is available for preview

- Jira: [DK26-3261](https://amali-tech.atlassian.net/browse/DK26-3261)

1. A test exists with at least 10 questions in its pool (for example 'QAFIX All-Types mvawppq91wums', which has 20).
2. The created date and time of at least 3 of its questions has been noted from the Questions list cards.
3. If possible, the test includes at least one archived or unpublished question.
4. If possible, one question was created on day 1-9 of a month and one at an hour of 12 (noon or midnight).
5. The test preview is opened from Test Management > Tests > the test's card > Preview (/dashboard/test-management/tests/preview-test?testId=...).

### PC-DK26-3203-03: An assessment with several tests and known dates is available for preview

- Jira: [DK26-3262](https://amali-tech.atlassian.net/browse/DK26-3262)

1. An assessment exists with at least 2 tests that were created at different times.
2. The created date and time of each of those tests has been noted from the Tests list cards.
3. The assessment preview is opened from Test Management > Assessments > the assessment's card > Preview (/dashboard/test-management/assessments/preview/<id>).

## Test Cases

### TC-DK26-3203-01: Test preview question cards show an absolute date instead of 'Added X ago'

- Jira: [DK26-3250](https://amali-tech.atlassian.net/browse/DK26-3250)
- Linked preconditions: PC-DK26-3203-01 (DK26-3260), PC-DK26-3203-02 (DK26-3261)
- Preconditions: Org administrator logged in on staging with the fix deployed; a test with at least 10 questions is available for preview.
- Steps:
  1. Open the test preview of the prepared test.
  2. Scroll to Questions Selected and look at the date label on each question card.
  3. Scroll through every question card in the preview.
  4. Use the browser's find (Ctrl+F) to search the page for 'ago'.
- Expected:
  - Every question card shows 'Added' followed by an absolute date, for example 'Added 01 Jul 2026, 4:22 PM'. No card shows a relative label such as 'Added 30 minutes ago', and searching for 'ago' finds no date label on the page.

### TC-DK26-3203-02: Assessment preview test cards show the test's created date

- Jira: [DK26-3251](https://amali-tech.atlassian.net/browse/DK26-3251)
- Linked preconditions: PC-DK26-3203-01 (DK26-3260), PC-DK26-3203-03 (DK26-3262)
- Preconditions: Org administrator logged in on staging with the fix deployed; an assessment with at least 2 tests is available for preview.
- Steps:
  1. Open the assessment preview of the prepared assessment.
  2. Scroll below Security Configurations Selected to the test cards.
  3. Look at the metadata line of each test card.
  4. Check that the title, Active status badge, domain, duration and View Test link are still on each card.
- Expected:
  - Every test card shows a created date, for example '16 Sep 2026, 2:16 PM', in its metadata line. The title, status badge, domain, duration and View Test link are all still shown.

### TC-DK26-3203-03: Test preview question date matches the source timestamp and the Questions list card

- Jira: [DK26-3252](https://amali-tech.atlassian.net/browse/DK26-3252)
- Linked preconditions: PC-DK26-3203-01 (DK26-3260), PC-DK26-3203-02 (DK26-3261)
- Preconditions: Org administrator logged in on staging with the fix deployed; the created dates of at least 3 questions in the test have been noted from the Questions list cards; browser developer tools available.
- Steps:
  1. Open the test preview with developer tools open on the Network tab.
  2. In the test preview API response, find the timestamp field for 3 questions (the field the old 'Added X ago' label was based on) and convert each to the local timezone.
  3. Compare each with the date on that question's card in the preview.
  4. Compare each with the date noted from the question's card on the Questions list.
- Expected:
  - Each preview card's date matches its API timestamp in the viewer's local time, in the same format as the list cards. If the timestamp is the question's created date, the preview matches the Questions list card exactly. If it is the date the question was added to the test, any difference from the list card is recorded and confirmed with the developer, not treated as a pass by default.

### TC-DK26-3203-04: Assessment preview test date matches the Tests list card for the same test

- Jira: [DK26-3253](https://amali-tech.atlassian.net/browse/DK26-3253)
- Linked preconditions: PC-DK26-3203-01 (DK26-3260), PC-DK26-3203-03 (DK26-3262)
- Preconditions: Org administrator logged in on staging with the fix deployed; the created dates of the assessment's tests have been noted from the Tests list cards.
- Steps:
  1. Open the assessment preview of the prepared assessment.
  2. Note the date on each test card.
  3. Compare each date with the one noted from that test's card on the Tests list.
  4. Check that tests created at different times show different dates on the preview.
- Expected:
  - Each test card in the assessment preview shows exactly the same date and time as its Tests list card, character for character. Each card shows its own test's date, not a neighbouring card's date or the assessment's own date.

### TC-DK26-3203-05: Preview dates follow the DD MMM YYYY, H:MM AM/PM format rules

- Jira: [DK26-3254](https://amali-tech.atlassian.net/browse/DK26-3254)
- Linked preconditions: PC-DK26-3203-01 (DK26-3260), PC-DK26-3203-02 (DK26-3261), PC-DK26-3203-03 (DK26-3262)
- Preconditions: Org administrator logged in on staging with the fix deployed; the prepared test and assessment are available for preview, ideally with a date on day 1-9 and one at the 12 o'clock hour.
- Steps:
  1. Open the test preview and check the dates on at least 10 question cards.
  2. Open the assessment preview and check the dates on its test cards.
  3. For each date, check the day, month, year, hour, minutes and AM/PM parts.
  4. Look in particular for a date with a day from 1 to 9 and a time at the 12 o'clock hour.
- Expected:
  - Every date has a two-digit day (06, not 6), a three-letter English month (Jul, Sep), a four-digit year, a comma, an hour from 1 to 12 with no leading zero, two-digit minutes and AM or PM. Noon shows as 12:xx PM and midnight as 12:xx AM, never 0:xx. Both previews use the same format as the list cards.

### TC-DK26-3203-06: Preview dates are correct for the viewer's timezone

- Jira: [DK26-3255](https://amali-tech.atlassian.net/browse/DK26-3255)
- Linked preconditions: PC-DK26-3203-01 (DK26-3260), PC-DK26-3203-02 (DK26-3261), PC-DK26-3203-03 (DK26-3262)
- Preconditions: Org administrator logged in on staging with the fix deployed; the prepared test and assessment are available; browser developer tools available to override the timezone.
- Steps:
  1. Note the date on one question card in the test preview and one test card in the assessment preview.
  2. In developer tools, change the timezone (Sensors > Location, for example America/New_York).
  3. Reload both previews and note the same two dates again.
  4. With New York time still set, open the Questions and Tests list cards for the same items and compare.
- Expected:
  - After the timezone change, both previews show the same moment shifted into New York time, still as an absolute date in the same format. The preview dates match the list cards for the same items under the same timezone.

### TC-DK26-3203-07: Archived and Unpublished labels on test preview question cards are unchanged

- Jira: [DK26-3256](https://amali-tech.atlassian.net/browse/DK26-3256)
- Linked preconditions: PC-DK26-3203-01 (DK26-3260), PC-DK26-3203-02 (DK26-3261)
- Preconditions: Org administrator logged in on staging with the fix deployed; the prepared test includes at least one archived or unpublished question.
- Steps:
  1. Open the test preview of the prepared test.
  2. Find the card of an archived question and the card of an unpublished question.
  3. Check the status labels and the date on each of those cards.
  4. Compare with an active question card.
- Expected:
  - Archived and unpublished question cards still show their Archived or Unpublished label as before, and also show the absolute 'Added' date. The label and the date do not overlap or replace each other, and active cards show the date without a status label.

### TC-DK26-3203-08: Preview cards show no broken text when the API returns no date

- Jira: [DK26-3257](https://amali-tech.atlassian.net/browse/DK26-3257)
- Linked preconditions: PC-DK26-3203-01 (DK26-3260), PC-DK26-3203-02 (DK26-3261), PC-DK26-3203-03 (DK26-3262)
- Preconditions: Org administrator logged in on staging with the fix deployed; browser developer tools with response override (Network > Override content) available.
- Steps:
  1. In developer tools, override the assessment preview API response so one test has its created date set to null and another has the field removed, then reload.
  2. Check those two test cards.
  3. Override the test preview API response so one question has no date timestamp, then reload and check that card.
  4. Remove all overrides and reload both previews.
- Expected:
  - Assessment preview test cards with no date show their other information as normal, with no date and no stray separator. The test preview question card with no date shows no 'Added' label on its own and no fallback to a relative label. No text such as 'Invalid Date', 'NaN', 'null', 'undefined' or '01 Jan 1970' appears, and there are no console errors. After the overrides are removed, all dates show again.

### TC-DK26-3203-09: Preview dates do not crowd out the card content

- Jira: [DK26-3258](https://amali-tech.atlassian.net/browse/DK26-3258)
- Linked preconditions: PC-DK26-3203-01 (DK26-3260), PC-DK26-3203-02 (DK26-3261), PC-DK26-3203-03 (DK26-3262)
- Preconditions: Org administrator logged in on staging with the fix deployed; the prepared test (with a long question text) and assessment (with a long test title) are available.
- Steps:
  1. Open the test preview at a desktop width of 1440 px or more and check a question card with long text and its '...' menu.
  2. Open the assessment preview and check a test card with a long title, its Active badge and View Test link.
  3. Resize the browser to about 1024 px and then to about 768 px, and check both previews again.
  4. Turn on dark mode with the moon icon and check both previews again.
- Expected:
  - At every width, the date and all existing content are readable on both previews. The date does not overlap the question text, the '...' menu, the Active badge or the View Test link, and is not split mid-value if the line wraps. The date is legible in both light and dark mode.

### TC-DK26-3203-10: Test and assessment previews still work with the dates shown

- Jira: [DK26-3259](https://amali-tech.atlassian.net/browse/DK26-3259)
- Linked preconditions: PC-DK26-3203-01 (DK26-3260), PC-DK26-3203-02 (DK26-3261), PC-DK26-3203-03 (DK26-3262)
- Preconditions: Org administrator logged in on staging with the fix deployed; the prepared test and assessment are available for preview.
- Steps:
  1. In the test preview, change Sort by to each available option and check the order of the question cards and their dates.
  2. Open the '...' menu on a question card and check that its options appear.
  3. In the assessment preview, click View Test on a test card and check that the correct test opens.
  4. Go back to the assessment preview and check that View report, History and Add Tag still open as before.
  5. Use Back on both previews and check that you return to the right list.
- Expected:
  - Sort by reorders the question cards as before, and each card keeps its own date after sorting (dates move with their cards). The '...' menu, View Test, View report, History, Add Tag and Back all work as before the fix, and every card still shows its absolute date after returning to a preview.
