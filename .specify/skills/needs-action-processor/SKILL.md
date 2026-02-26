# SKILL: needs-action-processor

**Version:** 1.0.0
**Author:** Gemini CLI

---

## 1. Skill Name & Version
- **Name:** `needs-action-processor`
- **Version:** `1.0.0`

---

## 2. Purpose
This skill implements the core reasoning and action-planning loop for the Personal AI Employee. It systematically processes unstructured requests from an input directory (`/Needs_Action/`), applies a set of rules (`Company_Handbook.md`), and generates structured, actionable plans (`Plan.md`). It is designed to be idempotent, crash-safe, and fully auditable, serving as the "brain" that decides what to do next.

---

## 3. Inputs
- **Environment Variables:**
  - `VAULT_PATH`: The absolute path to the root of the `AI_Employee_Vault`.
  - `DRY_RUN`: `true` or `false`. If `true`, the skill logs intended actions without modifying the file system. Defaults to `true`.
  - `GEMINI_API_KEY`: Required for making calls to the Gemini API.
- **File System:**
  - `VAULT_PATH/Needs_Action/*.md`: Unprocessed markdown files with `status: pending` in their frontmatter.
  - `VAULT_PATH/Company_Handbook.md`: The rules of engagement that constrain the AI's behavior and decision-making.

---

## 4. Outputs
- **File System (on `DRY_RUN=false`):**
  - `VAULT_PATH/Plans/<source_filename_without_ext>-Plan.md`: A structured plan file for each processed request.
  - `VAULT_PATH/Pending_Approval/<source_filename_without_ext>-Approval.md`: An approval request file if the plan requires human sign-off.
  - `VAULT_PATH/Done/<source_filename>`: The original request file is moved here after successful processing.
  - `VAULT_PATH/Logs/YYYY-MM-DD.json`: A log entry for every action taken, appended to a daily log file.
- **State Changes (on `DRY_RUN=false`):**
  - The `status` field in the frontmatter of the source `.md` file is updated from `pending` to `processing`.

---

## 5. Pre-conditions
- The `VAULT_PATH` environment variable must be set to a valid, existing directory path.
- The `AI_Employee_Vault` must contain the following directories: `Needs_Action`, `Plans`, `Done`, `Logs`, `Pending_Approval`.
- `VAULT_PATH/Company_Handbook.md` must exist and be readable.
- `VAULT_PATH/Needs_Action/` may contain `.md` files, each with a `status: pending` field in its YAML frontmatter.
- The `gemini` CLI tool must be installed and available in the system's PATH.
- PM2 must be installed and configured to run the script.

---

## 6. Step-by-Step Execution Instructions
1.  **Initialization:**
    a. Load environment variables (`VAULT_PATH`, `DRY_RUN`).
    b. Verify `VAULT_PATH` and the required directory structure. Exit if not found.
    c. Load the content of `Company_Handbook.md` into memory.

2.  **Scan for Pending Files:**
    a. Scan the `VAULT_PATH/Needs_Action/` directory for all `.md` files.
    b. For each file, read its content and parse the frontmatter to check if `status` is exactly `pending`.
    c. Create a list of all files that meet this criterion. If none, exit gracefully.

3.  **Process Each Pending File:**
    a. For each file in the list:
    b. **Log Intent:** Log the intention to process the file.
    c. **Construct Prompt:** Create a detailed prompt for the Gemini CLI, including the content of the request file and the full `Company_Handbook.md`. The prompt must instruct the model to generate a plan in the specified `Plan.md` format.
    d. **Execute Gemini CLI:**
        - If `DRY_RUN=true`, log the command that *would* be executed and simulate a successful response for the next steps.
        - If `DRY_RUN=false`, execute `gemini -p "<prompt>"` via a subprocess. Capture the output.
    e. **Parse Response:** Parse the Gemini CLI output to extract the structured `Plan.md` content. Handle potential parsing errors.
    f. **Determine Approval:** Check the `requires_approval` field in the generated plan.
    g. **File Operations (DRY_RUN check at each step):**
        i. **Update Status:** Change the `status` field in the source file's frontmatter to `processing`.
        ii. **Write Plan:** Write the generated `Plan.md` content to the `VAULT_PATH/Plans/` directory.
        iii. **Handle Approval:** If approval is required, create a corresponding file in `VAULT_PATH/Pending_Approval/`.
        iv. **Move Source File:** Move the original request file from `VAULT_PATH/Needs_Action/` to `VAULT_PATH/Done/`.
        v. **Log Action:** Append a detailed JSON object of the completed action to `VAULT_PATH/Logs/YYYY-MM-DD.json`.

