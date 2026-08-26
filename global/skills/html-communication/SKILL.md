---
name: html-communication
description: Use when the user requests a standalone HTML artifact or a visual report best explored outside chat, or when user says "HTML" with no context.
---

# HTML communication

Create a self-contained HTML document with visual hierarchy suited to the material. Use interaction, color, diagrams, or responsive layout only when they improve comprehension.

Write it to the user-facing output location supplied by the environment. If none exists, use a task-specific workspace directory.

## Publishing

Publish only when the user requests a shareable URL. Use the `file-upload` skill for the publishing workflow. If the user says "LINK", always upload the file.
