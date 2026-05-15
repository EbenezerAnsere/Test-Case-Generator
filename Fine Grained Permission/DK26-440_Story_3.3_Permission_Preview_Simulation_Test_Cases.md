# Story 3.3 — Permission Preview & Simulation Test Cases

**User Story:** As a tenant admin, I want to simulate a user's permissions so that I can verify correct access before assigning roles.

**Related Issue:** DK26-440

---

## Test Case 1: View Admin Dashboard - Permission Summary
**ID:** TC-3.3-001  
**Priority:** High  
**Status:** Not Started

### Preconditions
- User has Tenant Admin role
- Admin dashboard is accessible
- System contains users with various permissions
- User is authenticated

### Steps
1. Tenant admin navigates to Admin Dashboard
2. Clicks on "Permission Management" section
3. Views the permission overview

### Expected Results
- Dashboard displays:
  - Total number of unique permissions in system
  - Total number of roles created
  - Total number of users with assigned roles
  - Permission distribution chart (breakdown by resource)
  - Recent permission changes (last 7 days)
  - Users with most permissions
  - Unused/rarely-used permissions
- Information is up-to-date and accurate
- Dashboard is responsive and loads quickly

### Postconditions
- Admin gains overview of permission usage across system

---

## Test Case 2: View Specific User's Effective Permissions
**ID:** TC-3.3-002  
**Priority:** High  
**Status:** Not Started

### Preconditions
- User "john_smith" exists with assigned roles
- John's roles include: "Question Editor", "Test Manager"
- These roles contain various permissions
- Tenant admin is authenticated

### Steps
1. Tenant admin navigates to "Manage Users" section
2. Searches for and selects user "john_smith"
3. Clicks "View Permissions" or "View Effective Permissions"
4. Views the complete permission matrix for john_smith

### Expected Results
- Page displays:
  - User name: john_smith
  - Assigned roles: "Question Editor", "Test Manager"
  - Complete list of effective permissions grouped by resource:
    - **User Management:** [list of permissions and their status]
    - **Test Management:**
      - Domain: [permissions]
      - Questions: [permissions]
      - Tests: [permissions]
      - Assessments: [permissions]
    - **Reports Management:** [permissions]
    - **Skills Management:** [permissions]
  - Each permission shows:
    - Permission name
    - Status (✓ Granted)
    - Source (from which role)
    - Last updated date
- Permissions are organized clearly and logically

### Postconditions
- Admin can verify user has correct permissions before assigning new roles

---

## Test Case 3: Simulation Mode - Add Role and Preview Changes
**ID:** TC-3.3-003  
**Priority:** High  
**Status:** Not Started

### Preconditions
- Tenant admin is viewing user "jane_doe"'s current permissions
- Jane currently has role: "Viewer"
- A new role "Domain Manager" is available
- Simulation mode is accessible

### Steps
1. Tenant admin enters simulation mode (button: "Simulate Permission Changes")
2. Currently assigned role "Viewer" is shown with its permissions
3. Admin selects additional role "Domain Manager" to assign
4. System shows preview of changes
5. Admin clicks "What if?" or "Preview Changes" button

### Expected Results
- Simulation mode activates (indicated by banner: "Simulation Mode - Changes are not saved")
- Original permissions from "Viewer" role are displayed
- Preview shows:
  - Current permissions (from "Viewer")
  - New permissions (from "Domain Manager")
  - **Added permissions:** (highlighted in green)
    - Create Domain
    - Edit Domain
    - Delete Domain
    - View Domain Settings
  - Combined effective permissions after role assignment
  - No duplicate permissions in the combined list
- Changes are NOT applied to the actual user

### Postconditions
- Admin can exit simulation without saving
- Admin can save changes if satisfied
- Original user permissions remain unchanged during simulation

---

## Test Case 4: Simulation Mode - Remove Role and Preview Changes
**ID:** TC-3.3-004  
**Priority:** High  
**Status:** Not Started

### Preconditions
- Tenant admin is in simulation mode viewing user "michael_brown"
- Michael currently has roles: "Assessment Creator", "Report Viewer"
- Simulation mode is active
- Admin wants to remove "Assessment Creator" role

### Steps
1. In simulation mode, admin views Michael's current roles
2. Admin selects "Assessment Creator" role
3. Admin clicks "Remove Role" or unchecks the role
4. System shows preview of permission changes

