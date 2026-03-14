# Research: Silver Tier Communication & Social Automation

## Decision: LinkedIn API v2 Usage
- **Decision**: Use `ugcPosts` endpoint with `w_member_social` scope.
- **Rationale**: Industry standard for personal/page social sharing. Requires LinkedIn Developer App.
- **Alternatives considered**: `shares` API (deprecated/legacy).
- **Finding**: App review is required for `w_member_social`. Users must submit their app for review before live posting is possible. `DRY_RUN` will simulate the call during review period.

## Decision: WhatsApp Web Monitoring
- **Decision**: Playwright with a persistent browser context and specific data-testids.
- **Rationale**: WhatsApp Web uses React; stable selectors like `[data-testid="icon-unread-count"]` are the most reliable way to detect messages without a formal (and expensive) Business API.
- **Alternatives considered**: `selenium` (slower, harder to manage sessions), Official API (too expensive/restrictive for personal FTE).
- **Finding**: Session persistence is achieved by saving the `user_data_dir`. QR scan is only needed on session expiry or first run.

## Decision: Node.js MCP Server Registration
- **Decision**: Local MCP server over `stdio` transport, registered in Gemini CLI's `mcp.json`.
- **Rationale**: Standard Model Context Protocol (MCP) pattern for local tool extension. Allows Gemini CLI to "discover" email tools dynamically.
- **Finding**: On Windows 10, the configuration is typically in `%APPDATA%\gemini-cli\mcp.json`. Absolute paths must use double backslashes `\\`.

## Dependency Best Practices
- **google-api-python-client**: Use `build('gmail', 'v1', ...)` with service account or OAuth2 user credentials. User credentials required for "me" userId.
- **Playwright**: Always use `headless=False` for the initial QR scan, then `headless=True` for PM2 background operation.
- **msvcrt**: Required for Windows-specific non-blocking file locking to prevent `approved_actions.json` corruption during concurrent Silver actions.
