# GroundView field BOM — P19→P20 (expandable to P22)

**Status:** ACTIVE_ACQUISITION  
**Purpose:** Exact kit for **2 receivers now** (P19 one-site → P20 dual-site). Buy a third identical kit for P22 corridor (≥3 sites).  
**Do not** claim empirical PASS until hardware is on-site and capture runs with `GROUNDVIEW_MODE=field`.

## Kit per receiver (×2 now, ×3 for P22)

| Qty | Item | Spec / notes | Est. USD | Buy |
| --- | --- | --- | ---: | --- |
| 1 | RTL-SDR Blog V4 (or RTL-SDR V3) | USB SDR; rtl_433 TPMS-capable (315/433 MHz region-dependent) | 40–50 | [RTL-SDR Blog store](https://www.rtl-sdr.com/buy-rtl-sdr-dvb-t-dongles/) / Amazon “RTL-SDR Blog V4” |
| 1 | Antenna | Magnetic-mount or mast; prefer 433 MHz whip for US TPMS-heavy bands; keep a 315 MHz option if local fleet uses it | 15–40 | Same vendors; “433 MHz SMA magnetic mount” |
| 1 | SMA adapters / short coax | Match dongle connector (SMA/MCX) to antenna; keep feedline short | 10–20 | Amazon / Digi-Key |
| 1 | Field host | Raspberry Pi 4/5 (4GB+) **or** Intel NUC / used mini-PC; durable local disk for spool | 60–200 | Raspberry Pi authorized reseller / local |
| 1 | microSD / SSD | ≥32 GB for Pi; prefer USB SSD for spool durability | 15–80 | — |
| 1 | USB extension / powered hub | Reduce RFI from host; keep dongle away from CPU | 10–25 | — |
| 1 | Weather / dust enclosure | Outdoor or vehicle-mount as needed; vent RF cable | 20–60 | — |
| 1 | Power | Pi PSU or PoE/inverter plan for overnight | 10–40 | — |

## Shared / once

| Qty | Item | Spec / notes | Est. USD |
| --- | --- | --- | ---: |
| 1 | NTP path | chrony/NTP on host; optional USB GPS (u-blox) later for tighter clockQuality | 0–40 |
| 1 | Secrets store | Offline file for `GROUNDVIEW_RECEIVER_SECRETS_FILE` (see `SECRETS_SETUP.md`) | 0 |
| 1 | Central host | Laptop/desktop running SkyView field HTTP (`GROUNDVIEW_MODE=field`); **not Vercel** | existing |
| 0–1 | Truth aid (optional) | Manual clicker / phone video for vehicle counts — **never** feeds matcher-v1 | 0–50 |

## Roll-up cost

| Scope | Receivers | Approx. range |
| --- | --- | ---: |
| P19 only | 1 | **$180–$550** |
| P19→P20 | 2 | **$350–$1,050** |
| P22 corridor | 3 | **$520–$1,550** |

Prices fluctuate; treat as planning estimates, not POs.

## Budget lock (operator buy now)

**Approved working budget: \$450 mid-kit for P19→P20 (2× SDR + antennas + adapters + USB extensions).**  
Use the existing Mac as central + lean field host for P19 (skip Pi until overnight/outdoor). Add Pi kits later if needed (+\$150–400/site).

| Cart (buy today) | Qty | Target USD |
| --- | ---: | ---: |
| RTL-SDR Blog V4 dongle | 2 | ~\$90–100 |
| 433 MHz SMA magnetic-mount antenna | 2 | ~\$40–80 |
| SMA/MCX adapter + short coax (match dongle) | 2 | ~\$25–40 |
| USB extension (1–2 m, ferrite if available) | 2 | ~\$20–40 |
| Optional: 315 MHz whip (fleet-dependent) | 1 | ~\$15–25 |
| Optional: weather pouch / dry box | 1–2 | ~\$20–50 |
| **Cart total (lean, no Pi)** | | **~\$210–\$335** |
| **Contingency / tax / shipping** | | **→ plan \$450** |
| Full dual Pi hosts (optional later) | 2 | +\$300–700 |

**P19-only floor if cash-tight:** 1× V4 + antenna + adapter + USB ext ≈ **\$100–180** (Mac host). Still plan the second dongle before claiming P20.

## Software stack (no purchase)

- `rtl_433` (build or package)
- GroundView receiver-node: `node scripts/groundview-receiver-node.mjs`
- Field capture: `scripts/groundview-field-capture.sh`
- Central: SkyView on `wip/groundview` with `GROUNDVIEW_MODE=field`

## Acquisition checklist (operator marks)

Copy into session `prerequisites` (all REQUIRED must be `true` before live P19 PASS):

1. [ ] `sdr` — dongle in hand, enumerated by host (`lsusb` / Device Manager)
2. [ ] `antenna` — mounted; height/notes recorded in survey worksheet
3. [ ] `host` — Pi/mini-PC imaged; spool path writable
4. [ ] `site` — Site A survey filled (`sites/SITE_A.md` + worksheet)
5. [ ] `secrets` — secrets file created **outside** repo
6. [ ] `clock` — chrony/NTP healthy; clockQuality draft recorded
7. [ ] `truth_aid` (optional) — count method chosen

## Explicitly out of BOM

- Production Vercel deploy
- Camera/OCR as matcher input
- Anything that mutates `groundview_match_v1`
