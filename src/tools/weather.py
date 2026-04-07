"""Weather tools — Open-Meteo API (free, no key)."""

from __future__ import annotations

from src.http import client
from fastmcp import FastMCP

API = "https://api.open-meteo.com/v1/forecast"
GEOCODE = "https://geocoding-api.open-meteo.com/v1/search"

WEATHER_CODES = {
    0: "صافي",
    1: "صافي غالباً",
    2: "غائم جزئياً",
    3: "غائم",
    45: "ضباب",
    48: "ضباب متجمد",
    51: "رذاذ خفيف",
    53: "رذاذ",
    55: "رذاذ كثيف",
    61: "مطر خفيف",
    63: "مطر",
    65: "مطر غزير",
    71: "ثلج خفيف",
    73: "ثلج",
    75: "ثلج كثيف",
    95: "عاصفة رعدية",
}


def register_weather_tools(mcp: FastMCP) -> None:

    @mcp.tool()
    async def get_weather(city: str) -> str:
        """Get current weather for a city."""
        try:
            async with client() as c:
                # Geocode city name
                geo_resp = await c.get(GEOCODE, params={"name": city, "count": 1, "language": "ar"})
                geo_data = geo_resp.json()

                results = geo_data.get("results", [])
                if not results:
                    return f"لم أجد مدينة باسم: {city}"

                lat = results[0]["latitude"]
                lon = results[0]["longitude"]
                city_name = results[0].get("name", city)

                # Get weather
                resp = await c.get(API, params={
                    "latitude": lat,
                    "longitude": lon,
                    "current_weather": True,
                    "timezone": "auto",
                })
                data = resp.json()

            current = data.get("current_weather", {})
            temp = current.get("temperature", "?")
            wind = current.get("windspeed", "?")
            code = current.get("weathercode", 0)
            description = WEATHER_CODES.get(code, "غير معروف")

            return (
                f"الطقس في {city_name}\n\n"
                f"الحالة: {description}\n"
                f"الحرارة: {temp}°C\n"
                f"الرياح: {wind} كم/س"
            )
        except Exception as e:
            return f"خطأ: {type(e).__name__}"

    @mcp.tool()
    async def get_forecast(city: str, days: int = 3) -> str:
        """Get weather forecast for a city (1-7 days)."""
        days = min(max(days, 1), 7)

        try:
            async with client() as c:
                geo_resp = await c.get(GEOCODE, params={"name": city, "count": 1, "language": "ar"})
                geo_data = geo_resp.json()

                results = geo_data.get("results", [])
                if not results:
                    return f"لم أجد مدينة باسم: {city}"

                lat = results[0]["latitude"]
                lon = results[0]["longitude"]
                city_name = results[0].get("name", city)

                resp = await c.get(API, params={
                    "latitude": lat,
                    "longitude": lon,
                    "daily": "temperature_2m_max,temperature_2m_min,weathercode",
                    "timezone": "auto",
                    "forecast_days": days,
                })
                data = resp.json()

            daily = data.get("daily", {})
            dates = daily.get("time", [])
            maxs = daily.get("temperature_2m_max", [])
            mins = daily.get("temperature_2m_min", [])
            codes = daily.get("weathercode", [])

            result = f"توقعات الطقس — {city_name} ({days} أيام)\n\n"
            for i in range(len(dates)):
                desc = WEATHER_CODES.get(codes[i], "?")
                result += f"{dates[i]}: {desc} | {mins[i]}° - {maxs[i]}°\n"

            return result
        except Exception as e:
            return f"خطأ: {type(e).__name__}"
