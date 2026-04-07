"""Zakat and Islamic finance tools."""

from __future__ import annotations

from src.errors import api_error, safe_json
from src.http import client
from fastmcp import FastMCP

NISAB_GOLD_GRAMS = 85
ZAKAT_RATE = 0.025  # 2.5%


def register_zakat_tools(mcp: FastMCP) -> None:

    @mcp.tool()
    async def calculate_zakat(
        amount: float,
        currency: str = "SAR",
        wealth_type: str = "cash",
    ) -> str:
        """Calculate zakat on wealth.

        wealth_type: cash, gold, silver, stocks, business
        """
        if amount < 0:
            return api_error("invalid_input")
        try:
            zakat_amount = amount * ZAKAT_RATE

            type_names = {
                "cash": "نقد",
                "gold": "ذهب",
                "silver": "فضة",
                "stocks": "أسهم",
                "business": "عروض تجارة",
            }
            type_ar = type_names.get(wealth_type, wealth_type)

            result = f"حساب الزكاة\n\n"
            result += f"المبلغ: {amount:,.2f} {currency}\n"
            result += f"النوع: {type_ar}\n"
            result += f"النسبة: 2.5%\n"
            result += f"الزكاة المستحقة: {zakat_amount:,.2f} {currency}\n\n"
            result += f"تنبيه: هذا حساب تقريبي. استشر مستشارك الشرعي للحالات المعقدة."
            return result
        except Exception:
            return api_error("connection")

    @mcp.tool()
    async def get_gold_price() -> str:
        """Get current gold price for nisab calculation."""
        try:
            async with client() as c:
                resp = await c.get(
                    "https://api.gold-api.com/price/XAU",
                    timeout=10.0,
                )
                data = safe_json(resp)

            if data is None:
                return api_error("parse")

            price_usd = data.get("price", 0)
            if price_usd <= 0:
                return "لم أتمكن من جلب سعر الذهب. تحقق يدوياً من السعر."

            nisab_usd = price_usd * NISAB_GOLD_GRAMS / 31.1035  # troy oz to grams
            nisab_sar = nisab_usd * 3.75  # approximate SAR

            return (
                f"سعر الذهب الحالي\n\n"
                f"الأونصة: ${price_usd:,.2f}\n"
                f"الغرام: ${price_usd / 31.1035:,.2f}\n\n"
                f"نصاب الزكاة ({NISAB_GOLD_GRAMS} غرام ذهب):\n"
                f"  بالدولار: ${nisab_usd:,.2f}\n"
                f"  بالريال (تقريبي): {nisab_sar:,.2f} ر.س"
            )
        except Exception:
            return api_error("connection")
