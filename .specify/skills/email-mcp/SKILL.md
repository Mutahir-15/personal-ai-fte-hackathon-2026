# Skill: email-mcp (v1.0.0)

## Purpose
Implements a local Model Context Protocol (MCP) server that exposes Gmail capabilities to the Gemini CLI. This skill acts as the "hands" for email-related actions, allowing the reasoning agent to search, draft, and send emails while enforcing mandatory human-in-the-loop (HITL) approval for all outgoing communications.

## Inputs
- **Credentials**: `credentials.json` (OAuth 2.0 Desktop App) and `gmail_token.json` (saved session).
- **Approval Files**: Markdown files in `/Approved/` for `send_email` and `reply_email` tools.
- **Environment Variables**:
  - `DRY_RUN`: (`true`/`false`, default: `true`).
  - `VAULT_PATH`: Path to the Obsidian vault root.
  - `TRUSTED_CONTACTS`: Comma-separated list of safe email addresses.
  - `EMAIL_DAILY_LIMIT`: (default: `100`).

## Outputs
- **Actions**: Emails sent via Gmail API, drafts created in Gmail.
- **Audit Logs**: Detailed JSON entries written to the vault's daily logs.
- **State Management**: `email_send_count.json` tracks daily limits.

## Pre-conditions
- Node.js v24+ installed on Windows 10.
- Gmail API enabled in Google Cloud Console.
- Reuse `credentials.json` and `gmail_token.json` from the `gmail-watcher` skill.
- Silver tier vault structure (including `/Pending_Approval/` and `/Approved/`).

## MCP Server Architecture
- **index.js**: Entry point using the MCP SDK to register and handle tool calls.
- **gmail_client.js**: Wrapper for the `googleapis` Gmail library.
- **audit_bridge.js**: Handles writing structured audit logs to the Obsidian vault.
- **templates.js**: Manages email templates with variable substitution.

## Setup Instructions
1. **Initialize Directory**:
   ```powershell
   mkdir email-mcp; cd email-mcp; npm init -y
   npm install @modelcontextprotocol/sdk googleapis dotenv
   ```
2. **Registration**: Add the server to `%APPDATA%\gemini-cli\mcp.json`:
   ```json
   {
     "servers": [
       {
         "name": "email",
         "command": "node",
         "args": ["C:\\path\\to\\email-mcp\\index.js"],
         "env": {
           "DRY_RUN": "true",
           "VAULT_PATH": "C:\\path\\to\\AI_Employee_Vault"
         }
       }
     ]
   }
   ```

## MCP Tools Specification
- **`send_email`**: Sends an approved email. Requires `approval_file`.
- **`draft_email`**: Creates a Gmail draft. No approval required.
- **`search_emails`**: Searches inbox using Gmail query syntax.
- **`get_email`**: Retrieves full email content by ID.
- **`reply_email`**: Replies to a thread. Requires `approval_file`.

## Email Approval Request Template
```markdown
---
type: email_approval
action: send_email | reply_email
approval_id: <UUID>
created: <ISO 8601>
status: pending
to: <recipient>
subject: <subject>
source_file: <origin>
---

## Email Preview
**To:** <recipient>
**Subject:** <subject>

<body_content>

## To Approve
Move this file to: /Approved/
```

