# Research: Bronze Vault Foundation

## 1. PM2 Persistence on Windows 10
- **Decision**: Use `pm2-startup-windows` or `NSSM` to ensure PM2 survives reboots.
- **Rationale**: Windows does not have a native `pm2 startup` command like Linux.
- **Best Practices**:
    - Set `PM2_HOME` as a system environment variable (e.g., `C:\ProgramData\pm2\.pm2`).
    - Use an `ecosystem.config.js` for process management.
    - Use the `-u` flag in Python for unbuffered logging to see output in `pm2 logs` immediately.
- **Alternatives Considered**: Windows Task Scheduler (rejected as less manageable than PM2 for multiple scripts).

## 2. Filesystem Monitoring with `watchdog`
- **Decision**: Use the Python `watchdog` library with the native `Observer`.
- **Rationale**: It uses the efficient `ReadDirectoryChangesW` API on Windows, avoiding high-CPU polling.
- **Best Practices**:
    - Implement a small delay (debounce) in `on_created` to ensure files are fully written before processing.
    - Use `time.sleep(1)` in the main loop to keep the process alive efficiently.
- **Alternatives Considered**: `polling` (rejected due to high CPU/latency).

## 3. File Integrity & Locking
- **Decision**: Use the `filelock` library for inter-process synchronization.
- **Rationale**: `filelock` provides a clean `with` statement abstraction over the native `msvcrt.locking` on Windows.
- **Best Practices**:
    - Always use a separate `.lock` file (e.g., `audit.json.lock`) to avoid "Permission Denied" errors on the data file itself.
    - Use `timeout` in `acquire()` to prevent deadlocks.
- **Alternatives Considered**: Direct `msvcrt.locking` (rejected as too low-level and error-prone regarding byte offsets).

## 4. Gemini CLI Integration
- **Decision**: Absolute path-based interaction via Python `subprocess`.
- **Rationale**: Ensures the CLI can reliably find the vault and configuration regardless of the current working directory of the PM2 process.
- **Best Practices**:
    - Wrap CLI calls in a safety layer that checks for `DRY_RUN` environment variables.
    - Log all CLI inputs/outputs to the audit log.
