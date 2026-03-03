# Bronze Vault Foundation: Autonomous AI FTE (Bronze Tier)

Bronze Vault is the foundational layer for a personal autonomous AI agent, built to operate locally on Windows 10 using an Obsidian-based knowledge vault and a skill-driven architecture.

## 🏗 Architecture

- **Vault-First**: Obsidian is the single source of truth. The agent communicates with the human via folder movements and markdown files.
- **Skill-Driven**: All AI capabilities are defined as `SKILL.md` files, ensuring clear boundaries and testable behaviors.
- **Safe Autonomy**: The system defaults to `DRY_RUN=true`. Sensitive or irreversible actions require Human-in-the-Loop (HITL) approval via the `Approved/` folder.
- **Transparent**: Every action is logged in JSON format to `/Logs/` and tracked via Prompt History Records (PHR).

## 📋 Prerequisites

- **OS**: Windows 10+
- **Python**: 3.13+
- **Node.js**: Required for PM2 process management.
- **Gemini CLI**: The primary reasoning engine.
- **Obsidian**: Recommended for interacting with the vault.

## 🚀 Setup Instructions

### 1. Clone & Install
```powershell
git clone <repo-url>
cd personal-ai-fte-hackathon-2026
pip install -r requirements.txt
npm install -g pm2 pm2-startup-windows
```

### 2. Environment Configuration
Create a `.env` file in the root directory:
```env
DRY_RUN=true
VAULT_ROOT=C:/Users/<YourUser>/Obsidian/Agent_Vault
DROP_FOLDER_PATH=C:/Users/<YourUser>/Desktop/AI_Drop
```

### 3. Initialize Vault
Create the 9 required folders and 3 seed markdown files:
```powershell
python -m src.cli.init_vault
```

### 4. Configure Persistence
Register PM2 as a Windows service and start the orchestrator:
```powershell
powershell -File scripts/powershell/setup_pm2_persistence.ps1
```

## 🛠 Skill Index

| Skill | Description | Location |
|-------|-------------|----------|
| **vault-setup** | Initializes the 9-folder structure and seed files. | `.specify/skills/vault-setup/` |
| **filesystem-watcher** | Monitors the drop folder and moves files to the vault. | `.specify/skills/filesystem-watcher/` |
| **needs-action-processor** | Wraps raw files in markdown metadata for AI analysis. | `.specify/skills/needs-action-processor/` |
| **hitl-approval** | Manages the approval queue and authorization flow. | `.specify/skills/hitl-approval/` |
| **audit-logger** | Records all agent activity in auditable JSON logs. | `.specify/skills/audit-logger/` |
| **orchestrator** | Manages the lifecycle of all agent services. | `.specify/skills/orchestrator/` |
| **pm2-setup** | Ensures persistent execution on Windows 10. | `.specify/skills/pm2-setup/` |

## 🛡 Security & Safety

- **DRY_RUN**: Always check logs in `DRY_RUN=true` mode before enabling live execution.
- **HITL**: No file is moved or deleted outside of the `Approved` flow.
- **Audit Logs**: Logs are retained for 90 days in `Vault/Logs/YYYY-MM-DD.json`.
- **PHR**: All agent prompts and responses are recorded in `history/prompts/`.

## 🧪 Testing

Run the test suite to verify the foundation:
```powershell
python -m pytest tests/unit/ tests/integration/
```
