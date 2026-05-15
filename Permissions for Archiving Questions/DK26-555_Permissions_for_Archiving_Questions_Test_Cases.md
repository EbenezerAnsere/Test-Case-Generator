# DK26-555: Permissions for Archiving Questions

Ticket: https://amali-tech.atlassian.net/browse/DK26-555
Status: In Progress QA

## Review Summary

This story is focused on permission-based access to the archive question action. The key objective is to ensure only authorized users can archive questions, and that permission changes take effect without leaving stale access.

## Test Plan

- Goal: Confirm archive question functionality is available only to permitted users.
- Scope: UI visibility, action enablement, backend enforcement, and permission lifecycle behavior.
- Test set: Permissions for Archiving Questions
- Environment: QA or staging environment with configurable user roles/permissions.
- Preconditions:
  - A question exists for archiving.
  - `User A` has the archive permission.
  - `User B` does not have the archive permission.

## Test Cases

### TC-DK26-555-01: Archive Question with Permission

- Objective: Validate a permitted user can archive a question successfully.
- Steps:
  1. Log in as `User A`.
  2. Open an active question details page.
  3. Confirm the "Archive" control is visible and enabled.
  4. Click "Archive" and confirm if prompted.
- Expected:
  - Successful archive confirmation appears.
  - The question is moved to archived status or removed from active lists.
  - A success message appears.
  - Any relevant audit record logs the archive by `User A`.

### TC-DK26-555-02: Archive Action Hidden for Unauthorized User

- Objective: Verify unauthorized users cannot access the archive action.
- Steps:
  1. Log in as `User B`.
  2. Open the same or another question details page.
  3. Look for the archive action in UI controls and menus.
- Expected:
  - The archive action is not visible or is disabled.
  - The user cannot trigger an archive operation.
  - If the action is somehow accessible, the system returns an authorization failure.

### TC-DK26-555-03: Permission Change Applies Immediately

- Objective: Confirm permission updates change archive access immediately.
- Steps:
  1. Log in as an admin or permission manager.
  2. Grant `User B` the archive permission.
  3. Log in as `User B`, refresh the page, and verify the archive action is visible.
  4. Revoke the archive permission from `User B`.
  5. Refresh again and verify the archive action is no longer available.
- Expected:
  - Granting permission immediately enables archive access.
  - Revoking permission immediately removes access.
  - No residual archive ability remains after revoke.

## Critical Edge Cases

- EC-1: Attempt to archive an already archived question.
  - Expected: System prevents the action and shows an appropriate state/error.
- EC-2: User gains permission but uses an old page session.
  - Expected: Refresh or relogin updates UI state and proper access is applied.
- EC-3: User loses permission mid-session.
  - Expected: After refresh, the archive option disappears and the action is blocked.

## Notes for Review

- These cases are intentionally limited to three core scenarios plus a few edge cases.
- Execution should focus on permission correctness, not exhaustive UI permutations.
- If acceptance criteria include a specific label, role, or policy name, substitute the generic "Archive Questions" permission with that exact permission name.
