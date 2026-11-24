# DK26-3301: FE - 4.6.8: Create from File – Review & Create (details, settings, summary)

Ticket: https://amali-tech.atlassian.net/browse/DK26-3301
Type: Task
Status: In Progress QA
Parent: DK26-3146 Epic 4; part of DK26-3220 FE - Story 4.6: Create an Assessment from File
Design: Figma 'Review & Create'
Xray folder: `Quarter 4/Ebenezer/Frontend/DK26-3301 FE - 4.6.8: Create from File – Review & Create (details, settings, summary)`
Test Set: DK26-3629
Test Plan: DK26-3106
Test Execution: DK26-3107
Companion set: DK26-3600 (fred.pekyi, linked to DK26-3301): DK26-3594 to DK26-3597, preconditions DK26-3598 and DK26-3599

## Review Summary

Review & Create is the last step of the Create from File wizard. It has:

- Basic Information: Assessment Title*, Assessment Instructions* (the same rich text editor as manual creation), Pass Mark* and optional Tags.
- The security and other settings, reused from manual creation with the same defaults and validation.
- A sticky Summary: Domain, Tests, Questions per candidate, Duration, Pass mark, questions Added to the bank, and a 'Review Tests' link back to Configure Tests.
- Back and Create Assessment buttons.

fred.pekyi's set DK26-3600 already tests the four acceptance criteria at a basic level: required fields against manual (DK26-3594), settings and defaults against manual (DK26-3595), the summary (DK26-3596), and values kept on Back and forward (DK26-3597). To avoid duplicating them, this set adds only what they leave out:

- Full field validation: pass-mark boundaries and formats (TC-01), title blanks, length and special characters (TC-02), rich-text formatting and unsafe content in instructions (TC-03), and tags (TC-04).
- Settings reaching the created assessment, now that Create (DK26-3302) is Done (TC-05). Defaults coming from the organisation's Proctoring Settings (TC-06). Dependent options (TC-07).
- Harder summary cases: existing questions included from the domain not counted as 'Added to the bank', and excluded tests (TC-08). A new domain's name, and a domain changed on an earlier step (TC-09). The Review Tests link and the sticky sidebar (TC-10).
- Keyboard, widths and dark mode (TC-11).

Note: linking these tests to fred's preconditions DK26-3598 and DK26-3599 was not done, because those issues belong to another person. PC-DK26-3301-01 (DK26-3628) refers to them in its definition instead.

## Acceptance Criteria Coverage

| Acceptance criterion | This set | fred.pekyi's set (DK26-3600) |
| --- | --- | --- |
| Required field validation matches manual creation. | TC-01, TC-02, TC-03, TC-04 | DK26-3594 |
| Settings are identical to manual creation (shared components, no duplication). | TC-05, TC-06, TC-07 | DK26-3595 |
| Summary reflects wizard state accurately. | TC-08, TC-09, TC-10 | DK26-3596 |
| Values preserved on Back/forward. | TC-09, TC-10 | DK26-3597 |
| Quality: keyboard, widths, dark mode | TC-11 | — |

## Preconditions (Xray Precondition issues)

### PC-DK26-3301-01: Reference data for Review & Create settings and summary checks

