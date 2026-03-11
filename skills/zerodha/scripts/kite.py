#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# dependencies = ["httpx>=0.28", "click>=8.1"]
# ///
"""Zerodha Kite Connect v3 API CLI.

Requires env vars: KITE_API_KEY, KITE_ACCESS_TOKEN (and KITE_API_SECRET for login).
Run with: uv run scripts/kite.py <command>
"""

import hashlib
import json
import os
import sys
from typing import Any

import click
import httpx

BASE_URL = "https://api.kite.trade"


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------


class KiteClient:
    """Thin wrapper over Kite Connect v3 REST API using httpx."""

    def __init__(self) -> None:
        self.api_key = os.environ.get("KITE_API_KEY", "")
        self.api_secret = os.environ.get("KITE_API_SECRET", "")
        self.access_token = os.environ.get("KITE_ACCESS_TOKEN", "")
        if not self.api_key:
            click.echo("Error: KITE_API_KEY not set", err=True)
            raise SystemExit(1)
        self._client = httpx.Client(
            base_url=BASE_URL,
            headers={
                "X-Kite-Version": "3",
                "Authorization": f"token {self.api_key}:{self.access_token}",
            },
            timeout=30.0,
        )

    def _require_token(self) -> None:
        if not self.access_token:
            click.echo(
                "Error: KITE_ACCESS_TOKEN not set. Complete the login flow first.",
                err=True,
            )
            raise SystemExit(1)

    def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | list[tuple[str, str]] | None = None,
        data: dict[str, str] | None = None,
        json_body: Any | None = None,
    ) -> Any:
        """Make an authenticated API request. Returns parsed JSON or prints CSV."""
        self._require_token()
        try:
            resp = self._client.request(
                method,
                path,
                params=params,
                data=data,
                json=json_body,
            )
        except httpx.HTTPError as exc:
            click.echo(f"Network error: {exc}", err=True)
            raise SystemExit(1) from exc
        content_type = resp.headers.get("content-type", "")

        # Handle HTTP errors with Kite's JSON error format
        if resp.status_code >= 400:
            try:
                err = resp.json()
                click.echo(
                    f"Error {resp.status_code}: {err.get('message', resp.text)}",
                    err=True,
                )
                if "error_type" in err:
                    click.echo(f"Type: {err['error_type']}", err=True)
            except (json.JSONDecodeError, ValueError):
                click.echo(f"Error {resp.status_code}: {resp.text}", err=True)
            raise SystemExit(1)

        if "text/csv" in content_type:
            click.echo(resp.text, nl=False)
            return None

        return resp.json()

    def token_exchange(self, request_token: str) -> Any:
        """Exchange request_token for access_token (does not need existing session)."""
        if not self.api_secret:
            click.echo("Error: KITE_API_SECRET not set", err=True)
            raise SystemExit(1)
        checksum = hashlib.sha256(
            (self.api_key + request_token + self.api_secret).encode()
        ).hexdigest()
        try:
            resp = self._client.post(
                "/session/token",
                data={
                    "api_key": self.api_key,
                    "request_token": request_token,
                    "checksum": checksum,
                },
                headers={"X-Kite-Version": "3", "Authorization": ""},
            )
        except httpx.HTTPError as exc:
            click.echo(f"Network error: {exc}", err=True)
            raise SystemExit(1) from exc
        if resp.status_code >= 400:
            click.echo(f"Error {resp.status_code}: {resp.text}", err=True)
            raise SystemExit(1)
        return resp.json()


def pp(data: Any) -> None:
    """Pretty-print JSON data."""
    click.echo(json.dumps(data, indent=2))


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


@click.group()
@click.pass_context
def cli(ctx: click.Context) -> None:
    """Zerodha Kite Connect v3 CLI."""
    ctx.ensure_object(dict)


def get_client(ctx: click.Context) -> KiteClient:
    """Lazily create client on first use (avoids env var check on --help)."""
    if "client" not in ctx.obj:
        ctx.obj["client"] = KiteClient()
    return ctx.obj["client"]


# ---- Auth ----


