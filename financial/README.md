# Mabeline Financial

Next.js dashboard for SEC return scans and penny-forward screening.

## Develop

```bash
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## Refresh data

One command from the Mabeline repo root:

```bash
bin/mabel-catalog financial              # commodity + moneyball + sync
bin/mabel-catalog commodity-economy --sync  # physical economy only
bin/mabel-catalog sync-financial         # copy receipts only
```

Receipts synced to `src/data/` and `public/data/`:

- `return_scan_receipt_v1.json`
- `penny_forward_screen_v1.json`
- `moneyball_aggregate_v1.json`
- `freight_movement_receipt_v1.json`
- `commodity_economy_v1.json`

Pages: `/` (overview), `/commodity` (full physical economy).

Then rebuild and redeploy.

## Deploy

Deployed on Vercel. Push to `main` triggers a new build.
