# SITE_A — Kansas City metro commercial freight observation

**Status:** ACTIVE_ACQUISITION (coordinates candidate; operator must survey + confirm legal posture)  
**Receiver:** `GV-RX-FIELD-01`  
**Geography default:** Kansas City metro (SkyView / Mabeline home theater)

## Selection criteria (locked)

1. Sustained Class 8 / commercial freight volume (interstate, state truck route, or terminal approach).
2. **Legal observation posture:** operator-owned property, leased site, or publicly accessible ROW where standing with an SDR/antenna is lawful — **no trespass**.
3. Defensible surveyed coordinates (GPS + written landmark) for receiver profile install epoch.
4. Power + network path for field host (or offline spool + later upload).
5. Antenna mounting that does not invent vehicle GPS (coverage pin = receiver site only).

## Candidate corridor locations (operator picks one, surveys, fills worksheet)

Coordinates are **planning candidates** from public map knowledge of KC freight arterials — not claimed installs. Operator must verify access and refine lat/lon on site.

| ID | Area | Approx. focus | Why |
| --- | --- | --- | --- |
| A1 | I-435 / I-70 east KC interchange approaches | ~39.12 N, −94.48 W | Heavy through-freight; public ROW observation only |
| A2 | I-35 / I-29 downtown loop approaches | ~39.10 N, −94.58 W | Commercial density; RF noise risk higher |
| A3 | I-70 / Kansas Ave / Central Industrial Dist. approaches | ~39.10 N, −94.60 W | Yard/terminal approach traffic; prefer operator-owned lot if available |
| A4 | Operator-owned / leased property along designated truck route | TBD by operator | **Preferred** when available |

**Selected Site A (operator fills):**

- Candidate ID: ________
- Final lat: ________
- Final lon: ________
- Datum: WGS84
- Access posture: ☐ owned ☐ leased ☐ public ROW (describe): ________
- Antenna height AGL (m): ________
- Mounting: ________
- Photo refs: ________

## RF / ops notes

- Expect passenger TPMS density ≠ Class 8 prevalence — **measure**, do not inherit FMVSS 138 passenger rates.
- Urban RF noise may reduce decode rates; poor observability is a valid P19 finding.
- Keep dongle away from host CPU; use short quality feedline.
- Record rtl_433 version + frequency flags in receiver profile.

## Day-of checklist

1. Fill [`SITE_A_SURVEY.json`](./SITE_A_SURVEY.json) completely.
2. Freeze profile/clock: `node scripts/groundview-field-freeze.mjs --survey field/sites/SITE_A_SURVEY.json`
3. Mark session `prerequisites.site=true` only after survey is real.
4. Capture: `scripts/groundview-field-capture.sh` with `GROUNDVIEW_MODE=field` on central.

## Photo checklist

- [ ] Antenna + mount
- [ ] Host placement
- [ ] Horizon / roadway view (context only)
- [ ] Cable routing
- [ ] Power source
