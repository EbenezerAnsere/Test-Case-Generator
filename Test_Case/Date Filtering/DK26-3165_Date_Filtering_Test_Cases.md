# DK26-3165: FE - Story 5.4: Date Filtering for Questions, Tests, and Assessments

Ticket: https://amali-tech.atlassian.net/browse/DK26-3165
Status: In Progress QA
Parent: DK26-3147 Epic 5: Improve Question and Test Management
Related: DK26-3174 (BE, Code on Staging), DK26-3181 (UX, Done, has the designs)
Xray folder: `Quarter 4/Ebenezer/Frontend/DK26-3165 FE - Story 5.4: Date Filtering for Questions, Tests, and Assessments`
Test Set: DK26-3281
Test Plan: DK26-3106
Test Execution: DK26-3107

## Review Summary

Administrators get a date filter on the Questions, Tests and Assessments lists. The FE ticket has no comments or attachments, so the expected behaviour comes from the UX designs on DK26-3181:

- Filter by gets a 'Date Range' option.
- A Date panel offers the presets Last 7 days, Last 30 days, This month and Last month, Start and End date pickers, and Clear and Apply buttons.
- The applied filter shows as a chip, for example 'Created: Oct 8 - Oct 14, 2026 x'.
- When nothing matches, the 'No Results Found' empty state is shown.

The chip label shows that the agreed date field is the **created date**.

Points to confirm with the team, since the ticket does not define them: whether the start and end dates are inclusive (TC-06 expects whole days), how a single date or an end date before the start is handled (TC-10), and whether days follow the viewer's timezone (TC-13).

## Acceptance Criteria Coverage

| Acceptance criterion | Covered by |
| --- | --- |
| Add date filtering to question, test, and assessment list views. | TC-01, TC-02 |
| Support filtering by at least one agreed date field such as created date or updated date. | TC-03, TC-04, TC-05, TC-08 |
| Allow users to select a start date and end date. | TC-01, TC-07, TC-10 |
| Ensure results update correctly when the date filter is applied, changed, or cleared. | TC-03, TC-08, TC-09, TC-12 |
| Validate date filtering against known test records covering dates inside and outside the selected range. | TC-03, TC-04, TC-05, TC-06, TC-13 |
| Quality checks: empty state, layout, accessibility | TC-11, TC-14 |

## Preconditions (Xray Precondition issues)

### PC-DK26-3165-01: Org administrator logged in on staging with the date filtering build deployed

