"""Hijri calendar tools — Aladhan API (free, no key)."""

from __future__ import annotations

import re

from src.errors import api_error, safe_json
from src.http import client
from fastmcp import FastMCP

API = "https://api.aladhan.com/v1"

ISLAMIC_EVENTS = [
    ("1", "محرم", "رأس السنة الهجرية"),
    ("10", "محرم", "يوم عاشوراء"),
    ("12", "ربيع الأول", "المولد النبوي"),
    ("27", "رجب", "ليلة الإسراء والمعراج"),
    ("15", "شعبان", "ليلة النصف من شعبان"),
    ("1", "رمضان", "بداية شهر رمضان"),
    ("27", "رمضان", "ليلة القدر (المرجحة)"),
    ("1", "شوال", "عيد الفطر"),
    ("9", "ذو الحجة", "يوم عرفة"),
    ("10", "ذو الحجة", "عيد الأضحى"),
]


def register_hijri_tools(mcp: FastMCP) -> None:

    @mcp.tool()
    async def hijri_today() -> str:
        """Get today's Hijri date."""
        try:
            async with client() as c:
                resp = await c.get(f"{API}/gToH")
                data = safe_json(resp)

            if data is None:
                return api_error("parse")

            if data.get("code") != 200:
                return "خطأ: لم أتمكن من جلب التاريخ الهجري"

            h = data["data"]["hijri"]
            g = data["data"]["gregorian"]
            return (
                f"اليوم: {h['day']} {h['month']['ar']} {h['year']} هـ\n"
                f"الموافق: {g['date']}\n"
                f"اليوم: {h['weekday']['ar']}"
            )
        except Exception:
            return api_error("connection")

    @mcp.tool()
    async def convert_date(
        date: str,
        direction: str = "g_to_h",
    ) -> str:
        """Convert between Gregorian and Hijri dates.

        direction: 'g_to_h' (Gregorian to Hijri) or 'h_to_g' (Hijri to Gregorian).
        date format: DD-MM-YYYY
        """
        if direction not in ("g_to_h", "h_to_g"):
            return api_error("invalid_input")
        if not re.match(r"^\d{2}-\d{2}-\d{4}$", date):
            return api_error("invalid_input")
        endpoint = "gToH" if direction == "g_to_h" else "hToG"
        try:
            async with client() as c:
                resp = await c.get(f"{API}/{endpoint}/{date}")
                data = safe_json(resp)

            if data is None:
                return api_error("parse")

            if data.get("code") != 200:
                return f"خطأ: لم أتمكن من تحويل التاريخ {date}"

            h = data["data"]["hijri"]
            g = data["data"]["gregorian"]
            return (
                f"هجري: {h['day']} {h['month']['ar']} {h['year']} هـ\n"
                f"ميلادي: {g['date']}"
            )
        except Exception:
            return api_error("connection")

    @mcp.tool()
    async def islamic_events() -> str:
        """List major Islamic events with their Hijri dates."""
        result = "المناسبات الإسلامية:\n\n"
        for day, month, event in ISLAMIC_EVENTS:
            result += f"  {day} {month} — {event}\n"
        return result
