"""Quran search tools — AlQuran Cloud API (free, no key)."""

from __future__ import annotations

import httpx
from fastmcp import FastMCP

API = "https://api.alquran.cloud/v1"


def register_quran_tools(mcp: FastMCP) -> None:

    @mcp.tool()
    async def search_quran(
        query: str,
        language: str = "ar",
    ) -> str:
        """Search the Quran by keyword. Returns matching verses."""
        edition = "quran-uthmani" if language == "ar" else f"en.sahih"
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{API}/search/{query}/all/{edition}")
            data = resp.json()

        if data.get("code") != 200:
            return f"لم أجد نتائج لـ: {query}"

        matches = data["data"]["matches"][:10]
        result = f"نتائج البحث عن «{query}» — {len(data['data']['matches'])} آية\n\n"
        for m in matches:
            surah = m["surah"]["name"]
            number = m["numberInSurah"]
            result += f"﴿{m['text']}﴾\n"
            result += f"— {surah} : {number}\n\n"
        return result

    @mcp.tool()
    async def get_verse(
        surah: int,
        ayah: int,
        edition: str = "quran-uthmani",
    ) -> str:
        """Get a specific verse by surah and ayah number."""
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{API}/ayah/{surah}:{ayah}/{edition}")
            data = resp.json()

        if data.get("code") != 200:
            return f"خطأ: لم أجد الآية {surah}:{ayah}"

        ayah_data = data["data"]
        return (
            f"﴿{ayah_data['text']}﴾\n"
            f"— {ayah_data['surah']['name']} : {ayah_data['numberInSurah']}"
        )

    @mcp.tool()
    async def get_surah(
        surah_number: int,
        edition: str = "quran-uthmani",
    ) -> str:
        """Get surah metadata and first few verses."""
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{API}/surah/{surah_number}/{edition}")
            data = resp.json()

        if data.get("code") != 200:
            return f"خطأ: لم أجد السورة رقم {surah_number}"

        s = data["data"]
        result = f"{s['name']} ({s['englishName']})\n"
        result += f"عدد الآيات: {s['numberOfAyahs']} | {s['revelationType']}\n\n"
        for ayah in s["ayahs"][:5]:
            result += f"﴿{ayah['text']}﴾ ({ayah['numberInSurah']})\n"
        if s["numberOfAyahs"] > 5:
            result += f"\n... و {s['numberOfAyahs'] - 5} آية أخرى"
        return result
