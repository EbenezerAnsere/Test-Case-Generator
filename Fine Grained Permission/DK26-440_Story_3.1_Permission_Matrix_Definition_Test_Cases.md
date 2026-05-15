# Story 3.1 — Permission Matrix Definition Test Cases

**User Story:** As a platform architect, I want a complete list of granular permissions so that the system can support modular growth.

**Related Issue:** DK26-440

---

## Test Case 1: Create New Permission
**ID:** TC-3.1-001  
**Priority:** High  
**Status:** Not Started

### Preconditions
- User has platform architect role
- Permission management interface is accessible
- No duplicate permission exists with the same name

### Steps
1. Navigate to Permission Management screen
2. Click "Create New Permission" button
3. Enter permission name: "View Reports"
4. Select resource group: "Reports Management"
5. Enter description: "Allows users to view generated reports"
6. Set status: "Active"
7. Click "Save" button

### Expected Results
- Permission is successfully created with unique ID
- Permission appears in the permission list
- Status shows "Active"
- Confirmation message displayed: "Permission created successfully"
- Permission is immediately available for role assignment

### Postconditions
- New permission is stored in the database
- Audit log records the creation with timestamp and creator

---

## Test Case 2: Read/View Permission Details
**ID:** TC-3.1-002  
**Priority:** High  
**Status:** Not Started

### Preconditions
- Multiple permissions exist in the system
- User has platform architect role

### Steps
1. Navigate to Permission Management screen
2. View list of all permissions
3. Click on permission "Create Question"
4. View permission details panel

### Expected Results
- Permission list displays all permissions with:
  - Permission name
  - Resource group
  - Status (Active/Inactive)
  - Creation date
  - Last modified date
- Details panel shows:
  - Full permission name
  - Resource group assignment
  - Description
  - Current status
  - Assigned roles (if any)
  - Usage statistics

### Postconditions
- No changes made to the permission
- User can navigate back to list

---

## Test Case 3: Update Permission Details
**ID:** TC-3.1-003  
**Priority:** High  
**Status:** Not Started

### Preconditions
- Permission "Edit Questions" exists and is Active
- User has platform architect role
- No other permissions have the same new name

### Steps
1. Navigate to Permission Management
2. Search for permission "Edit Questions"
3. Click edit button
4. Update description to "Allows users to modify question content and settings"
5. Click "Save" button

### Expected Results
- Permission details are updated successfully
- Updated description is displayed in the permission list
- Confirmation message: "Permission updated successfully"
- Change timestamp is recorded
- All existing role assignments remain intact

### Postconditions
- Permission change is logged in audit trail
- Affected roles still have the updated permission

---

## Test Case 4: Delete Permission (Active)
**ID:** TC-3.1-004  
**Priority:** Medium  
**Status:** Not Started

### Preconditions
- Permission "Archive Assessment" exists with 0 role assignments
- User has platform architect role

### Steps
1. Navigate to Permission Management
2. Search for permission "Archive Assessment"
3. Click delete button
4. Confirm deletion in popup dialog

### Expected Results
- Permission is deleted from the system
- Confirmation message displayed
- Permission no longer appears in permission list
- System shows success notification

### Postconditions
- Delete action is recorded in audit log
- No orphaned role associations exist

---

## Test Case 5: Delete Permission (In Use)
**ID:** TC-3.1-005  
**Priority:** Medium  
**Status:** Not Started

### Preconditions
- Permission "View Domain" is assigned to 3 roles (Admin, Viewer, Manager)
- User has platform architect role

### Steps
1. Navigate to Permission Management
2. Search for permission "View Domain"
3. Click delete button

### Expected Results
- System displays warning dialog:
  "This permission is assigned to 3 roles. Deleting it will remove it from all role assignments. Continue?"
- Delete button shows confirmation message
- List of affected roles is displayed (Admin, Viewer, Manager)

