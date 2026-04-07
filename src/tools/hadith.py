"""Hadith search tools — fawazahmed0 API (free, no key)."""

from __future__ import annotations

from src.errors import api_error, safe_json
from src.http import client
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

VALID_BOOKS = set(BOOKS.keys())


def register_hadith_tools(mcp: FastMCP) -> None:

    @mcp.tool()
    async def search_hadith(
        query: str,
        book: str = "bukhari",
    ) -> str:
        """Search hadith by keyword. Books: bukhari, muslim, abudawud, tirmidhi, nasai, ibnmajah."""
        if book not in VALID_BOOKS:
            return f"كتاب غير معروف: {book}. الكتب المتاحة: {', '.join(VALID_BOOKS)}"
        book_name = BOOKS[book]
        try:
            async with client() as c:
                resp = await c.get(f"{API}/books/{book}", params={"range": "1-300"})
                data = safe_json(resp)

            if data is None:
                return f"خطأ: لم أتمكن من الوصول لقاعدة بيانات {book_name}"

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
        except Exception:
            return api_error("connection")

    @mcp.tool()
    async def get_hadith(
        book: str,
        number: int,
    ) -> str:
        """Get a specific hadith by book and number."""
        if book not in VALID_BOOKS:
            return f"كتاب غير معروف: {book}. الكتب المتاحة: {', '.join(VALID_BOOKS)}"
        book_name = BOOKS[book]
        try:
            async with client() as c:
                resp = await c.get(f"{API}/books/{book}/{number}")
                data = safe_json(resp)

            if data is None:
                return f"خطأ: لم أجد الحديث رقم {number} في {book_name}"

            # API returns text under data.contents.arab or data.arab
            h = data.get("data", {})
            arab_text = ""
            if isinstance(h, dict):
                contents = h.get("contents", {})
                if isinstance(contents, dict):
                    arab_text = contents.get("arab", "")
                if not arab_text:
                    arab_text = h.get("arab", "")

            if not arab_text:
                return f"خطأ: لم أجد نص الحديث رقم {number} في {book_name}"

            return (
                f"{arab_text}\n\n"
                f"— {book_name}، رقم {h.get('number', number)}\n\n"
                f"تنبيه: لا تحكم على صحة حديث من عندك. ارجع لأهل العلم."
            )
        except Exception:
            return api_error("connection")
