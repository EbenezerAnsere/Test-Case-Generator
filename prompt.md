# What This Does
Automates the boring part of QA: creating test cases in Xray and moving Jira tickets through the workflow.
## The 7-Step Flow
1. **Read** — System reads the full ticket from Jira (summary, description, acceptance criteria)
2. **Create Test Cases** — Writes test cases in Xray in relation to the acceptance criteria, places them in the correct folder (creates subfolder if needed)
3. **Create Test Set** — Builds a test set per story and links it to the corresponding test cases
4. **Link to Plans** — Adds the test set to Test Execution and Test Plan
5. **Update Status** — After testing completes,I will update you to moves the ticket through(Flow might change):
   `Todo → Dev Done → Code on Staging → In Progress QA → Review → Done`
   (applied per test case)
## Config File Location
Load `agent-config.json` at the start of EVERY run: "YOUR ROOT FOLDER"
Execute shell commands over writing scripts to accomplish tasks