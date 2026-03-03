---
id: 9
title: Acknowledge SKILL.md Read-Only Mandate
stage: misc
date: 2026-03-02
surface: agent
model: gemini-2.0-flash
feature: 001-bronze-vault-foundation
branch: 001-bronze-vault-foundation
user: ADMINS
command: Acknowledge user mandate regarding SKILL files
labels: ["policy", "mandate", "skills"]
links:
  spec: specs/001-bronze-vault-foundation/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - none
tests:
  - none
---

## Prompt

I have also added some missing context in the SKILL files. Now make sure you donot edit or re-write the SKILL without the permission.

## Response snapshot

Acknowledged the mandate to treat SKILL.md files as read-only unless explicit permission is granted by the user.

## Outcome

- ✅ Impact: Established a strict operational boundary regarding skill definitions.
- 🧪 Tests: none
- 📁 Files: none
- 🔁 Next prompts: Proceed to Phase 5: Filesystem Watcher.
- 🧠 Reflection: User trust is paramount; respecting manual updates to core documentation is essential for collaborative SDD.

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): PASS
- Prompt variant (if applicable): none
- Next experiment (smallest change to try): none
