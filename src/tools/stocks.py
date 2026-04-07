"""Saudi stocks tools — Twelve Data API (requires TWELVE_DATA_KEY env var)."""

from __future__ import annotations

import os

from src.http import client
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
    async def get_stock_price(symbol: str) -> str:
        """Get stock price from Tadawul. Use ticker like '2222.SAU' or Arabic name like 'أرامكو'.

        Requires TWELVE_DATA_KEY environment variable.
        """
        api_key = os.environ.get("TWELVE_DATA_KEY", "")
        if not api_key:
            return (
                "خطأ: متغير البيئة TWELVE_DATA_KEY غير مضبوط.\n"
                "سجل مجاناً في twelvedata.com واضبط المتغير:\n"
                "export TWELVE_DATA_KEY=your_key"
            )

        ticker = SAUDI_TICKERS.get(symbol, symbol)
        if "." not in ticker:
            ticker = f"{ticker}.SAU"

        try:
            async with client() as c:
                resp = await c.get(f"{API}/quote", params={"symbol": ticker, "apikey": api_key})
                if resp.status_code == 401:
                    return "خطأ: مفتاح الواجهة البرمجية غير صالح. تحقق من TWELVE_DATA_KEY."
                if resp.status_code == 429:
                    return "خطأ: تم تجاوز الحد المسموح. حاول لاحقاً."
                if resp.status_code != 200:
                    return f"خطأ: لم أتمكن من الوصول لخدمة الأسهم"

                data = resp.json()

            name = data.get("name", symbol)
            price = data.get("close", "غير متاح")
            change = data.get("change", "?")
            pct = data.get("percent_change", "?")

            return (
                f"سهم {name} ({ticker})\n\n"
                f"السعر: {price} ر.س\n"
                f"التغير: {change} ({pct}%)\n\n"
                f"تنبيه: هذا ليس نصيحة استثمارية."
            )
        except Exception:
            return "خطأ: تعذر الاتصال بخدمة الأسهم. حاول لاحقاً."

    @mcp.tool()
    async def list_saudi_tickers() -> str:
        """List common Saudi stock tickers."""
        result = "أسهم سعودية شائعة:\n\n"
        for name, ticker in SAUDI_TICKERS.items():
            result += f"  {name}: {ticker}\n"
        result += "\nللمزيد: tadawul.com.sa"
        return result