@cli.command("token-exchange")
@click.option(
    "--request-token", required=True, help="Request token from OAuth callback"
)
@click.pass_context
def token_exchange(ctx: click.Context, request_token: str) -> None:
    """Exchange request_token for access_token."""
    client = get_client(ctx)
    result = client.token_exchange(request_token)
    pp(result)
    if result.get("status") == "success":
        token = result["data"].get("access_token", "")
        click.echo(f'\nExport this to use the API:\nexport KITE_ACCESS_TOKEN="{token}"')


@cli.command()
@click.pass_context
def profile(ctx: click.Context) -> None:
    """Get user profile."""
    pp(get_client(ctx).request("GET", "/user/profile"))


@cli.command()
@click.option("--segment", type=click.Choice(["equity", "commodity"]), default=None)
@click.pass_context
def margins(ctx: click.Context, segment: str | None) -> None:
    """Get funds and margins."""
    path = f"/user/margins/{segment}" if segment else "/user/margins"
    pp(get_client(ctx).request("GET", path))


@cli.command()
@click.pass_context
def logout(ctx: click.Context) -> None:
    """Invalidate session."""
    client = get_client(ctx)
    pp(
        client.request(
            "DELETE",
            "/session/token",
            params={
                "api_key": client.api_key,
                "access_token": client.access_token,
            },
        )
    )


# ---- Orders ----


@cli.command("order-place")
@click.option("--exchange", required=True)
@click.option("--tradingsymbol", required=True)
@click.option("--transaction-type", required=True, type=click.Choice(["BUY", "SELL"]))
@click.option(
    "--order-type", required=True, type=click.Choice(["MARKET", "LIMIT", "SL", "SL-M"])
)
@click.option("--quantity", required=True, type=int)
@click.option(
    "--product", required=True, type=click.Choice(["CNC", "NRML", "MIS", "MTF"])
)
@click.option("--price", type=float, default=None)
@click.option("--trigger-price", type=float, default=None)
@click.option("--validity", type=click.Choice(["DAY", "IOC", "TTL"]), default=None)
@click.option("--disclosed-quantity", type=int, default=None)
@click.option("--variety", default="regular")
@click.option("--tag", default=None)
@click.pass_context
def order_place(
    ctx: click.Context,
    exchange: str,
    tradingsymbol: str,
    transaction_type: str,
    order_type: str,
    quantity: int,
    product: str,
    price: float | None,
    trigger_price: float | None,
    validity: str | None,
    disclosed_quantity: int | None,
    variety: str,
    tag: str | None,
) -> None:
    """Place an order."""
    form: dict[str, str] = {
        "tradingsymbol": tradingsymbol,
        "exchange": exchange,
        "transaction_type": transaction_type,
        "order_type": order_type,
        "quantity": str(quantity),
        "product": product,
    }
    if price is not None:
        form["price"] = str(price)
    if trigger_price is not None:
        form["trigger_price"] = str(trigger_price)
    if validity:
        form["validity"] = validity
    if disclosed_quantity is not None:
        form["disclosed_quantity"] = str(disclosed_quantity)
    if tag:
        form["tag"] = tag
    pp(get_client(ctx).request("POST", f"/orders/{variety}", data=form))


@cli.command("order-modify")
@click.option("--order-id", required=True)
@click.option("--quantity", type=int, default=None)
@click.option("--price", type=float, default=None)
@click.option("--order-type", default=None)
@click.option("--trigger-price", type=float, default=None)
@click.option("--validity", default=None)
@click.option("--disclosed-quantity", type=int, default=None)
@click.option("--variety", default="regular")
@click.pass_context
def order_modify(
    ctx: click.Context,
    order_id: str,
    quantity: int | None,
    price: float | None,
    order_type: str | None,
    trigger_price: float | None,
    validity: str | None,
    disclosed_quantity: int | None,
    variety: str,
) -> None:
    """Modify a pending order."""
    form: dict[str, str] = {}
    if quantity is not None:
        form["quantity"] = str(quantity)
    if price is not None:
        form["price"] = str(price)
    if order_type:
        form["order_type"] = order_type
    if trigger_price is not None:
        form["trigger_price"] = str(trigger_price)
    if validity:
        form["validity"] = validity
    if disclosed_quantity is not None:
        form["disclosed_quantity"] = str(disclosed_quantity)
    pp(get_client(ctx).request("PUT", f"/orders/{variety}/{order_id}", data=form))


