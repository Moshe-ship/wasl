"""Arabic NLP tools — diacritization, text analysis."""

from __future__ import annotations

import re
import unicodedata
from fastmcp import FastMCP

# Arabic Unicode ranges
ARABIC_RANGE = re.compile(r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]+")
DIACRITICS = re.compile(r"[\u064B-\u065F\u0670]")
TATWEEL = "\u0640"


def register_nlp_tools(mcp: FastMCP) -> None:

    @mcp.tool()
    async def normalize_arabic(text: str) -> str:
        """Normalize Arabic text — standardize alef forms, remove tatweel, normalize taa marbuta."""
        result = text
        # Normalize alef forms
        result = re.sub(r"[أإآا]", "ا", result)
        # Normalize taa marbuta
        result = result.replace("ة", "ه")
        # Normalize alef maqsura
        result = result.replace("ى", "ي")
        # Remove tatweel
        result = result.replace(TATWEEL, "")
        return f"النص الأصلي: {text}\nالنص المطبّع: {result}"

    @mcp.tool()
    async def remove_diacritics(text: str) -> str:
        """Remove diacritics (tashkeel) from Arabic text."""
        result = DIACRITICS.sub("", text)
        return f"بدون تشكيل: {result}"

    @mcp.tool()
    async def count_arabic_stats(text: str) -> str:
        """Count Arabic text statistics — characters, words, sentences."""
        arabic_chars = sum(1 for c in text if "\u0600" <= c <= "\u06FF")
        words = len(text.split())
        sentences = len(re.split(r"[.!?؟،؛]", text))
        has_diacritics = bool(DIACRITICS.search(text))

        return (
            f"إحصائيات النص:\n\n"
            f"الكلمات: {words}\n"
            f"الأحرف العربية: {arabic_chars}\n"
            f"الجمل (تقريبي): {sentences}\n"
            f"يحتوي تشكيل: {'نعم' if has_diacritics else 'لا'}"
        )

    @mcp.tool()
    async def check_bidi(text: str) -> str:
        """Check text for invisible bidirectional Unicode characters (Trojan Source CVE-2021-42574)."""
        dangerous_chars = {
            "\u200F": "RTL Mark",
            "\u200E": "LTR Mark",
            "\u202A": "LTR Embedding",
            "\u202B": "RTL Embedding",
            "\u202C": "Pop Directional",
            "\u202D": "LTR Override",
            "\u202E": "RTL Override",
            "\u2066": "LTR Isolate",
            "\u2067": "RTL Isolate",
            "\u2068": "First Strong Isolate",
            "\u2069": "Pop Directional Isolate",
        }

        found = []
        for i, char in enumerate(text):
            if char in dangerous_chars:
                found.append(f"  موقع {i}: {dangerous_chars[char]} (U+{ord(char):04X})")

        if not found:
            return "النص آمن — لا توجد أحرف يونيكود ثنائية الاتجاه مخفية."

        result = f"تحذير: وُجدت {len(found)} أحرف مخفية!\n\n"
        result += "\n".join(found)
        result += f"\n\nمرجع: CVE-2021-42574 (Trojan Source)"
        return result
