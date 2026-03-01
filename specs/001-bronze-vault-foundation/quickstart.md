# Quickstart: Bronze Vault Foundation

## 1. Prerequisites
- Windows 10
- Python 3.13+
- Node.js (for PM2)
- Obsidian (Knowledge Base GUI)
- Gemini CLI installed and configured

## 2. Installation
1.  Clone the repository.
2.  Install dependencies:
    ```powershell
    pip install -r requirements.txt
    npm install -g pm2 pm2-startup-windows
    ```
3.  Configure environment variables:
    ```powershell
    cp .env.example .env
    # Edit .env and set VAULT_ROOT to your desired Obsidian path
    ```

## 3. Initialization
Run the vault setup skill to create the folder structure and seed files:
```powershell
python -m src.cli.init_vault
```

## 4. Start the System
Register and start the processes with PM2:
```powershell
pm2 start ecosystem.config.js
pm2 save
pm2-startup install
```

## 5. Usage
1.  Open Obsidian and point it to your `VAULT_ROOT`.
2.  Drop a file into the `/Needs_Action/` folder.
3.  Check `/Logs/` to see the filesystem watcher detect the file.
4.  Check `Dashboard.md` for a real-time status update.

## 6. Safe Execution
All scripts default to `DRY_RUN=true`. To enable live execution, set `DRY_RUN=false` in your `.env` file after verifying behavior in logs.