### Expected Results
- Simulation preview displays:
  - Original permissions before removal
  - **Removed permissions:** (highlighted in red)
    - Create Assessment
    - Edit Assessment
    - Delete Assessment
    - Schedule Assessment
  - Remaining permissions after removal (from "Report Viewer" role)
  - Clear visual indication of what will be lost
  - List of conflicting features that may not work:
    - "Create Assessment" button will be disabled
    - Assessment management will be read-only
- Warnings are displayed for critical permission removals

### Postconditions
- Admin can confirm removal or cancel simulation
- Original user permissions unchanged until confirmed

---

## Test Case 5: Simulation Mode - Highlight Conflicting Permissions
**ID:** TC-3.3-005  
**Priority:** High  
**Status:** Not Started

### Preconditions
- Tenant admin is simulating permission assignment for user "sarah_jones"
- Simulation involves assigning multiple roles that may have conflicts
- System is configured to detect permission conflicts
- Simulation mode is active

### Steps
1. Admin selects multiple roles for sarah_jones:
   - "Test Editor" (includes: Create Test, Edit Test, Publish Test)
   - "Test Approver" (includes: Approve Test, Edit Test)
2. System analyzes combined permissions for conflicts
3. Admin views the conflict report

### Expected Results
- Simulation preview shows conflicts:
  - **Duplicate Permissions:** (highlighted in yellow)
    - Edit Test (exists in both roles - system consolidates to single permission)
  - **Potential Conflicts:**
    - Publish Test: Only in "Test Editor"
    - Approve Test: Only in "Test Approver"
    - Workflow consideration: "Approver" typically shouldn't edit what they approve
  - Warning message: "User will have both Edit and Approve permissions on Tests. This may create approval conflicts."
  - Recommendation: "Consider separating these roles or creating a specialized role."
- Detailed conflict explanation is provided

### Postconditions
- Admin is informed of potential issues
- Admin can proceed, modify, or cancel the simulation

---

## Test Case 6: Simulation Mode - Permission Overrides
**ID:** TC-3.3-006  
**Priority:** Medium  
**Status:** Not Started

### Preconditions
- Tenant admin is simulating permissions for user "alex_kumar"
- Organizational policy states: "Only Admins can delete domains"
- Role "Domain Manager" includes "Delete Domain" permission
- System has permission override rules configured

### Steps
1. Admin enters simulation mode for alex_kumar
2. Admin assigns "Domain Manager" role
3. System checks for permission overrides
4. Admin reviews override warnings

### Expected Results
- Simulation shows:
  - "Delete Domain" permission would be granted
  - **Override Alert:** "WARNING - Permission 'Delete Domain' violates organizational policy"
  - Policy rule: "Only Admin role should have Delete Domain permission"
  - Current user would have: "Domain Manager" (not Admin)
  - Recommendation: "Assign 'Admin' role instead or create custom role"
- Admin can:
  - Cancel assignment
  - Override the policy (with audit log)
  - Modify role assignment
- Clear reasoning is provided

### Postconditions
- Admin makes informed decision about override
- Override decision is logged if approved

---

## Test Case 7: Preview User Access - Full Feature Walkthrough
**ID:** TC-3.3-007  
**Priority:** High  
**Status:** Not Started

### Preconditions
- Tenant admin wants to preview user "diana_wilson"'s actual system access
- Diana has role "Question Editor"
- System access simulation is available

### Steps
1. Admin navigates to "User Permission Preview"
2. Selects user "diana_wilson"
3. Clicks "Preview User Access" or "Simulate User View"
4. System simulates Diana's view of the system
5. Admin walks through different system sections

