"""Arabic translation and dialect detection tools."""

from __future__ import annotations

import re
from fastmcp import FastMCP

DIALECT_MARKERS = {
    "gulf": {
        "words": ["ابي", "ابغى", "وش", "شلونك", "زين", "يالله", "الحين", "بعدين", "وايد", "خلاص"],
        "name_ar": "خليجي",
    },
    "egyptian": {
        "words": ["عايز", "ازيك", "كده", "ازاي", "بتاع", "فين", "ليه", "دلوقتي", "اوي", "حاجة"],
        "name_ar": "مصري",
    },
    "levantine": {
        "words": ["بدي", "كيفك", "هلق", "شو", "هيك", "منيح", "كتير", "يلا", "بكرا", "هون"],
        "name_ar": "شامي",
    },
    "maghrebi": {
        "words": ["بغيت", "لاباس", "بزاف", "واش", "كيفاش", "ديال", "ماشي", "زعما", "راه", "خاصني"],
        "name_ar": "مغاربي",
    },
    "msa": {
        "words": ["أريد", "أرغب", "يجب", "ينبغي", "لذلك", "إذن", "حيث", "بالتالي", "علاوة"],
        "name_ar": "فصحى",
    },
}


def _detect_dialect(text: str) -> tuple[str, str, float]:
    """Detect Arabic dialect from text. Returns (code, name_ar, confidence)."""
    text_lower = text.strip()
    scores: dict[str, int] = {}

    for dialect, info in DIALECT_MARKERS.items():
        score = sum(1 for word in info["words"] if word in text_lower)
        if score > 0:
            scores[dialect] = score

    if not scores:
        return "msa", "فصحى", 0.5

    best = max(scores, key=scores.get)
    total_markers = sum(scores.values())
    confidence = scores[best] / max(total_markers, 1)
    return best, DIALECT_MARKERS[best]["name_ar"], min(confidence, 1.0)


def _contains_arabic(text: str) -> bool:
    return any("\u0600" <= c <= "\u06FF" for c in text)


def register_translate_tools(mcp: FastMCP) -> None:

    @mcp.tool()
    async def detect_dialect(text: str) -> str:
        """Detect the Arabic dialect of the given text.

        Identifies: Gulf (خليجي), Egyptian (مصري), Levantine (شامي), Maghrebi (مغاربي), MSA (فصحى).
        """
        if not _contains_arabic(text):
            return "النص لا يحتوي على عربي"

        code, name_ar, confidence = _detect_dialect(text)
        return (
            f"اللهجة المكتشفة: {name_ar} ({code})\n"
            f"الثقة: {confidence:.0%}\n"
            f"النص: {text[:100]}"
        )

    @mcp.tool()
    async def detect_language(text: str) -> str:
        """Detect if text is Arabic, English, or mixed."""
        arabic_chars = sum(1 for c in text if "\u0600" <= c <= "\u06FF")
        latin_chars = sum(1 for c in text if "a" <= c.lower() <= "z")
        total = arabic_chars + latin_chars

        if total == 0:
            return "لم أتمكن من تحديد اللغة"

        arabic_ratio = arabic_chars / total

        if arabic_ratio > 0.8:
            dialect_code, dialect_name, _ = _detect_dialect(text)
            return f"اللغة: عربي ({dialect_name})"
        elif arabic_ratio < 0.2:
            return "اللغة: إنجليزي"
        else:
            return f"اللغة: مختلط (عربي {arabic_ratio:.0%}، إنجليزي {1-arabic_ratio:.0%})"

    @mcp.tool()
    async def convert_arabizi(text: str) -> str:
        """Convert Arabizi (Franco-Arabic like '7abibi') to Arabic script."""
        mappings = {
            "2": "ء", "3": "ع", "5": "خ", "6": "ط",
            "7": "ح", "8": "ق", "9": "ص",
            "3'": "غ", "5'": "خ", "6'": "ظ", "9'": "ض",
        }
        result = text
        # Apply multi-char mappings first
        for arabizi, arabic in sorted(mappings.items(), key=lambda x: -len(x[0])):
            result = result.replace(arabizi, arabic)
        return f"التحويل: {result}"
