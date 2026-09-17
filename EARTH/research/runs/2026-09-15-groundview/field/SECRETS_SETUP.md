# GroundView receiver secrets setup

**Never commit secrets.** Never put secrets in observations, manifests, STATUS, or spool NDJSON.

## This Mac (already done)

Secrets live at `~/.config/groundview/receiver-secrets.json` (mode 600).  
Env helper: `source ~/.config/groundview/env.sh`  
Do **not** re-generate unless rotating — rotating invalidates field nodes until redeployed.

## Generate secrets file (outside repo)

```bash
mkdir -p "$HOME/.config/groundview"
umask 077
python3 - <<'PY'
import json, secrets, pathlib
path = pathlib.Path.home() / ".config/groundview/receiver-secrets.json"
# Add/replace receiver IDs to match profiles (P19 Site A uses GV-RX-FIELD-01).
payload = {
  "GV-RX-FIELD-01": secrets.token_urlsafe(32),
  "GV-RX-FIELD-02": secrets.token_urlsafe(32),
  "GV-RX-FIELD-03": secrets.token_urlsafe(32),
}
path.write_text(json.dumps(payload, indent=2) + "\n")
path.chmod(0o600)
print(path)
PY
export GROUNDVIEW_RECEIVER_SECRETS_FILE="$HOME/.config/groundview/receiver-secrets.json"
```

Confirm:

```bash
test -f "$GROUNDVIEW_RECEIVER_SECRETS_FILE" && echo "secrets: ok"
# Must NOT live under the git worktree:
case "$GROUNDVIEW_RECEIVER_SECRETS_FILE" in
  *mabeline*|*SkyView*|*EARTH*) echo "ERROR: secrets inside repo tree"; exit 1;;
esac
```

## Wire into processes

| Process | Env |
| --- | --- |
| Central field host | `GROUNDVIEW_MODE=field` + `GROUNDVIEW_RECEIVER_SECRETS_FILE=...` |
| Receiver-node / capture script | same secrets file; `RECEIVER_ID=GV-RX-FIELD-01` |

## Rotation / quarantine

Use `securityLifecycle.mjs` descriptors: revoke → quarantine → re-issue. After rotation, update the secrets file and restart node + central. Do not leave old secrets in shell history (prefer file only).

## Mark prerequisite

When the file exists outside the repo and both field host + receiver-node can read it:

```bash
# In your session JSON only (operator edit):
# "prerequisites": { ..., "secrets": true }
node scripts/groundview-p19-field.mjs --prereq-status
```
