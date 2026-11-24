# DK26-3298: FE - 4.6.5: Create from File – Domain selection (existing or new)

Ticket: https://amali-tech.atlassian.net/browse/DK26-3298
Type: Task
Status: In Progress QA
Parent: DK26-3146 Epic 4; part of DK26-3220 FE - Story 4.6: Create an Assessment from File
Design: Figma 'Upload & Check – Select Domain / Domain Selected / Create Domain'
Xray folder: `Quarter 4/Ebenezer/Frontend/DK26-3298 FE - 4.6.5: Create from File – Domain selection (existing or new)`
Test Set: DK26-3616
Test Plan: DK26-3106
Test Execution: DK26-3107
Companion set: DK26-3529 (Philip Odzor, linked to DK26-3220): DK26-3519 to DK26-3528

## Review Summary

After a successful upload, the user picks the domain the questions go into. They either add to an existing domain, using a search box and a list showing 'N categories', or create a new one with a required Domain Name and an optional Description. The choice is held in wizard state and Continue is enabled only once a domain is chosen or a valid name is entered. The API contract adds that the preview flags a new name that is already taken (nameTaken), that the domain permission is needed only when a new domain or category would be created, and that the domain is built only when the assessment is created.

Philip Odzor already wrote 10 screen-level tests for this step (DK26-3519 to DK26-3528, test set DK26-3529, linked to DK26-3220). They cover the two options, search and empty results, selecting a domain, switching options, the required name, whitespace-only names, Back for an existing domain, and searching regardless of capitals. To avoid duplicating them, this set covers only what they leave out:

- Real data. On 2026-10-28 Philip found the list was mock data (5 of 7 domains did not exist in the organisation, and the counts were wrong against 3,006 real domains). TC-01 to TC-04 check the real data path, scale, debounced search and that the chosen domain is used.
- Contract rules for a new domain: duplicate names (TC-05), length limits and special characters (TC-06), creation only at the final Create (TC-07), and a name taken in the meantime (TC-10).
- The new-domain path surviving Back (TC-08), the domain permission (TC-09), an organisation with no domains (TC-11), and accessibility, widths and dark mode (TC-12).

All of these are blocked until the real domain API is connected (PC-DK26-3298-01).

## Acceptance Criteria Coverage

| Acceptance criterion | This set | Philip's set (DK26-3529) |
| --- | --- | --- |
| Search filters domains (debounced, server or client per API). | TC-01, TC-02, TC-03 | DK26-3521, DK26-3528 |
| Switching between options keeps UI consistent and validation correct. | TC-08 | DK26-3523 |
| Domain name required error shown. | TC-05, TC-06 | DK26-3524, DK26-3525, DK26-3527 |
| Selection preserved when coming Back to this step. | TC-04, TC-08 | DK26-3526 |
| Scope: store the choice; decide when a new domain is created; Continue rules | TC-04, TC-07, TC-09, TC-10, TC-11 | DK26-3519, DK26-3520, DK26-3522 |
| Quality: keyboard, widths, dark mode | TC-12 | — |

## Preconditions (Xray Precondition issues)

### PC-DK26-3298-01: Domain step connected to the real API on staging

