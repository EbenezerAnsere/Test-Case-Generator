# Dark Mode — DK26-139 Test Cases

**User Story:** As a User, I want to switch to dark mode so that I can use the platform comfortably in low-light environments.

**Related Issue:** DK26-139

---

## Acceptance Criteria
- Toggle available in the user profile or header.
- Dark mode applies to:
  - Dashboard
  - Assessment screens
  - Admin pages
  - Modals and dialogs
- Dark mode respects accessibility standards (contrast ratio ≥ 4.5:1).
- User preference is stored and persists across sessions.
- Dark mode applies instantly without page reload.

---

## Test Cases for QA

| Mark | ID | Title | Preconditions | Steps | Expected Result |
| --- | --- | --- | --- | --- | --- |
| [ ] | TC-DM-001 | Enable dark mode from profile or header | User is logged in and on any page with the profile/header toggle visible | Open the user profile or header menu; locate the dark mode toggle; turn on dark mode | Dark mode activates immediately and the UI switches to dark theme without page reload |
| [ ] | TC-DM-002 | Verify dark mode on Dashboard | Dark mode is enabled | Navigate to the Dashboard | Dashboard renders in dark theme |
| [ ] | TC-DM-003 | Verify dark mode on Assessment screens | Dark mode is enabled | Navigate to an assessment screen | Assessment screen renders in dark theme |
| [ ] | TC-DM-004 | Verify dark mode on Admin pages | Dark mode is enabled | Navigate to an admin page | Admin page renders in dark theme |
| [ ] | TC-DM-005 | Verify dark mode on modals and dialogs | Dark mode is enabled | Open a modal or dialog from any page | Modal or dialog renders in dark theme |
| [ ] | TC-DM-006 | Verify accessibility contrast in dark mode | Dark mode is enabled | Inspect text, icons, buttons, and interactive elements across dark theme pages | UI elements remain readable and meet contrast ratio requirements |
| [ ] | TC-DM-007 | Persist dark mode after page refresh | Dark mode is enabled | Refresh the browser page | Dark mode remains enabled after the page refresh |
| [ ] | TC-DM-008 | Persist dark mode across sessions | Dark mode is enabled | Sign out and sign back in | Dark mode preference remains enabled after sign in |
| [ ] | TC-DM-009 | Disable dark mode | Dark mode is enabled | Open profile or header menu and turn off dark mode | UI switches back to light theme immediately and dark mode toggle is off |
