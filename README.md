# Mabeline

Transport evidence graph: truck = sensor, commodity = signal.

## Live demo (Vercel)

**https://mabeline.vercel.app** — Iran/oil/truck proof at [`/iran`](https://mabeline.vercel.app/iran), THG map at [`/thg`](https://mabeline.vercel.app/thg).

Repo: https://github.com/kbmillard/mabeline · Vercel root: `financial/`

```bash
cd financial && npm install && npm run dev
```

## Catalog CLI

```bash
bin/mabel-catalog thg-linear --from-month 202401 --top-n 50
bin/mabel-catalog thg-query --sctg2 17
```

Raw evidence (`_unwrapped/`, `warehouse/`) is gitignored and not deployed.
