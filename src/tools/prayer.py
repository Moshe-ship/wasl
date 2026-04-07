"""Prayer times tools — Aladhan API (free, no key)."""

from __future__ import annotations

from src.errors import api_error, safe_json
from src.http import client
from fastmcp import FastMCP

API = "https://api.aladhan.com/v1"

METHODS = {
    "umm_al_qura": 4,
    "egyptian": 5,
    "isna": 2,
    "mwl": 3,
    "karachi": 1,
}


def register_prayer_tools(mcp: FastMCP) -> None:

    @mcp.tool()
    async def get_prayer_times(
        city: str,
        country: str = "SA",
        method: int = 4,
    ) -> str:
        """Get prayer times for a city. Default method 4 (Umm al-Qura/Saudi).

        Methods: 1=Karachi, 2=ISNA, 3=MWL, 4=Umm al-Qura, 5=Egyptian
        """
        if not city.strip():
            return api_error("invalid_input")
        try:
            async with client() as c:
                resp = await c.get(
                    f"{API}/timingsByCity",
                    params={"city": city, "country": country, "method": method},
                )
                data = safe_json(resp)

            if data is None:
                return api_error("parse")

            if data.get("code") != 200:
                return f"خطأ: لم أتمكن من جلب أوقات الصلاة لـ {city}"

            timings = data["data"]["timings"]
            date = data["data"]["date"]
            hijri = date["hijri"]
            gregorian = date["gregorian"]["date"]

            result = f"أوقات الصلاة — {city}\n"
            result += f"{hijri['day']} {hijri['month']['ar']} {hijri['year']} هـ | {gregorian}\n\n"
            result += f"الفجر: {timings['Fajr']}\n"
            result += f"الشروق: {timings['Sunrise']}\n"
            result += f"الظهر: {timings['Dhuhr']}\n"
            result += f"العصر: {timings['Asr']}\n"
            result += f"المغرب: {timings['Maghrib']}\n"
            result += f"العشاء: {timings['Isha']}\n"
            return result
        except Exception:
            return api_error("connection")

    @mcp.tool()
    async def get_qibla_direction(
        latitude: float,
        longitude: float,
    ) -> str:
        """Get qibla direction from coordinates."""
        try:
            async with client() as c:
                resp = await c.get(f"{API}/qibla/{latitude}/{longitude}")
                data = safe_json(resp)

            if data is None:
                return api_error("parse")

            if data.get("code") != 200:
                return "خطأ: لم أتمكن من حساب اتجاه القبلة"

            direction = data["data"]["direction"]
            return f"اتجاه القبلة: {direction:.2f} درجة من الشمال"
        except Exception:
            return api_error("connection")
