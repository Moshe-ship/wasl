"""Arabic names tools — built-in database."""

from __future__ import annotations

from fastmcp import FastMCP

NAMES_DB = {
    "محمد": {"meaning": "المحمود، كثير الحمد", "origin": "عربي", "gender": "ذكر", "quran": True},
    "فاطمة": {"meaning": "الفاطمة من الرضاعة", "origin": "عربي", "gender": "أنثى", "quran": False},
    "عبدالله": {"meaning": "عبد الله", "origin": "عربي", "gender": "ذكر", "quran": False},
    "عائشة": {"meaning": "ذات الحياة", "origin": "عربي", "gender": "أنثى", "quran": False},
    "أحمد": {"meaning": "أكثر حمداً", "origin": "عربي", "gender": "ذكر", "quran": True},
    "مريم": {"meaning": "العابدة المتعبدة", "origin": "عبري معرّب", "gender": "أنثى", "quran": True},
    "خالد": {"meaning": "الدائم الباقي", "origin": "عربي", "gender": "ذكر", "quran": False},
    "نورة": {"meaning": "الضياء والإشراق", "origin": "عربي", "gender": "أنثى", "quran": False},
    "سلطان": {"meaning": "صاحب السلطة والحجة", "origin": "عربي", "gender": "ذكر", "quran": True},
    "ريم": {"meaning": "الظبي الأبيض", "origin": "عربي", "gender": "أنثى", "quran": False},
    "عمر": {"meaning": "الحياة والعمر", "origin": "عربي", "gender": "ذكر", "quran": False},
    "سارة": {"meaning": "السيدة، الأميرة", "origin": "عبري معرّب", "gender": "أنثى", "quran": False},
    "يوسف": {"meaning": "يزيد الله", "origin": "عبري معرّب", "gender": "ذكر", "quran": True},
    "هند": {"meaning": "المئة من الإبل", "origin": "عربي", "gender": "أنثى", "quran": False},
    "إبراهيم": {"meaning": "أبو الجمهور", "origin": "عبري معرّب", "gender": "ذكر", "quran": True},
    "لمى": {"meaning": "سمرة الشفاه", "origin": "عربي", "gender": "أنثى", "quran": False},
    "عبدالرحمن": {"meaning": "عبد الرحمن", "origin": "عربي", "gender": "ذكر", "quran": False},
    "غيث": {"meaning": "المطر", "origin": "عربي", "gender": "ذكر", "quran": False},
    "ريان": {"meaning": "باب في الجنة للصائمين", "origin": "عربي", "gender": "ذكر", "quran": False},
    "جنى": {"meaning": "ما يُجنى من الثمر", "origin": "عربي", "gender": "أنثى", "quran": True},
    "تالا": {"meaning": "النخلة الصغيرة", "origin": "عربي", "gender": "أنثى", "quran": False},
    "سلمان": {"meaning": "السالم الخالي من العيوب", "origin": "عربي", "gender": "ذكر", "quran": False},
    "ليان": {"meaning": "النعومة والرخاء", "origin": "عربي", "gender": "أنثى", "quran": False},
    "تركي": {"meaning": "صاحب الجمال", "origin": "تركي معرّب", "gender": "ذكر", "quran": False},
    "دانة": {"meaning": "اللؤلؤة الكبيرة", "origin": "عربي", "gender": "أنثى", "quran": False},
}


def register_names_tools(mcp: FastMCP) -> None:

    @mcp.tool()
    async def lookup_name(name: str) -> str:
        """Look up the meaning of an Arabic name."""
        try:
            info = NAMES_DB.get(name)
            if not info:
                # Try partial match
                matches = [n for n in NAMES_DB if name in n or n in name]
                if matches:
                    info = NAMES_DB[matches[0]]
                    name = matches[0]
                else:
                    return f"لم أجد اسم «{name}» في القاعدة. جرب اسم عربي شائع."

            quran_note = "مذكور في القرآن" if info["quran"] else "غير مذكور في القرآن"
            return (
                f"اسم: {name}\n"
                f"المعنى: {info['meaning']}\n"
                f"الأصل: {info['origin']}\n"
                f"الجنس: {info['gender']}\n"
                f"{quran_note}"
            )
        except Exception:
            return "خطأ: تعذر البحث عن الاسم."

    @mcp.tool()
    async def suggest_names(
        gender: str = "ذكر",
        quranic_only: bool = False,
    ) -> str:
        """Suggest Arabic names. gender: 'ذكر' (male) or 'أنثى' (female)."""
        if gender not in ("ذكر", "أنثى"):
            return "خطأ: الجنس يجب أن يكون 'ذكر' أو 'أنثى'"
        try:
            filtered = {
                name: info for name, info in NAMES_DB.items()
                if info["gender"] == gender
                and (not quranic_only or info["quran"])
            }

            if not filtered:
                return f"لم أجد أسماء مطابقة للمعايير"

            result = f"أسماء {'قرآنية ' if quranic_only else ''}{'ذكور' if gender == 'ذكر' else 'إناث'}:\n\n"
            for name, info in filtered.items():
                result += f"  {name} — {info['meaning']}\n"
            return result
        except Exception:
            return "خطأ: تعذر اقتراح الأسماء."