- Jira: [DK26-3613](https://amali-tech.atlassian.net/browse/DK26-3613)

1. Staging runs a build that contains DK26-3298, with the domain list served by the real API and not mock data. On 2026-10-28 Philip Odzor found the list was still mock (5 of 7 domains did not exist in the organisation, and the counts were wrong), so confirm with Ishaque Appiah that the real API is connected before running these tests.
2. The 'Create Assessment from File' feature flag is on.
3. The tester is signed in as an organisation administrator who can create assessments, domains and tests.
4. The screen tests in test set DK26-3529 (Philip Odzor, DK26-3519 to DK26-3528) cover the step's basic behaviour. These tests add to them.

### PC-DK26-3298-02: Known domains and a matching workbook are prepared

- Jira: [DK26-3614](https://amali-tech.atlassian.net/browse/DK26-3614)

1. The organisation has many domains (staging had 3,006 on 2026-10-28), so search and scrolling can be checked at real scale.
2. At least 3 domains have been noted from the Domains tab with their exact names and category counts, including one with 0 categories and one with several.
3. One domain has a category whose name matches a sheet category in the prepared workbook (for example a domain 'JavaScript' with a category 'Core Syntax').
4. A valid .xlsx workbook following the master template is ready to upload, and the name of an existing domain is noted for duplicate-name checks.

### PC-DK26-3298-03: Users and sessions for permission and race checks

- Jira: [DK26-3615](https://amali-tech.atlassian.net/browse/DK26-3615)

1. User C can create assessments and tests but their role does not include the permission to create domains.
2. A second organisation administrator session (another browser or private window) is available to create a domain while the first user is in the wizard.
3. An organisation with no domains (for example a fresh QA organisation) is available, or this case is noted as not testable.

## Test Cases

### TC-DK26-3298-01: The domain list shows this organisation's real domains with correct category counts

- Jira: [DK26-3601](https://amali-tech.atlassian.net/browse/DK26-3601)
- Linked preconditions: PC-DK26-3298-01 (DK26-3613), PC-DK26-3298-02 (DK26-3614)
- Preconditions: Real domain API connected on staging; org administrator signed in; the names and category counts of at least 3 domains noted from the Domains tab.
- Steps:
  1. Go to Assessments > Create New Assessment > Create from file and upload the prepared workbook.
  2. On the domain panel, find each of the noted domains in the existing-domain list, using search if needed.
  3. Compare each row's name and 'N categories' with the Domains tab, including the domain with 0 categories.
  4. Open developer tools on the Network tab and check that the list comes from an API request, not from a static or mock file.
- Expected:
  - The list contains this organisation's own domains only, each with exactly the name and category count shown on the Domains tab. A domain with no categories shows '0 categories'. No domain from the mock data, or from another organisation, appears. The list is loaded from the domains API.

### TC-DK26-3298-02: Search is debounced and always shows results for the final search term

- Jira: [DK26-3602](https://amali-tech.atlassian.net/browse/DK26-3602)
- Linked preconditions: PC-DK26-3298-01 (DK26-3613), PC-DK26-3298-02 (DK26-3614)
- Preconditions: Real domain API connected; org administrator on the domain panel after a successful upload; developer tools open on the Network tab.
- Steps:
  1. Type a domain name quickly, one character at a time without pausing, and watch the requests sent.
  2. Stop typing and note when the list updates.
  3. Type a short term, then quickly change it to a longer, more specific term.
  4. Type a term with spaces before and after it.
- Expected:
  - Typing does not send a request for every keystroke: the search waits until the user pauses, or filters in the browser if the full list is already loaded. The list always shows the results for what is currently in the box, never results from an earlier, slower request. Leading and trailing spaces do not stop a domain from being found.

### TC-DK26-3298-03: The list stays usable with thousands of domains

- Jira: [DK26-3603](https://amali-tech.atlassian.net/browse/DK26-3603)
- Linked preconditions: PC-DK26-3298-01 (DK26-3613), PC-DK26-3298-02 (DK26-3614)
- Preconditions: Real domain API connected; the organisation has thousands of domains (about 3,006 on staging).
- Steps:
  1. Open the domain panel and time how long the existing-domain list takes to appear.
  2. Scroll the list from top to bottom.
  3. Find a domain near the end of the alphabet by scrolling, and another by searching.
  4. Watch the browser for freezing, and the console for errors.
- Expected:
  - The list appears within a few seconds and scrolls smoothly inside its own scrollable area without the page freezing. Every domain can be reached, either by scrolling (with more loading as the user scrolls, if the list is paged) or by searching. No console errors appear.

### TC-DK26-3298-04: The chosen existing domain is the one used in the next step

- Jira: [DK26-3604](https://amali-tech.atlassian.net/browse/DK26-3604)
- Linked preconditions: PC-DK26-3298-01 (DK26-3613), PC-DK26-3298-02 (DK26-3614)
- Preconditions: Real domain API connected; one domain has a category matching a sheet category in the uploaded workbook.
- Steps:
  1. After uploading, choose the domain that has a matching category and click Continue.
  2. In the Network tab, check that the preview request is sent with that domain's ID (preview?domainId=...).
  3. On Configure Tests, check that the test with the matching category offers its existing questions.
  4. Go Back, choose a different domain with no matching category, and continue again.
- Expected:
  - The preview request uses the ID of the domain that was chosen. Configure Tests reflects that domain: the matching category offers to include its existing questions. After going back and choosing a different domain, a new preview is requested for it and the offer goes away. No old domain choice is carried over.

### TC-DK26-3298-05: A new domain name that already exists is flagged

- Jira: [DK26-3605](https://amali-tech.atlassian.net/browse/DK26-3605)
- Linked preconditions: PC-DK26-3298-01 (DK26-3613), PC-DK26-3298-02 (DK26-3614)
- Preconditions: Real domain API connected; the exact name of an existing domain is noted.
- Steps:
  1. Choose Create a new domain and enter the exact name of an existing domain.
  2. Enter the same name again in different capitals and with spaces before and after it.
  3. Read any message and check whether Continue is available.
  4. Change the name to one that does not exist.
- Expected:
  - An existing name is flagged next to the Domain Name field, whatever its capitals or surrounding spaces, using the nameTaken result from the preview. The user is told to choose an existing domain or pick another name, and cannot continue with the duplicate. A new, unused name clears the message.

### TC-DK26-3298-06: New domain name and description handle length limits and special characters

- Jira: [DK26-3606](https://amali-tech.atlassian.net/browse/DK26-3606)
- Linked preconditions: PC-DK26-3298-01 (DK26-3613)
- Preconditions: Real domain API connected; org administrator on the domain panel after a successful upload.
- Steps:
  1. Choose Create a new domain and type a very long name (for example 300 characters).
  2. Enter a name with special characters, such as 'C# & .NET "Core"', and with leading and trailing spaces.
  3. Enter a very long description.
  4. Continue and complete the wizard with the special-character name, then open the new domain on the Domains tab.
- Expected:
  - The name and description cannot exceed their maximum length: either typing stops at the limit or a message gives the limit, matching manual domain creation. Special characters are accepted and saved exactly as entered, with surrounding spaces trimmed. Nothing is cut off silently or shown as escaped characters.

### TC-DK26-3298-07: A new domain is created only when the assessment is created

- Jira: [DK26-3607](https://amali-tech.atlassian.net/browse/DK26-3607)
- Linked preconditions: PC-DK26-3298-01 (DK26-3613), PC-DK26-3298-02 (DK26-3614)
- Preconditions: Real domain API connected; org administrator signed in; a unique new domain name chosen, such as 'QA-3298-<date>'.
- Steps:
  1. Choose Create a new domain, enter the unique name and a description, and click Continue.
  2. In another tab, search the Domains tab for that name.
  3. Go Back, change the name, and continue again. Then leave the wizard and confirm leaving.
  4. Start again with the unique name and complete the wizard through Create Assessment.
  5. Search the Domains tab for both names.
- Expected:
  - No domain is created by Continue, by going Back or by leaving the wizard: the Domains tab does not show either name before Create. After Create Assessment, exactly one domain exists, with the final name and description, holding the new tests and questions. The earlier name was never created.

### TC-DK26-3298-08: The new-domain name and description are kept when coming Back

- Jira: [DK26-3608](https://amali-tech.atlassian.net/browse/DK26-3608)
- Linked preconditions: PC-DK26-3298-01 (DK26-3613)
- Preconditions: Real domain API connected; org administrator on the domain panel after a successful upload.
- Steps:
  1. Choose Create a new domain, enter a name and description, and click Continue.
  2. Click Back to return to Upload & Check.
  3. Check which option is selected and what the fields contain.
  4. Switch to Add to an existing domain, then back to Create a new domain, and check the fields again.
- Expected:
  - Coming Back shows Create a new domain still selected, with the same name and description, and Continue still available. Switching options and back either keeps the typed values or clears them consistently. The choice sent on Create is always the option currently selected.

### TC-DK26-3298-09: A user who cannot create domains is not offered a new domain

- Jira: [DK26-3609](https://amali-tech.atlassian.net/browse/DK26-3609)
- Linked preconditions: PC-DK26-3298-01 (DK26-3613), PC-DK26-3298-03 (DK26-3615)
- Preconditions: Real domain API connected; User C (can create assessments but not domains) signed in.
- Steps:
  1. As User C, open Create from file and upload the workbook.
  2. Look at the Create a new domain option.
  3. Choose an existing domain and continue through the wizard.
  4. If the new-domain option can still be used, enter a new name and try to finish the wizard.
- Expected:
  - For User C, Create a new domain is hidden, or disabled with a short explanation, following permissions in the check response. Adding to an existing domain still works. If a new domain is attempted anyway, Create is refused with a clear permission message, and no domain or assessment is created.

### TC-DK26-3298-10: A domain name taken by someone else after it was entered is caught at Create

- Jira: [DK26-3610](https://amali-tech.atlassian.net/browse/DK26-3610)
- Linked preconditions: PC-DK26-3298-01 (DK26-3613), PC-DK26-3298-03 (DK26-3615)
- Preconditions: Real domain API connected; two org administrator sessions available.
- Steps:
  1. In session 1, choose Create a new domain with a unique name and continue to Review & Create.
  2. In session 2, create a domain with that same name on the Domains tab.
  3. In session 1, click Create Assessment.
  4. Read the message, check which step is highlighted, then change the name or choose the existing domain and create again.
- Expected:
  - Create is refused with a message that the domain name is now taken, and the Upload & Check step (the domain field) is highlighted so the user can go straight to it. All other entered data is kept. After choosing another name or the existing domain, Create succeeds and no duplicate domain exists.

### TC-DK26-3298-11: An organisation with no domains can still create one

- Jira: [DK26-3611](https://amali-tech.atlassian.net/browse/DK26-3611)
- Linked preconditions: PC-DK26-3298-01 (DK26-3613), PC-DK26-3298-03 (DK26-3615)
- Preconditions: Real domain API connected; an administrator of an organisation with no domains signed in.
- Steps:
  1. Open Create from file and upload the workbook.
  2. Look at the Add to an existing domain option and its list.
  3. Choose Create a new domain, enter a name and continue.
- Expected:
  - The existing-domain list shows a clear empty state that suggests creating a new domain, not a blank area or an endless loading indicator. Creating a new domain works and the user can continue.

### TC-DK26-3298-12: The domain panel is usable by keyboard, at different widths and in dark mode

- Jira: [DK26-3612](https://amali-tech.atlassian.net/browse/DK26-3612)
- Linked preconditions: PC-DK26-3298-01 (DK26-3613)
- Preconditions: Real domain API connected; org administrator on the domain panel after a successful upload.
- Steps:
  1. Using only the keyboard, switch between the two radio cards, search, move through the domain list, select a domain and reach Continue.
  2. Check that focus is visible and that each list row is announced with its name and category count.
  3. View the panel at 1440 px, about 1024 px and about 768 px wide.
  4. Turn on dark mode and check the cards, list, selected row, required marker and error message.
- Expected:
  - Every action can be done by keyboard with a visible focus outline, and the radio cards behave as a radio group. Rows are announced with their name and category count. At every width, the cards, search box and list fit without overlapping or cutting off text. In dark mode the selected row, required marker and error message are clearly visible.