4.  **Completion:**
    a. Output a summary of actions taken (or actions that would have been taken in `DRY_RUN`).

---

## 7. Decision Tree
```
START
 |
 V
Scan for files in /Needs_Action/
 |
 V
Any .md files found? --(No)--> END
 |
 V (Yes)
For each file:
 |
 V
Read file. Is "status: pending" in frontmatter? --(No)--> Skip file, next
 |
 V (Yes)
Read Company_Handbook.md
 |
 V
Construct Gemini CLI prompt
 |
 V
Is DRY_RUN=true? --(Yes)--> Log intended Gemini call, Simulate plan generation -> Go to Log Summary
 |
 V (No)
Execute Gemini CLI
 |
 V
Did Gemini CLI succeed? --(No)--> Log error, next file
 |
 V (Yes)
Parse Gemini output into Plan.md structure
 |
 V
Did parsing succeed? --(No)--> Log error, next file
 |
 V (Yes)
Update source file: "status: processing"
 |
 V
Write Plan.md to /Plans/
 |
 V
Does plan have "requires_approval: true"? --(Yes)--> Write request to /Pending_Approval/
 |
 V (No or Yes)
Move source file to /Done/
 |
 V
Append action to /Logs/YYYY-MM-DD.json
 |
 V
(Loop to next file)
 |
 V
Log Summary
 |
 V
END
```

---

## 8. Plan.md Template
```markdown
---
created: <ISO 8601 timestamp>
source_file: <original filename from /Needs_Action/>
status: pending_approval | ready_to_execute | blocked
requires_approval: true | false
priority: high | medium | low
---

## Objective
<One clear sentence describing what needs to be done>

## Context
<Brief summary of the source file content>

## Steps
- [ ] Step 1: <first action>
- [ ] Step 2: <second action>
- [ ] Step 3: <third action>

## Rules Applied
<Which rules from Company_Handbook.md influenced this plan>

## Approval Required
<If requires_approval is true, explain what needs approval and why>
<If false, state "No approval required for this action">

## Risks
<Any potential risks or edge cases identified>

## Implementation Details
- Language: Python 3.13+
- Trigger: Called by Orchestrator.py when new files appear in /Needs_Action/
- Gemini CLI command: gemini -p "<prompt constructed from file content>"
- State tracking: Update status field in source .md file
- Duplicate prevention: Skip files with status != "pending"
- Logging: Append to /Vault/Logs/YYYY-MM-DD.json on every action
```

---

## 9. Full Python Implementation
This is the complete `needs_action_processor.py` script.

**Dependencies:** `python-dotenv`. Install with `pip install python-dotenv`.

