---
name: zerodha
description: Zerodha Kite Connect v3 and pykiteconnect workflows for Indian market automation. Use this skill whenever the user mentions Zerodha, Kite, Kite Connect, pykiteconnect, Indian broker APIs, NSE/BSE/MCX trading automation, stock quotes, OHLC or historical candles, holdings or margins, GTT or alerts, instrument token lookup, or building/debugging algo-trading apps on Indian markets - even if they only ask for Python SDK code, API auth help, or broker integration without naming Kite Connect explicitly.
metadata:
  author: mr-karan
  display-name: Zerodha
---

# Zerodha Kite Connect v3

Build trading and investment platforms on India's largest retail broker using the Kite Connect REST API and WebSocket streaming.

## How To Use This Skill Well

This skill is not just a command wrapper. Use it to reason about the full Zerodha workflow safely:

- Prefer the official SDKs for production app code, especially `zerodha/pykiteconnect` for Python apps.
- Use the bundled CLI for quick validation, debugging auth/session issues, checking endpoint payloads, and reproducing problems outside an app codebase.
- Before placing or modifying live orders, first verify user profile, margins, instrument identifiers, and quote/historical data.
- Treat `/instruments` as the source of truth for exchange + tradingsymbol + instrument token mapping. Do not hardcode tokens across expiries.
- When building bots or trading workflows, account for rate limits, session expiry, market hours, and app permissions like Alerts access.

## Recommended Agent Workflow

When helping a user with Zerodha automation, follow this order unless the task clearly needs something else:

1. Confirm authentication flow and access token generation.
2. Fetch profile, margins, and required permissions.
3. Resolve instruments using quotes/instruments before using historical or trading endpoints.
4. Use read-only endpoints first (`profile`, `margins`, `quote`, `ltp`, `ohlc`, `historical`, `holdings`, `positions`).
5. Only then move to state-changing endpoints like orders, GTT, alerts, or position conversion.
6. For production Python integrations, prefer `pykiteconnect`; use the CLI here mainly for validation and troubleshooting.

## Choose The Right Tool

- Use `scripts/kite.py` when you need fast endpoint validation, auth debugging, or a reproducible CLI repro outside application code.
- Use `references/pykiteconnect.md` when the user wants production Python code, app integration examples, or SDK-style usage.
- Use raw REST request knowledge from this skill when the user is working in Go, Node.js, Java, or a custom HTTP client.

## Zerodha-Specific Gotchas

- `access_token` is session-scoped and typically expires the next trading day; handle re-login cleanly.
- Instrument tokens are not permanent identifiers across futures/options expiries. Re-resolve instruments instead of hardcoding old tokens.
- `/instruments` is large; download and cache it thoughtfully instead of fetching it repeatedly in hot paths.
- Alerts API access depends on app permissions. A valid session does not guarantee Alerts endpoints are enabled.
- Quote and historical endpoints have tighter rate limits than some other APIs; do not assume uniform limits.
- For live trading flows, verify margins and holdings before attempting writes; many user-visible failures are preflight issues, not API bugs.

## Default Safety Rules

- Prefer read-only checks first unless the user explicitly asks for a state-changing action.
- When testing live accounts, avoid placing orders just to validate auth; use `profile`, `margins`, `quote`, `ohlc`, and `historical` first.
- If the user asks for production trading automation, recommend `pykiteconnect` or official SDKs instead of building around the CLI wrapper.
- When debugging order failures, inspect `error_type`, account permissions, product/exchange compatibility, and margin availability before retrying.

## Prerequisites

1. Active Zerodha trading account with 2FA TOTP enabled
2. Developer account at https://developers.kite.trade/login
3. Create an app to get `api_key` and `api_secret`
4. Configure a redirect URL for the OAuth login flow

## Setup

```bash
export KITE_API_KEY="your_api_key"
export KITE_API_SECRET="your_api_secret"
export KITE_ACCESS_TOKEN="your_access_token"  # obtained after login flow
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| KITE_API_KEY | Yes | API key from Kite developer console |
| KITE_API_SECRET | Yes | API secret (never expose in client apps) |
| KITE_ACCESS_TOKEN | Yes | Session token from login flow (expires 6 AM next day) |

## Authentication Flow

The login flow is OAuth-based:

1. Redirect user to `https://kite.zerodha.com/connect/login?v=3&api_key=xxx`
2. On success, user is redirected to your `redirect_url` with a `request_token` query param
3. Exchange `request_token` for `access_token` by POSTing to `/session/token` with a SHA-256 checksum of `api_key + request_token + api_secret`
4. Use `access_token` for all subsequent requests

### Signing Requests

All authenticated requests must include:
```
Authorization: token api_key:access_token
X-Kite-Version: 3
```

## API Base URL

```
https://api.kite.trade
```

## Usage

The CLI uses `uv` for dependency management (httpx, click are auto-resolved via inline script metadata).