### Postconditions
- If user confirms: Permission is deleted and removed from all roles
- If user cancels: Permission remains unchanged
- Action is logged in audit trail

---

## Test Case 6: Permissions Grouped by Resource - User Management
**ID:** TC-3.1-006  
**Priority:** High  
**Status:** Not Started

### Preconditions
- Multiple permissions exist for User Management resource
- User has platform architect role

### Steps
1. Navigate to Permission Management screen
2. View permissions grouped by resource
3. Expand "User Management" resource group
4. Verify all user management permissions are listed

### Expected Results
- Permissions under "User Management" include:
  - Create User
  - Edit User
  - Delete User
  - View User List
  - Activate/Deactivate User
  - Assign Roles to User
  - Reset User Password
- All permissions are clearly grouped and labeled
- Group can be expanded/collapsed

### Postconditions
- Other resource groups remain collapsed
- No permissions are misplaced

---

## Test Case 7: Permissions Grouped by Resource - Test Management
**ID:** TC-3.1-007  
**Priority:** High  
**Status:** Not Started

### Preconditions
- Multiple permissions exist for Test Management resource
- User has platform architect role

### Steps
1. Navigate to Permission Management screen
2. Expand "Test Management" resource group
3. Verify all test management sub-groups are visible

### Expected Results
- Test Management expands to show sub-groups:
  - **Domain Permissions:**
    - Create Domain
    - Edit Domain
    - Delete Domain
    - View Domain
  - **Questions Permissions:**
    - Create Question
    - Edit Question
    - Delete Question
    - View Question
    - Publish Question
  - **Test Permissions:**
    - Create Test
    - Edit Test
    - Delete Test
    - Conduct Test
    - View Test Results
  - **Assessment Permissions:**
    - Create Assessment
    - Edit Assessment
    - Delete Assessment
    - View Assessment Results

### Postconditions
- All permissions are organized logically
- Sub-groups are clearly labeled

---

## Test Case 8: Permissions Grouped by Resource - Reports Management
**ID:** TC-3.1-008  
**Priority:** High  
**Status:** Not Started

### Preconditions
- Multiple permissions exist for Reports Management resource
- User has platform architect role

### Steps
1. Navigate to Permission Management screen
2. Expand "Reports Management" resource group

### Expected Results
- Reports Management displays permissions:
  - Generate Report
  - View Report
  - Export Report
  - Delete Report
  - Schedule Report
  - Manage Report Templates

### Postconditions
- Permissions are correctly categorized

---

## Test Case 9: Permissions Grouped by Resource - Skills Management
**ID:** TC-3.1-009  
**Priority:** High  
**Status:** Not Started

### Preconditions
- Multiple permissions exist for Skills Management resource
- User has platform architect role

### Steps
1. Navigate to Permission Management screen
2. Expand "Skills Management" resource group

### Expected Results
- Skills Management displays permissions:
  - Create Skill
  - Edit Skill
  - Delete Skill
  - View Skill List
  - Assign Skill to Question

### Postconditions
- All permissions are present and correctly grouped

---

## Test Case 10: Activate Permission
**ID:** TC-3.1-010  
**Priority:** High  
**Status:** Not Started

### Preconditions
- Permission "Create Skill" exists with status "Inactive"
- User has platform architect role

### Steps
1. Navigate to Permission Management
2. Search for permission "Create Skill"
3. Click on the permission
4. Toggle status from "Inactive" to "Active"
5. Click "Save" button

### Expected Results
- Permission status changes to "Active"
- Confirmation message: "Permission activated successfully"
- Permission becomes available for role assignment
- Status indicator shows green/active state

### Postconditions
- Change is reflected immediately in the system
- Roles can now be assigned this permission
- Audit log records the activation

---

## Test Case 11: Deactivate Permission
**ID:** TC-3.1-011  
**Priority:** High  
**Status:** Not Started

