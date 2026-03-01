---
id: 1
title: Explaining Skills vs Sub-Agents
stage: general
date: 2026-02-28
surface: agent
model: gemini-2.0-flash-thinking-exp-01-21
feature: none
branch: none
user: ADMINS
command: what is the difference between skills and sub-agents?
labels: ["clarification", "architecture", "definitions"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - none
tests:
  - none
---

## Prompt

what is the difference between skills and sub-agents?

## Response snapshot

The primary difference lies in **how** I interact with them and their **impact** on my behavior:

*   **Sub-Agents** are specialized, external tools that I delegate specific tasks to. I "call" them to get an answer or a structured report (e.g., calling `codebase_investigator` for deep analysis).
*   **Skills** are procedural instruction sets that I "activate" to augment my own internal logic. Once activated via `activate_skill`, they provide expert guidance and specialized rules that take precedence over my general defaults for the duration of a task.

In short: Sub-agents are **consultants** I ask for help; skills are **specialized training** I apply to my own workflow.

## Outcome

- ✅ Impact: User understands the core architectural components of Gemini CLI (Skills vs Sub-Agents).
- 🧪 Tests: none
- 📁 Files: none
- 🔁 Next prompts: none
- 🧠 Reflection: Clarification of these terms is essential for the user to understand how to best leverage the assistant's capabilities.

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): n/a
- Prompt variant (if applicable): n/a
- Next experiment (smallest change to try): n/a
