# Story 3.2 — Action-Level Permission Enforcement Test Cases

**User Story:** As a developer integrating the permission system, I want permission checks at the API and UI level so that unauthorized actions are blocked consistently.

**Related Issue:** DK26-440

---

## Test Case 1: API Guard - Authorized Request
**ID:** TC-3.2-001  
**Priority:** High  
**Status:** Not Started

### Preconditions
- User has "Create Question" permission assigned
- API endpoint `/api/questions/create` is protected
- User is authenticated with valid token

### Steps
1. User makes POST request to `/api/questions/create`
2. Request includes valid authentication token
3. Request body contains question data

### Expected Results
- API checks user's permissions before processing
- Permission "Create Question" is found in user's role
- Request is processed successfully
- HTTP response: 201 Created
- New question is created and returned with ID

### Postconditions
- Action is logged with user ID, timestamp, and action type
- Question appears in the system

---

## Test Case 2: API Guard - Unauthorized Request (Missing Permission)
**ID:** TC-3.2-002  
**Priority:** High  
**Status:** Not Started

### Preconditions
- User does NOT have "Create Question" permission
- User is authenticated with valid token
- API endpoint `/api/questions/create` is protected

### Steps
1. User makes POST request to `/api/questions/create`
2. Request includes valid authentication token
3. Request body contains question data

### Expected Results
- API checks user's permissions
- Permission "Create Question" is NOT found in user's role
- Request is denied
- HTTP response: 403 Forbidden
- Response body includes error message: "Permission denied: You do not have permission to create questions"
- Request is NOT processed

### Postconditions
- No question is created
- Action attempt is logged in security log

---

## Test Case 3: API Guard - Unauthorized Request (No Authentication)
**ID:** TC-3.2-003  
**Priority:** High  
**Status:** Not Started

### Preconditions
- API endpoint `/api/questions/create` is protected
- No authentication token is provided

### Steps
1. User makes POST request to `/api/questions/create`
2. Request does NOT include authentication token
3. Request body contains question data

### Expected Results
- API rejects request before permission check
- HTTP response: 401 Unauthorized
- Response body: "Authentication token is missing or invalid"
- Request is NOT processed

### Postconditions
- Action is not logged (authentication failed)
- No question is created

---

## Test Case 4: UI Element - Button Disabled When Missing Permission
**ID:** TC-3.2-004  
**Priority:** High  
**Status:** Not Started

### Preconditions
- User does NOT have "Edit Domain" permission
- User is authenticated and logged in
- Domain management page is loaded

### Steps
1. User navigates to Domain Management page
2. User views the list of domains
3. User looks for the "Edit Domain" button on a domain row

### Expected Results
- "Edit Domain" button is present but DISABLED (grayed out)
- Button has cursor style indicating it's not clickable
- Tooltip appears on hover: "You don't have permission to edit domains"
- Button click does NOT trigger any action

### Postconditions
- Other authorized actions (if any) remain enabled
- User understands they lack this permission

---

## Test Case 5: UI Element - Button Hidden When Missing Permission
**ID:** TC-3.2-005  
**Priority:** High  
**Status:** Not Started

### Preconditions
- User does NOT have "Delete Assessment" permission
- User is authenticated and logged in
- Assessment list page is loaded

### Steps
1. User navigates to Assessment Management page
2. User views the list of assessments
3. User looks for the "Delete Assessment" button

### Expected Results
- "Delete Assessment" button is NOT visible on the page
- Button is completely hidden (not disabled)
- No space is reserved for the hidden button
- Page layout is clean without the button

### Postconditions
- Other authorized buttons are visible
- User does not see the option to delete assessments

---

## Test Case 6: UI Element - Menu Item Hidden
**ID:** TC-3.2-006  
**Priority:** High  
**Status:** Not Started

### Preconditions
- User does NOT have "View Report" permission
- User is authenticated and logged in
- Main navigation menu is visible

### Steps
1. User opens the main navigation menu
2. User looks for "Reports" menu item

