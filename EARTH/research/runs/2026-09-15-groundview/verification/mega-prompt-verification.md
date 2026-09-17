# GroundView mega-prompt verification pack (§74/75)

Generated: 2026-09-16T00:57:38.037Z
Report hash: `5181947702e0c7fda983f2582217eed0d621a6a018cba457fe110bb11db42820`

## Regression

- Required: **36/9/20/5/89.29**
- Observed: **36/9/20/5/89.29**
- OK: **true**

## Tests

- pass: 83
- fail: 0

## Matcher

- frozen: `groundview_match_v1`
- forbidden label: `confirmed`

## Presentation defaults

- showJourneys: false
- showMovementEnvelopes: false
- showGaps: false

## P19 state

- outcome: **FIELD_VALIDATION_REQUIRED**
- missing prerequisites: sdr, antenna, host, site, secrets, clock
- fabricated metrics: **false**

## Deferred empirical

- P19 physical capture
- P20 dual-site field
- P21 independently labelled field eval
- P22 corridor continuity
- P23 authoritative live motion
- P25 persistent regional ops
- P26–P27 real multi-region / episode ops
- P28–P30 production maturity under authorization

## Risks

- Physical SDR/site not yet acquired — empirical gates remain FIELD_VALIDATION_REQUIRED
- Do not deploy vercel --prod without explicit authorization
- Do not mutate groundview_match_v1

## Next action

Acquire P19 prerequisites (SDR, antenna, field host, surveyed site, secrets, clock); run field capture with GROUNDVIEW_MODE=field