- Jira: [DK26-3628](https://amali-tech.atlassian.net/browse/DK26-3628)

1. fred.pekyi's preconditions also apply: DK26-3598 (Organisation Admin can reach Review & Create, and the manual flow is deployed) and DK26-3599 (a valid two-sheet workbook with pools of 4 and 3).
2. A domain exists with a category whose name matches a category in the workbook, so existing questions can be included on Configure Tests. Its number of existing questions in that category is noted.
3. The organisation's defaults on Settings > Proctoring Settings are noted (enabled features, intervals, severity band), so defaults can be compared.
4. A reference assessment has been created through the manual flow, with known settings, to compare against.
5. Create Assessment works on staging (DK26-3302 is Done), so created assessments can be opened and checked.

## Test Cases

### TC-DK26-3301-01: Pass mark accepts whole numbers from 1 to 100 only, as in manual creation

- Jira: [DK26-3617](https://amali-tech.atlassian.net/browse/DK26-3617)
- Linked preconditions: PC-DK26-3301-01 (DK26-3628); also DK26-3598 and DK26-3599 (fred.pekyi)
- Preconditions: Organisation Admin on Review & Create after uploading a valid workbook (DK26-3598, DK26-3599).
- Steps:
  1. Enter each of these pass marks in turn and read the result: 0, 1, 100, -5, 50.5, 'abc', and ' 70 ' with spaces.
  2. Check whether Create Assessment is available after each value.
  3. Enter the same values in the manual Create New Assessment flow and compare.
- Expected:
  - Only whole numbers from 1 to 100 are accepted. 1 and 100 are valid, while 0, negative numbers, decimals and letters are refused with a clear message (the contract's message is 'Pass mark must be a whole number from 1 to 100'), or cannot be typed at all. Spaces are trimmed. The behaviour and messages match the manual flow.

### TC-DK26-3301-02: Assessment title rejects blanks and over-long text and keeps special characters

- Jira: [DK26-3618](https://amali-tech.atlassian.net/browse/DK26-3618)
- Linked preconditions: PC-DK26-3301-01 (DK26-3628); also DK26-3598 and DK26-3599 (fred.pekyi)
- Preconditions: Organisation Admin on Review & Create after uploading a valid workbook.
- Steps:
  1. Enter a title made only of spaces and try to continue to Create.
  2. Enter a title longer than the manual flow's limit (for example 300 characters).
  3. Enter a title with special characters, such as 'C# & .NET "Basics" – Level 2', and create the assessment.
  4. Open the created assessment and compare its title.
- Expected:
  - A title of only spaces is treated as empty and shows the required message. The maximum length is enforced as in the manual flow, either by stopping typing or with a message. Special characters are saved and shown exactly as typed, with surrounding spaces trimmed.

### TC-DK26-3301-03: Assessment instructions keep their formatting, and empty or unsafe content is handled

- Jira: [DK26-3619](https://amali-tech.atlassian.net/browse/DK26-3619)
- Linked preconditions: PC-DK26-3301-01 (DK26-3628); also DK26-3598 and DK26-3599 (fred.pekyi)
- Preconditions: Organisation Admin on Review & Create after uploading a valid workbook.
- Steps:
  1. In the instructions editor, add only empty lines (press Enter a few times) and try to create.
  2. Write instructions with bold, italic, a bulleted list, a numbered list and a link.
  3. Paste in text containing '<script>alert(1)</script>' and an image tag with an onerror handler.
  4. Create the assessment, then open its preview and the candidate's instructions page.
- Expected:
  - Instructions with only empty lines count as empty and show the required message, as in the manual flow. Bold, italic, lists and links are saved and shown as formatted on the preview and the candidate page. Script and event-handler content is not run anywhere: it is removed or shown as plain text. The editor is the same one used in manual creation.

### TC-DK26-3301-04: Tags can be added and removed as in manual creation

- Jira: [DK26-3620](https://amali-tech.atlassian.net/browse/DK26-3620)
- Linked preconditions: PC-DK26-3301-01 (DK26-3628); also DK26-3598 and DK26-3599 (fred.pekyi)
- Preconditions: Organisation Admin on Review & Create after uploading a valid workbook; at least one tag already exists in the organisation.
- Steps:
  1. Add a new tag, an existing tag (check whether it is suggested), and the same tag twice.
  2. Add a tag in different capitals from an existing one, and one with spaces around it.
  3. Remove one tag.
  4. Create the assessment and check its tags on the preview and in the Assessments list filter.
- Expected:
  - Tags behave as in manual creation: existing tags are suggested, duplicates are not added twice, spaces are trimmed, and removed tags are not saved. The created assessment carries exactly the tags shown at Create, and can be found by those tags.

### TC-DK26-3301-05: The created assessment carries exactly the settings chosen on Review & Create

- Jira: [DK26-3621](https://amali-tech.atlassian.net/browse/DK26-3621)
- Linked preconditions: PC-DK26-3301-01 (DK26-3628); also DK26-3598 and DK26-3599 (fred.pekyi)
- Preconditions: Organisation Admin on Review & Create; Create Assessment works on staging; a manually created reference assessment is available.
- Steps:
  1. On Review & Create, turn on Honour Code, ID Capture, Candidate Capture (choose an interval), Screen Capture (choose an interval), Track Idle Time, Track Window Violation, Copy & paste detection and Suspicious typing. Choose a severity band, turn on the survey and set a retake delay.
  2. Create the assessment.
  3. Open the created assessment's preview and its edit settings.
  4. Compare each setting with what was chosen, and with the reference assessment created manually with the same choices.
- Expected:
  - Every setting chosen on Review & Create is saved on the created assessment, including the capture intervals, severity band, survey and retake delay. They are shown the same way as on the manually created reference. No setting is lost, reset to its default or changed.

### TC-DK26-3301-06: Settings defaults follow the organisation's Proctoring Settings, as in manual creation

- Jira: [DK26-3622](https://amali-tech.atlassian.net/browse/DK26-3622)
- Linked preconditions: PC-DK26-3301-01 (DK26-3628); also DK26-3598 and DK26-3599 (fred.pekyi)
- Preconditions: Organisation Admin; the organisation's Proctoring Settings defaults are noted.
- Steps:
  1. Open Review & Create in a fresh wizard and note the defaults of every security and other setting.
  2. Open the manual flow and note its defaults.
  3. Change one default on Settings > Proctoring Settings (for example the screen capture interval), start a new Create from File wizard and check the setting again.
  4. Put the Proctoring Settings default back.
- Expected:
  - Review & Create starts with the same defaults as the manual flow, taken from the organisation's Proctoring Settings. After the organisation default is changed, a new wizard starts with the new value, just as the manual flow does.

### TC-DK26-3301-07: Dependent settings show and hide their options as in manual creation

- Jira: [DK26-3623](https://amali-tech.atlassian.net/browse/DK26-3623)
- Linked preconditions: PC-DK26-3301-01 (DK26-3628); also DK26-3598 and DK26-3599 (fred.pekyi)
- Preconditions: Organisation Admin on Review & Create after uploading a valid workbook.
- Steps:
  1. Turn Candidate Capture and Screen Capture on and off and watch their interval options.
  2. Turn Suspicious typing on and off and watch the proctoring severity options.
  3. Turn the retake option on and set the delay to its minimum, below the minimum, and empty.
  4. Do the same in the manual flow and compare.
- Expected:
  - Turning a setting on shows its options, and turning it off hides them so they are not saved. Required sub-options are validated with the same messages and limits as the manual flow. Nothing appears on one flow that is missing on the other.

### TC-DK26-3301-08: Summary counts only new questions as added to the bank and totals only included tests

- Jira: [DK26-3624](https://amali-tech.atlassian.net/browse/DK26-3624)
- Linked preconditions: PC-DK26-3301-01 (DK26-3628); also DK26-3598 and DK26-3599 (fred.pekyi)
- Preconditions: Organisation Admin; a domain has a category matching a workbook category, with a known number of existing questions.
- Steps:
  1. Upload the workbook, choose the domain with the matching category and continue.
  2. On Configure Tests, include existing questions for the matching test and exclude one other test. Note each test's pool, questions to be assigned and time.
  3. Continue to Review & Create and read every line of the Summary.
  4. Calculate the expected values by hand and compare.
- Expected:
  - Domain shows the chosen domain's name. Tests counts only the included tests. Questions per candidate is the sum of 'questions to be assigned' over included tests. Duration is the sum of their times, in a readable format such as '1 hr 15 mins'. 'Added to the bank' counts only the new questions from the file, not the existing ones included from the domain, and not the excluded test's questions. Pass mark matches Basic Information.

### TC-DK26-3301-09: Summary shows a new domain's name, and follows a domain change made on an earlier step

- Jira: [DK26-3625](https://amali-tech.atlassian.net/browse/DK26-3625)
- Linked preconditions: PC-DK26-3301-01 (DK26-3628); also DK26-3598 and DK26-3599 (fred.pekyi)
- Preconditions: Organisation Admin; a valid workbook.
- Steps:
  1. Upload the workbook, choose Create a new domain with a unique name, and continue to Review & Create.
  2. Read the Summary's Domain line.
  3. Go Back to Upload & Check, switch to an existing domain, and continue to Review & Create again.
  4. Read the Summary, and check that the Basic Information and settings entered before are kept.
- Expected:
  - The Summary shows the new domain's name (marked as new, if the design does so). After switching to an existing domain on the earlier step, the Summary shows that domain, and any counts that depend on it are updated. The title, instructions, pass mark, tags and settings already entered on Review & Create are kept.

### TC-DK26-3301-10: Review Tests link returns to Configure Tests, and the sticky summary stays visible

- Jira: [DK26-3626](https://amali-tech.atlassian.net/browse/DK26-3626)
- Linked preconditions: PC-DK26-3301-01 (DK26-3628); also DK26-3598 and DK26-3599 (fred.pekyi)
- Preconditions: Organisation Admin on Review & Create after uploading a valid workbook.
- Steps:
  1. Scroll down through the long security settings section and watch the Summary sidebar.
  2. Click 'Review Tests' in the Summary.
  3. On Configure Tests, change one test's time and continue.
  4. Check the Summary and the stepper.
- Expected:
  - The Summary sidebar stays in view while scrolling, without covering the form. 'Review Tests' opens Configure Tests with its values intact, and the stepper highlights that step. After continuing, the Summary's duration reflects the change, and the Review & Create values are unchanged.

### TC-DK26-3301-11: Review & Create is usable by keyboard, at different widths and in dark mode

- Jira: [DK26-3627](https://amali-tech.atlassian.net/browse/DK26-3627)
- Linked preconditions: PC-DK26-3301-01 (DK26-3628); also DK26-3598 and DK26-3599 (fred.pekyi)
- Preconditions: Organisation Admin on Review & Create after uploading a valid workbook.
- Steps:
  1. Using only the keyboard, fill in every Basic Information field, including the rich text editor and tags, toggle settings, and reach Back and Create Assessment.
  2. Check that required fields and error messages are announced by a screen reader.
  3. View the step at 1440 px, about 1024 px and about 768 px wide, and check where the Summary sidebar goes.
  4. Turn on dark mode and check the form, the settings toggles, the rich text editor and the Summary.
- Expected:
  - Every field and setting can be used by keyboard with a visible focus outline. Required markers and errors are announced. At narrower widths the Summary moves below or above the form, or stays readable, without overlapping fields. In dark mode all text, toggles, the editor content and the Summary are readable.
