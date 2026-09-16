# GroundView field install — day-of ops

**Central must use `GROUNDVIEW_MODE=field`.** Fixture/synthetic seed is forbidden for empirical sessions.

## 0. Prerequisites

- Kit from [`BOM.md`](./BOM.md) in hand
- Secrets from [`SECRETS_SETUP.md`](./SECRETS_SETUP.md)
- Site survey draft [`sites/SITE_A_SURVEY.json`](./sites/SITE_A_SURVEY.json)

## 1. Field host (Raspberry Pi / mini-PC)

```bash
# Debian/Ubuntu/Raspberry Pi OS
sudo apt update
sudo apt install -y git build-essential libusb-1.0-0-dev cmake pkg-config chrony
# rtl_433 — prefer distro package if available, else build from source:
#   https://github.com/merbanan/rtl_433
sudo apt install -y rtl-433 || true
rtl_433 -h | head
chronyc tracking   # should show synchronized / low offset
```

Create spool directory:

```bash
mkdir -p "$HOME/groundview-spool/GV-RX-FIELD-01"
```

## 2. SkyView checkout (central or same host)

```bash
cd /path/to/mabeline/SkyView
git checkout wip/groundview
export GROUNDVIEW_MODE=field
export GROUNDVIEW_RECEIVER_SECRETS_FILE="$HOME/.config/groundview/receiver-secrets.json"
# Start local SkyView / field HTTP surface (npm run dev or field-only host)
npm run dev
```

Confirm mode rejects synthetic seed (empty store until authenticated node events).

## 3. Freeze install epoch (before first capture)

```bash
cd /path/to/mabeline/SkyView
node scripts/groundview-field-freeze.mjs \
  --survey ../EARTH/research/runs/2026-09-15-groundview/field/sites/SITE_A_SURVEY.json \
  --session ../EARTH/research/runs/2026-09-15-groundview/field/sessions/p19_active.json
```

This writes `receiver_profile` + `clock_quality` into the session JSON. **Do not** change antenna/SDR mid-session without a new install epoch.

## 4. Capture pipeline

```bash
export RECEIVER_ID=GV-RX-FIELD-01
export GROUNDVIEW_RECEIVER_SECRETS_FILE="$HOME/.config/groundview/receiver-secrets.json"
export GROUNDVIEW_CENTRAL_URL="http://127.0.0.1:5173"   # or your field central
export SPOOL_DIR="$HOME/groundview-spool/$RECEIVER_ID"
export GROUNDVIEW_MODE=field

# Reject if mode wrong:
test "$GROUNDVIEW_MODE" = "field" || { echo "GROUNDVIEW_MODE must be field"; exit 1; }

bash scripts/groundview-field-capture.sh
```

Pipeline: `rtl_433 -F json` → receiver-node spool (`source_event_id` at boundary) → HMAC upload to `/api/groundview/node/events`.

## 5. Denominators + integrity (after window)

Operator fills counts from observation only, then:

```bash
node scripts/groundview-field-analyze.mjs \
  --session ../EARTH/research/runs/2026-09-15-groundview/field/sessions/p19_active.json
```

Analyzes: denominator validation, synthetic_fixture count (must be 0), manifest-v2 verify, sensor-ID stability diagnostics, session record outcome.

## 6. Record outcome

```bash
node scripts/groundview-p19-field.mjs --session-json ../EARTH/research/runs/2026-09-15-groundview/field/sessions/p19_active.json
```

Update `GROUNDVIEW_STATUS.md` with PASS (including poor observability) or keep FIELD_VALIDATION_REQUIRED while hardware/site still in transit.

## Failure modes

| Symptom | Action |
| --- | --- |
| No USB SDR | Do not fabricate; leave `prerequisites.sdr=false` |
| chrony unsynced | Mark TIMING_INELIGIBLE; do not widen matcher-v1 |
| Upload 401/403 | Check secrets file + receiver_id match |
| synthetic_fixture in field store | **Invalidate** session |
| Profile change mid-run | New install epoch; do not pool silently |
