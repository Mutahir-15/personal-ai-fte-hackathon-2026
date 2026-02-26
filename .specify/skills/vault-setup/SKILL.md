# Skill: Vault Setup (v1.0.0)

## Purpose
This skill initializes the complete Obsidian vault folder structure and seeds all required markdown files for the Personal AI Employee (Bronze Tier). It establishes the foundational directory and file structure upon which all other AI employee operations depend.

## Inputs
-   **`VAULT_ROOT_PATH`**: The absolute path to where the Obsidian vault should be created or updated (e.g., `C:\Users\<YOUR_USERNAME>\AI_Employee_Vault`). This is passed as a command-line argument to the Python script.

## Outputs
-   **Folders Created**:
    -   `{{VAULT_ROOT_PATH}}\Needs_Action`
    -   `{{VAULT_ROOT_PATH}}\Plans`
    -   `{{VAULT_ROOT_PATH}}\Done`
    -   `{{VAULT_ROOT_PATH}}\Pending_Approval`
    -   `{{VAULT_ROOT_PATH}}\Approved`
    -   `{{VAULT_ROOT_PATH}}\Rejected`
    -   `{{VAULT_ROOT_PATH}}\Vault\Logs`
    -   `{{VAULT_ROOT_PATH}}\Accounting`
    -   `{{VAULT_ROOT_PATH}}\Briefings`
-   **Seed Markdown Files Created**:
    -   `{{VAULT_ROOT_PATH}}\Dashboard.md` (containing a template for bank balance, pending messages, active projects)
    -   `{{VAULT_ROOT_PATH}}\Company_Handbook.md` (containing rules of engagement for the AI agent)
    -   `{{VAULT_ROOT_PATH}}\Business_Goals.md` (containing Q1 objectives, revenue targets, and key metrics table)

## Pre-conditions
-   **Operating System**: Windows 10.
-   **Python**: Python 3.13+ installed and accessible via `python` or `python3` command.
-   **Permissions**: The user running this skill must have sufficient read/write/create permissions for the specified `VAULT_ROOT_PATH`.

## Step-by-Step Execution Instructions
To execute the `vault-setup` skill:

1.  **Save Python Script**: Save the `vault_setup.py` content (provided below) into the directory: `{{YOUR_PROJECT_ROOT}}\.specify\skills\vault-setup\vault_setup.py`.
2.  **Run the Script**: Open a PowerShell terminal and execute the script, providing the desired vault root path. Replace `<YOUR_USERNAME>` and `<YOUR_VAULT_NAME>` with your actual details.

    ```powershell
    python .specify/skills/vault-setup/vault_setup.py "C:\Users\<YOUR_USERNAME>\<YOUR_VAULT_NAME>"
    ```
    (Example: `python .specify/skills/vault-setup/vault_setup.py "C:\Users\JohnDoe\AI_Employee_Vault"`)

3.  **Monitor Output**: Observe the terminal output for messages indicating folder creation and file seeding. Any errors will be logged to the console.

