"""Quran search tools — AlQuran Cloud API (free, no key)."""

from __future__ import annotations

from src.errors import api_error, safe_json
from src.http import client
from fastmcp import FastMCP

API = "https://api.alquran.cloud/v1"


def register_quran_tools(mcp: FastMCP) -> None:

    @mcp.tool()
    async def search_quran(
        query: str,
        language: str = "ar",
    ) -> str:
        """Search the Quran by keyword. Returns matching verses."""
        edition = "quran-uthmani" if language == "ar" else "en.sahih"
        try:
            async with client() as c:
                resp = await c.get(f"{API}/search/{query}/all/{edition}")
                data = safe_json(resp)

            if data is None:
                return api_error("parse")

            # AlQuran Cloud returns 404 status but includes data when results exist
            matches_data = data.get("data", {})
            if isinstance(matches_data, str):
                return f"لم أجد نتائج لـ: {query}"

            matches = matches_data.get("matches", [])
            if not matches:
                return f"لم أجد نتائج لـ: {query}"

            count = matches_data.get("count", len(matches))
            result = f"نتائج البحث عن «{query}» — {count} آية\n\n"
            for m in matches[:10]:
                surah = m["surah"]["name"]
                number = m["numberInSurah"]
                result += f"﴿{m['text']}﴾\n"
                result += f"— {surah} : {number}\n\n"
            return result
        except Exception:
            return api_error("connection")

    @mcp.tool()
    async def get_verse(
        surah: int,
        ayah: int,
        edition: str = "quran-uthmani",
    ) -> str:
        """Get a specific verse by surah and ayah number. Surah 1-114."""
        if surah < 1 or surah > 114:
            return "رقم السورة يجب أن يكون بين 1 و 114"
        try:
            async with client() as c:
                resp = await c.get(f"{API}/ayah/{surah}:{ayah}/{edition}")
                data = safe_json(resp)

            if data is None:
                return api_error("parse")

            if data.get("code") != 200:
                return f"لم أجد الآية {surah}:{ayah}"

            ayah_data = data["data"]
            return (
                f"﴿{ayah_data['text']}﴾\n"
                f"— {ayah_data['surah']['name']} : {ayah_data['numberInSurah']}"
            )
        except Exception:
            return api_error("connection")

    @mcp.tool()
    async def get_surah(
        surah_number: int,
        edition: str = "quran-uthmani",
    ) -> str:
        """Get surah metadata and first verses. Surah 1-114."""
        if surah_number < 1 or surah_number > 114:
            return "رقم السورة يجب أن يكون بين 1 و 114"
        try:
            async with client() as c:
                resp = await c.get(f"{API}/surah/{surah_number}/{edition}")
                data = safe_json(resp)

            if data is None:
                return api_error("parse")

            if data.get("code") != 200:
                return f"لم أجد السورة رقم {surah_number}"

            s = data["data"]
            revelation = "مكية" if s.get("revelationType") == "Meccan" else "مدنية"
            result = f"{s['name']}\n"
            result += f"عدد الآيات: {s['numberOfAyahs']} | {revelation}\n\n"
            for ayah in s["ayahs"][:5]:
                result += f"﴿{ayah['text']}﴾ ({ayah['numberInSurah']})\n"
            if s["numberOfAyahs"] > 5:
                result += f"\n... و {s['numberOfAyahs'] - 5} آية أخرى"
            return result
        except Exception:
            return api_error("connection")
