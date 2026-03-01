# Data Model: Bronze Vault Foundation

## 1. Audit Log Entry (`Logs/YYYY-MM-DD.json`)
The audit log is a JSON array of objects, one per agent action.

```json
{
  "timestamp": "ISO-8601 string",
  "agent_id": "string (e.g., gemini-cli-1)",
  "skill": "string (e.g., filesystem-watcher)",
  "action": "string (e.g., file_detected)",
  "input": "object | string",
  "output": "object | string",
  "status": "string (success | error | dry_run)",
  "metadata": {
    "file_path": "string",
    "execution_time_ms": "number",
    "dry_run": "boolean"
  }
}
```

## 2. Watcher State (`.watcher_state/processed_files.json`)
A mapping to prevent duplicate processing of the same file.

```json
{
  "files": {
    "absolute_path_to_file": {
      "hash": "sha256 string",
      "detected_at": "ISO-8601",
      "processed_at": "ISO-8601 | null"
    }
  }
}
```

## 3. Session State (`.watcher_state/current_session.json`)
Tracking the current runtime status.

```json
{
  "session_id": "uuid string",
  "start_time": "ISO-8601",
  "last_heartbeat": "ISO-8601",
  "active_processes": ["orchestrator", "watcher", "processor"],
  "stats": {
    "actions_processed": 0,
    "errors_encountered": 0
  }
}
```

## 4. HITL Approval Queue (`.watcher_state/approved_actions.json`)
List of actions approved by moving files to `/Approved/`.

```json
{
  "approved": [
    {
      "request_id": "uuid string",
      "approved_at": "ISO-8601",
      "original_request_file": "string (path in /Pending_Approval/)",
      "action_type": "string"
    }
  ]
}
```