@cli.command("order-cancel")
@click.option("--order-id", required=True)
@click.option("--variety", default="regular")
@click.pass_context
def order_cancel(ctx: click.Context, order_id: str, variety: str) -> None:
    """Cancel a pending order."""
    pp(get_client(ctx).request("DELETE", f"/orders/{variety}/{order_id}"))


@cli.command("orders")
@click.pass_context
def orders(ctx: click.Context) -> None:
    """List all orders for today."""
    pp(get_client(ctx).request("GET", "/orders"))


@cli.command("order-history")
@click.option("--order-id", required=True)
@click.pass_context
def order_history(ctx: click.Context, order_id: str) -> None:
    """Get order history."""
    pp(get_client(ctx).request("GET", f"/orders/{order_id}"))


@cli.command("trades")
@click.pass_context
def trades(ctx: click.Context) -> None:
    """List all trades for today."""
    pp(get_client(ctx).request("GET", "/trades"))


# ---- Portfolio ----


@cli.command("holdings")
@click.pass_context
def holdings(ctx: click.Context) -> None:
    """Get equity holdings."""
    pp(get_client(ctx).request("GET", "/portfolio/holdings"))


@cli.command("positions")
@click.pass_context
def positions(ctx: click.Context) -> None:
    """Get positions."""
    pp(get_client(ctx).request("GET", "/portfolio/positions"))


@cli.command("position-convert")
@click.option("--tradingsymbol", required=True)
@click.option("--exchange", required=True)
@click.option("--transaction-type", required=True, type=click.Choice(["BUY", "SELL"]))
@click.option("--position-type", required=True, type=click.Choice(["overnight", "day"]))
@click.option("--quantity", required=True, type=int)
@click.option("--old-product", required=True)
@click.option("--new-product", required=True)
@click.pass_context
def position_convert(
    ctx: click.Context,
    tradingsymbol: str,
    exchange: str,
    transaction_type: str,
    position_type: str,
    quantity: int,
    old_product: str,
    new_product: str,
) -> None:
    """Convert position margin product."""
    pp(
        get_client(ctx).request(
            "PUT",
            "/portfolio/positions",
            data={
                "tradingsymbol": tradingsymbol,
                "exchange": exchange,
                "transaction_type": transaction_type,
                "position_type": position_type,
                "quantity": str(quantity),
                "old_product": old_product,
                "new_product": new_product,
            },
        )
    )


# ---- Market Quotes ----


@cli.command("quote")
@click.option(
    "--instruments", "-i", required=True, multiple=True, help="EXCHANGE:SYMBOL"
)
@click.pass_context
def quote(ctx: click.Context, instruments: tuple[str, ...]) -> None:
    """Get full market quotes (up to 500 instruments)."""
    pp(get_client(ctx).request("GET", "/quote", params=[("i", i) for i in instruments]))


@cli.command("ltp")
@click.option(
    "--instruments", "-i", required=True, multiple=True, help="EXCHANGE:SYMBOL"
)
@click.pass_context
def ltp(ctx: click.Context, instruments: tuple[str, ...]) -> None:
    """Get LTP quotes (up to 1000 instruments)."""
    pp(
        get_client(ctx).request(
            "GET", "/quote/ltp", params=[("i", i) for i in instruments]
        )
    )


@cli.command("ohlc")
@click.option(
    "--instruments", "-i", required=True, multiple=True, help="EXCHANGE:SYMBOL"
)
@click.pass_context
def ohlc(ctx: click.Context, instruments: tuple[str, ...]) -> None:
    """Get OHLC quotes (up to 1000 instruments)."""
    pp(
        get_client(ctx).request(
            "GET", "/quote/ohlc", params=[("i", i) for i in instruments]
        )
    )


@cli.command("instruments")
@click.option("--exchange", default=None)
@click.pass_context
def instruments(ctx: click.Context, exchange: str | None) -> None:
    """Download instrument list (CSV)."""
    path = f"/instruments/{exchange}" if exchange else "/instruments"
    get_client(ctx).request("GET", path)


# ---- Historical ----


