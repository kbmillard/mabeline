# P20–P23 physical execution chain

Blocked on **P19 PASS** (or honest P19 findings that still leave dual-site scientifically meaningful — default: require P19 PASS).

## Gate rules

| Gate | Requires | Software ready | Empirical |
| --- | --- | --- | --- |
| P20 | P19 PASS + Site B + second kit | `p20p21Field.mjs`, comparability | dual capture + truth material |
| P21 | P20 PASS + frozen labels | freeze/join/promotion | independently labelled field evidence |
| P22 | P21 complete enough + Site C | corridor experiment | ≥3-site continuity |
| P23 | P22 PASS | presentation flags | enable journeys/envelopes with provenance chrome |

## Commands (after P19 PASS)

```bash
# Templates
node scripts/groundview-p20-p23-templates.mjs

# Comparability (filled profiles)
node -e "
import { buildComparabilityReport } from './src/data/groundview/comparability.mjs';
import { createReceiverProfile } from './src/data/groundview/receiverProfile.mjs';
// load frozen profiles from sessions; write report under field/sessions/
"

# Blinded eval: freeze labels then join
# Promotion without field labels → RETAIN_V1 (already enforced)

# After P22 PASS only:
# layer setParams({ showJourneys: true, showMovementEnvelopes: true, showGaps: true })
```

## Current ledger

See `sessions/p19_acquisition_status.json` — P20–P23 empirical remain `FIELD_VALIDATION_REQUIRED` / blocked on P19 acquisition.
