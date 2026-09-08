"""Demo Ethiopian asset prices and deterministic investment calculations."""

from __future__ import annotations


STOCKS: dict[str, float] = {
    "ETH-TBILL": 100.00,
    "ETH-BOND": 102.50,
    "GOLD-GRAM": 9_450.00,
    "USD-SAVINGS": 56.90,
}


def calculate_investment(
    shares: float, purchase_price: float, current_price: float
) -> dict[str, float]:
    safe_shares = max(float(shares or 0), 0.0)
    safe_purchase_price = max(float(purchase_price or 0), 0.0)
    safe_current_price = max(float(current_price or 0), 0.0)
    cost = safe_shares * safe_purchase_price
    value = safe_shares * safe_current_price
    profit = value - cost
    return_pct = profit / cost * 100 if cost > 0 else 0.0

    return {
        "cost": cost,
        "value": value,
        "profit": profit,
        "return_pct": return_pct,
    }


SECTORS = {
    "ETH-TBILL": "Government securities", "ETH-BOND": "Government securities",
    "GOLD-GRAM": "Commodities", "USD-SAVINGS": "Cash and savings",
}


def calculate_portfolio(holdings: list[dict], quotes: dict[str, dict]) -> dict:
    rows, total_cost, total_value, total_dividends = [], 0.0, 0.0, 0.0
    for holding in holdings:
        quote = quotes.get(holding["ticker"], {})
        current_price = float(quote.get("price", holding["purchase_price"]))
        cost = float(holding["shares"]) * float(holding["purchase_price"])
        value = float(holding["shares"]) * current_price
        dividends = float(holding.get("dividends", 0))
        gain = value - cost + dividends
        rows.append({**holding, "current_price": current_price, "cost": cost, "value": value,
                     "gain": gain, "return_pct": gain / cost * 100 if cost else 0,
                     "sector": SECTORS.get(holding["ticker"], "Other")})
        total_cost += cost; total_value += value; total_dividends += dividends
    total_gain = total_value - total_cost + total_dividends
    for row in rows:
        row["allocation_pct"] = row["value"] / total_value * 100 if total_value else 0
    concentration = max((row["allocation_pct"] for row in rows), default=0)
    return {"rows": rows, "cost": total_cost, "value": total_value, "dividends": total_dividends,
            "gain": total_gain, "return_pct": total_gain / total_cost * 100 if total_cost else 0,
            "concentration_pct": concentration, "sectors": len({row["sector"] for row in rows})}
