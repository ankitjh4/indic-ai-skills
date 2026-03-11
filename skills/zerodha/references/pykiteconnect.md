# pykiteconnect Quick Reference

Use this file when the user wants production Python integration instead of CLI debugging.

Official repo: `https://github.com/zerodha/pykiteconnect`
Docs: `https://kite.trade/docs/pykiteconnect/v4/`

## Install

```bash
uv add kiteconnect
```

## Create client

```python
from kiteconnect import KiteConnect

kite = KiteConnect(api_key=api_key)
login_url = kite.login_url()
```

## Exchange request token

```python
from kiteconnect import KiteConnect

kite = KiteConnect(api_key=api_key)
session = kite.generate_session(request_token, api_secret=api_secret)
kite.set_access_token(session["access_token"])
```

## Read-only examples

```python
profile = kite.profile()
margins = kite.margins()
holdings = kite.holdings()
positions = kite.positions()
ltp = kite.ltp(["NSE:INFY", "NSE:SBIN"])
quote = kite.quote(["NSE:INFY"])
ohlc = kite.ohlc(["NSE:INFY"])
historical = kite.historical_data(
    instrument_token=408065,
    from_date="2025-01-01",
    to_date="2025-01-31",
    interval="day",
)
```

## Order example

```python
order_id = kite.place_order(
    variety=kite.VARIETY_REGULAR,
    exchange=kite.EXCHANGE_NSE,
    tradingsymbol="INFY",
    transaction_type=kite.TRANSACTION_TYPE_BUY,
    quantity=1,
    order_type=kite.ORDER_TYPE_MARKET,
    product=kite.PRODUCT_CNC,
)
```

## Practical guidance

- Prefer SDK constants like `kite.EXCHANGE_NSE` and `kite.PRODUCT_CNC` over handwritten strings.
- Wrap session generation and token persistence at the app boundary; do not scatter auth state across business logic.
- Cache instrument metadata and refresh it explicitly rather than querying ad hoc in high-frequency code.
- Start strategy debugging with read-only calls before wiring in order placement.