### Preconditions
- Permission "Publish Question" exists with status "Active"
- Permission is not currently assigned to any roles
- User has platform architect role

### Steps
1. Navigate to Permission Management
2. Search for permission "Publish Question"
3. Click on the permission
4. Toggle status from "Active" to "Inactive"
5. Click "Save" button

### Expected Results
- Permission status changes to "Inactive"
- Confirmation message: "Permission deactivated successfully"
- Permission is no longer available for new role assignments
- Status indicator shows gray/inactive state

### Postconditions
- Existing roles still have the permission (if assigned)
- System flags the permission as deprecated
- Audit log records the deactivation

---

## Test Case 12: Deactivate Permission (With Active Assignments)
**ID:** TC-3.1-012  
**Priority:** High  
**Status:** Not Started

### Preconditions
- Permission "View Report" is assigned to 5 active roles
- User has platform architect role

### Steps
1. Navigate to Permission Management
2. Search for permission "View Report"
3. Click on the permission
4. Attempt to toggle status to "Inactive"

### Expected Results
- System displays warning:
  "This permission is currently assigned to 5 roles. Deactivating it will prevent new assignments and may affect current users. Continue?"
- Shows list of affected roles
- Option to proceed or cancel

### Postconditions
- If confirmed: Permission is deactivated but existing assignments remain (for backward compatibility or as configured)
- If cancelled: Permission remains active
- Action is logged in audit trail

---

## Test Case 13: Permission Search and Filter
**ID:** TC-3.1-013  
**Priority:** Medium  
**Status:** Not Started

### Preconditions
- At least 50 permissions exist in the system
- User has platform architect role

### Steps
1. Navigate to Permission Management
2. Use search box to search for "Create"
3. Filter results by resource group "Test Management"
4. Filter results by status "Active"

### Expected Results
- Search results show permissions matching keyword "Create"
- Results are further filtered by Test Management resource
- Only Active permissions are displayed
- Result count is displayed (e.g., "12 permissions found")
- Results update in real-time as filters are applied

### Postconditions
- Filters can be cleared to show all permissions again
- Search history is not retained (privacy)

---

## Test Case 14: Permission Bulk Status Update
**ID:** TC-3.1-014  
**Priority:** Low  
**Status:** Not Started

### Preconditions
- Multiple permissions exist in the system
- User has platform architect role

### Steps
1. Navigate to Permission Management
2. Select 5 permissions using checkboxes
3. Click "Bulk Actions" dropdown
4. Select "Change Status to Active"
5. Confirm action

### Expected Results
- All 5 selected permissions status changes to "Active"
- Confirmation message: "5 permissions activated successfully"
- Changes are reflected immediately
- Bulk operation is logged as single entry with list of affected permissions

### Postconditions
- No unselected permissions are affected
- Audit trail records bulk action

---

## Test Case 15: Permission Name Uniqueness Validation
**ID:** TC-3.1-015  
**Priority:** High  
**Status:** Not Started

### Preconditions
- Permission "View Questions" already exists
- User has platform architect role
- Create permission form is open

### Steps
1. Navigate to Create Permission form
2. Enter permission name: "View Questions"
3. Click "Save" button

### Expected Results
- System displays error message: "Permission name 'View Questions' already exists. Please use a different name."
- Form is not submitted
- Focus returns to the permission name field
- Existing permission is not modified

### Postconditions
- User can modify the name and retry
- No duplicate permission is created

---

## Summary of Test Cases
- **Total Test Cases:** 15
- **High Priority:** 11
- **Medium Priority:** 2
- **Low Priority:** 2

**Coverage Areas:**
- ✓ CRUD Operations (Create, Read, Update, Delete)
- ✓ Resource Grouping (User Management, Test Management, Reports Management, Skills Management)
- ✓ Status Management (Activate/Deactivate)
- ✓ Validation and Error Handling
- ✓ Bulk Operations
- ✓ Search and Filtering
