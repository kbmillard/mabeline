# Mabeline

Transport evidence graph: truck = sensor, commodity = signal.

## Live demo (Vercel)

Next.js app in `financial/` — financial board at `/`, THG petroleum corridor demo at `/thg`.

```bash
cd financial && npm install && npm run dev
```

## Catalog CLI

```bash
bin/mabel-catalog thg-linear --from-month 202401 --top-n 50
bin/mabel-catalog thg-query --sctg2 17
```

Raw evidence (`_unwrapped/`, `warehouse/`) is gitignored and not deployed.
