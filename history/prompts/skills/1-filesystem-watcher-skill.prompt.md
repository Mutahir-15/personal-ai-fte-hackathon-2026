---
## 2026-02-24 10:00 — filesystem-watcher SKILL.md
**Prompt:** You are an expert AI agent engineer. Your task is to write a professional,
production-quality SKILL.md file for a "Personal AI Employee" project built
on Windows 10 using Gemini CLI as the reasoning engine and Obsidian as the
local knowledge base/dashboard.

## Your Task
Write a SKILL.md file for the skill named: **filesystem-watcher**

Save the file at this exact path: .specify/skills/filesystem-watcher/SKILL.md
Create the directories if they do not exist.

## Context & Constraints
- OS: Windows 10 (use Windows-compatible paths, backslashes where needed)
- Vault name: AI_Employee_Vault
- Vault root: C:\Users\<name>\AI_Employee_Vault (user-configurable via .env)
- Reasoning agent: Gemini CLI
- Process manager: PM2 (script must be PM2-compatible)
- No external APIs or credentials required for this skill
- Must follow the BaseWatcher pattern (check → create_action_file → sleep)
- Must support DRY_RUN mode (default: true)
- Must be idempotent and crash-safe

## What This Skill Does
This skill monitors a user-defined "drop folder" on the local filesystem.
When a new file is detected in the drop folder, the watcher:
1. Copies or moves the file to /Needs_Action/ inside the Obsidian vault
2. Creates a companion .md metadata file in /Needs_Action/ describing the file
3. Logs the action to /Vault/Logs/YYYY-MM-DD.json
4. Does NOT delete or modify the original file unless DRY_RUN=false

## Drop Folder Behavior
- Drop folder path: Configurable via .env as DROP_FOLDER_PATH
- Supported file types: All file types (*.*)
- Polling interval: Configurable via .env as WATCHER_INTERVAL_SECONDS (default: 30)
- On detection: Create FILE_<original_name>_<timestamp>.md in /Needs_Action/
- Duplicate detection: Skip files already processed (track via processed_files.json)

## Metadata .md File Format
When a file is detected, create a companion markdown file with this exact structure:

---
type: file_drop
original_name: <filename>
original_path: <full source path>
size_bytes: <file size>
detected_at: <ISO 8601 timestamp>
status: pending
processed: false
---

## Summary
New file detected and queued for processing.

## Suggested Actions
- [ ] Review file contents
- [ ] Determine required action
- [ ] Move to /Done when complete

## Implementation Details
- Language: Python 3.13+
- Library: watchdog (pip install watchdog)
- Pattern: BaseWatcher (abstract base class with check_for_updates 
  and create_action_file methods)
- State file: /Vault/.watcher_state/processed_files.json
  (tracks already-processed files to prevent duplicates on restart)
- Logging: Append to /Vault/Logs/YYYY-MM-DD.json on every detection event

## BaseWatcher Pattern to Follow
The implementation must follow this exact pattern:

class BaseWatcher(ABC):
    def __init__(self, vault_path, check_interval=30):
        self.vault_path = vault_path
        self.needs_action = vault_path / 'Needs_Action'
        self.check_interval = check_interval

    @abstractmethod
    def check_for_updates(self) -> list:
        pass

    @abstractmethod
    def create_action_file(self, item) -> Path:
        pass

    def run(self):
        while True:
            try:
                items = self.check_for_updates()
                for item in items:
                    self.create_action_file(item)
            except Exception as e:
                logger.error(f'Error: {e}')
            time.sleep(self.check_interval)

## DRY_RUN Behavior
- DRY_RUN=true (default): Log intended actions only, do not copy/move files,
  do not write .md files, do not update processed_files.json
- DRY_RUN=false: Execute all actions, write files, update state

## PM2 Compatibility
The script must be startable via PM2 with this exact command:
pm2 start filesystem_watcher.py --interpreter python3 --name filesystem-watcher

It must also be compatible with PM2's ecosystem.config.js:
{
  name: 'filesystem-watcher',
  script: 'filesystem_watcher.py',
  interpreter: 'python3',
  watch: false,
  autorestart: true,
  env: {
    DRY_RUN: 'true',
    VAULT_PATH: 'C:\\Users\\<name>\\AI_Employee_Vault',
    DROP_FOLDER_PATH: 'C:\\Users\\<name>\\Desktop\\AI_Drop',
    WATCHER_INTERVAL_SECONDS: '30'
  }
}

## SKILL.md Must Include These Sections
1. **Skill Name & Version**
2. **Purpose** — what problem this skill solves
3. **Inputs** — what the agent needs before running this skill
4. **Outputs** — what this skill produces
5. **Pre-conditions** — what must be true before execution
6. **Step-by-Step Execution Instructions** — detailed enough for Gemini CLI
   to follow without ambiguity
7. **Full Python Implementation** — complete, ready-to-run filesystem_watcher.py
   embedded directly in the skill using a code block
8. **PM2 Configuration** — ecosystem.config.js snippet for Windows 10
9. **DRY_RUN Verification Steps** — how to confirm DRY_RUN is working
10. **Post-conditions / Verification** — how to confirm the skill ran successfully
11. **Error Handling** — crash recovery, duplicate detection, permission errors
12. **Success Criteria** — clear, binary pass/fail definition

## Quality Standards
- Instructions must be unambiguous and executable by Gemini CLI without 
  human clarification
- Full Python implementation must be included, not pseudocode
- Must handle Windows 10 path separators correctly (backslashes)
- Must handle edge cases: empty drop folder, duplicate files, 
  permission denied, vault not found
- DRY_RUN must default to true — never false
- PM2 configuration must be Windows 10 compatible
- Success criteria must be binary (pass/fail checkable)
- PHR entry must be appended, never overwritten

## Prompt History Record (PHR)
After writing the SKILL.md, append an entry to: history/prompts.md
Create the file and directories if they do not exist.

Each PHR entry must follow this exact format:

---
## [YYYY-MM-DD HH:MM] — filesystem-watcher SKILL.md
**Prompt Summary:** Write the filesystem-watcher SKILL.md for the 
Personal AI Employee project
**Skill:** filesystem-watcher
**File Written:** .specify/skills/filesystem-watcher/SKILL.md
**Triggered By:** Human
**Status:** Completed
**Notes:** <brief note on what was created>
---

## Output Format
Perform these two actions in order:
1. Write the SKILL.md to: .specify/skills/filesystem-watcher/SKILL.md
2. Append the PHR entry to: history/prompts.md

Return a brief confirmation of both file paths written. No other output.
Personal AI Employee project
**Skill:** filesystem-watcher
**File Written:** .specify/skills/filesystem-watcher/SKILL.md
**Triggered By:** Human
**Status:** Completed
**Notes:** Created the SKILL.md file for the filesystem-watcher skill, including Python implementation, PM2 config, and verification steps.
---