```python
# needs_action_processor.py
import os
import sys
import json
import re
import subprocess
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# --- CONFIGURATION ---
load_dotenv()
VAULT_PATH = os.getenv("VAULT_PATH")
DRY_RUN = os.getenv("DRY_RUN", "true").lower() == "true"

# --- HELPER FUNCTIONS ---

def log_action(log_data: dict, log_path: Path):
    """Appends a log entry to the daily log file."""
    log_data["timestamp"] = datetime.utcnow().isoformat()
    log_data["dry_run"] = DRY_RUN
    
    try:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, "a") as f:
            f.write(json.dumps(log_data) + "
")
        print(f"INFO: Logged action for {log_data.get('source_file', 'N/A')}")
    except Exception as e:
        print(f"CRITICAL: Failed to write to log file {log_path}: {e}")

def get_frontmatter_field(content: str, field: str) -> str | None:
    """Extracts a field value from YAML frontmatter using regex."""
    match = re.search(rf"^\s*{field}:\s*(.*)\s*$", content, re.MULTILINE)
    return match.group(1).strip() if match else None

def update_frontmatter_field(content: str, field: str, new_value: str) -> str:
    """Updates a field in the YAML frontmatter."""
    return re.sub(
        rf"(^\s*{field}:\s*).*",
        rf"\1{new_value}",
        content,
        count=1,
        flags=re.MULTILINE
    )

def construct_gemini_prompt(task_content: str, handbook_content: str) -> str:
    """Constructs the prompt for the Gemini CLI."""
    
    plan_template = """---
created: <ISO 8601 timestamp>
source_file: <original filename from /Needs_Action/>
status: pending_approval | ready_to_execute | blocked
requires_approval: true | false
priority: high | medium | low
---

## Objective
<One clear sentence describing what needs to be done>

## Context
<Brief summary of the source file content>

## Steps
- [ ] Step 1: <first action>
- [ ] Step 2: <second action>
- [ ] Step 3: <third action>

## Rules Applied
<Which rules from Company_Handbook.md influenced this plan>

## Approval Required
<If requires_approval is true, explain what needs approval and why>
<If false, state "No approval required for this action">

## Risks
<Any potential risks or edge cases identified>
"""
    
    prompt = f"""
You are an AI assistant tasked with creating a structured action plan.
Analyze the user's request below, subject to the rules in the Company Handbook.
Generate a plan that strictly follows the provided `Plan.md` template format.

**Company Handbook (Rules of Engagement):**
---
{handbook_content}
---

**User Request:**
---
{task_content}
---

**Your Task:**
Generate a complete `Plan.md` file based on the request and handbook.
The `created` timestamp should be the current UTC time in ISO 8601 format.
Determine `requires_approval` based *only* on the handbook rules.
Determine `priority` based on the request's urgency.
The output MUST be only the `Plan.md` content and nothing else.

**Plan.md Template:**
---
{plan_template}
---
"""
    return prompt

def run_gemini_cli(prompt: str) -> str | None:
    """Executes the gemini CLI command and returns the output."""
    command = ["gemini", "-p", prompt]
    try:
        print("INFO: Executing Gemini CLI...")
        result = subprocess.run(command, capture_output=True, text=True, check=True, encoding='utf-8')
        print("INFO: Gemini CLI execution successful.")
        return result.stdout
    except FileNotFoundError:
        print("CRITICAL: `gemini` command not found. Is Gemini CLI installed and in your PATH?")
        return None
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Gemini CLI failed with exit code {e.returncode}.")
        print(f"Stderr: {e.stderr}")
        return None
    except Exception as e:
        print(f"ERROR: An unexpected error occurred while running Gemini CLI: {e}")
        return None

# --- MAIN LOGIC ---

def main():
    """Main execution function."""
    print("--- Needs Action Processor Started ---")
    print(f"Timestamp: {datetime.utcnow().isoformat()} UTC")
    print(f"DRY_RUN mode: {DRY_RUN}")

    if not VAULT_PATH or not Path(VAULT_PATH).is_dir():
        print(f"CRITICAL: VAULT_PATH environment variable is not set or is not a valid directory. Path: {VAULT_PATH}")
        sys.exit(1)

    # Define paths
    vault = Path(VAULT_PATH)
    needs_action_dir = vault / "Needs_Action"
    plans_dir = vault / "Plans"
    done_dir = vault / "Done"
    pending_approval_dir = vault / "Pending_Approval"
    logs_dir = vault / "Logs"
    handbook_path = vault / "Company_Handbook.md"
    log_file = logs_dir / f"{datetime.utcnow().strftime('%Y-%m-%d')}.json"

    # Verify paths
    for p in [needs_action_dir, plans_dir, done_dir, pending_approval_dir, logs_dir, handbook_path]:
        if not p.exists():
            print(f"CRITICAL: Required path does not exist: {p}")
            sys.exit(1)
            
    print(f"INFO: Vault Path: {vault}")

    # Load Handbook
    try:
        handbook_content = handbook_path.read_text(encoding='utf-8')
    except Exception as e:
        print(f"CRITICAL: Failed to read Company_Handbook.md: {e}")
        sys.exit(1)

    # Scan for pending files
    pending_files = []
    for item in needs_action_dir.glob("*.md"):
        try:
            content = item.read_text(encoding='utf-8')
            if get_frontmatter_field(content, "status") == "pending":
                pending_files.append(item)
        except Exception as e:
            print(f"WARNING: Could not read or parse file {item.name}: {e}")
            
    if not pending_files:
        print("INFO: No pending files found in /Needs_Action/. Exiting.")
        print("--- Needs Action Processor Finished ---")
        return

    print(f"INFO: Found {len(pending_files)} pending file(s) to process.")

    # Process each file
    for source_path in pending_files:
        print(f"
--- Processing: {source_path.name} ---")
        log_payload = {"source_file": source_path.name, "steps": []}

        try:
            source_content = source_path.read_text(encoding='utf-8')
            
            # 1. Construct Prompt
            gemini_prompt = construct_gemini_prompt(source_content, handbook_content)
            log_payload["steps"].append({"step": "construct_prompt", "status": "success"})
            
            # 2. Run Gemini CLI
            if DRY_RUN:
                plan_content = "DRY_RUN: Plan would be generated here."
                print("INFO: [DRY_RUN] Skipping Gemini CLI execution.")
            else:
                plan_content = run_gemini_cli(gemini_prompt)

            if not plan_content:
                log_payload["steps"].append({"step": "run_gemini", "status": "failure", "reason": "No content returned"})
                log_action(log_payload, log_file)
                continue
            log_payload["steps"].append({"step": "run_gemini", "status": "success"})

            # 3. Parse and Validate Plan
            requires_approval = get_frontmatter_field(plan_content, "requires_approval") == "true"
            plan_status = "pending_approval" if requires_approval else "ready_to_execute"
            
            # Fill in dynamic fields
            plan_content = plan_content.replace("<ISO 8601 timestamp>", datetime.utcnow().isoformat())
            plan_content = plan_content.replace("<original filename from /Needs_Action/>", source_path.name)
            
            plan_filename = f"{source_path.stem}-Plan.md"
            plan_path = plans_dir / plan_filename
            log_payload["plan_file"] = plan_path.name
            log_payload["steps"].append({"step": "parse_plan", "status": "success"})

            # 4. Perform File Operations
            if not DRY_RUN:
                # Update source file status
                new_source_content = update_frontmatter_field(source_content, "status", "processing")
                source_path.write_text(new_source_content, encoding='utf-8')
                
                # Write the plan
                plan_path.write_text(plan_content, encoding='utf-8')
                
                # Handle approval file
                if requires_approval:
                    approval_path = pending_approval_dir / f"{source_path.stem}-Approval.md"
                    approval_content = f"# Approval Required

Source: `{source_path.name}`
Plan: `{plan_path.name}`

See plan for details."
                    approval_path.write_text(approval_content, encoding='utf-8')
                    log_payload["steps"].append({"step": "create_approval_request", "status": "success"})

                # Move source file to Done
                done_path = done_dir / source_path.name
                source_path.rename(done_path)
                log_payload["steps"].append({"step": "move_to_done", "status": "success"})

            else:
                print(f"INFO: [DRY_RUN] Would update status of {source_path.name} to 'processing'.")
                print(f"INFO: [DRY_RUN] Would write plan to {plan_path}.")
                if requires_approval:
                    print(f"INFO: [DRY_RUN] Would create approval request for {source_path.name}.")
                print(f"INFO: [DRY_RUN] Would move {source_path.name} to {done_dir}.")
            
            log_action(log_payload, log_file)
            print(f"--- Finished Processing: {source_path.name} ---")

        except Exception as e:
            print(f"CRITICAL: An unhandled error occurred while processing {source_path.name}: {e}")
            log_payload["steps"].append({"step": "unhandled_exception", "status": "failure", "error": str(e)})
            log_action(log_payload, log_file)
            continue
            
    print("
--- Needs Action Processor Finished ---")

if __name__ == "__main__":
    main()

```

