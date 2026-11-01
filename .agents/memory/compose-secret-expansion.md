---
name: Compose secret expansion
description: Avoid leaking injected environment secrets while validating Docker Compose.
---

Never print the fully resolved Docker Compose configuration when it interpolates secrets. Prefer `docker compose config --quiet` for syntax validation, and keep secret-bearing output out of logs and chat.

**Why:** resolved Compose output expands environment variables, which can expose API credentials in command output.

**How to apply:** before validating Compose files that interpolate provider keys, choose a quiet validation command and do not grep or print the rendered configuration.