@cli.command("historical")
@click.option("--instrument-token", required=True)
@click.option(
    "--interval",
    required=True,
    type=click.Choice(
        [
            "minute",
            "3minute",
            "5minute",
            "10minute",
            "15minute",
            "30minute",
            "60minute",
            "day",
        ]
    ),
)
@click.option("--from", "from_date", required=True, help="yyyy-mm-dd [hh:mm:ss]")
@click.option("--to", "to_date", required=True, help="yyyy-mm-dd [hh:mm:ss]")
@click.option("--continuous", is_flag=True)
@click.option("--oi", is_flag=True)
@click.pass_context
def historical(
    ctx: click.Context,
    instrument_token: str,
    interval: str,
    from_date: str,
    to_date: str,
    continuous: bool,
    oi: bool,
) -> None:
    """Get historical candle data."""
    params: dict[str, str] = {"from": from_date, "to": to_date}
    if continuous:
        params["continuous"] = "1"
    if oi:
        params["oi"] = "1"
    pp(
        get_client(ctx).request(
            "GET",
            f"/instruments/historical/{instrument_token}/{interval}",
            params=params,
        )
    )


# ---- GTT ----


def _build_gtt_orders(
    gtt_type: str,
    exchange: str,
    tradingsymbol: str,
    trigger_values: str,
    transaction_type: str,
    quantity: int,
    price: str,
    product: str,
) -> tuple[list[float], list[dict[str, Any]]]:
    """Build trigger values and order list for GTT (supports single + two-leg)."""
    tvs = [float(v) for v in trigger_values.split(",")]
    prices = [float(p) for p in price.split(",")]
    txn_types = (
        transaction_type.split(",") if "," in transaction_type else [transaction_type]
    )

    expected_legs = 1 if gtt_type == "single" else 2
    if len(tvs) != expected_legs:
        raise click.UsageError(
            f"{gtt_type} GTT requires exactly {expected_legs} trigger value(s)."
        )
    if len(prices) != expected_legs:
        raise click.UsageError(
            f"{gtt_type} GTT requires exactly {expected_legs} price value(s)."
        )
    if len(txn_types) not in {1, expected_legs}:
        raise click.UsageError(
            f"{gtt_type} GTT requires 1 or {expected_legs} transaction type value(s)."
        )

    order_list = []
    for i, _ in enumerate(tvs):
        order_list.append(
            {
                "exchange": exchange,
                "tradingsymbol": tradingsymbol,
                "transaction_type": txn_types[i]
                if i < len(txn_types)
                else txn_types[0],
                "quantity": quantity,
                "order_type": "LIMIT",
                "product": product,
                "price": prices[i] if i < len(prices) else prices[0],
            }
        )
    return tvs, order_list


@cli.command("gtt-place")
@click.option(
    "--type", "gtt_type", required=True, type=click.Choice(["single", "two-leg"])
)
@click.option("--exchange", required=True)
@click.option("--tradingsymbol", required=True)
@click.option("--trigger-values", required=True, help="Comma-separated trigger prices")
@click.option("--last-price", required=True, type=float)
@click.option(
    "--transaction-type",
    required=True,
    help="BUY or SELL (comma-separated for two-leg)",
)
@click.option("--quantity", required=True, type=int)
@click.option(
    "--price", required=True, help="Limit price (comma-separated for two-leg)"
)
@click.option("--product", required=True, type=click.Choice(["CNC", "NRML", "MIS"]))
@click.pass_context
def gtt_place(
    ctx: click.Context,
    gtt_type: str,
    exchange: str,
    tradingsymbol: str,
    trigger_values: str,
    last_price: float,
    transaction_type: str,
    quantity: int,
    price: str,
    product: str,
) -> None:
    """Place a GTT order."""
    tvs, order_list = _build_gtt_orders(
        gtt_type,
        exchange,
        tradingsymbol,
        trigger_values,
        transaction_type,
        quantity,
        price,
        product,
    )
    pp(
        get_client(ctx).request(
            "POST",
            "/gtt/triggers",
            data={
                "type": gtt_type,
                "condition": json.dumps(
                    {
                        "exchange": exchange,
                        "tradingsymbol": tradingsymbol,
                        "trigger_values": tvs,
                        "last_price": last_price,
                    }
                ),
                "orders": json.dumps(order_list),
            },
        )
    )


@cli.command("gtt-list")
@click.pass_context
def gtt_list(ctx: click.Context) -> None:
    """List all GTTs."""
    pp(get_client(ctx).request("GET", "/gtt/triggers"))


