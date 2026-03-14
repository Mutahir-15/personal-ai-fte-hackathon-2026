import shutil
import json
from pathlib import Path
from datetime import datetime
from src.lib.base_action import BaseAction
from src.config.settings import Config
from src.services.audit_logger import AuditLogger
from src.lib.locking import FileLockManager

class NeedsActionProcessor(BaseAction):
    """Processes a detected file by wrapping it in markdown metadata and moving it to /Needs_Action/."""

    def __init__(self, dry_run: bool = None):
        super().__init__(dry_run)
        self.state_file = Config.STATE_DIR / "processed_files.json"
        
        # Ensure state directory exists
        Config.STATE_DIR.mkdir(parents=True, exist_ok=True)
        Config.NEEDS_ACTION_DIR.mkdir(parents=True, exist_ok=True)

    def _get_processed_files(self) -> dict:
        """Reads the processed files state from JSON."""
        if not self.state_file.exists():
            return {"files": {}}
        
        with FileLockManager.with_lock(self.state_file):
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                self.logger.error(f"Failed to read state file: {self.state_file}. Returning empty state.")
                return {"files": {}}

    def _update_processed_files(self, file_path: Path):
        """Adds a file to the processed files list in the state file."""
        if self.dry_run:
            return

        state = self._get_processed_files()
        
        # Add entry per data-model.md
        state["files"][str(file_path.absolute())] = {
            "hash": "sha256_placeholder", # For Bronze, we use path as unique key
            "detected_at": datetime.now().isoformat(),
            "processed_at": datetime.now().isoformat()
        }

        with FileLockManager.with_lock(self.state_file):
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2)

    def _construct_gemini_prompt(self, task_content: str, handbook_content: str) -> str:
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
        return f"""
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
The output MUST be only the `Plan.md` content and nothing else.

**Plan.md Template:**
---
{plan_template}
---
"""

    def _run_gemini_cli(self, prompt: str) -> str | None:
        """Executes the gemini CLI command and returns the output."""
        import subprocess
        try:
            self.logger.info("Executing Gemini CLI for plan generation...")
            # Using the .cmd wrapper directly and passing prompt via stdin
            gemini_cmd = r"C:\Users\ADMINS\AppData\Roaming\npm\gemini.cmd"
            result = subprocess.run(
                [gemini_cmd, "--prompt", "-"], 
                input=prompt,
                capture_output=True, text=True, check=True, encoding='utf-8'
            )
            return result.stdout
        except Exception as e:
            self.logger.error(f"Gemini CLI failed: {e}")
            if hasattr(e, 'stderr'):
                self.logger.error(f"Stderr: {e.stderr}")
            return None

    def execute(self, source_path: Path):
        """Moves file to Needs_Action, creates metadata, and generates a plan."""
        source_path = Path(source_path)
        if not source_path.exists():
            self.logger.error(f"Source path does not exist: {source_path}")
            return {"status": "error", "message": "File not found"}

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        sanitized_name = source_path.name.replace(" ", "_")
        dest_filename = f"{timestamp}_{sanitized_name}"
        dest_path = Config.NEEDS_ACTION_DIR / dest_filename
        metadata_path = Config.NEEDS_ACTION_DIR / f"FILE_{sanitized_name}_{timestamp}.md"
        plan_path = Config.VAULT_ROOT / "Plans" / f"PLAN_{sanitized_name}_{timestamp}.md"

        self.logger.info(f"Processing file: {source_path.name}")

        if self.dry_run:
            self.logger.info(f"DRY RUN — would create .md file: {metadata_path.name}")
            self.logger.info(f"DRY_RUN — would generate Plan.md: {plan_path.name}")
            return {"status": "success", "message": "DRY RUN - No files created"}

        try:
            # 1. Copy file to Needs_Action
            shutil.copy2(source_path, dest_path)
            
            # 2. Create metadata file
            file_content = ""
            try:
                file_content = source_path.read_text(encoding='utf-8', errors='ignore')
            except:
                file_content = "[Binary or unreadable content]"

            metadata_content = f"""---
type: file_drop
original_name: {source_path.name}
original_path: {str(source_path.absolute())}
size_bytes: {source_path.stat().st_size}
detected_at: {datetime.now().isoformat()}
status: pending
processed: false
---

## Summary
New file detected and queued for processing.

## Content Snippet
```
{file_content[:500]}
```

## Suggested Actions
- [ ] Review file contents
- [ ] Determine required action
- [ ] Move to /Done when complete
"""
            with open(metadata_path, 'w', encoding='utf-8') as f:
                f.write(metadata_content)

            # 3. Generate Plan.md via Gemini
            handbook_path = Config.VAULT_ROOT / "Company_Handbook.md"
            handbook_content = handbook_path.read_text(encoding='utf-8') if handbook_path.exists() else "No handbook found."
            
            prompt = self._construct_gemini_prompt(metadata_content, handbook_content)
            plan_content = self._run_gemini_cli(prompt)
            
            if plan_content:
                # Post-process Plan.md
                plan_content = plan_content.replace("<ISO 8601 timestamp>", datetime.now().isoformat())
                plan_content = plan_content.replace("<original filename from /Needs_Action/>", source_path.name)
                
                with open(plan_path, 'w', encoding='utf-8') as f:
                    f.write(plan_content)
                self.logger.info(f"Generated Plan.md: {plan_path.name}")

                # 4. Check for Approval Requirement
                requires_approval = "requires_approval: true" in plan_content.lower()
                if requires_approval:
                    from src.lib.approval_manager import ApprovalManager
                    manager = ApprovalManager(dry_run=self.dry_run)
                    
                    request_id = f"REQ_{sanitized_name}_{timestamp}"
                    description = f"Approve processing for {source_path.name}. Plan generated in {plan_path.name}."
                    input_data = {
                        "source": str(source_path.absolute()),
                        "dest": str(dest_path.absolute()),
                        "metadata": str(metadata_path.absolute()),
                        "plan": str(plan_path.absolute())
                    }
                    
                    # We override the filename to match the sanitized name if needed, 
                    # but create_request uses REQ_SKILL_TIMESTAMP format.
                    # To keep it consistent with what we had, we'll manually use the manager's queue
                    # or just use create_request with skill="FILE_DROP"
                    
                    manager.create_request(
                        skill="FILE_DROP",
                        action=sanitized_name,
                        description=description,
                        input_data=input_data
                    )
                    
                    # Wait, create_request will generate its own filename.
                    # If we want REQ_{sanitized_name}_{timestamp}.md, we need to adapt.
                    # But the new ApprovalWatcher regex handles REQ_FILE_DROP_TIMESTAMP.md just fine.
                    
                    self.logger.info(f"Approval request created via manager.")
            else:
                self.logger.warning("Failed to generate Plan.md content via Gemini.")

            # 5. Update state
            self._update_processed_files(source_path)

            # 6. Log action
            AuditLogger.log(
                action_type="process_file",
                actor="needs-action-processor",
                target=str(source_path),
                parameters={
                    "dest": str(dest_path), 
                    "metadata": str(metadata_path), 
                    "plan": str(plan_path) if plan_content else None,
                    "requires_approval": requires_approval if plan_content else False,
                    "file_size": source_path.stat().st_size
                },
                status="success",
                result="File processed, metadata, plan, and approval request created" if (plan_content and requires_approval) else "File processed"
            )

            return {
                "status": "success",
                "dest_path": str(dest_path),
                "metadata_path": str(metadata_path),
                "plan_path": str(plan_path) if plan_content else None
            }

        except Exception as e:
            self.logger.error(f"Failed to process file {source_path}: {e}")
            AuditLogger.log(
                action_type="process_file",
                actor="needs-action-processor",
                target=str(source_path),
                status="error",
                error_message=str(e)
            )
            return {"status": "error", "message": str(e)}
