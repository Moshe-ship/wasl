"""Hadith search tools — fawazahmed0 API (free, no key)."""

from __future__ import annotations

import httpx
from fastmcp import FastMCP

API = "https://api.hadith.gading.dev"

BOOKS = {
    "bukhari": "صحيح البخاري",
    "muslim": "صحيح مسلم",
    "abudawud": "سنن أبي داود",
    "tirmidhi": "جامع الترمذي",
    "nasai": "سنن النسائي",
    "ibnmajah": "سنن ابن ماجه",
}


def register_hadith_tools(mcp: FastMCP) -> None:

    @mcp.tool()
    async def search_hadith(
        query: str,
        book: str = "bukhari",
    ) -> str:
        """Search hadith by keyword. Books: bukhari, muslim, abudawud, tirmidhi, nasai, ibnmajah."""
        book_name = BOOKS.get(book, book)
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{API}/books/{book}", params={"range": "1-300"})
            data = resp.json()

        if data.get("code") != 200:
            return f"خطأ: لم أتمكن من البحث في {book_name}"

        hadiths = data.get("data", {}).get("hadiths", [])
        matches = [h for h in hadiths if query in h.get("arab", "")][:5]

        if not matches:
            return f"لم أجد أحاديث تحتوي على «{query}» في {book_name}"

        result = f"نتائج البحث في {book_name} عن «{query}»:\n\n"
        for h in matches:
            result += f"{h.get('arab', '')[:200]}\n"
            result += f"— رقم الحديث: {h.get('number', '?')}\n\n"

        result += "تنبيه: لا تحكم على صحة حديث من عندك. ارجع لأهل العلم."
        return result

    @mcp.tool()
    async def get_hadith(
        book: str,
        number: int,
    ) -> str:
        """Get a specific hadith by book and number."""
        book_name = BOOKS.get(book, book)
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{API}/books/{book}/{number}")
            data = resp.json()

        if data.get("code") != 200:
            return f"خطأ: لم أجد الحديث رقم {number} في {book_name}"

        h = data.get("data", {})
        return (
            f"{h.get('arab', '')}\n\n"
            f"— {book_name}، رقم {h.get('number', '?')}"
        )
