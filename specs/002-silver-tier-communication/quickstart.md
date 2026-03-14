# Quickstart: Silver Tier Setup

## Prerequisites
- Completed Bronze Tier (Vault structure, PM2 running).
- Node.js v24+ LTS.
- Python 3.13+.

## Step 1: Install Dependencies
```powershell
# Python
pip install google-auth-oauthlib google-api-python-client playwright requests requests-oauthlib
playwright install chromium

# Node.js (Email MCP)
cd src/email-mcp
npm install
```

## Step 2: Environment Variables
Add the following to your root `.env`:
```ini
# Gmail
GMAIL_CREDENTIALS_PATH=credentials.json
GMAIL_TOKEN_PATH=AI_Employee_Vault\.watcher_state\gmail_token.json

# WhatsApp
WHATSAPP_SESSION_PATH=AI_Employee_Vault\.watcher_state\whatsapp_session
WHATSAPP_KEYWORDS=urgent,asap,help

# LinkedIn
LINKEDIN_CLIENT_ID=your_id
LINKEDIN_CLIENT_SECRET=your_secret
LINKEDIN_AUTHOR_URN=urn:li:person:your_id

# HITL
ESCALATION_WARNING_HOURS=4
ESCALATION_CRITICAL_HOURS=20
```

## Step 3: First-Run Authentication
1. **Gmail**: Run `python src/services/gmail_watcher.py` manually once to open the browser and save `gmail_token.json`.
2. **WhatsApp**: Run `python src/services/whatsapp_watcher.py` with `HEADLESS=false` to scan the QR code.
3. **LinkedIn**: Follow the OAuth2 flow defined in `linkedin-poster` SKILL.md.

## Step 4: Register MCP Server
Add this to `%APPDATA%\gemini-cli\mcp.json`:
```json
{
  "servers": [
    {
      "name": "email",
      "command": "node",
      "args": ["C:\\path\\to\\src\\email-mcp\\index.js"],
      "env": {
        "VAULT_PATH": "C:\\path\\to\\AI_Employee_Vault"
      }
    }
  ]
}
```

## Step 5: Start PM2
```powershell
pm2 start ecosystem.config.js
pm2 save
```