@cli.command("gtt-get")
@click.option("--trigger-id", required=True)
@click.pass_context
def gtt_get(ctx: click.Context, trigger_id: str) -> None:
    """Get GTT details."""
    pp(get_client(ctx).request("GET", f"/gtt/triggers/{trigger_id}"))


@cli.command("gtt-modify")
@click.option("--trigger-id", required=True)
@click.option(
    "--type", "gtt_type", required=True, type=click.Choice(["single", "two-leg"])
)
@click.option("--exchange", required=True)
@click.option("--tradingsymbol", required=True)
@click.option("--trigger-values", required=True)
@click.option("--last-price", required=True, type=float)
@click.option(
    "--transaction-type",
    required=True,
    help="BUY or SELL (comma-separated for two-leg)",
)
@click.option("--quantity", required=True, type=int)
@click.option(
    "--price", required=True, help="Limit price (comma-separated for two-leg)"
)
@click.option("--product", required=True, type=click.Choice(["CNC", "NRML", "MIS"]))
@click.pass_context
def gtt_modify(
    ctx: click.Context,
    trigger_id: str,
    gtt_type: str,
    exchange: str,
    tradingsymbol: str,
    trigger_values: str,
    last_price: float,
    transaction_type: str,
    quantity: int,
    price: str,
    product: str,
) -> None:
    """Modify a GTT."""
    tvs, order_list = _build_gtt_orders(
        gtt_type,
        exchange,
        tradingsymbol,
        trigger_values,
        transaction_type,
        quantity,
        price,
        product,
    )
    pp(
        get_client(ctx).request(
            "PUT",
            f"/gtt/triggers/{trigger_id}",
            data={
                "type": gtt_type,
                "condition": json.dumps(
                    {
                        "exchange": exchange,
                        "tradingsymbol": tradingsymbol,
                        "trigger_values": tvs,
                        "last_price": last_price,
                    }
                ),
                "orders": json.dumps(order_list),
            },
        )
    )


@cli.command("gtt-delete")
@click.option("--trigger-id", required=True)
@click.pass_context
def gtt_delete(ctx: click.Context, trigger_id: str) -> None:
    """Delete a GTT."""
    pp(get_client(ctx).request("DELETE", f"/gtt/triggers/{trigger_id}"))


# ---- Alerts ----


@cli.command("alert-create")
@click.option("--name", required=True)
@click.option(
    "--type", "alert_type", required=True, type=click.Choice(["simple", "ato"])
)
@click.option("--lhs-exchange", required=True)
@click.option("--lhs-tradingsymbol", required=True)
@click.option("--lhs-attribute", default="LastTradedPrice")
@click.option("--operator", required=True)
@click.option(
    "--rhs-type", default="constant", type=click.Choice(["constant", "instrument"])
)
@click.option("--rhs-constant", type=float, default=None)
@click.option("--rhs-exchange", default=None)
@click.option("--rhs-tradingsymbol", default=None)
@click.option("--rhs-attribute", default=None)
@click.pass_context
def alert_create(
    ctx: click.Context,
    name: str,
    alert_type: str,
    lhs_exchange: str,
    lhs_tradingsymbol: str,
    lhs_attribute: str,
    operator: str,
    rhs_type: str,
    rhs_constant: float | None,
    rhs_exchange: str | None,
    rhs_tradingsymbol: str | None,
    rhs_attribute: str | None,
) -> None:
    """Create a price alert."""
    form: dict[str, str] = {
        "name": name,
        "type": alert_type,
        "lhs_exchange": lhs_exchange,
        "lhs_tradingsymbol": lhs_tradingsymbol,
        "lhs_attribute": lhs_attribute,
        "operator": operator,
        "rhs_type": rhs_type,
    }
    if rhs_constant is not None:
        form["rhs_constant"] = str(rhs_constant)
    if rhs_exchange:
        form["rhs_exchange"] = rhs_exchange
    if rhs_tradingsymbol:
        form["rhs_tradingsymbol"] = rhs_tradingsymbol
    if rhs_attribute:
        form["rhs_attribute"] = rhs_attribute
    pp(get_client(ctx).request("POST", "/alerts", data=form))


