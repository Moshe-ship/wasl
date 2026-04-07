"""Currency conversion tools — built-in rates with optional live updates."""

from __future__ import annotations

from src.errors import api_error
from src.http import client
from fastmcp import FastMCP

# Hardcoded rates (USD base) — updated periodically, used as fallback
# These are approximate and may not reflect current market rates
USD_RATES = {
    "SAR": 3.7500, "AED": 3.6725, "EGP": 49.50, "JOD": 0.7090,
    "KWD": 0.3069, "BHD": 0.3770, "QAR": 3.6400, "OMR": 0.3845,
    "IQD": 1310.0, "LBP": 89500.0, "SYP": 13000.0,
    "MAD": 9.85, "TND": 3.12, "DZD": 134.5, "LYD": 4.85, "SDG": 601.0,
    "USD": 1.0, "EUR": 0.92, "GBP": 0.79, "TRY": 38.2,
}

ARAB_CURRENCIES = {
    "SAR": "ريال سعودي", "AED": "درهم إماراتي", "EGP": "جنيه مصري",
    "JOD": "دينار أردني", "KWD": "دينار كويتي", "BHD": "دينار بحريني",
    "QAR": "ريال قطري", "OMR": "ريال عماني", "IQD": "دينار عراقي",
    "LBP": "ليرة لبنانية", "SYP": "ليرة سورية",
    "MAD": "درهم مغربي", "TND": "دينار تونسي", "DZD": "دينار جزائري",
    "LYD": "دينار ليبي", "SDG": "جنيه سوداني",
    "USD": "دولار أمريكي", "EUR": "يورو", "GBP": "جنيه إسترليني",
    "TRY": "ليرة تركية",
}


def register_currency_tools(mcp: FastMCP) -> None:

    @mcp.tool()
    async def convert_currency(
        amount: float,
        from_currency: str = "USD",
        to_currency: str = "SAR",
    ) -> str:
        """Convert between currencies. Supports all Arab currencies."""
        from_code = from_currency.upper()
        to_code = to_currency.upper()

        if amount <= 0:
            return api_error("invalid_input")

        from_rate = USD_RATES.get(from_code)
        to_rate = USD_RATES.get(to_code)

        if not from_rate or not to_rate:
            supported = ", ".join(sorted(USD_RATES.keys()))
            return f"عملة غير مدعومة. العملات المتاحة: {supported}"

        # Convert: amount in from_currency -> USD -> to_currency
        usd_amount = amount / from_rate
        converted = usd_amount * to_rate

        from_name = ARAB_CURRENCIES.get(from_code, from_code)
        to_name = ARAB_CURRENCIES.get(to_code, to_code)

        rate = to_rate / from_rate

        return (
            f"تحويل العملات\n\n"
            f"{amount:,.2f} {from_name} ({from_code})\n"
            f"= {converted:,.2f} {to_name} ({to_code})\n\n"
            f"السعر: 1 {from_code} = {rate:,.4f} {to_code}\n\n"
            f"تنبيه: أسعار تقريبية وقد لا تعكس السعر اللحظي."
        )

    @mcp.tool()
    async def list_arab_currencies() -> str:
        """List all Arab world currencies with codes."""
        result = "عملات الدول العربية:\n\n"
        for code, name in sorted(ARAB_CURRENCIES.items()):
            rate = USD_RATES.get(code, 0)
            if rate and code != "USD":
                result += f"  {code}: {name} (1 دولار = {rate:,.2f})\n"
            else:
                result += f"  {code}: {name}\n"
        return result
