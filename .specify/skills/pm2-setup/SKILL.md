# SKILL: pm2-setup

**Version:** 1.0.0
**Author:** Gemini CLI

---

## 1. Skill Name & Version
- **Name:** `pm2-setup`
- **Version:** `1.0.0`

---

## 2. Purpose
This skill provides a one-time, idempotent setup procedure to configure PM2 as a robust, persistent process manager on Windows 10. Standard script execution on Windows is fragile; processes terminate when terminals close and do not restart on crash or reboot. This skill solves that by installing and configuring PM2 to daemonize all agent processes, manage logs, and persist across system reboots, transforming the agent from a transient script into a reliable, 24/7 service.

---

## 3. Inputs
- **Node.js:** v24+ LTS installed and available in the system PATH.
- **Python:** v3.13+ installed and available in the system PATH.
- **npm:** A functioning Node Package Manager, installed with Node.js.
- **Project Root Path:** The absolute path to the root of the `personal-ai-fte-hackathon-2026` project.

---

## 4. Outputs
- A globally installed and running PM2 daemon.
- A fully configured `ecosystem.config.js` file at the project root.
- Windows Task Scheduler entry for PM2 to ensure persistence on boot.
- A `PM2_Cheatsheet.md` file in the `/Vault/` directory.
- All agent processes registered and running under PM2.

---

## 5. Pre-conditions
- Windows 10 operating system.
- Administrative privileges may be required to install global npm packages and create a startup task.
- Node.js v24+ and Python 3.13+ must be installed and correctly configured in the system's PATH environment variable.

---

## 6. 8-Step Installation Sequence
This skill is executed as a series of shell commands. Each step must be verified before proceeding to the next.

**STEP 1 — Verify Prerequisites:**
Execute these commands and validate their output:
1.  `node --version`: Must return a version string starting with `v24.` or higher.
2.  `python --version`: Must return a version string starting with `Python 3.13.` or higher.
3.  `npm --version`: Must return a valid version string.
*If any check fails, execution must stop, and the user must be informed of the missing prerequisite.*

**STEP 2 — Install PM2:**
Execute the global installation command:
- `npm install -g pm2`
Then verify the installation:
- `pm2 --version`: Must return a valid PM2 version string.
*If this fails, report a CRITICAL error and suggest troubleshooting steps (e.g., checking npm configuration, running as Administrator).*

**STEP 3 — Install Windows Startup Package:**
Execute the following commands in order:
1.  `npm install -g pm2-startup-windows`: Installs the persistence package.
2.  `pm2-startup-windows install`: Creates the startup entry in Windows Task Scheduler. A success message should be displayed.
*If this fails, provide the user with manual instructions for creating a Task Scheduler entry as a fallback.*

**STEP 4 — Create ecosystem.config.js:**
Generate the complete `ecosystem.config.js` file content (as defined in the next section) and write it to the project root directory. The agent must dynamically replace placeholders like `<project_root>` and `<name>` with the correct values from the user's environment.

**STEP 5 — Register Processes:**
Execute these commands from the project root directory:
1.  `pm2 start ecosystem.config.js`: Starts all applications defined in the config file.
2.  `pm2 save`: Saves the process list, enabling it to be resurrected on boot.
3.  `pm2 ls`: Displays the list of running processes. All apps should show status `online`.

**STEP 6 — Configure Log Rotation:**
Execute these commands to set up automatic log rotation:
1.  `pm2 install pm2-logrotate`
2.  `pm2 set pm2-logrotate:max_size 10M`
3.  `pm2 set pm2-logrotate:retain 30`
4.  `pm2 set pm2-logrotate:compress true`

**STEP 7 — Verify Health:**
Execute these commands to confirm the system is running correctly:
1.  `pm2 status`: Verify all processes show `online`.
2.  `pm2 logs --lines 20`: Check for any immediate errors in the logs.

**STEP 8 — Create PM2 Cheatsheet:**
Generate the content for `PM2_Cheatsheet.md` (as defined in a later section) and write it to the `VAULT_PATH/PM2_Cheatsheet.md` file.

---

## 7. Complete ecosystem.config.js
This content must be written to `ecosystem.config.js` in the project root. Placeholders must be replaced dynamically.

```javascript
// ecosystem.config.js
module.exports = {
  apps: [
    {
      name: 'orchestrator',
      script: '.\specify\skills\orchestrator\orchestrator.py',
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
        SESSION_PREFIX: 'AI_EMP',
        PYTHONPATH: '<project_root>'
      }
    },
    {
      name: 'hitl-approval',
      script: '.\specify\skills\hitl-approval\hitl_approval.py',
      interpreter: 'python3',
      cwd: '<project_root>',
      watch: false,
      autorestart: true,
      max_restarts: 10,
      restart_delay: 5000,
      log_date_format: 'YYYY-MM-DD HH:mm:ss',
      error_file: 'C:\Users\<name>\.pm2\logs\hitl-approval-error.log',
      out_file: 'C:\Users\<name>\.pm2\logs\hitl-approval-out.log',
      env: {
        DRY_RUN: 'true',
        VAULT_PATH: 'C:\Users\<name>\AI_Employee_Vault',
        PYTHONPATH: '<project_root>'
      }
    }
  ]
};
```

