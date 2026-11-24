# DK26-3294: FE - 4.6.1: Create from File – Feature flag, entry point & wizard shell

Ticket: https://amali-tech.atlassian.net/browse/DK26-3294
Type: Task
Status: In Progress QA
Parent: DK26-3146 Epic 4: Deliver Assessment Creation Improvements; part of DK26-3220 FE - Story 4.6: Create an Assessment from File
Design: Figma 'All Assessments / Upload & Check' (node 15463-112387)
Xray folder: `Quarter 4/Ebenezer/Frontend/DK26-3294 FE - 4.6.1: Create from File – Feature flag, entry point & wizard shell`
Test Set: DK26-3419
Test Plan: DK26-3106
Test Execution: DK26-3107

## Review Summary

This is the first of nine FE tasks for Story 4.6 (Create an Assessment from File). It delivers the frame of the flow, not its content. The 'Create New Assessment' button becomes a dropdown with 'Create manually' (unchanged) and 'Create from file' (with a 'New' badge), shown only to users who can create assessments and only when the 'Create Assessment from File' feature flag is on. The new route has a Back link, title and subtitle, a 3-step stepper (Upload & Check, Configure Tests, Review & Create), and a footer with Cancel, Back and Continue. A wizard state store keeps data between steps, and a route guard with a modal asks for confirmation before leaving once a file has been uploaded.

Points to watch:

- The feature flag (key create_assessment_from_file_796365, default ON) was created on the developer's local environment. It must also exist on the environment under test before TC-03 can run.
- The step contents come from later tasks that are still To Do: the API service and mocks (DK26-3295), Upload & Check (DK26-3296) and the remaining steps (DK26-3297 to DK26-3302). Tests that need an uploaded file (TC-07, TC-09, TC-11, TC-12) are blocked until upload works, through the real step or the mocks.
- Figma could not be opened from here because it needs a login. Expected copy comes from the UX ticket DK26-3219 screenshot and the ticket text.

## Acceptance Criteria Coverage

| Acceptance criterion | Covered by |
| --- | --- |
| Dropdown matches design; 'Create manually' behaves exactly as before. | TC-01, TC-02 |
| Option hidden when flag off or user lacks create permission (route also guarded). | TC-03, TC-04 |
| Stepper and footer render per design; steps can't be skipped forward. | TC-05, TC-06, TC-07, TC-08 |
| Data persists when moving Back/forward between steps. | TC-09 |
| Leaving after upload prompts for confirmation; no prompt before upload. | TC-10, TC-11, TC-12 |
| Quality checks: widths, dark mode, keyboard | TC-13 |

## Preconditions (Xray Precondition issues)

### PC-DK26-3294-01: Build with DK26-3294 deployed and the Create Assessment from File flag available