- Jira: [DK26-3278](https://amali-tech.atlassian.net/browse/DK26-3278)

1. Staging (amap-staging.amalitech-dev.net) runs the FE build for DK26-3165 together with the BE date filtering from DK26-3174.
2. The tester is logged in as an organisation administrator who can view questions, tests and assessments.
3. The browser cache has been cleared after the deployment, or a hard refresh has been done.
4. The UX designs from DK26-3181 (Figma) are available for reference.

### PC-DK26-3165-02: Known test records exist inside and outside a chosen date range

- Jira: [DK26-3279](https://amali-tech.atlassian.net/browse/DK26-3279)

1. A test date range has been chosen, for example the last 7 days.
2. For each of Questions, Tests and Assessments, at least 2 items were created inside the range and at least 2 outside it (before the start and after the end, where possible).
3. At least one item of each type was created on the start date and one on the end date of the range, and if possible one the day before the start and one the day after the end.
4. Items exist from the last 7 days, from 8-30 days ago, from earlier this month and from last month, so the presets can be checked.
5. The title and created date of every known item has been noted from its list card.

### PC-DK26-3165-03: List views have enough data for combined filters and paging

- Jira: [DK26-3280](https://amali-tech.atlassian.net/browse/DK26-3280)

1. Each of the Questions, Tests and Assessments lists has more than one page of results at the default page size.
2. The known items from the date range differ in at least one other filter value (for example difficulty, domain, question type or status).
3. The total count shown in 'Showing 1 to 10 of N Entries' has been noted for each list with no filters applied.

## Test Cases

### TC-DK26-3165-01: Date Range filter is available on the Questions list and matches the design

- Jira: [DK26-3264](https://amali-tech.atlassian.net/browse/DK26-3264)
- Linked preconditions: PC-DK26-3165-01 (DK26-3278)
- Preconditions: Org administrator logged in on staging with the date filtering build deployed; UX designs from DK26-3181 available.
- Steps:
  1. Go to Test Management > Questions.
  2. Open the Filter by menu and select Date Range.
  3. Open the Date dropdown that appears.
  4. Compare the panel with the UX design.
- Expected:
  - Filter by lists a Date Range option. Selecting it shows a Date dropdown, which opens a panel with the presets Last 7 days, Last 30 days, This month and Last month, a Start date and an End date picker, and Clear and Apply buttons, laid out as in the design. Both date pickers open a calendar, and dates can be picked or typed.

### TC-DK26-3165-02: Date Range filter is available on the Tests and Assessments lists

- Jira: [DK26-3265](https://amali-tech.atlassian.net/browse/DK26-3265)
- Linked preconditions: PC-DK26-3165-01 (DK26-3278)
- Preconditions: Org administrator logged in on staging with the date filtering build deployed.
- Steps:
  1. Go to Test Management > Tests, open Filter by and select Date Range, then open the Date panel.
  2. Go to Test Management > Assessments, open Filter by and select Date Range, then open the Date panel.
  3. Compare both panels with the one on the Questions list.
- Expected:
  - Tests and Assessments both offer Date Range in Filter by, with the same Date panel as Questions: the same presets, Start and End date pickers, and Clear and Apply buttons, behaving the same way.

### TC-DK26-3165-03: Questions list shows only questions created inside the selected range

- Jira: [DK26-3266](https://amali-tech.atlassian.net/browse/DK26-3266)
- Linked preconditions: PC-DK26-3165-01 (DK26-3278), PC-DK26-3165-02 (DK26-3279)
- Preconditions: Org administrator logged in on staging; known questions exist with created dates inside and outside the chosen range.
- Steps:
  1. Go to Test Management > Questions and note the total entries count.
  2. Open Filter by > Date Range, set the chosen Start date and End date, and click Apply.
  3. Go through every page of the filtered results and check the date on each card.
  4. Look for each known question inside the range, using search if needed.
  5. Look for each known question outside the range.
- Expected:
  - Every question shown has a created date within the selected start and end dates. All known questions inside the range are shown, and none of the known questions outside the range are shown. The entries count drops to match the filtered results.

### TC-DK26-3165-04: Tests list shows only tests created inside the selected range

- Jira: [DK26-3267](https://amali-tech.atlassian.net/browse/DK26-3267)
- Linked preconditions: PC-DK26-3165-01 (DK26-3278), PC-DK26-3165-02 (DK26-3279)
- Preconditions: Org administrator logged in on staging; known tests exist with created dates inside and outside the chosen range.
- Steps:
  1. Go to Test Management > Tests and note the total entries count.
  2. Open Filter by > Date Range, set the chosen Start date and End date, and click Apply.
  3. Go through every page of the filtered results and check the date on each card.
  4. Look for each known test inside the range and each known test outside the range.
- Expected:
  - Every test shown has a created date within the selected range. All known tests inside the range are shown and none outside it are shown. The entries count matches the filtered results.

### TC-DK26-3165-05: Assessments list shows only assessments created inside the selected range

- Jira: [DK26-3268](https://amali-tech.atlassian.net/browse/DK26-3268)
- Linked preconditions: PC-DK26-3165-01 (DK26-3278), PC-DK26-3165-02 (DK26-3279)
- Preconditions: Org administrator logged in on staging; known assessments exist with created dates inside and outside the chosen range.
- Steps:
  1. Go to Test Management > Assessments and note the total entries count.
  2. Open Filter by > Date Range, set the chosen Start date and End date, and click Apply.
  3. Go through every page of the filtered results and check the date on each card.
  4. Look for each known assessment inside the range and each known assessment outside the range.
- Expected:
  - Every assessment shown has a created date within the selected range. All known assessments inside the range are shown and none outside it are shown. The entries count matches the filtered results.

### TC-DK26-3165-06: Items created on the start and end dates are included, items just outside are not

- Jira: [DK26-3269](https://amali-tech.atlassian.net/browse/DK26-3269)
- Linked preconditions: PC-DK26-3165-01 (DK26-3278), PC-DK26-3165-02 (DK26-3279)
- Preconditions: Org administrator logged in on staging; known items exist created on the start date, on the end date, the day before the start and the day after the end.
- Steps:
  1. On the Questions list, apply a date range whose start and end dates match the boundary items.
  2. Check whether the items created on the start date (including early in the day) and on the end date (including late in the day, for example after 11 PM) are shown.
  3. Check whether the items created the day before the start and the day after the end are shown.
  4. Apply a single-day range where the start date and end date are the same day, and check the results.
  5. Repeat steps 1-3 on the Tests and Assessments lists.
- Expected:
  - The range is inclusive of whole days: items created at any time on the start date or the end date are shown, including late on the end date. Items from the day before the start or the day after the end are not shown. A single-day range shows exactly the items created on that day.

### TC-DK26-3165-07: Preset ranges fill the correct dates and return the matching items

- Jira: [DK26-3270](https://amali-tech.atlassian.net/browse/DK26-3270)
- Linked preconditions: PC-DK26-3165-01 (DK26-3278), PC-DK26-3165-02 (DK26-3279)
- Preconditions: Org administrator logged in on staging; known items exist from the last 7 days, 8-30 days ago, earlier this month and last month.
- Steps:
  1. On the Questions list, open the Date panel and click Last 7 days. Note the Start and End dates filled in, apply, and check the results.
  2. Repeat with Last 30 days.
  3. Repeat with This month.
  4. Repeat with Last month.
  5. Pick one preset on the Tests list and one on the Assessments list and check them the same way.
- Expected:
  - Each preset is highlighted when chosen and fills Start and End correctly relative to today: Last 7 days and Last 30 days end today, This month runs from the 1st of the current month to today, and Last month covers the whole previous calendar month. The results contain only items created in that period, and the known items fall in or out as expected.

### TC-DK26-3165-08: Applied filter chip is shown and results update when the range is changed

- Jira: [DK26-3271](https://amali-tech.atlassian.net/browse/DK26-3271)
- Linked preconditions: PC-DK26-3165-01 (DK26-3278), PC-DK26-3165-02 (DK26-3279)
- Preconditions: Org administrator logged in on staging; known items exist inside and outside two different ranges.
- Steps:
  1. On the Questions list, apply a custom date range.
  2. Check the chip shown next to the Date dropdown.
  3. Open the Date panel again, check that it shows the applied dates, change the end date to a different day and apply.
  4. Check the chip and the results again.
  5. Switch to a preset and apply, and check the chip and results again.
- Expected:
  - After Apply, a chip appears showing the field and range, for example 'Created: Oct 8 - Oct 14, 2026', with an x to remove it. Reopening the panel shows the applied dates. After each change, the chip updates to the new range and the results and entries count change to match it straight away, with no leftover items from the previous range and no need to reload.

### TC-DK26-3165-09: Clearing the date filter restores the full list

- Jira: [DK26-3272](https://amali-tech.atlassian.net/browse/DK26-3272)
- Linked preconditions: PC-DK26-3165-01 (DK26-3278), PC-DK26-3165-03 (DK26-3280)
- Preconditions: Org administrator logged in on staging; the unfiltered entries count of each list has been noted.
- Steps:
  1. On the Questions list, apply a date range so the results are reduced.
  2. Click the x on the applied filter chip.
  3. Apply a date range again, open the Date panel and click Clear.
  4. Check the date inputs and preset selection in the panel after clearing.
  5. Repeat steps 1-2 on the Tests and Assessments lists.
- Expected:
  - Removing the chip or clicking Clear removes the date filter. The chip disappears, the Start and End dates and preset selection are emptied, and the list returns to all items with the entries count back to the noted total. Clearing does not remove other filters or the search text.

### TC-DK26-3165-10: Invalid or incomplete date ranges are handled clearly

- Jira: [DK26-3273](https://amali-tech.atlassian.net/browse/DK26-3273)
- Linked preconditions: PC-DK26-3165-01 (DK26-3278)
- Preconditions: Org administrator logged in on staging with the date filtering build deployed.
- Steps:
  1. On the Questions list, open the Date panel, set an End date earlier than the Start date and click Apply.
  2. Set only a Start date with no End date and click Apply, then set only an End date with no Start date and click Apply.
  3. Type an impossible date, such as 02/30/2026 or letters, into a date input.
  4. Set a range entirely in the future and click Apply.
  5. Click Apply with both dates empty.
- Expected:
  - An end date before the start date is blocked, either by disabling Apply, showing a clear validation message or preventing that date being picked. It is never sent as a filter that silently returns wrong results. A single date and an empty panel behave as designed: either they are blocked with a message, or they filter as open-ended 'from' or 'to' ranges. The chip always shows what was actually applied. Impossible typed dates are rejected. A future range returns the empty state. No errors appear in the console.

### TC-DK26-3165-11: Empty state is shown when no items fall in the range

- Jira: [DK26-3274](https://amali-tech.atlassian.net/browse/DK26-3274)
- Linked preconditions: PC-DK26-3165-01 (DK26-3278)
- Preconditions: Org administrator logged in on staging with the date filtering build deployed; a range with no created items is known (for example a range in the future or before the organisation existed).
- Steps:
  1. On the Questions list, apply a date range that contains no questions.
  2. Check the list area.
  3. Repeat on the Tests and Assessments lists.
  4. Remove the chip on each list.
- Expected:
  - Each list shows the 'No Results Found' empty state with the illustration and the text 'We couldn't find anything matching your search. Try adjusting your keywords or filters.', as in the design. The chip stays visible so the filter can be changed or removed, and no pagination for empty pages is shown. Removing the chip brings the items back.

### TC-DK26-3165-12: Date filter works together with search, other filters and paging

- Jira: [DK26-3275](https://amali-tech.atlassian.net/browse/DK26-3275)
- Linked preconditions: PC-DK26-3165-01 (DK26-3278), PC-DK26-3165-02 (DK26-3279), PC-DK26-3165-03 (DK26-3280)
- Preconditions: Org administrator logged in on staging; lists have more than one page, and the known items differ in other filter values.
- Steps:
  1. On the Questions list, go to page 2 or later, then apply a date range.
  2. Check which page is shown and the entries count.
  3. Add another filter (for example Difficulty levels or Domains) and check the results.
  4. Type a search term matching some of the known items and check the results.
  5. Change the page size and move between pages of the filtered results.
  6. Remove the date chip only and check that the other filter and the search stay in place.
  7. Repeat steps 1-4 on the Tests and Assessments lists with a filter those lists offer.
- Expected:
  - Applying the date filter goes back to page 1. With other filters and search added, results meet all of them at once, inside the date range, and the count is correct. Paging and page size work within the filtered results and no unfiltered items appear on later pages. Removing the date filter keeps the other filters and the search.

### TC-DK26-3165-13: Date filter uses the viewer's local day boundaries, consistent with the card dates

- Jira: [DK26-3276](https://amali-tech.atlassian.net/browse/DK26-3276)
- Linked preconditions: PC-DK26-3165-01 (DK26-3278), PC-DK26-3165-02 (DK26-3279)
- Preconditions: Org administrator logged in on staging; a known item was created late in the evening local time (for example after 11 PM) or early in the morning; browser developer tools available to override the timezone and read the filter request.
- Steps:
  1. Apply a range on the Questions list whose end date is the local date shown on the card of the late-evening item.
  2. Open developer tools on the Network tab and check the start and end values sent in the filter request.
  3. Check whether the late-evening item is shown.
  4. Change the browser timezone (Sensors > Location, for example America/New_York), reload, apply the same calendar dates again and check the results against the dates now shown on the cards.
- Expected:
  - The filter treats days by the viewer's local timezone, the same way the card dates are shown. Any item whose card date falls within the selected dates is included, even if its UTC date is a different day. After the timezone change, the results still agree with the card dates shown in that timezone. The request values cover the full local start and end days.

### TC-DK26-3165-14: Date filter panel is usable at different widths, in dark mode and by keyboard

- Jira: [DK26-3277](https://amali-tech.atlassian.net/browse/DK26-3277)
- Linked preconditions: PC-DK26-3165-01 (DK26-3278)
- Preconditions: Org administrator logged in on staging with the date filtering build deployed.
- Steps:
  1. Open the Date panel on the Questions list at 1440 px, about 1024 px and about 768 px wide.
  2. Apply a range at each width and check the chip next to the Date dropdown and Multiselect.
  3. Turn on dark mode with the moon icon and check the panel, calendar, chip and empty state.
  4. Using only the keyboard (Tab, Enter, Esc), open the panel, choose a preset, enter dates, apply and remove the chip.
  5. Click outside the open panel without applying.
- Expected:
  - The panel, calendar and chip fit the screen at every width without overlapping the cards, search field or Multiselect. All text and selected states are readable in dark mode. The whole flow can be done by keyboard with a visible focus outline, and Esc closes the panel. Clicking outside closes the panel without applying unsaved changes.
