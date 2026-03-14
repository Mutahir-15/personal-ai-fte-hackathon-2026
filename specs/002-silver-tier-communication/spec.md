# Feature Specification: Personal AI Employee — Silver Tier

**Feature Branch**: `002-silver-tier-communication`  
**Created**: 2026-03-14  
**Status**: Draft  
**Input**: User description: "Personal AI Employee — Autonomous FTE (Silver Tier)..."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Email Intake & Triage (Priority: P1)

As a user, I want the AI to monitor my Gmail inbox for important unread emails and create action items in my Obsidian vault so that I can process them locally.

**Why this priority**: Core intake mechanism for communications. Essential for the "Silver Tier" as a communication layer.

**Independent Test**: Send an unread email labeled 'IMPORTANT' to the monitored Gmail account; verify an `.md` file appears in `VAULT_ROOT/Needs_Action/` within 120 seconds.

**Acceptance Scenarios**:

1. **Given** a new unread email with label 'IMPORTANT', **When** the gmail-watcher polls the inbox, **Then** it creates a structured `.md` file in `/Needs_Action/` with high priority.
2. **Given** a previously processed email, **When** the gmail-watcher polls the inbox, **Then** it does not create a duplicate `.md` file.

---

### User Story 2 - WhatsApp Detection (Priority: P2)

As a user, I want the AI to detect urgent WhatsApp messages containing specific keywords and create action items in my vault.

**Why this priority**: Extends the communication intake to instant messaging, which is often more time-sensitive.

**Independent Test**: Receive a WhatsApp message containing "urgent"; verify a corresponding `.md` file appears in `VAULT_ROOT/Needs_Action/` within 30 seconds.

**Acceptance Scenarios**:

1. **Given** a new WhatsApp message containing "asap", **When** the whatsapp-watcher scans the chat list, **Then** it creates a structured `.md` file in `/Needs_Action/`.
2. **Given** an expired session, **When** the watcher starts, **Then** it prompts the user for a QR code scan gracefully.

---

### User Story 3 - LinkedIn Post Generation & Approval (Priority: P3)

As a user, I want the AI to generate professional LinkedIn posts based on my business goals and handbook, but only publish them after I have approved them.

**Why this priority**: Automates outbound communication while maintaining strict human-in-the-loop (HITL) quality control.

**Independent Test**: Trigger post generation; verify a draft appears in `/Pending_Approval/`. Move the file to `/Approved/`; verify it is published to LinkedIn within the scheduled window.

**Acceptance Scenarios**:

1. **Given** updated business goals, **When** the linkedin-poster runs, **Then** it creates a draft in `/Pending_Approval/` with hashtags.
2. **Given** an approved LinkedIn draft, **When** the poster processes approvals, **Then** it publishes to LinkedIn and logs the success.

---

### User Story 4 - Local MCP Email Actions (Priority: P2)

As a user, I want to interact with my Gmail inbox (search, draft, send) using Gemini CLI commands via an MCP server, with mandatory approval for any sent items.

**Why this priority**: Provides the "hands" for the AI to respond to the intake items triaged in Story 1.

**Independent Test**: Ask Gemini CLI to draft an email; verify a draft appears in Gmail. Ask it to send an email; verify an approval request appears in `/Pending_Approval/`.

**Acceptance Scenarios**:

1. **Given** an instruction to send an email, **When** Gemini CLI calls the MCP tool, **Then** it creates an approval file in `/Pending_Approval/` instead of sending immediately.
2. **Given** an approved email send request, **When** the HITL processor detects it, **Then** it executes the send via the MCP server.

---

### User Story 5 - Enhanced HITL Approval & Escalation (Priority: P1)

As a user, I want a priority-ordered dashboard of pending approvals with escalation alerts for items that have been waiting too long.

**Why this priority**: Critical safety and management layer for all Silver Tier actions.

**Independent Test**: Create multiple approval requests of different types; verify they are ordered correctly in `Dashboard.md`. Wait 4 hours; verify a warning alert appears.

**Acceptance Scenarios**:

1. **Given** multiple pending approvals, **When** the dashboard is updated, **Then** email sends to new contacts appear at the top as CRITICAL.
2. **Given** a request pending for 20 hours, **When** the escalation check runs, **Then** a CRITICAL alert is added to `Dashboard.md`.

### Edge Cases

- **Session Expiry**: How does the system handle WhatsApp/LinkedIn token expiry? (Handled by alerting user in Dashboard.md).
- **Rate Limits**: What happens if Gmail/LinkedIn rate limits are hit? (Exponential backoff and warning logs implemented).
- **Conflicting Approvals**: How are concurrent approvals handled? (File locking via `msvcrt` on Windows).
- **New Contacts**: Sending emails to contacts not in `TRUSTED_CONTACTS`. (Mandatory flag and critical priority).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST monitor Gmail for unread messages labeled as important.
- **FR-002**: System MUST monitor WhatsApp Web for unread messages matching specific keywords.
- **FR-003**: System MUST provide a local MCP server exposing Gmail capabilities (send, draft, search, get, reply).
- **FR-004**: System MUST generate LinkedIn posts based on `Business_Goals.md` and `Company_Handbook.md`.
- **FR-005**: System MUST require human approval for ALL outgoing emails and LinkedIn posts.
- **FR-006**: System MUST order pending approvals by priority (Critical > High > Medium > Low).
- **FR-007**: System MUST provide escalation alerts in `Dashboard.md` at 4h, 8h, and 20h thresholds.
- **FR-008**: System MUST support batch approval of multiple files.
- **FR-009**: System MUST track approval metrics (lifetime and daily).
- **FR-010**: System MUST maintain full backward compatibility with Bronze tier scripts and state.

### Key Entities *(include if feature involves data)*

- **Email Action**: Represents a triaged email or a pending send/reply. Attributes: `email_id`, `thread_id`, `recipient`, `subject`, `priority`.
- **WhatsApp Action**: Represents a detected urgent message. Attributes: `message_hash`, `sender`, `content`, `keyword`.
- **LinkedIn Post**: Represents a generated or published post. Attributes: `post_id`, `content`, `scheduled_time`, `status`.
- **Approval Request**: A wrapper for any action requiring human consent. Attributes: `approval_id`, `type`, `priority`, `expiry`, `status`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of detected urgent emails/messages result in a `.md` file in `/Needs_Action/`.
- **SC-002**: Zero emails or LinkedIn posts are published without an explicit entry in `approved_actions.json`.
- **SC-003**: The approval queue in `Dashboard.md` is updated within 60 seconds of any state change.
- **SC-004**: Escalation alerts appear within 5 minutes of hitting the 4h/8h/20h thresholds.
- **SC-005**: 100% of Bronze tier functionality remains operational after Silver deployment.
