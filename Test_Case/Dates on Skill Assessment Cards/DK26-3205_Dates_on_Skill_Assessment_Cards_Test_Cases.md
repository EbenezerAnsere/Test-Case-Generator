# DK26-3205: FE - Show date on the assessment selection cards in the skill creation flow

Ticket: https://amali-tech.atlassian.net/browse/DK26-3205
Status: In Progress QA
Related: DK26-3166 FE - Story 5.5: Absolute Dates on Question, Test, and Assessment Cards; DK26-3206 (assessment selection defect on the same screen)
Xray folder: `Quarter 4/Ebenezer/Frontend/DK26-3205 FE - Show date on the assessment selection cards in the skill creation flow`
Test Set: DK26-3249
Test Plan: DK26-3106
Test Execution: DK26-3107

## Review Summary

This is a follow-up to DK26-3166, raised during QA on staging. On Skills > Create Skill > Step 2: Assessment Assignment, the assessment cards showed no date, so 335 assessments with near-identical generated names could not be told apart by recency. The fix (commit 9bd61905a, shipped with DK26-3203 and DK26-3204) adds the created date after the test count using `formatAbsoluteDate()` in the viewer's local timezone, and hides it when the API returns no date. The developer only rendered it locally with injected sample data, so these tests use real staging assessments.

Out of scope: selecting an assessment on this screen does not work and is tracked separately as DK26-3206. TC-09 checks that the rest of the step still works and does not judge selection.

## Acceptance Criteria Coverage

| Acceptance criterion | Covered by |
| --- | --- |
| Assessment cards on the skill creation assessment-assignment step show the created date. | TC-01, TC-02, TC-06 |
| The format matches the list cards: DD MMM YYYY, H:MM AM/PM. | TC-03, TC-04 |
| The date is correct for the viewer's timezone. | TC-05 |
| Quality checks: layout, missing date, regression | TC-07, TC-08, TC-09 |

## Preconditions (Xray Precondition issues)

### PC-DK26-3205-01: Org administrator logged in on staging with the DK26-3205 fix deployed

