"""Weather tools — Open-Meteo API (free, no key)."""

from __future__ import annotations

from src.errors import api_error, safe_json
from src.http import client
from fastmcp import FastMCP

API = "https://api.open-meteo.com/v1/forecast"
GEOCODE = "https://geocoding-api.open-meteo.com/v1/search"

WEATHER_CODES = {
    0: "صافي", 1: "صافي غالباً", 2: "غائم جزئياً", 3: "غائم",
    45: "ضباب", 48: "ضباب متجمد",
    51: "رذاذ خفيف", 53: "رذاذ", 55: "رذاذ كثيف",
    61: "مطر خفيف", 63: "مطر", 65: "مطر غزير",
    71: "ثلج خفيف", 73: "ثلج", 75: "ثلج كثيف",
    95: "عاصفة رعدية",
}


async def _geocode(c, city: str) -> tuple[float, float, str] | None:
    """Geocode a city name. Returns (lat, lon, localized_name) or None."""
    resp = await c.get(GEOCODE, params={"name": city, "count": 1, "language": "ar"})
    data = safe_json(resp)
    if data is None:
        return None
    results = data.get("results", [])
    if not results:
        return None
    r = results[0]
    return r["latitude"], r["longitude"], r.get("name", city)


def register_weather_tools(mcp: FastMCP) -> None:

    @mcp.tool()
    async def get_weather(city: str) -> str:
        """Get current weather for a city."""
        if not city.strip():
            return api_error("invalid_input")
        try:
            async with client() as c:
                geo = await _geocode(c, city)
                if not geo:
                    return f"لم أجد مدينة باسم: {city}"
                lat, lon, city_name = geo

                resp = await c.get(API, params={
                    "latitude": lat, "longitude": lon,
                    "current_weather": "true", "timezone": "auto",
                })
                data = safe_json(resp)
                if data is None:
                    return api_error("unavailable")

            current = data.get("current_weather", {})
            if not current:
                return f"خطأ: لم أتمكن من قراءة بيانات الطقس لـ {city_name}"

            temp = current.get("temperature", "?")
            wind = current.get("windspeed", "?")
            code = current.get("weathercode", 0)
            description = WEATHER_CODES.get(code, "غير معروف")

            return (
                f"الطقس في {city_name}\n\n"
                f"الحالة: {description}\n"
                f"الحرارة: {temp} درجة مئوية\n"
                f"الرياح: {wind} كم/س"
            )
        except Exception:
            return api_error("connection")

    @mcp.tool()
    async def get_forecast(city: str, days: int = 3) -> str:
        """Get weather forecast for a city (1-7 days)."""
        if not city.strip():
            return api_error("invalid_input")
        days = min(max(days, 1), 7)
        try:
            async with client() as c:
                geo = await _geocode(c, city)
                if not geo:
                    return f"لم أجد مدينة باسم: {city}"
                lat, lon, city_name = geo

                resp = await c.get(API, params={
                    "latitude": lat, "longitude": lon,
                    "daily": "temperature_2m_max,temperature_2m_min,weathercode",
                    "timezone": "auto", "forecast_days": days,
                })
                data = safe_json(resp)
                if data is None:
                    return api_error("unavailable")

            daily = data.get("daily", {})
            dates = daily.get("time", [])
            maxs = daily.get("temperature_2m_max", [])
            mins = daily.get("temperature_2m_min", [])
            codes = daily.get("weathercode", [])

            if not dates:
                return f"خطأ: لم أتمكن من جلب التوقعات لـ {city_name}"

            result = f"توقعات الطقس — {city_name} ({days} أيام)\n\n"
            for i in range(len(dates)):
                desc = WEATHER_CODES.get(codes[i] if i < len(codes) else 0, "?")
                mn = mins[i] if i < len(mins) else "?"
                mx = maxs[i] if i < len(maxs) else "?"
                result += f"{dates[i]}: {desc} | {mn}° - {mx}°\n"
            return result
        except Exception:
            return api_error("connection")