```bash
# Get user profile
uv run scripts/kite.py profile

# Get funds/margins
uv run scripts/kite.py margins
uv run scripts/kite.py margins --segment equity

# Place a regular order
uv run scripts/kite.py order-place \
  --exchange NSE --tradingsymbol INFY \
  --transaction-type BUY --order-type MARKET \
  --quantity 1 --product CNC

# Place a limit order
uv run scripts/kite.py order-place \
  --exchange NSE --tradingsymbol SBIN \
  --transaction-type BUY --order-type LIMIT \
  --quantity 5 --product CNC --price 750

# Modify an order
uv run scripts/kite.py order-modify \
  --order-id 151220000000000 --quantity 3 --price 760

# Cancel an order
uv run scripts/kite.py order-cancel --order-id 151220000000000

# List today's orders
uv run scripts/kite.py orders

# Get order history
uv run scripts/kite.py order-history --order-id 151220000000000

# List today's trades
uv run scripts/kite.py trades

# Get holdings
uv run scripts/kite.py holdings

# Get positions
uv run scripts/kite.py positions

# Get full market quote
uv run scripts/kite.py quote -i NSE:INFY -i NSE:SBIN

# Get LTP
uv run scripts/kite.py ltp -i NSE:INFY -i BSE:SENSEX

# Get OHLC
uv run scripts/kite.py ohlc -i NSE:INFY -i NSE:RELIANCE

# Get historical candle data
uv run scripts/kite.py historical \
  --instrument-token 408065 --interval day \
  --from "2025-01-01" --to "2025-01-31"

# Download instrument list (CSV)
uv run scripts/kite.py instruments
uv run scripts/kite.py instruments --exchange NSE

# Place a GTT (single leg)
uv run scripts/kite.py gtt-place \
  --type single --exchange NSE --tradingsymbol INFY \
  --trigger-values 702.0 --last-price 798.0 \
  --transaction-type BUY --quantity 1 --price 702.5 --product CNC

# List GTTs
uv run scripts/kite.py gtt-list

# Get GTT details
uv run scripts/kite.py gtt-get --trigger-id 123

# Delete a GTT
uv run scripts/kite.py gtt-delete --trigger-id 123

# Create a simple alert
uv run scripts/kite.py alert-create \
  --name "NIFTY Alert" --type simple \
  --lhs-exchange INDICES --lhs-tradingsymbol "NIFTY 50" \
  --operator ">=" --rhs-constant 27000

# List alerts
uv run scripts/kite.py alert-list

# Delete alert
uv run scripts/kite.py alert-delete --uuid "$ALERT_UUID"

# Calculate order margins
uv run scripts/kite.py margins-order \
  --exchange NSE --tradingsymbol INFY \
  --transaction-type BUY --quantity 1 \
  --order-type MARKET --product CNC

# Logout (invalidate session)
uv run scripts/kite.py logout
```

## API Endpoints Reference

### User

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/session/token` | Exchange request_token for access_token |
| GET | `/user/profile` | Get user profile |
| GET | `/user/margins` | Get funds & margins (all segments) |
| GET | `/user/margins/:segment` | Get funds & margins (equity or commodity) |
| DELETE | `/session/token` | Logout / invalidate session |

### Orders

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/orders/:variety` | Place order (variety: regular, amo, co, iceberg, auction) |
| PUT | `/orders/:variety/:order_id` | Modify pending order |
| DELETE | `/orders/:variety/:order_id` | Cancel pending order |
| GET | `/orders` | List all orders for the day |
| GET | `/orders/:order_id` | Get order history |
| GET | `/trades` | List all trades for the day |
| GET | `/orders/:order_id/trades` | Get trades for a specific order |

#### Order Constants

| Parameter | Values |
|-----------|--------|
| variety | `regular`, `amo`, `co`, `iceberg`, `auction` |
| order_type | `MARKET`, `LIMIT`, `SL`, `SL-M` |
| product | `CNC` (equity delivery), `NRML` (F&O normal), `MIS` (intraday), `MTF` (margin trading) |
| validity | `DAY`, `IOC`, `TTL` |
| transaction_type | `BUY`, `SELL` |
| exchange | `NSE`, `BSE`, `NFO`, `CDS`, `BCD`, `MCX` |

#### Order Parameters (Place)

| Parameter | Required | Description |
|-----------|----------|-------------|
| tradingsymbol | Yes | Exchange tradingsymbol |
| exchange | Yes | NSE, BSE, NFO, CDS, BCD, MCX |
| transaction_type | Yes | BUY or SELL |
| order_type | Yes | MARKET, LIMIT, SL, SL-M |
| quantity | Yes | Quantity to transact |
| product | Yes | CNC, NRML, MIS, MTF |
| price | No | For LIMIT orders |
| trigger_price | No | For SL, SL-M orders |
| disclosed_quantity | No | Quantity to disclose publicly |
| validity | No | DAY (default), IOC, TTL |
| validity_ttl | No | Minutes for TTL validity |
| tag | No | Alphanumeric, max 20 chars |
| market_protection | No | 0 (none), 0-100 (custom %), -1 (auto) |
| autoslice | No | true/false for freeze quantity auto-splitting |