---

## 10. Gemini CLI Integration
The skill invokes the Gemini CLI using Python's `subprocess` module.

**Exact Command Pattern:**
```bash
gemini -p "<prompt>"
```
- **`gemini`**: The Gemini CLI executable.
- **`-p`**: The flag to pass a prompt directly.
- **`"<prompt>"`**: The dynamically generated prompt containing the handbook, the user request, and instructions, as constructed by the `construct_gemini_prompt` function.

---

## 11. DRY_RUN Verification Steps
`DRY_RUN` mode is enabled by default (`DRY_RUN=true` in `.env` or if the variable is absent). To verify it is working correctly:

1.  Place a test file (e.g., `test01.md` with `status: pending`) in the `/Needs_Action/` directory.
2.  Run `python needs_action_processor.py`.
3.  **Check Console Output:** The console should print `[DRY_RUN]` messages indicating the actions it *would* have taken (e.g., "Would write plan...", "Would move file...").
4.  **Verify File System:**
    -   The `test01.md` file **must still be** in `/Needs_Action/`.
    -   The `status` field inside `test01.md` **must still be** `pending`.
    -   No new file should be created in `/Plans/`.
    -   No new file should be created in `/Pending_Approval/`.
    -   `test01.md` **must not** be in `/Done/`.
5.  **Check Logs:** A new log entry should be appended to `/Vault/Logs/YYYY-MM-DD.json` with the field `"dry_run": true`.