---

## 8. PM2 Cheatsheet
This content must be written to `/Vault/PM2_Cheatsheet.md`.

```markdown
# PM2 Cheatsheet — Personal AI Employee

## Daily Commands
| Command | Description |
|---------|-------------|
| pm2 status | Show all process statuses |
| pm2 logs | Stream all logs live |
| pm2 logs orchestrator | Stream orchestrator logs only |
| pm2 logs hitl-approval | Stream HITL watcher logs only |
| pm2 flush | Clear all log files |

## Process Control
| Command | Description |
|---------|-------------|
| pm2 start ecosystem.config.js | Start all processes |
| pm2 stop all | Stop all processes |
| pm2 restart all | Restart all processes |
| pm2 reload all | Zero-downtime reload |
| pm2 delete all | Remove all processes from PM2 |

## Individual Process Control
| Command | Description |
|---------|-------------|
| pm2 start orchestrator | Start orchestrator only |
| pm2 stop orchestrator | Stop orchestrator only |
| pm2 restart orchestrator | Restart orchestrator only |
| pm2 start hitl-approval | Start HITL watcher only |
| pm2 stop hitl-approval | Stop HITL watcher only |

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
```

---

## 9. Windows 10 Specific Notes
- **Paths:** Always use double backslashes (``) for paths within the `ecosystem.config.js` file, as it is a JavaScript file.
- **Python Alias:** Windows does not have a `python3` alias by default. If `python3` is not in your PATH, PM2 will fail to find the interpreter. You can create a permanent alias or ensure your Python 3 installation is named `python3.exe` and is in the PATH. A temporary fix for the current shell is `doskey python3=python $*`.
- **Task Scheduler:** `pm2-startup-windows` works by creating an entry in the Windows Task Scheduler. You can view or debug it by running `Task Scheduler` and looking for a task named "PM2".
- **Logs Location:** PM2's centralized logs are typically stored at `C:\Users\<YourUsername>\.pm2\logs`.

---

## 10. Verification Steps
To verify a successful setup, execute the following in order:
1.  **`pm2 status`**: The expected output is a table where both `orchestrator` and `hitl-approval` show the status `online`.
2.  **`pm2 logs --lines 10`**: The expected output is a stream of the last 10 log lines from all processes with no `ERROR` or `CRITICAL` messages related to startup.
3.  **Reboot Test**: Restart Windows. After logging back in, open a terminal and run `pm2 status`. The expected output is that all processes are `online` without any manual intervention.
4.  **Crash Test**: Manually kill a process with `pm2 stop orchestrator`. The expected behavior is that PM2 automatically restarts it within the configured `restart_delay` (5 seconds). Verify with `pm2 status`.

---

## 11. Troubleshooting Guide
- **Process in `errored` state:** Run `pm2 logs <name>` to inspect the specific error. This is often due to a syntax error in the Python script or a missing dependency.
- **`python3: command not found`:** PM2 cannot find the Python interpreter. See the "Python Alias" note in the "Windows 10 Specific Notes" section.
- **Processes not starting on boot:**
    - Re-run `pm2-startup-windows install`.
    - Open Windows Task Scheduler and check that the "PM2" task is present and enabled.
    - Ensure you ran `pm2 save` after starting the processes.
- **`EPERM` or permission errors:** Try running the command prompt or PowerShell as an Administrator, especially for global `npm` installs and `pm2-startup-windows`.

---

## 12. Post-conditions / Verification
A successful execution of this skill is confirmed when:
- The `ecosystem.config.js` file exists at the project root.
- The `PM2_Cheatsheet.md` file exists in the vault.
- The command `pm2 status` shows `orchestrator` and `hitl-approval` as `online`.
- The Windows Task Scheduler contains an enabled task for PM2.

---

## 13. Error Handling
- **Node.js/Python Not Found:** The skill must abort at Step 1 with a clear message instructing the user to install the required version.
- **PM2 Install Fails:** The skill must abort at Step 2, suggesting the user check their `npm` configuration and internet connection, or try running as Administrator.
- **Task Scheduler Permission Denied:** The skill must abort at Step 3, informing the user that it could not create the startup task and providing a link to manual instructions.
- **Python Not In PATH:** If `pm2 start` fails because `python3` is not found, the error must be reported with a suggestion to create a `python3` alias.

---

## 14. Success Criteria
The skill execution is a **SUCCESS** if and only if all 8 installation steps are completed without error, and the verification command `pm2 status` shows all defined processes as `online`.

The execution is a **FAILURE** if any of the 8 steps fail to complete successfully.