- Jira: [DK26-3246](https://amali-tech.atlassian.net/browse/DK26-3246)

1. Staging (amap-staging.amalitech-dev.net) runs a build that contains the DK26-3205 fix (branch feature/DK26-3203-absolute-dates-previews-and-selection-cards, commit 9bd61905a).
2. The tester is logged in as an organisation administrator who can create skills.
3. The browser cache has been cleared after the deployment, or a hard refresh has been done.

### PC-DK26-3205-02: Organisation holds many real assessments with known created dates

- Jira: [DK26-3247](https://amali-tech.atlassian.net/browse/DK26-3247)

1. The organisation has more than 25 assessments, so the Assessment Assignment list has more than one page (staging currently lists 335).
2. The created date and time of at least 3 assessments has been noted from the Assessments list cards.
3. Several assessments have near-identical generated names (for example SMOKE-BUILD-... or QAFIX-... assessments) and were created at different times.
4. If possible, one assessment was created on day 1-9 of a month and one at an hour of 12 (noon or midnight).

### PC-DK26-3205-03: Skill creation is open on Step 2: Assessment Assignment

- Jira: [DK26-3248](https://amali-tech.atlassian.net/browse/DK26-3248)

1. Go to Test Management > Skills > All Skills and click + Create New > Create Skill.
2. On Basic Details, enter a skill title and description and click Next.
3. Step 2: Assessment Assignment (/dashboard/test-management/skills/create-skill/assessment-assignment) is shown with the Beginner level tab selected and the 'assessments found' count shown.

## Test Cases

### TC-DK26-3205-01: Assessment cards on skill creation Step 2 show the created date

- Jira: [DK26-3237](https://amali-tech.atlassian.net/browse/DK26-3237)
- Linked preconditions: PC-DK26-3205-01 (DK26-3246), PC-DK26-3205-02 (DK26-3247), PC-DK26-3205-03 (DK26-3248)
- Preconditions: Org administrator logged in on staging with the fix deployed; real assessments exist; skill creation is open on Step 2: Assessment Assignment.
- Steps:
  1. On Step 2: Assessment Assignment, with the Beginner tab selected, look at the metadata line of each assessment card on the first page.
  2. Scroll to the bottom of the first page and check every card.
  3. Check that the title, description, duration, test count and View Assessment link are still on each card.
- Expected:
  - Every assessment card shows a created date after the test count, for example '30 mins • 2 test • 16 Oct 2026, 7:57 AM'. No relative label such as '3 days ago' appears. The title, description, duration, test count and View Assessment link are all still shown.

### TC-DK26-3205-02: Created date is shown on every skill level tab, in search results and on later pages

- Jira: [DK26-3238](https://amali-tech.atlassian.net/browse/DK26-3238)
- Linked preconditions: PC-DK26-3205-01 (DK26-3246), PC-DK26-3205-02 (DK26-3247), PC-DK26-3205-03 (DK26-3248)
- Preconditions: Org administrator logged in on staging with the fix deployed; more than 25 assessments exist; skill creation is open on Step 2: Assessment Assignment.
- Steps:
  1. On the Beginner tab, confirm the cards show a created date.
  2. Switch to the Intermediate tab, and to any other level tab shown, and check the cards.
  3. Type part of an assessment name into Search Assessment and check the cards in the results.
  4. Clear the search, go to the second page of results and check the cards.
  5. Go back to the first page and check the cards again.
- Expected:
  - On every level tab, in search results and on every page, each assessment card shows its created date in the same place and format. No card loses its date after switching tabs, searching, paging or going back.

### TC-DK26-3205-03: Skill Step 2 date matches the Assessments list card for the same assessment

- Jira: [DK26-3239](https://amali-tech.atlassian.net/browse/DK26-3239)
- Linked preconditions: PC-DK26-3205-01 (DK26-3246), PC-DK26-3205-02 (DK26-3247), PC-DK26-3205-03 (DK26-3248)
- Preconditions: Org administrator logged in on staging with the fix deployed; the created dates of at least 3 assessments have been noted from the Assessments list cards.
- Steps:
  1. Open Test Management > Assessments and write down the date shown on the cards of 3 chosen assessments.
  2. Open skill creation Step 2: Assessment Assignment.
  3. Find the same 3 assessments using Search Assessment.
  4. Compare the date on each Step 2 card with the date written down from the list card.
- Expected:
  - For each assessment, the Step 2 card shows exactly the same date and time as its Assessments list card, character for character, in the format DD MMM YYYY, H:MM AM/PM (for example 16 Oct 2026, 7:57 AM).

### TC-DK26-3205-04: Created date follows the DD MMM YYYY, H:MM AM/PM format rules

- Jira: [DK26-3240](https://amali-tech.atlassian.net/browse/DK26-3240)
- Linked preconditions: PC-DK26-3205-01 (DK26-3246), PC-DK26-3205-02 (DK26-3247), PC-DK26-3205-03 (DK26-3248)
- Preconditions: Org administrator logged in on staging with the fix deployed; assessments exist with varied created dates, ideally including a day from 1-9 and an hour of 12; skill creation is open on Step 2.
- Steps:
  1. On Step 2, look at the dates on at least 10 assessment cards across more than one page.
  2. For each date, check the day, month, year, hour, minutes and AM/PM parts.
  3. Look in particular for a date with a day from 1 to 9 and a time at the 12 o'clock hour.
- Expected:
  - Every date has a two-digit day (06, not 6), a three-letter English month (May, Oct), a four-digit year, a comma, an hour from 1 to 12 with no leading zero, two-digit minutes and AM or PM. Noon shows as 12:xx PM and midnight as 12:xx AM, never 0:xx.

### TC-DK26-3205-05: Created date is correct for the viewer's timezone

- Jira: [DK26-3241](https://amali-tech.atlassian.net/browse/DK26-3241)
- Linked preconditions: PC-DK26-3205-01 (DK26-3246), PC-DK26-3205-02 (DK26-3247), PC-DK26-3205-03 (DK26-3248)
- Preconditions: Org administrator logged in on staging with the fix deployed; skill creation is open on Step 2; browser developer tools available to read the API response and override the timezone.
- Steps:
  1. Open developer tools on the Network tab and reload Step 2: Assessment Assignment.
  2. In the assessments API response, find the created timestamp of 2 assessments and convert each to the local timezone.
  3. Compare each with the date on that assessment's card.
  4. In developer tools, change the timezone (Sensors > Location, for example America/New_York) and reload Step 2.
  5. Check the same 2 cards again and compare them with the Assessments list cards viewed in the same timezone.
- Expected:
  - Each card's date matches the API timestamp converted to the viewer's local time. After the timezone change, the cards show the same moment in New York time, still as an absolute date in the same format, and they match the Assessments list cards in that timezone.

### TC-DK26-3205-06: Created date tells apart assessments with near-identical names

- Jira: [DK26-3242](https://amali-tech.atlassian.net/browse/DK26-3242)
- Linked preconditions: PC-DK26-3205-01 (DK26-3246), PC-DK26-3205-02 (DK26-3247), PC-DK26-3205-03 (DK26-3248)
- Preconditions: Org administrator logged in on staging with the fix deployed; several assessments share a generated name prefix and were created at different times; skill creation is open on Step 2.
- Steps:
  1. On Step 2, search for a shared name prefix such as 'QAFIX' or 'SMOKE-BUILD'.
  2. Note the title and date shown on each matching card.
  3. Open the API response in developer tools, or the Assessments list cards, and find the created timestamp for each of those assessments.
  4. Compare each card's date with the created timestamp of that same assessment.
- Expected:
  - Each card shows the created date of its own assessment, not a date from a neighbouring card or a shared placeholder. Assessments created at different times show different dates, so the most recent one can be identified from the cards alone.

### TC-DK26-3205-07: Created date does not crowd out the assessment card content

- Jira: [DK26-3243](https://amali-tech.atlassian.net/browse/DK26-3243)
- Linked preconditions: PC-DK26-3205-01 (DK26-3246), PC-DK26-3205-02 (DK26-3247), PC-DK26-3205-03 (DK26-3248)
- Preconditions: Org administrator logged in on staging with the fix deployed; at least one assessment has a long title and description; skill creation is open on Step 2.
- Steps:
  1. Open Step 2 at a desktop width of 1440 px or more and check a card with a long title and description and a card with short values.
  2. Resize the browser to about 1024 px and then to a narrow width of about 768 px, and check the same cards again.
  3. Turn on dark mode with the moon icon and check the cards again.
- Expected:
  - At every width, the title, description, duration, test count, created date and View Assessment link are all readable. Nothing overlaps, is clipped or is pushed off the card. If the line wraps, the date moves down as a whole and is not split mid-value. The date is legible in both light and dark mode.

### TC-DK26-3205-08: Card shows no date or broken text when the API returns no created date

- Jira: [DK26-3244](https://amali-tech.atlassian.net/browse/DK26-3244)
- Linked preconditions: PC-DK26-3205-01 (DK26-3246), PC-DK26-3205-03 (DK26-3248)
- Preconditions: Org administrator logged in on staging with the fix deployed; skill creation is open on Step 2; browser developer tools with response override (Network > Override content) available.
- Steps:
  1. In developer tools, override the assessments API response for Step 2 so one assessment has its created date set to null and another has the field removed.
  2. Reload Step 2 and look at those two cards.
  3. Remove the overrides and reload.
- Expected:
  - Cards with no created date show their title, description, duration, test count and View Assessment link as normal, with no date and no stray bullet separator. No text such as 'Invalid Date', 'NaN', 'null', 'undefined' or '01 Jan 1970' appears, and there are no console errors. Other cards still show their dates. After the overrides are removed, every card shows its date again.

### TC-DK26-3205-09: Assessment Assignment step still works with the created date shown

- Jira: [DK26-3245](https://amali-tech.atlassian.net/browse/DK26-3245)
- Linked preconditions: PC-DK26-3205-01 (DK26-3246), PC-DK26-3205-02 (DK26-3247), PC-DK26-3205-03 (DK26-3248)
- Preconditions: Org administrator logged in on staging with the fix deployed; skill creation is open on Step 2. Selecting an assessment is out of scope here because of the separate defect DK26-3206.
- Steps:
  1. On Step 2, check that the 'assessments found' count is shown and matches the search results.
  2. Click View Assessment on one card and check what opens, then return to Step 2.
  3. Check that the level tab and search you had before are kept, and that the cards still show their dates.
  4. Skip the step as the instructions allow, go to Preview & Save and save the skill.
  5. Open the saved skill from All Skills.
- Expected:
  - The assessments found count, Search Assessment, the level tabs and View Assessment all work as they did before the fix, and the cards still show their dates after returning. The step can be skipped and the skill saves and opens without errors. Selecting an assessment is not judged here because DK26-3206 tracks it.