### Expected Results
- "Reports" menu item is NOT visible in the navigation menu
- Other menu items are visible and functional
- Menu structure is clean without gaps

### Postconditions
- User cannot navigate to Reports section
- Other navigation options remain accessible

---

## Test Case 7: UI Element - Form Field Readonly When Missing Permission
**ID:** TC-3.2-007  
**Priority:** Medium  
**Status:** Not Started

### Preconditions
- User has "View Question" but NOT "Edit Question" permission
- Question details page is loaded
- User is authenticated

### Steps
1. User navigates to Question Details page
2. User views the question form
3. User attempts to modify question content

### Expected Results
- Form fields are displayed but in READ-ONLY mode
- Text fields are not editable (input cursor appears but changes don't register)
- "Save" button is disabled or hidden
- "Edit" button shows: "You don't have permission to edit this question"

### Postconditions
- User can view the information but cannot modify it
- No accidental changes can occur

---

## Test Case 8: Permission Failure Logging - API Denial
**ID:** TC-3.2-008  
**Priority:** High  
**Status:** Not Started

### Preconditions
- User (ID: user_123) does NOT have "Create Skill" permission
- User is authenticated
- API endpoint `/api/skills/create` is protected
- Audit logging system is active

### Steps
1. User attempts POST request to `/api/skills/create`
2. Request is denied due to missing permission
3. Check audit/security log

### Expected Results
- Audit log entry is created with:
  - User ID: user_123
  - Action: "CREATE_SKILL"
  - Timestamp: Current date/time
  - Result: "DENIED"
  - Reason: "Missing permission: Create Skill"
  - IP Address: User's IP
  - User Agent: Browser information
- Log entry is searchable and retrievable

### Postconditions
- Security team can audit permission denial attempts
- Suspicious patterns can be identified

---

## Test Case 9: Permission Failure Logging - Multiple Failed Attempts
**ID:** TC-3.2-009  
**Priority:** High  
**Status:** Not Started

### Preconditions
- User (ID: user_456) lacks "Delete Question" permission
- User is authenticated
- Audit logging is active

### Steps
1. User attempts to delete Question 1 - DENIED
2. User attempts to delete Question 2 - DENIED
3. User attempts to delete Question 3 - DENIED
4. View audit log for user_456

### Expected Results
- Audit log shows 3 separate entries for delete denials
- Each entry has:
  - Timestamp (chronologically ordered)
  - Resource ID (Question 1, 2, 3)
  - Denial reason
- System may flag user for suspicious activity (3 denials in short time)
- Alert notification sent to administrators (if configured)

### Postconditions
- Security team is alerted to potential unauthorized access attempts
- User activity can be monitored

---

## Test Case 10: Permission Success Logging - API Authorization
**ID:** TC-3.2-010  
**Priority:** High  
**Status:** Not Started

### Preconditions
- User (ID: user_789) has "Create Domain" permission
- User is authenticated
- API endpoint `/api/domains/create` is protected
- Audit logging is active

### Steps
1. User makes POST request to `/api/domains/create`
2. Request is authorized and processed successfully
3. Domain is created with ID: domain_999
4. Check audit log

### Expected Results
- Audit log entry is created with:
  - User ID: user_789
  - Action: "CREATE_DOMAIN"
  - Timestamp: Current date/time
  - Result: "SUCCESS"
  - Resource ID: domain_999
  - IP Address: User's IP
  - Changes made: [list of field values]
- Log entry is retrievable and searchable

### Postconditions
- Complete audit trail exists for all data modifications
- Compliance requirements are met

---

## Test Case 11: API Guard - Expired Session Token
**ID:** TC-3.2-011  
**Priority:** Medium  
**Status:** Not Started

### Preconditions
- User's session token has expired
- API endpoint `/api/tests/create` is protected
- User previously had valid authentication

### Steps
1. User makes request with expired token
2. Token timestamp is more than 1 hour old
3. API checks token validity

### Expected Results
- API rejects the request
- HTTP response: 401 Unauthorized
- Response: "Session has expired. Please login again."
- User is forced to re-authenticate

### Postconditions
- User must login again to get new token
- Security is maintained

---

## Test Case 12: UI Element - Partial Feature Access
**ID:** TC-3.2-012  
**Priority:** Medium  
**Status:** Not Started

### Preconditions
- User has "View Test" and "Edit Test" but NOT "Delete Test" permission
- Test details page is loaded
- User is authenticated

### Steps
1. User navigates to Test Details page
2. User views action buttons available
3. User attempts each action

### Expected Results
- "View Test" button/functionality - ENABLED
- "Edit Test" button - ENABLED
- "Delete Test" button - DISABLED or HIDDEN
- Edit functionality works normally
- View functionality works normally
- Delete action is prevented

### Postconditions
- User has appropriate access granularity
- Partial permissions work as expected

---

## Test Case 13: API Guard - Role-Based Permission Enforcement
**ID:** TC-3.2-013  
**Priority:** High  
**Status:** Not Started

### Preconditions
- User "admin_user" has role "Tenant Admin"
- Role "Tenant Admin" includes permissions:
  - Create Domain
  - Edit Domain
  - Create Assessment
  - Edit Assessment
- User is authenticated

### Steps
1. User attempts to create a Domain
2. User attempts to create an Assessment
3. User attempts to delete a Domain (NOT in role)

### Expected Results
- Create Domain: SUCCESS (permission granted via role)
- Create Assessment: SUCCESS (permission granted via role)
- Delete Domain: DENIED (permission not in role)
- Each action is verified against role's permission list

### Postconditions
- Role-based enforcement works correctly
- Individual permissions from role are applied

---

## Test Case 14: API Guard - Direct Permission vs Role Permission
**ID:** TC-3.2-014  
**Priority:** Medium  
**Status:** Not Started

### Preconditions
- User has:
  - Role: "Question Editor" (includes "Create Question", "Edit Question")
  - Direct Permission: "Publish Question"
- User is authenticated

### Steps
1. User attempts to create a question
2. User attempts to edit a question
3. User attempts to publish a question

### Expected Results
- Create Question: SUCCESS (from role)
- Edit Question: SUCCESS (from role)
- Publish Question: SUCCESS (from direct permission)
- System correctly aggregates permissions from both role and direct assignments

### Postconditions
- Permission aggregation works correctly
- User has combined set of all applicable permissions

---

## Test Case 15: Error Message - Clear Permission Denial Message
**ID:** TC-3.2-015  
**Priority:** Medium  
**Status:** Not Started

### Preconditions
- User lacks "Export Report" permission
- User attempts to export a report via UI
- System is configured to show clear error messages

### Steps
1. User clicks "Export Report" button
2. API processes the request
3. Permission check fails
4. Error message is displayed to user

### Expected Results
- Error message is displayed:
  "Access Denied: You do not have permission to export reports. Contact your administrator if you believe this is incorrect."
- Message is:
  - Clear and understandable (non-technical)
  - Shows the specific permission required
  - Suggests action (contact admin)
  - Not a generic 403 error
- Message appears in user-friendly dialog or toast notification

### Postconditions
- User understands why action was denied
- User knows how to request access

---

## Summary of Test Cases
- **Total Test Cases:** 15
- **High Priority:** 10
- **Medium Priority:** 5

**Coverage Areas:**
- ✓ API Permission Guards (Authorization/Denial)
- ✓ UI Element Control (Buttons, Menus, Fields)
- ✓ Permission Failure Logging and Audit Trail
- ✓ Error Handling and Messages
- ✓ Session/Token Management
- ✓ Role-Based Permission Integration
- ✓ Multiple Permission Scenarios

**Key Testing Dimensions:**
- Authorized vs. Unauthorized requests
- UI visibility and interactivity
- Comprehensive audit logging
- User-friendly error messages
- Session management
- Role-based vs. direct permissions
