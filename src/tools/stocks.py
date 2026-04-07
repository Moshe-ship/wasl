"""Saudi stocks tools — Twelve Data API (free tier: 800 req/day)."""

from __future__ import annotations

import os

import httpx
from fastmcp import FastMCP

API = "https://api.twelvedata.com"

SAUDI_TICKERS = {
    "أرامكو": "2222.SAU",
    "الراجحي": "1120.SAU",
    "stc": "7010.SAU",
    "سابك": "2010.SAU",
    "الأهلي": "1180.SAU",
    "المراعي": "2280.SAU",
    "اكسترا": "4003.SAU",
    "جرير": "4190.SAU",
}


def register_stocks_tools(mcp: FastMCP) -> None:

    @mcp.tool()
    async def get_stock_price(
        symbol: str,
    ) -> str:
        """Get stock price from Tadawul. Use ticker like '2222.SAU' for Aramco, or Arabic name like 'أرامكو'.

        Requires TWELVE_DATA_KEY environment variable.
        """
        api_key = os.environ.get("TWELVE_DATA_KEY", "demo")

        # Map Arabic name to ticker
        ticker = SAUDI_TICKERS.get(symbol, symbol)
        if not ticker.endswith(".SAU") and not "." in ticker:
            ticker = f"{ticker}.SAU"

        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{API}/quote",
                params={"symbol": ticker, "apikey": api_key},
            )
            data = resp.json()

        if "code" in data and data["code"] != 200:
            return f"خطأ: لم أتمكن من جلب سعر {symbol}. تأكد من رمز السهم."

        name = data.get("name", symbol)
        price = data.get("close", "?")
        change = data.get("change", "?")
        pct = data.get("percent_change", "?")
        volume = data.get("volume", "?")

        return (
            f"سهم {name} ({ticker})\n\n"
            f"السعر: {price} ر.س\n"
            f"التغير: {change} ({pct}%)\n"
            f"الحجم: {volume}\n\n"
            f"تنبيه: هذا ليس نصيحة استثمارية."
        )

    @mcp.tool()
    async def list_saudi_tickers() -> str:
        """List common Saudi stock tickers."""
        result = "أسهم سعودية شائعة:\n\n"
        for name, ticker in SAUDI_TICKERS.items():
            result += f"  {name}: {ticker}\n"
        result += "\nللمزيد من الرموز: tadawul.com.sa"
        return result