### Expected Results
- Simulation shows:
  - Dashboard as Diana would see it (only accessible features)
  - **Question Management:** Visible (Diana has Create Question, Edit Question)
    - "Create Question" button is visible and enabled
    - "Edit Question" button is visible and enabled
    - "Delete Question" button is HIDDEN (not in role)
  - **Domain Management:** HIDDEN or DISABLED (Diana doesn't have permissions)
  - **Test Management:** Visible (Diana has Create Test)
  - **Reports:** HIDDEN (Diana doesn't have view permission)
  - **Skills Management:** HIDDEN
  - Navigation menu shows only accessible sections
  - Confirmation: "This preview shows exactly what diana_wilson will see and be able to do in the system"

### Postconditions
- Admin verifies feature access matches expectations
- Admin can identify missing or excess permissions

---

## Test Case 8: Effective Permissions Report
**ID:** TC-3.3-008  
**Priority:** Medium  
**Status:** Not Started

### Preconditions
- Tenant admin wants to generate a permission report
- Users exist with various role assignments
- Report generation feature is available

### Steps
1. Admin navigates to "Reports" > "Permission Reports"
2. Selects "Effective Permissions Report"
3. Applies filters:
   - User role: "Test Manager"
   - Resource: "Test Management"
   - Status: "Active"
4. Generates report

### Expected Results
- Report displays:
  - Title: "Effective Permissions Report"
  - Filters applied: User role = Test Manager, Resource = Test Management, Status = Active
  - Table with columns:
    - User Name
    - User Email
    - Primary Role
    - Secondary Roles
    - Permission: Create Test
    - Permission: Edit Test
    - Permission: Delete Test
    - Permission: Conduct Test
    - Permission: View Test Results
    - Last Updated
  - Summary statistics:
    - Total users in report: 23
    - Total permissions analyzed: 115
    - Average permissions per user: 5
  - Data can be exported as CSV or PDF
  - Report is sortable and filterable

### Postconditions
- Admin can analyze permission distribution
- Report can be used for compliance audits

---

## Test Case 9: Permission Simulation - Cross-Tenant Verification
**ID:** TC-3.3-009  
**Priority:** Medium  
**Status:** Not Started

### Preconditions
- System is multi-tenant
- Tenant Admin for "Organization A" is logged in
- Attempting to view user from "Organization B"
- System has cross-tenant data isolation

### Steps
1. Tenant Admin logs into "Organization A"
2. Attempts to access user "Organization B"'s user details
3. Attempts to simulate permissions for that user

### Expected Results
- Request is DENIED
- Message: "You don't have permission to view other organization's users"
- User is redirected to Organization A's user list
- No data from Organization B is visible
- Action is logged in security audit trail

### Postconditions
- Data isolation between tenants is maintained
- Tenant admins cannot access other organizations' data

---

## Test Case 10: Simulation Mode - Role Hierarchy Display
**ID:** TC-3.3-010  
**Priority:** Medium  
**Status:** Not Started

### Preconditions
- Tenant admin is simulating permissions
- System has defined role hierarchy:
  - Super Admin > Admin > Manager > Editor > Viewer
- Role inheritance is configured

### Steps
1. Admin enters simulation mode for a user
2. Admin views role hierarchy diagram
3. Selects "Editor" role to assign
4. System shows inherited permissions

### Expected Results
- Hierarchy diagram shows:
  - Parent role: "Editor"
  - Inherited from: "Viewer" role
  - Specific permissions for "Editor" role
  - Inherited permissions from "Viewer":
    - View Question
    - View Test
    - View Assessment
    - View Reports
  - Custom permissions for "Editor":
    - Create Question
    - Edit Question
    - Create Test
  - Total effective permissions = inherited + custom
- Clear visual representation of hierarchy

### Postconditions
- Admin understands permission inheritance
- Admin can make informed role decisions

---

## Test Case 11: Permission Conflict Detection - Same Permission from Multiple Roles
**ID:** TC-3.3-011  
**Priority:** Medium  
**Status:** Not Started

### Preconditions
- User simulation is in progress
- Admin is assigning multiple roles to user "robert_johnson"
- Both "Assessment Creator" and "Assessment Manager" roles include "Edit Assessment" permission

### Steps
1. Admin selects both roles: "Assessment Creator" and "Assessment Manager"
2. System analyzes permission overlap
3. Admin reviews the consolidated permissions

### Expected Results
- Simulation displays:
  - **Role 1 - Assessment Creator:**
    - Create Assessment
    - Edit Assessment
    - View Assessment
  - **Role 2 - Assessment Manager:**
    - Edit Assessment
    - Delete Assessment
    - Manage Assessment Workflow
  - **Consolidated Effective Permissions:**
    - Create Assessment ✓
    - Edit Assessment ✓ (consolidated - appears only once)
    - View Assessment ✓
    - Delete Assessment ✓
    - Manage Assessment Workflow ✓
  - Note: "No duplicate permissions - Edit Assessment is consolidated"
  - Total unique permissions: 5 (not 6)

### Postconditions
- Admin sees clear, non-duplicative permission list
- No confusion from permission duplication

---

## Test Case 12: Simulation Results - Save as New Role Template
**ID:** TC-3.3-012  
**Priority:** Low  
**Status:** Not Started

### Preconditions
- Tenant admin has completed a successful permission simulation
- Resulting permission set is useful for multiple users
- Simulation mode is completed with satisfactory results

### Steps
1. Admin reviews final simulated permissions
2. Admin clicks "Save as New Role Template"
3. Enters role name: "Advanced Question Manager"
4. Enters description: "Manages questions and their properties with full control"
5. Clicks "Save"

### Expected Results
- New role is created with the exact permission set from simulation
- Role name: "Advanced Question Manager"
- Role description: as provided
- Role status: "Active"
- All simulated permissions are assigned to new role
- Confirmation message: "Role created successfully. You can now assign this role to users."
- New role appears in role management list

### Postconditions
- Reusable role template is created
- Future permission assignments can use this role
- Time saved on repeated role creation

---

## Test Case 13: Simulation - Compare Two Users' Permissions
**ID:** TC-3.3-013  
**Priority:** Medium  
**Status:** Not Started

### Preconditions
- Tenant admin wants to compare permissions between two users
- User 1: "emma_davis" - Current permissions set A
- User 2: "frank_miller" - Current permissions set B
- Permission comparison feature is available

### Steps
1. Admin navigates to "Manage Users"
2. Selects User 1 (emma_davis)
3. Clicks "Compare Permissions"
4. Selects User 2 (frank_miller) to compare against
5. Views comparison

### Expected Results
- Comparison matrix displays:
  - **Permission Name | emma_davis | frank_miller | Difference**
  - View Question | ✓ | ✓ | (same)
  - Create Question | ✓ | ✗ | emma_davis has
  - Edit Question | ✓ | ✓ | (same)
  - Delete Question | ✗ | ✓ | frank_miller has
  - Publish Question | ✗ | ✗ | (neither has)
  - [additional permissions listed]
  - Summary:
    - Permissions only emma_davis has: 3
    - Permissions only frank_miller has: 2
    - Shared permissions: 12
- Differences highlighted in color (green for included, red for excluded)
- Useful for identifying permission gaps

### Postconditions
- Admin can quickly identify permission differences
- Admin can align permissions across similar users

---

## Test Case 14: Audit Trail - Permission Simulation Changes
**ID:** TC-3.3-014  
**Priority:** Medium  
**Status:** Not Started

### Preconditions
- Tenant admin has completed permission simulations
- Audit logging is configured
- Admin commits simulated changes

### Steps
1. Admin completes simulation for user "grace_lee"
2. Admin clicks "Apply Changes" to confirm simulation
3. Check audit log for the changes

### Expected Results
- Audit log records:
  - Action: "PERMISSION_SIMULATION_APPLIED"
  - Admin User: "admin_user_id"
  - Target User: "grace_lee" (user_id_456)
  - Timestamp: Current date/time
  - Changes Made:
    - Added Role: "Test Manager"
    - Added Permissions: [list]
    - Removed Permissions: [list]
  - Simulation Review Time: 5 minutes
  - Admin Comment/Reason: "User promotion to Test Manager role"
  - Status: "SUCCESS"
- Entry is immutable and tamper-evident

### Postconditions
- Complete audit trail of simulations and actual changes
- Accountability for permission modifications

---

## Test Case 15: Simulation Timeout - Session Expiry
**ID:** TC-3.3-015  
**Priority:** Low  
**Status:** Not Started

### Preconditions
- Tenant admin has started a permission simulation
- Admin is on the simulation screen
- Simulation timeout is set to 30 minutes
- No activity from admin for 35 minutes

### Steps
1. Admin enters simulation mode
2. Admin reviews permissions (takes 35 minutes)
3. System detects inactivity
4. Session expires

### Expected Results
- After 30 minutes of inactivity:
  - Notification appears: "Simulation session will expire in 5 minutes due to inactivity"
  - Admin can click "Continue Session" to extend
  - If no action taken:
    - Simulation is cancelled
    - No changes are saved
    - Admin is redirected to user list
    - Message: "Simulation session has expired. Please start over if needed."
- If "Continue Session" is clicked:
  - Session is extended for another 30 minutes
  - Work is preserved

### Postconditions
- Inactive sessions are automatically terminated
- Security and resource protection

---

## Summary of Test Cases
- **Total Test Cases:** 15
- **High Priority:** 8
- **Medium Priority:** 6
- **Low Priority:** 1

**Coverage Areas:**
- ✓ Admin Dashboard and Overview
- ✓ View Effective Permissions
- ✓ Simulation Mode (Add/Remove Roles)
- ✓ Conflict Detection
- ✓ Permission Overrides
- ✓ User Access Preview
- ✓ Permission Reports
- ✓ Role Hierarchy
- ✓ Permission Comparison
- ✓ Audit Trails
- ✓ Security (Cross-tenant, Session Management)

**Key Features Tested:**
- Permission preview before assignment
- What-if scenario analysis
- Conflict and override detection
- Role comparison and templates
- Comprehensive audit logging
- Multi-tenant security
- Session management