- Jira: [DK26-3416](https://amali-tech.atlassian.net/browse/DK26-3416)

1. The environment under test (staging, amap-staging.amalitech-dev.net, or QA) runs a build that contains DK26-3294.
2. The feature flag 'Create Assessment from File' (key create_assessment_from_file_796365, category ASSESSMENT, type BOOLEAN, public) exists on that environment. The developer's comment says it was created on the local environment, so it must also be created on the environment under test.
3. The tester can open Feature Flags and switch this flag on and off.
4. The Figma frames 'All Assessments / Upload & Check' are available for comparison.

### PC-DK26-3294-02: One user who can create assessments and one who cannot

- Jira: [DK26-3417](https://amali-tech.atlassian.net/browse/DK26-3417)

1. User A has a role that can create assessments today (for example an organisation administrator) and sees the 'Create New Assessment' button on the Assessments tab.
2. User B belongs to the same organisation and can open the Assessments tab, but their role does not include the permission to create assessments.
3. Both users can log in on the environment under test, in separate browsers or private windows.

### PC-DK26-3294-03: A file can be uploaded on the Upload & Check step

- Jira: [DK26-3418](https://amali-tech.atlassian.net/browse/DK26-3418)

1. A valid .xlsx workbook that follows the master template is available (for example the downloaded master template filled with a few questions).
2. Uploading on the Upload & Check step works on the environment under test, either through the real step (DK26-3296 with the backend from DK26-3221) or through the mocks from DK26-3295.
3. If neither is available yet, tests that need an uploaded file are blocked and are run once the upload step is delivered.

## Test Cases

### TC-DK26-3294-01: Create New Assessment opens a menu with Create manually and Create from file

- Jira: [DK26-3403](https://amali-tech.atlassian.net/browse/DK26-3403)
- Linked preconditions: PC-DK26-3294-01 (DK26-3416), PC-DK26-3294-02 (DK26-3417)
- Preconditions: Build deployed with the flag on; logged in as User A, who can create assessments.
- Steps:
  1. Go to Test Management > Assessments.
  2. Click 'Create New Assessment'.
  3. Check the options in the menu that opens and compare it with the Figma design.
  4. Click outside the menu, then open it again and press Esc.
- Expected:
  - 'Create New Assessment' opens a dropdown with two options: 'Create manually' and 'Create from file', and 'Create from file' has a 'New' badge. The button, menu, labels, badge and spacing match the design. Clicking outside or pressing Esc closes the menu without navigating.

### TC-DK26-3294-02: Create manually behaves exactly as the existing flow did

- Jira: [DK26-3404](https://amali-tech.atlassian.net/browse/DK26-3404)
- Linked preconditions: PC-DK26-3294-01 (DK26-3416), PC-DK26-3294-02 (DK26-3417)
- Preconditions: Build deployed with the flag on; logged in as User A; at least one active test exists to assign.
- Steps:
  1. On the Assessments tab, open 'Create New Assessment' and choose 'Create manually'.
  2. Check the URL and the first screen against the existing manual flow (/dashboard/test-management/assessments/create-assessments).
  3. Complete the manual flow: enter details, assign a test, set security options and save.
  4. Open the new assessment from the Assessments list.
- Expected:
  - 'Create manually' opens the same route and screens as the old 'Create New Assessment' button, with no new steps, fields or prompts. The assessment is created and opens from the list exactly as before.

### TC-DK26-3294-03: Create from file is hidden and its route blocked when the feature flag is off

- Jira: [DK26-3405](https://amali-tech.atlassian.net/browse/DK26-3405)
- Linked preconditions: PC-DK26-3294-01 (DK26-3416), PC-DK26-3294-02 (DK26-3417)
- Preconditions: Build deployed; logged in as User A; the tester can toggle the flag on the Feature Flags page.
- Steps:
  1. On the Feature Flags page, switch 'Create Assessment from File' off.
  2. Reload the Assessments tab and open 'Create New Assessment'.
  3. Open the Create from file page directly by typing or pasting its URL.
  4. Switch the flag back on, reload the Assessments tab and open 'Create New Assessment' again.
- Expected:
  - With the flag off, 'Create from file' does not appear and 'Create manually' still works. Opening the Create from file URL directly does not show the wizard: the user is redirected to the Assessments list or a not-available page, with no errors. With the flag back on, 'Create from file' appears again.

### TC-DK26-3294-04: Create from file is hidden and its route blocked for a user without create permission

- Jira: [DK26-3406](https://amali-tech.atlassian.net/browse/DK26-3406)
- Linked preconditions: PC-DK26-3294-01 (DK26-3416), PC-DK26-3294-02 (DK26-3417)
- Preconditions: Build deployed with the flag on; User B (no create-assessment permission) can log in; the Create from file URL is known from User A's session.
- Steps:
  1. Log in as User B and go to Test Management > Assessments.
  2. Check whether 'Create New Assessment' or a 'Create from file' option is visible.
  3. Open the Create from file page directly by pasting its URL.
  4. Log in as User A in another window and confirm that 'Create from file' is visible to them.
- Expected:
  - User B sees neither 'Create from file' nor any way into the wizard, just as they cannot create assessments manually today. Opening the URL directly redirects User B away or shows an access-denied page without loading the wizard. User A sees and can use the option.

### TC-DK26-3294-05: Create an Assessment from File page shell matches the design

- Jira: [DK26-3407](https://amali-tech.atlassian.net/browse/DK26-3407)
- Linked preconditions: PC-DK26-3294-01 (DK26-3416), PC-DK26-3294-02 (DK26-3417)
- Preconditions: Build deployed with the flag on; logged in as User A.
- Steps:
  1. On the Assessments tab, open 'Create New Assessment' and choose 'Create from file'.
  2. Check the URL, the breadcrumb and which tab is active.
  3. Check the Back link, title and subtitle.
  4. Compare the page with the Figma frame.
- Expected:
  - A new page opens on its own route, with the Assessments tab still active. It shows a 'Back' link, the title 'Create an Assessment from File' and the subtitle 'Upload your workbook/CSV and process it into an assessment, ready for dispatch.' The layout, fonts and spacing match the design.

### TC-DK26-3294-06: Stepper shows the three steps with the active step highlighted

- Jira: [DK26-3408](https://amali-tech.atlassian.net/browse/DK26-3408)
- Linked preconditions: PC-DK26-3294-01 (DK26-3416), PC-DK26-3294-02 (DK26-3417)
- Preconditions: Build deployed with the flag on; logged in as User A; the Create from file page is open.
- Steps:
  1. Check the stepper below the subtitle.
  2. Check the label, icon and order of each step.
  3. Check which step is highlighted on arrival.
  4. If a later step can be reached (see PC-DK26-3294-03), move to it and check the highlight again.
- Expected:
  - The stepper shows three steps in this order: Upload & Check, Configure Tests, Review & Create, each with its icon as in the design. Upload & Check is highlighted on arrival and the other two look inactive. When the user moves to another step, only that step is highlighted.

### TC-DK26-3294-07: Footer shows Cancel, Back and Continue, with Continue disabled until the step is valid

- Jira: [DK26-3409](https://amali-tech.atlassian.net/browse/DK26-3409)
- Linked preconditions: PC-DK26-3294-01 (DK26-3416), PC-DK26-3294-02 (DK26-3417), PC-DK26-3294-03 (DK26-3418)
- Preconditions: Build deployed with the flag on; logged in as User A; a valid workbook available for upload.
- Steps:
  1. On the Upload & Check step with nothing uploaded, check the footer buttons and their state.
  2. Click Continue while it looks disabled.
  3. Upload a valid workbook and choose a domain, then check Continue again.
  4. Continue to Configure Tests and check the footer there, including Back.
- Expected:
  - The footer matches the design: Cancel and Continue on the first step, plus Back from the second step on. Continue is disabled and does nothing until the step is valid, then becomes enabled. Back on a later step returns to the previous step.

### TC-DK26-3294-08: Steps cannot be skipped forward

- Jira: [DK26-3410](https://amali-tech.atlassian.net/browse/DK26-3410)
- Linked preconditions: PC-DK26-3294-01 (DK26-3416), PC-DK26-3294-02 (DK26-3417)
- Preconditions: Build deployed with the flag on; logged in as User A; the Create from file page is open on Upload & Check with nothing uploaded.
- Steps:
  1. Click 'Configure Tests' and then 'Review & Create' in the stepper.
  2. If the steps have their own URLs or query parameters, open the Configure Tests and Review & Create URLs directly.
  3. Use the browser's forward button after having visited a later step and come back, if possible.
  4. Use the keyboard (Tab and Enter) on the stepper items.
- Expected:
  - The user stays on Upload & Check: clicking a later step in the stepper does nothing, or shows that the step is not yet available. Opening a later step's URL directly sends the user back to the first step that is not complete. No route or key press reaches Configure Tests or Review & Create before the earlier step is valid.

### TC-DK26-3294-09: Entered data is kept when moving Back and forward between steps

- Jira: [DK26-3411](https://amali-tech.atlassian.net/browse/DK26-3411)
- Linked preconditions: PC-DK26-3294-01 (DK26-3416), PC-DK26-3294-02 (DK26-3417), PC-DK26-3294-03 (DK26-3418)
- Preconditions: Build deployed with the flag on; logged in as User A; a valid workbook available and the later steps reachable.
- Steps:
  1. Upload a valid workbook, note the file name, size and counts, choose a domain, and click Continue.
  2. On Configure Tests, change the questions to be assigned and the time for one test and exclude another, then click Continue.
  3. On Review & Create, enter a title, instructions, pass mark and a tag.
  4. Click Back twice to return to Upload & Check, then click Continue twice to return to Review & Create.
  5. At each step on the way, check the values entered earlier. Also go back once using the stepper, if it allows going back.
- Expected:
  - Going Back and forward keeps everything entered. Upload & Check still shows the same file, size, counts and chosen domain with no new upload. Configure Tests keeps the changed values and the excluded test. Review & Create keeps the title, instructions, pass mark and tag. Nothing is reset or duplicated.

### TC-DK26-3294-10: No leave confirmation before a file is uploaded

- Jira: [DK26-3412](https://amali-tech.atlassian.net/browse/DK26-3412)
- Linked preconditions: PC-DK26-3294-01 (DK26-3416), PC-DK26-3294-02 (DK26-3417)
- Preconditions: Build deployed with the flag on; logged in as User A; the Create from file page is open with nothing uploaded.
- Steps:
  1. Click Cancel.
  2. Open Create from file again and click the Back link.
  3. Open Create from file again and click another item in the sidebar (for example Dashboard).
  4. Open Create from file again and click another Test Management tab (for example Questions).
  5. Open Create from file again and use the browser's back button.
- Expected:
  - Each action leaves the page straight away with no confirmation modal. Cancel and the Back link go to the Assessments list, and the sidebar, tab and browser back go where they normally would.

### TC-DK26-3294-11: Leaving after a file is uploaded asks for confirmation on every exit route

- Jira: [DK26-3413](https://amali-tech.atlassian.net/browse/DK26-3413)
- Linked preconditions: PC-DK26-3294-01 (DK26-3416), PC-DK26-3294-02 (DK26-3417), PC-DK26-3294-03 (DK26-3418)
- Preconditions: Build deployed with the flag on; logged in as User A; a valid workbook available for upload.
- Steps:
  1. Upload a valid workbook, then click Cancel and check the modal that appears.
  2. Choose to stay, then click the Back link.
  3. Choose to stay, then click a sidebar item.
  4. Choose to stay, then click another Test Management tab, and then use the browser's back button.
  5. Move to Configure Tests and repeat one exit there, for example a sidebar item.
- Expected:
  - After a file is uploaded, every exit (Cancel, the Back link, sidebar, another tab, browser back, from any step) opens a confirmation modal before leaving. The modal explains that the progress will be lost and offers a way to stay and a way to leave. Choosing to stay closes the modal and keeps the user on the same step with all data in place.

### TC-DK26-3294-12: Confirming leave discards the wizard and a new visit starts empty

- Jira: [DK26-3414](https://amali-tech.atlassian.net/browse/DK26-3414)
- Linked preconditions: PC-DK26-3294-01 (DK26-3416), PC-DK26-3294-02 (DK26-3417), PC-DK26-3294-03 (DK26-3418)
- Preconditions: Build deployed with the flag on; logged in as User A; a valid workbook available for upload.
- Steps:
  1. Upload a valid workbook, choose a domain and continue to Configure Tests.
  2. Click a sidebar item and confirm leaving in the modal.
  3. Check where the user lands.
  4. Go back to Assessments, choose 'Create from file' again and check the wizard.
  5. Check the Assessments list for any new or draft assessment.
- Expected:
  - Confirming leave goes to the chosen destination. Opening Create from file again starts fresh on Upload & Check with no file, domain or test settings from before, and no leave prompt until a new file is uploaded. No assessment or draft was created by the abandoned wizard.

### TC-DK26-3294-13: Dropdown, stepper and footer are usable at different widths, in dark mode and by keyboard

- Jira: [DK26-3415](https://amali-tech.atlassian.net/browse/DK26-3415)
- Linked preconditions: PC-DK26-3294-01 (DK26-3416), PC-DK26-3294-02 (DK26-3417)
- Preconditions: Build deployed with the flag on; logged in as User A.
- Steps:
  1. At 1440 px, about 1024 px and about 768 px wide, open the 'Create New Assessment' menu and the Create from file page.
  2. Turn on dark mode with the moon icon and check the menu, 'New' badge, stepper highlight, disabled Continue and leave modal.
  3. Using only the keyboard (Tab, Enter, Esc), open the menu, choose 'Create from file', reach the footer buttons and, after an upload, open and dismiss the leave modal.
  4. Check the browser console throughout.
- Expected:
  - At every width, the menu, stepper and footer fit on screen without overlapping or being cut off. In dark mode, all text, the badge, the active step and the disabled state are readable and distinct. The whole flow can be done by keyboard with a visible focus outline, the leave modal keeps focus inside it and Esc closes it. No console errors appear.
