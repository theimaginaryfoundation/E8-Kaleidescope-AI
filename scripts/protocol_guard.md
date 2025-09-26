# Optional Local Guard (Pre-Push Hook)

To reduce the chance of bypassing the protocol locally, you can install a pre-push hook that warns when code/docs change without a new session log.

1) Create `.githooks/pre-push` with:

```
#!/usr/bin/env bash
set -euo pipefail

changed=$(git diff --name-only --cached | wc -l | tr -d ' ')
sessions_changed=$(git diff --name-only --cached | rg '^docs/sessions/.*\.md$' -n | wc -l | tr -d ' ')

if [ "$changed" -gt 0 ] && [ "$sessions_changed" -eq 0 ]; then
  echo "[protocol-guard] No session log updated in this push. STRICT MODE requires a session log."
  echo "[protocol-guard] Consider adding a session log under docs/sessions/ before pushing."
fi
```

2) Install locally (one-time):

```
git config core.hooksPath .githooks
chmod +x .githooks/pre-push
```

This does not block pushes by default; it provides a visible warning.

