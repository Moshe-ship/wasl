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
        result = _arabizi_to_arabic(text)
        return f"النص الأصلي: {text}\nالتحويل: {result}"


def _arabizi_to_arabic(text: str) -> str:
    """Convert Arabizi to Arabic with proper vowel handling.

    Short vowels between consonants are dropped (Arabic doesn't write them).
    Long vowels (aa, ee, oo, ou) map to alef/ya/waw.
    Vowels at word start or end are kept.
    """
    CONSONANTS = {
        "b": "ب", "t": "ت", "j": "ج", "d": "د", "r": "ر",
        "z": "ز", "s": "س", "f": "ف", "q": "ق", "k": "ك",
        "l": "ل", "m": "م", "n": "ن", "h": "ه", "w": "و",
        "y": "ي", "p": "ب", "v": "ف", "g": "ج", "x": "كس",
    }
    DIGITS = {
        "2": "ء", "3": "ع", "5": "خ", "6": "ط",
        "7": "ح", "8": "ق", "9": "ص",
    }
    LONG_VOWELS = {
        "aa": "ا", "ee": "ي", "oo": "و", "ou": "و", "ii": "ي", "uu": "و",
    }
    MULTI = [
        ("sh", "ش"), ("ch", "تش"), ("kh", "خ"), ("gh", "غ"),
        ("th", "ث"), ("dh", "ذ"), ("ph", "ف"),
        ("3'", "غ"), ("5'", "خ"), ("6'", "ظ"), ("9'", "ض"),
    ]

    words = text.lower().split()
    arabic_words = []

    for word in words:
        # Apply multi-char consonant clusters first
        w = word
        for lat, ar in MULTI:
            w = w.replace(lat, ar)

        # Deduplicate doubled consonants (shadda) BEFORE vowel processing
        # In Arabizi, "ll" = ل with shadda, "mm" = م with shadda, etc.
        deduped = []
        for j, ch in enumerate(w):
            if j > 0 and ch == w[j - 1] and ch in CONSONANTS:
                continue  # Skip the second of a doubled consonant
            deduped.append(ch)
        w = "".join(deduped)

        # Apply long vowels AFTER dedup
        for lat, ar in LONG_VOWELS.items():
            w = w.replace(lat, ar)

        # Now process character by character
        out = []
        i = 0
        chars = list(w)
        while i < len(chars):
            c = chars[i]

            # Already Arabic (from multi-char replacement)
            if "\u0600" <= c <= "\u06FF":
                out.append(c)
                i += 1
                continue

            # Digit mappings
            if c in DIGITS:
                out.append(DIGITS[c])
                i += 1
                continue

            # Consonants always map
            if c in CONSONANTS:
                out.append(CONSONANTS[c])
                i += 1
                continue

            # Vowels: only emit if at word start, word end, or adjacent to another vowel
            if c in "aeiou":
                at_start = (i == 0)
                at_end = (i == len(chars) - 1)
                next_is_vowel = (i + 1 < len(chars) and chars[i + 1] in "aeiou")
                prev_is_vowel = (i > 0 and chars[i - 1] in "aeiou")

                if at_start:
                    # Word-initial vowel: emit alef
                    out.append("ا" if c == "a" else "ي" if c in "ei" else "و")
                elif at_end:
                    # Word-final vowels: always emit (they're real letters)
                    if c in "iy":
                        out.append("ي")
                    elif c in "ou":
                        out.append("و")
                    elif c == "a":
                        out.append("ا")
                    elif c == "e":
                        out.append("ة")  # taa marbuta is common word-final 'e'
                else:
                    # Mid-word: 'a' and 'e' are short vowels (fatha/kasra) — drop
                    # 'i' maps to ي, 'u'/'o' maps to و (these are real Arabic letters)
                    if c == "i":
                        out.append("ي")
                    elif c in "uo":
                        out.append("و")
                    # 'a' and 'e' between consonants: drop (short vowel/diacritic)
                i += 1
                continue

            # Anything else (spaces, punctuation) pass through
            out.append(c)
            i += 1

        arabic_words.append("".join(out))

    return " ".join(arabic_words)
