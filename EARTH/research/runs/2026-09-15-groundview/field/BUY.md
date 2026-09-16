# GroundView — buy cart (operator action)

**Budget lock: \$450** for lean dual-receiver RF kit (no Pi). Mac is field host for P19.

## Buy now (Amazon / rtl-sdr.com — same day / 2-day)

Search strings (exact enough):

1. `RTL-SDR Blog V4` ×2 — ~\$45–50 each  
2. `433 MHz SMA magnetic mount antenna` ×2 — ~\$20–40 each  
3. `SMA male to MCX` or adapter set matching V4 connector ×2 — ~\$10–20  
4. `USB 2.0 extension cable 6ft` ×2 — ~\$10–20  

Optional same cart: `315 MHz SMA antenna`, small dry box.

## Do not buy yet

- Raspberry Pi kits (defer until overnight outdoor sites)
- Camera/OCR gear (never feeds matcher-v1)
- Anything “GPS vehicle tracker” style (wrong product)

## After delivery

1. Plug dongle → confirm USB enumerate  
2. `source ~/.config/groundview/env.sh`  
3. Fill `sites/SITE_A_SURVEY.json` on site  
4. `bash scripts/groundview-field-day.sh all`

Secrets + `rtl_433` + spool dirs are already on this Mac.