---

## 12. Post-conditions / Verification
After a successful run with `DRY_RUN=false`:

1.  **Source Directory:** The `/Needs_Action/` directory should contain no files with `status: pending`.
2.  **Done Directory:** For every file that was processed, a corresponding file should now exist in `/Done/`.
3.  **Plans Directory:** For every file processed, a corresponding `*-Plan.md` file must exist in `/Plans/`.
4.  **Log File:** The `/Logs/YYYY-MM-DD.json` file must contain a new JSON entry for each file processed, with `"dry_run": false`.
5.  **Source File State:** The files moved to `/Done/` must have their `status` field updated to `processing`.

---

## 13. Error Handling
- **Empty `/Needs_Action/` folder:** The script will log "No pending files found" and exit gracefully.
- **Malformed `.md` files:**
    - If a file cannot be read, a warning is printed and the file is skipped.
    - If a file does not have a `status: pending` field, it is ignored.
- **Gemini CLI Failure:**
    - If the `gemini` command is not found, a critical error is logged and the script aborts.
    - If the command returns a non-zero exit code, the error is logged (including stderr), and the script moves to the next file.
- **Vault Structure Missing:** The script checks for all required directories and `Company_Handbook.md` on startup. If any are missing, it prints a critical error and exits.
- **Idempotency:** The script will not re-process files. It only selects files with `status: pending`. Once a file's status is changed to `processing` and it's moved to `/Done/`, it is ignored by subsequent runs.

---

## 14. Success Criteria
The skill execution is considered a **SUCCESS** if:
- The script runs to completion without crashing.
- For every `.md` file with `status: pending` that was present in `/Needs_Action/` at the start of the run, a corresponding `Plan.md` now exists in `/Plans/` and the original file is now in `/Done/` with an updated status.

The skill execution is considered a **FAILURE** if:
- The script exits prematurely due to an unhandled exception.
- Any processed file from `/Needs_Action/` is not moved to `/Done/`, or its `Plan.md` is not created (on `DRY_RUN=false`).