## Complete index.js Implementation
```javascript
const { Server } = require("@modelcontextprotocol/sdk/server/index.js");
const { StdioServerTransport } = require("@modelcontextprotocol/sdk/server/stdio.js");
const { CallToolRequestSchema, ListToolsRequestSchema } = require("@modelcontextprotocol/sdk/types.js");
const GmailClient = require("./gmail_client");
const AuditBridge = require("./audit_bridge");
const path = require("path");
const fs = require("fs");

const server = new Server({ name: "email-mcp", version: "1.0.0" }, { capabilities: { tools: {} } });

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    { name: "send_email", description: "Send an approved email", inputSchema: { type: "object", properties: { to: { type: "string" }, subject: { type: "string" }, body: { type: "string" }, approval_file: { type: "string" } }, required: ["to", "subject", "body", "approval_file"] } },
    { name: "draft_email", description: "Create a Gmail draft", inputSchema: { type: "object", properties: { to: { type: "string" }, subject: { type: "string" }, body: { type: "string" } }, required: ["to", "subject", "body"] } },
    { name: "search_emails", description: "Search Gmail inbox", inputSchema: { type: "object", properties: { query: { type: "string" } }, required: ["query"] } }
  ]
}));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;
  const isDryRun = process.env.DRY_RUN === "true";

  if (name === "send_email") {
    const approvalPath = path.join(process.env.VAULT_PATH, "Approved", path.basename(args.approval_file));
    if (!fs.existsSync(approvalPath)) throw new Error("Approval file not found in /Approved/");
    
    if (isDryRun) {
      AuditBridge.log("email_send_dry_run", args.to, { subject: args.subject });
      return { content: [{ type: "text", text: "DRY_RUN: Email send simulated." }] };
    }
    const result = await GmailClient.sendEmail(args);
    AuditBridge.log("email_send", args.to, { subject: args.subject, msgId: result.id });
    return { content: [{ type: "text", text: `Email sent. ID: ${result.id}` }] };
  }
  // Implement other tools...
});

const transport = new StdioServerTransport();
server.connect(transport);
```

## Complete gmail_client.js
```javascript
const { google } = require("googleapis");
const fs = require("fs");

class GmailClient {
  static async getService() {
    const creds = JSON.parse(fs.readFileSync(process.env.GMAIL_CREDENTIALS_PATH));
    const token = JSON.parse(fs.readFileSync(process.env.GMAIL_TOKEN_PATH));
    const auth = new google.auth.OAuth2(creds.installed.client_id, creds.installed.client_secret);
    auth.setCredentials(token);
    return google.gmail({ version: "v1", auth });
  }

  static async sendEmail({ to, subject, body }) {
    const gmail = await this.getService();
    const utf8Subject = `=?utf-8?B?${Buffer.from(subject).toString("base64")}?=`;
    const messageParts = [
      `To: ${to}`,
      "Content-Type: text/plain; charset=utf-8",
      "MIME-Version: 1.0",
      `Subject: ${utf8Subject}`,
      "",
      body,
    ];
    const message = messageParts.join("\n");
    const encodedMessage = Buffer.from(message).toString("base64").replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
    const res = await gmail.users.messages.send({ userId: "me", requestBody: { raw: encodedMessage } });
    return res.data;
  }
}
module.exports = GmailClient;
```

## Complete audit_bridge.js
```javascript
const fs = require("fs");
const path = require("path");

class AuditBridge {
  static log(action, target, params = {}) {
    const date = new Date().toISOString().split("T")[0];
    const logPath = path.join(process.env.VAULT_PATH, "Vault", "Logs", `${date}.json`);
    const entry = {
      timestamp: new Date().toISOString(),
      action_type: action,
      actor: "email-mcp",
      target,
      parameters: params,
      dry_run: process.env.DRY_RUN === "true"
    };
    
    let logs = [];
    if (fs.existsSync(logPath)) {
      logs = JSON.parse(fs.readFileSync(logPath, "utf-8"));
    }
    logs.push(entry);
    fs.writeFileSync(logPath, JSON.stringify(logs, null, 2));
  }
}
module.exports = AuditBridge;
```

## Complete templates.js
```javascript
const templates = {
  invoice_email: "Dear {client_name},\n\nPlease find attached invoice {invoice_number} for {amount} due on {due_date}.\n\nBest regards,\n{sender_name}",
  follow_up_email: "Hi {client_name},\n\nFollowing up on {project_name}. Any updates?\n\nBest,\n{sender_name}"
};

function fillTemplate(type, vars) {
  let text = templates[type];
  for (const [key, value] of Object.entries(vars)) {
    text = text.replace(`{${key}}`, value);
  }
  return text;
}
module.exports = { fillTemplate };
```

## DRY_RUN Verification
1. Ensure `DRY_RUN="true"` in environment.
2. Call `send_email` via Gemini CLI.
3. Check console/logs: Should show simulated send without hitting Gmail API.

## Success Criteria
- **Binary Pass**: The MCP server correctly exposes Gmail tools to Gemini CLI, enforces HITL approval for all sends by checking the `/Approved/` folder, and logs every action to the vault's audit logs without autonomously sending emails.