@cli.command("alert-list")
@click.option(
    "--status", type=click.Choice(["enabled", "disabled", "deleted"]), default=None
)
@click.pass_context
def alert_list(ctx: click.Context, status: str | None) -> None:
    """List alerts."""
    params = {"status": status} if status else None
    pp(get_client(ctx).request("GET", "/alerts", params=params))


@cli.command("alert-get")
@click.option("--uuid", required=True)
@click.pass_context
def alert_get(ctx: click.Context, uuid: str) -> None:
    """Get alert details."""
    pp(get_client(ctx).request("GET", f"/alerts/{uuid}"))


@cli.command("alert-modify")
@click.option("--uuid", required=True)
@click.option("--name", required=True)
@click.option(
    "--type", "alert_type", required=True, type=click.Choice(["simple", "ato"])
)
@click.option("--lhs-exchange", required=True)
@click.option("--lhs-tradingsymbol", required=True)
@click.option("--lhs-attribute", default="LastTradedPrice")
@click.option("--operator", required=True)
@click.option("--rhs-type", default="constant")
@click.option("--rhs-constant", type=float, default=None)
@click.option("--rhs-exchange", default=None)
@click.option("--rhs-tradingsymbol", default=None)
@click.option("--rhs-attribute", default=None)
@click.pass_context
def alert_modify(
    ctx: click.Context,
    uuid: str,
    name: str,
    alert_type: str,
    lhs_exchange: str,
    lhs_tradingsymbol: str,
    lhs_attribute: str,
    operator: str,
    rhs_type: str,
    rhs_constant: float | None,
    rhs_exchange: str | None,
    rhs_tradingsymbol: str | None,
    rhs_attribute: str | None,
) -> None:
    """Modify an alert."""
    form: dict[str, str] = {
        "name": name,
        "type": alert_type,
        "lhs_exchange": lhs_exchange,
        "lhs_tradingsymbol": lhs_tradingsymbol,
        "lhs_attribute": lhs_attribute,
        "operator": operator,
        "rhs_type": rhs_type,
    }
    if rhs_constant is not None:
        form["rhs_constant"] = str(rhs_constant)
    if rhs_exchange:
        form["rhs_exchange"] = rhs_exchange
    if rhs_tradingsymbol:
        form["rhs_tradingsymbol"] = rhs_tradingsymbol
    if rhs_attribute:
        form["rhs_attribute"] = rhs_attribute
    pp(get_client(ctx).request("PUT", f"/alerts/{uuid}", data=form))


@cli.command("alert-delete")
@click.option("--uuid", required=True)
@click.pass_context
def alert_delete(ctx: click.Context, uuid: str) -> None:
    """Delete an alert."""
    pp(get_client(ctx).request("DELETE", "/alerts", params={"uuid": uuid}))


@cli.command("alert-history")
@click.option("--uuid", required=True)
@click.pass_context
def alert_history(ctx: click.Context, uuid: str) -> None:
    """Get alert trigger history."""
    pp(get_client(ctx).request("GET", f"/alerts/{uuid}/history"))


# ---- Margin Calculation ----


@cli.command("margins-order")
@click.option("--exchange", required=True)
@click.option("--tradingsymbol", required=True)
@click.option("--transaction-type", required=True, type=click.Choice(["BUY", "SELL"]))
@click.option("--quantity", required=True, type=int)
@click.option("--order-type", required=True)
@click.option("--product", required=True)
@click.option("--price", type=float, default=None)
@click.option("--trigger-price", type=float, default=None)
@click.option("--variety", default="regular")
@click.pass_context
def margins_order(
    ctx: click.Context,
    exchange: str,
    tradingsymbol: str,
    transaction_type: str,
    quantity: int,
    order_type: str,
    product: str,
    price: float | None,
    trigger_price: float | None,
    variety: str,
) -> None:
    """Calculate order margins."""
    pp(
        get_client(ctx).request(
            "POST",
            "/margins/orders",
            json_body=[
                {
                    "exchange": exchange,
                    "tradingsymbol": tradingsymbol,
                    "transaction_type": transaction_type,
                    "variety": variety,
                    "product": product,
                    "order_type": order_type,
                    "quantity": quantity,
                    "price": price or 0,
                    "trigger_price": trigger_price or 0,
                }
            ],
        )
    )


if __name__ == "__main__":
    cli()