## Full Python Implementation
```python
import os
import sys
from pathlib import Path
from datetime import datetime

# Logging function for consistent output
def log_message(level, message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {level.upper()}: {message}")

def setup_vault(vault_root_path_str: str):
    """
    Sets up the Obsidian vault folder structure and seeds required markdown files.
    This function is idempotent.
    """
    vault_root_path = Path(vault_root_path_str)

    if not vault_root_path.exists():
        try:
            vault_root_path.mkdir(parents=True, exist_ok=True)
            log_message("INFO", f"Created vault root: {vault_root_path}")
        except Exception as e:
            log_message("ERROR", f"Failed to create vault root {vault_root_path}: {e}")
            sys.exit(1)
    else:
        log_message("INFO", f"Vault root already exists: {vault_root_path}. Ensuring structure is correct.")

    # Define sub-folders relative to the vault root
    sub_folders = [
        "Needs_Action",
        "Plans",
        "Done",
        "Pending_Approval",
        "Approved",
        "Rejected",
        "Vault/Logs",        # Nested path for logs as per prompt context
        "Accounting",
        "Briefings",
    ]

    for folder in sub_folders:
        path = vault_root_path / folder
        try:
            path.mkdir(parents=True, exist_ok=True)
            log_message("INFO", f"Ensured folder exists: {path}")
        except Exception as e:
            log_message("ERROR", f"Failed to create folder {path}: {e}")
            # Do not exit, try to continue with other folders/files

    # Define seed markdown files and their content
    seed_files = {
        "Dashboard.md": """# AI Employee Dashboard

## 💰 Bank Balance
- Current Balance: $ [INSERT CURRENT BALANCE]
- Last Updated: [YYYY-MM-DD HH:MM]

## 📩 Pending Messages
- [ ] Review new messages from [Sender 1]
- [ ] Respond to [Topic 2] with [Recipient]
- [ ] Follow up on [Task 3]

## 🚀 Active Projects
- **Project Alpha**: [Status]
  - Next Action: [Action]
  - Due Date: [YYYY-MM-DD]
- **Project Beta**: [Status]
  - Next Action: [Action]
  - Due Date: [YYYY-MM-DD]

## ✅ Quick Links
- [[Company_Handbook]]
- [[Business_Goals]]
- [[Needs_Action]]
""",
        "Company_Handbook.md": """# Company Handbook for AI Employee

## 📜 Rules of Engagement

1.  **Prioritization**:
    -   Urgent tasks from human oversight take precedence.
    -   Tasks with direct impact on business goals are prioritized next.
    -   Routine maintenance and logging should be handled asynchronously where possible.

2.  **Communication**:
    -   Maintain clear, concise, and professional communication.
    -   Report progress and significant findings regularly.
    -   Seek clarification immediately if instructions are ambiguous.

3.  **Autonomy & Initiative**:
    -   Act within defined parameters and skill sets.
    -   Proactively identify potential issues or improvements and bring them to attention.
    -   Document decisions and rationale in ADRs where appropriate.

4.  **Security & Privacy**:
        -   Never disclose sensitive information.
        -   Adhere strictly to data handling policies.
        -   Flag any perceived security vulnerabilities.

5.  **Learning & Improvement**:
    -   Continuously analyze and adapt based on feedback and new information.
    -   Suggest improvements to workflows and skills.

## 🔒 Confidentiality
All internal company information, data, and strategies are to be treated as strictly confidential.

## 🤝 Collaboration
Work seamlessly with other AI agents and human team members. Avoid redundant efforts.
""",
        "Business_Goals.md": """# Business Goals

## 🎯 Q1 Objectives (YYYY)

-   **Objective 1**: [Description]
    -   Key Results:
        -   KR 1: [Metric] to [Target] by [Date]
        -   KR 2: [Metric] to [Target] by [Date]
-   **Objective 2**: [Description]
    -   Key Results:
        -   KR 1: [Metric] to [Target] by [Date]
        -   KR 2: [Metric] to [Target] by [Date]

## 📈 Revenue Targets

| Quarter | Target Revenue | Actual Revenue | Status |
| :------ | :------------- | :------------- | :----- |
| Q1      | $[AMOUNT]     | $[AMOUNT]     | [Status]|
| Q2      | $[AMOUNT]     | $[AMOUNT]     | [Status]|
| Q3      | $[AMOUNT]     | $[AMOUNT]     | [Status]|
| Q4      | $[AMOUNT]     | $[AMOUNT]     | [Status]|

## 📊 Key Performance Indicators (KPIs)

-   **Customer Satisfaction (CSAT)**: [Target %]
-   **Operational Efficiency**: [Target % reduction in overhead]
-   **Feature Adoption**: [Target % of users]
-   **Error Rate**: [Target % reduction]
"""
    }

    for filename, content in seed_files.items():
        file_path = vault_root_path / filename
        if not file_path.exists():
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                log_message("INFO", f"Created seed file: {file_path}")
            except Exception as e:
                log_message("ERROR", f"Failed to create seed file {file_path}: {e}")
        else:
            log_message("INFO", f"Seed file already exists: {file_path}. Skipping creation to maintain idempotency.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        log_message("ERROR", "Usage: python vault_setup.py <VAULT_ROOT_PATH>")
        sys.exit(1)
    
    vault_path_arg = sys.argv[1]
    setup_vault(vault_path_arg)
    log_message("INFO", "Vault setup process completed.")
```

## Seed File Templates
### Dashboard.md Template
```markdown
# AI Employee Dashboard

## 💰 Bank Balance
- Current Balance: $ [INSERT CURRENT BALANCE]
- Last Updated: [YYYY-MM-DD HH:MM]

## 📩 Pending Messages
- [ ] Review new messages from [Sender 1]
- [ ] Respond to [Topic 2] with [Recipient]
- [ ] Follow up on [Task 3]

## 🚀 Active Projects
- **Project Alpha**: [Status]
  - Next Action: [Action]
  - Due Date: [YYYY-MM-DD]
- **Project Beta**: [Status]
  - Next Action: [Action]
  - Due Date: [YYYY-MM-DD]

## ✅ Quick Links
- [[Company_Handbook]]
- [[Business_Goals]]
- [[Needs_Action]]
```

