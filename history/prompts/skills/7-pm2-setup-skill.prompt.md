
---
## [2026-02-26 17:14] — pm2-setup SKILL.md
**Skill:** pm2-setup
**File Written:** .specify/skills/pm2-setup/SKILL.md
**Triggered By:** Human
**Status:** Completed

**Full Prompt:**
```
You are an expert AI agent engineer. Your task is to write a professional,
production-quality SKILL.md file for a "Personal AI Employee" project built
on Windows 10 using Gemini CLI as the reasoning engine and Obsidian as the
local knowledge base/dashboard.

## Your Task
Write a SKILL.md file for the skill named: **pm2-setup**

Save the file at this exact path: .specify/skills/pm2-setup/SKILL.md
Create the directories if they do not exist.

## Prompt History Record (PHR)
After writing the SKILL.md, append an entry to: history/prompts/skills
Create the file and directories if they do not exist.

Each PHR entry must follow this exact format:

---
## [YYYY-MM-DD HH:MM] — pm2-setup SKILL.md
**Skill:** pm2-setup
**File Written:** .specify/skills/pm2-setup/SKILL.md
**Triggered By:** Human
**Status:** Completed

**Full Prompt:**
<Paste the entire prompt that was given to you here, verbatim,
inside a markdown code block>

**Notes:** <brief note on what was created>
---

## Context & Constraints
- OS: Windows 10 ONLY (no Linux/Mac commands)
- Vault name: AI_Employee_Vault
- Vault root: Configurable via .env as VAULT_PATH
- Reasoning agent: Gemini CLI
- Node.js: v24+ LTS required
- Python: 3.13+ required
- This skill sets up PM2 as the process manager for ALL watcher
  scripts and the Orchestrator
- Must handle Windows 10 startup persistence via pm2-startup-windows

## What This Skill Does
This skill configures PM2 as the persistent process manager for the
entire Personal AI Employee system on Windows 10. It:
1. Verifies Node.js v24+ and Python 3.13+ are installed
2. Installs PM2 globally via npm
3. Installs pm2-startup-windows for boot persistence on Windows 10
4. Creates the complete ecosystem.config.js for all Bronze tier
   components
5. Registers all processes with PM2
6. Configures PM2 to start automatically on Windows 10 boot
7. Verifies all processes are running and healthy
8. Sets up PM2 log rotation to prevent disk fill
9. Creates a PM2 management cheatsheet in the vault at
   /Vault/PM2_Cheatsheet.md
10. Logs setup completion to audit-logger

## Why PM2 on Windows 10
Standard Python scripts run in terminal are fragile on Windows 10:
- They die when the terminal is closed
- They crash on unhandled exceptions and do not restart
- They do not survive system reboots
- They have no centralized log management

PM2 solves all of these by:
- Daemonizing scripts (run in background, survive terminal close)
- Auto-restarting on crash with configurable delay
- Persisting across reboots via pm2-startup-windows
- Centralizing logs at: C:\Users\<name>\.pm2\logs

## Installation Steps

STEP 1 — Verify Prerequisites:
- Check Node.js version: node --version (must be v24+)
- Check Python version: python --version (must be 3.13+)
- Check npm version: npm --version
- If any check fails: log error with installation instructions and exit

STEP 2 — Install PM2:
- Run: npm install -g pm2
- Verify: pm2 --version
- If installation fails: log CRITICAL error with troubleshooting steps

STEP 3 — Install Windows Startup Package:
- Run: npm install -g pm2-startup-windows
- Run: pm2-startup-windows install
- Verify startup entry created in Windows Task Scheduler
- If fails: provide manual Task Scheduler setup instructions as fallback

STEP 4 — Create ecosystem.config.js:
- Write complete ecosystem.config.js to project root
- Include all Bronze tier components:
  - orchestrator
  - filesystem-watcher
- All DRY_RUN defaults to true
- All paths must use Windows-compatible double backslashes

STEP 5 — Register Processes:
- Run: pm2 start ecosystem.config.js
- Verify all processes show status: online
- Run: pm2 save (freeze process list)
- Run: pm2 ls (display all running processes)

STEP 6 — Configure Log Rotation:
- Run: pm2 install pm2-logrotate
- Configure max log size: 10MB
- Configure retention: 30 days
- Configure compression: true

STEP 7 — Verify Health:
- Run: pm2 status (all processes must show online)
- Run: pm2 logs --lines 20 (verify no startup errors)
- Write health summary to /Vault/Dashboard.md PM2 section

STEP 8 — Create PM2 Cheatsheet:
- Write PM2_Cheatsheet.md to /Vault/PM2_Cheatsheet.md
- Include all common PM2 commands for Windows 10

## Complete ecosystem.config.js
The skill must generate this exact file:

module.exports = {
  apps: [
    {
      name: 'orchestrator',
      script: 'orchestrator.py',
      interpreter: 'python3',
      cwd: '<project_root>',
      watch: false,
      autorestart: true,
      max_restarts: 10,
      restart_delay: 5000,
      log_date_format: 'YYYY-MM-DD HH:mm:ss',
      error_file: 'C:\Users\<name>\.pm2\logs\orchestrator-error.log',
      out_file: 'C:\Users\<name>\.pm2\logs\orchestrator-out.log',
      env: {
        DRY_RUN: 'true',
        VAULT_PATH: 'C:\Users\<name>\AI_Employee_Vault',
        DROP_FOLDER_PATH: 'C:\Users\<name>\Desktop\AI_Drop',
        WATCHER_INTERVAL_SECONDS: '30',
        LOG_RETENTION_DAYS: '90',
        SESSION_PREFIX: 'AI_EMP'
      }
    },
    {
      name: 'filesystem-watcher',
      script: 'filesystem_watcher.py',
      interpreter: 'python3',
      cwd: '<project_root>',
      watch: false,
      autorestart: true,
      max_restarts: 10,
      restart_delay: 5000,
      log_date_format: 'YYYY-MM-DD HH:mm:ss',
      error_file: 'C:\Users\<name>\.pm2\logs\filesystem-watcher-error.log',
      out_file: 'C:\Users\<name>\.pm2\logs\filesystem-watcher-out.log',
      env: {
        DRY_RUN: 'true',
        VAULT_PATH: 'C:\Users\<name>\AI_Employee_Vault',
        DROP_FOLDER_PATH: 'C:\Users\<name>\Desktop\AI_Drop',
        WATCHER_INTERVAL_SECONDS: '30'
      }
    }
  ]
}

## PM2 Cheatsheet Template
Write this to /Vault/PM2_Cheatsheet.md:

# PM2 Cheatsheet — Personal AI Employee

## Daily Commands
| Command | Description |
|---------|-------------|
| pm2 status | Show all process statuses |
| pm2 logs | Stream all logs live |
| pm2 logs orchestrator | Stream orchestrator logs only |
| pm2 logs filesystem-watcher | Stream watcher logs only |
| pm2 flush | Clear all log files |

## Process Control
| Command | Description |
|---------|-------------|
| pm2 start ecosystem.config.js | Start all processes |
| pm2 stop all | Stop all processes |
| pm2 restart all | Restart all processes |
| pm2 reload all | Zero-downtime reload |
| pm2 delete all | Remove all processes |

## Individual Process Control
| Command | Description |
|---------|-------------|
| pm2 start orchestrator | Start orchestrator only |
| pm2 stop orchestrator | Stop orchestrator only |
| pm2 restart orchestrator | Restart orchestrator only |
| pm2 start filesystem-watcher | Start watcher only |
| pm2 stop filesystem-watcher | Stop watcher only |

## Persistence Commands
| Command | Description |
|---------|-------------|
| pm2 save | Save current process list for reboot |
| pm2 resurrect | Manually restore saved process list |
| pm2-startup-windows install | Re-enable boot startup |
| pm2-startup-windows uninstall | Disable boot startup |

## Monitoring
| Command | Description |
|---------|-------------|
| pm2 monit | Real-time CPU and memory monitor |
| pm2 info orchestrator | Detailed process information |
| pm2 describe orchestrator | Full process metadata |

## Log Rotation
| Command | Description |
|---------|-------------|
| pm2 install pm2-logrotate | Install log rotation |
| pm2 set pm2-logrotate:max_size 10M | Set max log size |
| pm2 set pm2-logrotate:retain 30 | Keep 30 days of logs |
| pm2 set pm2-logrotate:compress true | Enable compression |

## Troubleshooting
- Process keeps restarting: pm2 logs <name> to check errors
- Process not starting on boot: re-run pm2-startup-windows install
- Logs filling disk: pm2 flush then check pm2-logrotate config
- Wrong Python version: verify interpreter path in ecosystem.config.js

## Required .env Variables for PM2
PROJECT_ROOT=C:\Users\<name>\personal-ai-employee
VAULT_PATH=C:\Users\<name>\AI_Employee_Vault
DROP_FOLDER_PATH=C:\Users\<name>\Desktop\AI_Drop
DRY_RUN=true
WATCHER_INTERVAL_SECONDS=30
LOG_RETENTION_DAYS=90

## Windows 10 Specific Notes
- PM2 on Windows requires Node.js in PATH
- pm2-startup-windows uses Windows Task Scheduler (not systemd)
- Use double backslashes in all paths inside ecosystem.config.js
- Python must be accessible as 'python3' in PATH
  (add alias if needed: doskey python3=python $*)
- PM2 logs stored at: C:\Users\<name>\.pm2\logs
- Task Scheduler entry name: PM2

## Verification Commands
After setup run these in order to verify:

1. pm2 status
   Expected: All processes show status "online"

2. pm2 logs --lines 5
   Expected: No ERROR or CRITICAL entries

3. Restart Windows and verify:
   Expected: pm2 status shows all processes running after reboot

4. Kill orchestrator manually and verify:
   Expected: PM2 restarts it within restart_delay (5 seconds)

## SKILL.md Must Include These Sections
1. **Skill Name & Version**
2. **Purpose** — why PM2 is essential for Windows 10 persistence
3. **Inputs** — Node.js, Python, npm, project root path
4. **Outputs** — running PM2 daemon, ecosystem.config.js,
   PM2_Cheatsheet.md, boot persistence
5. **Pre-conditions** — Node.js v24+, Python 3.13+, npm available
6. **8-Step Installation Sequence** — exact ordered steps
7. **Complete ecosystem.config.js** — fully populated for Windows 10
8. **PM2 Cheatsheet** — complete markdown table embedded in skill
9. **Windows 10 Specific Notes** — path handling, python3 alias,
   Task Scheduler details
10. **Verification Steps** — 4-step verification including reboot test
11. **Troubleshooting Guide** — common Windows 10 PM2 issues
12. **Post-conditions / Verification** — how to confirm skill ran
    successfully
13. **Error Handling** — Node.js not found, PM2 install fails,
    Task Scheduler permission denied, Python not in PATH
14. **Success Criteria** — clear, binary pass/fail definition

## Quality Standards
- Instructions must be unambiguous and executable by Gemini CLI
  without human clarification
- All commands must be Windows 10 CMD/PowerShell compatible
- No Linux or Mac specific commands anywhere
- All paths must use double backslashes
- Python3 alias issue on Windows 10 must be explicitly addressed
- Reboot persistence must be verified, not assumed
- DRY_RUN does not apply to this setup skill —
  it is a one-time configuration skill
- Success criteria must be binary (pass/fail checkable)
- PHR entry must be appended to history/prompts/skills,
  never overwritten

## Output Format
Perform these two actions in order:
1. Write the SKILL.md to: .specify/skills/pm2-setup/SKILL.md
2. Append the PHR entry to: history/prompts/skills

Return a brief confirmation of both file paths written. No other output.
```

**Notes:** Created the complete `SKILL.md` for the `pm2-setup` skill. This skill is a procedural guide for the agent to install and configure the PM2 process manager on Windows 10 for persistence and reliability.
---
