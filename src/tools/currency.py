"""Currency conversion tools — exchangerate.host (free, no key)."""

from __future__ import annotations

from src.http import client
from fastmcp import FastMCP

API = "https://api.exchangerate.host/latest"

ARAB_CURRENCIES = {
    "SAR": "ريال سعودي",
    "AED": "درهم إماراتي",
    "EGP": "جنيه مصري",
    "JOD": "دينار أردني",
    "KWD": "دينار كويتي",
    "BHD": "دينار بحريني",
    "QAR": "ريال قطري",
    "OMR": "ريال عماني",
    "IQD": "دينار عراقي",
    "LBP": "ليرة لبنانية",
    "SYP": "ليرة سورية",
    "MAD": "درهم مغربي",
    "TND": "دينار تونسي",
    "DZD": "دينار جزائري",
    "LYD": "دينار ليبي",
    "SDG": "جنيه سوداني",
    "USD": "دولار أمريكي",
    "EUR": "يورو",
    "GBP": "جنيه إسترليني",
}


def register_currency_tools(mcp: FastMCP) -> None:

    @mcp.tool()
    async def convert_currency(
        amount: float,
        from_currency: str = "USD",
        to_currency: str = "SAR",
    ) -> str:
        """Convert between currencies. Supports all Arab currencies (SAR, AED, EGP, JOD, KWD, etc.)."""
        from_code = from_currency.upper()
        to_code = to_currency.upper()

        try:
            async with client() as c:
                resp = await c.get(API, params={"base": from_code, "symbols": to_code})
                data = resp.json()

            if not data.get("success", True):
                # Fallback: use approximate rates
                return _fallback_convert(amount, from_code, to_code)

            rate = data.get("rates", {}).get(to_code)
            if rate is None:
                return _fallback_convert(amount, from_code, to_code)

            converted = amount * rate
            from_name = ARAB_CURRENCIES.get(from_code, from_code)
            to_name = ARAB_CURRENCIES.get(to_code, to_code)

            return (
                f"تحويل العملات\n\n"
                f"{amount:,.2f} {from_name} ({from_code})\n"
                f"= {converted:,.2f} {to_name} ({to_code})\n"
                f"السعر: 1 {from_code} = {rate:,.4f} {to_code}"
            )
        except Exception:
            return _fallback_convert(amount, from_code, to_code)

    @mcp.tool()
    async def list_arab_currencies() -> str:
        """List all Arab world currencies with codes."""
        result = "عملات الدول العربية:\n\n"
        for code, name in sorted(ARAB_CURRENCIES.items()):
            result += f"  {code}: {name}\n"
        return result


def _fallback_convert(amount: float, from_code: str, to_code: str) -> str:
    """Approximate conversion using hardcoded rates as fallback."""
    approx_to_usd = {
        "SAR": 0.2667, "AED": 0.2723, "EGP": 0.0204, "JOD": 1.4104,
        "KWD": 3.2573, "BHD": 2.6525, "QAR": 0.2747, "OMR": 2.5974,
        "MAD": 0.1013, "USD": 1.0, "EUR": 1.08, "GBP": 1.26,
    }
    from_rate = approx_to_usd.get(from_code)
    to_rate = approx_to_usd.get(to_code)

    if not from_rate or not to_rate:
        return f"لم أتمكن من تحويل {from_code} إلى {to_code}. جرب أزواج العملات الشائعة."

    converted = amount * (from_rate / to_rate)
    return (
        f"تحويل تقريبي (قد لا يعكس السعر الحالي):\n\n"
        f"{amount:,.2f} {from_code} ≈ {converted:,.2f} {to_code}"
    )