### Company_Handbook.md Template
```markdown
# Company Handbook for AI Employee

## 📜 Rules of Engagement

1.  **Prioritization**:
    -   Urgent tasks from human oversight take precedence.
    -   Tasks with direct impact on business goals are prioritized next.
    -   Routine maintenance and logging should be handled asynchronously where possible.

2.  **Communication**:
    -   Maintain clear, concise, and professional communication.
    -   Report progress and significant findings regularly.
    -   Seek clarification immediately if instructions are ambiguous.

3.  **Autonomy & Initiative**:
    -   Act within defined parameters and skill sets.
    -   Proactively identify potential issues or improvements and bring them to attention.
    -   Document decisions and rationale in ADRs where appropriate.

4.  **Security & Privacy**:
    -   Never disclose sensitive information.
    -   Adhere strictly to data handling policies.
    -   Flag any perceived security vulnerabilities.

5.  **Learning & Improvement**:
    -   Continuously analyze and adapt based on feedback and new information.
    -   Suggest improvements to workflows and skills.

## 🔒 Confidentiality
All internal company information, data, and strategies are to be treated as strictly confidential.

## 🤝 Collaboration
Work seamlessly with other AI agents and human team members. Avoid redundant efforts.
```

### Business_Goals.md Template
```markdown
# Business Goals

## 🎯 Q1 Objectives (YYYY)

-   **Objective 1**: [Description]
    -   Key Results:
        -   KR 1: [Metric] to [Target] by [Date]
        -   KR 2: [Metric] to [Target] by [Date]
-   **Objective 2**: [Description]
    -   Key Results:
        -   KR 1: [Metric] to [Target] by [Date]
        -   KR 2: [Metric] to [Target] by [Date]

## 📈 Revenue Targets

| Quarter | Target Revenue | Actual Revenue | Status |
| :------ | :------------- | :------------- | :----- |
| Q1      | $[AMOUNT]     | $[AMOUNT]     | [Status]|
| Q2      | $[AMOUNT]     | $[AMOUNT]     | [Status]|
| Q3      | $[AMOUNT]     | $[AMOUNT]     | [Status]|
| Q4      | $[AMOUNT]     | $[AMOUNT]     | [Status]|

## 📊 Key Performance Indicators (KPIs)

-   **Customer Satisfaction (CSAT)**: [Target %]
-   **Operational Efficiency**: [Target % reduction in overhead]
-   **Feature Adoption**: [Target % of users]
-   **Error Rate**: [Target % reduction]
```

## Post-conditions / Verification
To verify successful execution of the `vault-setup` skill:

1.  **Check Folder Structure**: Navigate to the `VAULT_ROOT_PATH` (e.g., `C:\Users\JohnDoe\AI_Employee_Vault`) in your file explorer.
    -   Confirm that all specified folders (`Needs_Action`, `Plans`, `Done`, `Pending_Approval`, `Approved`, `Rejected`, `Vault\Logs`, `Accounting`, `Briefings`) exist within the vault root.
2.  **Check Seed Files**: Verify that `Dashboard.md`, `Company_Handbook.md`, and `Business_Goals.md` exist directly under the `VAULT_ROOT_PATH`.
3.  **Inspect File Content**: Open each `.md` file and ensure its content matches the templates provided in this skill description.
4.  **Idempotency Check**: Run the skill a second time with the exact same `VAULT_ROOT_PATH`. Confirm that no errors occur and that existing files are not overwritten or duplicated. The console output should indicate that existing folders/files are skipped.

## Error Handling
The `vault-setup` skill incorporates the following error handling:

-   **Invalid Path**: If `VAULT_ROOT_PATH` is not provided as a command-line argument, the script will exit with an error message.
-   **Permission Denied**: If the script lacks sufficient permissions to create folders or files, it will log an `ERROR` message to the console and attempt to continue with other operations. A fatal error during vault root creation will cause the script to exit.
-   **Idempotency**: The script is designed to be idempotent. It uses `mkdir(exist_ok=True)` for folders and checks `if not file_path.exists()` before writing seed files. This prevents errors if the skill is run multiple times and ensures existing files are not overwritten. Warnings will be logged for skipped file creations.

## Success Criteria
The `vault-setup` skill is deemed successful if:

-   All specified folders are created or confirmed to exist at the `VAULT_ROOT_PATH`.
-   All specified seed markdown files (`Dashboard.md`, `Company_Handbook.md`, `Business_Goals.md`) are created or confirmed to exist at the `VAULT_ROOT_PATH` with their correct content.
-   The script completes without critical errors (exit code 0).
-   The skill can be run multiple times without corrupting existing data or causing errors, demonstrating idempotency.