### GTT (Good Till Triggered)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/gtt/triggers` | Place GTT |
| GET | `/gtt/triggers` | List all GTTs |
| GET | `/gtt/triggers/:id` | Get GTT details |
| PUT | `/gtt/triggers/:id` | Modify GTT |
| DELETE | `/gtt/triggers/:id` | Delete GTT |

GTT types: `single` (one trigger value, one order) and `two-leg` (OCO: two trigger values, two orders).

### Alerts

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/alerts` | Create alert (simple or ATO) |
| GET | `/alerts` | List all alerts |
| GET | `/alerts/:uuid` | Get alert details |
| PUT | `/alerts/:uuid` | Modify alert |
| DELETE | `/alerts?uuid=:uuid` | Delete alert(s) |
| GET | `/alerts/:uuid/history` | Get alert trigger history |

Alert types: `simple` (notification only) and `ato` (Alert Triggers Order).
Operators: `<=`, `>=`, `<`, `>`, `==`.
Max 500 active alerts per user.

### Portfolio

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/portfolio/holdings` | Long-term equity holdings |
| GET | `/portfolio/positions` | Short-term positions (net + day) |
| PUT | `/portfolio/positions` | Convert position margin product |
| GET | `/portfolio/holdings/auctions` | Current auction listings |

### Market Quotes & Instruments

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/instruments` | Full instrument list (CSV, ~08:30 AM daily) |
| GET | `/instruments/:exchange` | Instrument list for specific exchange |
| GET | `/quote?i=EXCHANGE:SYMBOL` | Full quote (up to 500 instruments) |
| GET | `/quote/ohlc?i=EXCHANGE:SYMBOL` | OHLC + LTP (up to 1000 instruments) |
| GET | `/quote/ltp?i=EXCHANGE:SYMBOL` | LTP only (up to 1000 instruments) |

### Historical Candle Data

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/instruments/historical/:token/:interval` | OHLCV candles |

Intervals: `minute`, `3minute`, `5minute`, `10minute`, `15minute`, `30minute`, `60minute`, `day`.
Query params: `from`, `to` (format: `yyyy-mm-dd hh:mm:ss`), `continuous` (0/1), `oi` (0/1).

### WebSocket Streaming

Endpoint: `wss://ws.kite.trade?api_key=xxx&access_token=xxx`

- Up to 3000 instruments per connection, max 3 connections per API key
- Modes: `ltp` (8 bytes), `quote` (44 bytes), `full` (184 bytes with market depth)
- Binary messages for market data, JSON text for order postbacks/alerts

Actions:
```json
{"a": "subscribe", "v": [408065, 884737]}
{"a": "unsubscribe", "v": [408065]}
{"a": "mode", "v": ["full", [408065]]}
```

### Margin Calculation

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/margins/orders` | Calculate margins for orders (JSON body) |
| POST | `/margins/basket` | Calculate margins for spread orders (JSON body) |
| POST | `/charges/orders` | Virtual contract note with charges breakdown |

### Postbacks / Webhooks

Register a `postback_url` in your app config. Order status changes trigger a POST with JSON payload.
Validate with SHA-256 checksum: `sha256(order_id + order_timestamp + api_secret)`.

## Rate Limits

| Endpoint | Limit |
|----------|-------|
| `/quote` | 1 req/sec |
| Historical candle | 3 req/sec |
| Order placement | 10 req/sec |
| All other | 10 req/sec |

Max 3000 orders/day per user/API key. Max 25 modifications per order.

## Error Handling

All errors return JSON with `status: "error"`, `message`, and `error_type`.

| Exception | HTTP | Description |
|-----------|------|-------------|
| TokenException | 403 | Session expired, must re-login |
| UserException | 4xx | Account-related errors |
| OrderException | 4xx | Order placement/retrieval failures |
| InputException | 400 | Missing or invalid parameters |
| MarginException | 4xx | Insufficient funds |
| HoldingException | 4xx | Insufficient holdings for sell |
| NetworkException | 5xx | OMS communication failure |
| DataException | 5xx | OMS response parsing failure |
| GeneralException | 500 | Unclassified error |

## Official SDKs

| Language | Repository |
|----------|-----------|
| Python | [zerodha/pykiteconnect](https://github.com/zerodha/pykiteconnect) |
| Go | [zerodha/gokiteconnect](https://github.com/zerodha/gokiteconnect) |
| Java | [zerodha/javakiteconnect](https://github.com/zerodha/javakiteconnect) |
| Node.js | [zerodha/kiteconnectjs](https://github.com/zerodha/kiteconnectjs) |
| PHP | [zerodha/phpkiteconnect](https://github.com/zerodha/phpkiteconnect) |
| .NET/C# | [zerodha/dotnetkiteconnect](https://github.com/zerodha/dotnetkiteconnect) |

## API Reference

- Docs: https://kite.trade/docs/connect/v3/
- Developer Portal: https://developers.kite.trade
- Forum: https://kite.trade/forum
