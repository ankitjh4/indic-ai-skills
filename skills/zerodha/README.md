# Zerodha Skill

Quick start for the Zerodha Kite Connect skill.

## What this skill is for

- Understanding Zerodha Kite Connect auth, rate limits, and endpoint behavior
- Exploring instruments, quotes, holdings, positions, margins, and historical candles safely
- Validating payloads and debugging API issues before writing production code
- Using the official Zerodha SDKs, especially `pykiteconnect`, with better context

## Best practice

- Use `scripts/kite.py` for debugging, quick checks, and reproducing issues
- Use `zerodha/pykiteconnect` for production Python integrations
- Start with read-only endpoints before touching live orders, GTTs, or alerts
- Treat `instruments` as the source of truth for exchange, symbol, and token lookup

## Setup

```bash
export KITE_API_KEY="your_api_key"
export KITE_API_SECRET="your_api_secret"
export KITE_ACCESS_TOKEN="your_access_token"
```

## Quick checks

```bash
uv run scripts/kite.py profile
uv run scripts/kite.py margins --segment equity
uv run scripts/kite.py ltp -i NSE:INFY -i NSE:SBIN
uv run scripts/kite.py historical --instrument-token 408065 --interval day --from "2025-01-01" --to "2025-01-31"
uv run scripts/kite.py instruments --exchange NSE > nse_instruments.csv
```

## Production Python

If you're building an app, prefer the official library:

- `https://github.com/zerodha/pykiteconnect`

See `references/pykiteconnect.md` for a quick SDK-oriented reference.

Use this skill's `SKILL.md` for the full workflow, endpoint reference, gotchas, and safety guidance.
