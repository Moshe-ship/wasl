"""Tests for Wasl MCP tools."""

import pytest
from src.tools.translate import _detect_dialect, _contains_arabic
from src.tools.nlp import DIACRITICS


def test_detect_dialect_gulf():
    code, name, conf = _detect_dialect("ابي احجز فندق في دبي")
    assert code == "gulf"
    assert name == "خليجي"


def test_detect_dialect_egyptian():
    code, name, conf = _detect_dialect("عايز اروح القاهرة")
    assert code == "egyptian"
    assert name == "مصري"


def test_detect_dialect_levantine():
    code, name, conf = _detect_dialect("بدي احجز تكسي هلق")
    assert code == "levantine"
    assert name == "شامي"


def test_detect_dialect_maghrebi():
    code, name, conf = _detect_dialect("بغيت نمشي لكازا بزاف")
    assert code == "maghrebi"
    assert name == "مغاربي"


def test_detect_dialect_msa():
    code, name, conf = _detect_dialect("أريد أن أحجز غرفة في الفندق")
    assert code == "msa"
    assert name == "فصحى"


def test_detect_dialect_unknown():
    code, name, conf = _detect_dialect("hello world")
    assert code == "msa"  # default fallback


def test_contains_arabic():
    assert _contains_arabic("مرحبا") is True
    assert _contains_arabic("hello") is False
    assert _contains_arabic("hello مرحبا") is True
    assert _contains_arabic("12345") is False


def test_diacritics_regex():
    text_with = "بِسْمِ اللَّهِ"
    text_without = "بسم الله"
    assert DIACRITICS.search(text_with) is not None
    assert DIACRITICS.search(text_without) is None


def test_zakat_calculation():
    # 2.5% of 100,000 = 2,500
    from src.tools.zakat import ZAKAT_RATE
    assert ZAKAT_RATE == 0.025
    assert 100000 * ZAKAT_RATE == 2500


def test_saudi_tickers():
    from src.tools.stocks import SAUDI_TICKERS
    assert "أرامكو" in SAUDI_TICKERS
    assert SAUDI_TICKERS["أرامكو"] == "2222.SAU"


def test_weather_codes():
    from src.tools.weather import WEATHER_CODES
    assert WEATHER_CODES[0] == "صافي"
    assert WEATHER_CODES[63] == "مطر"


def test_hadith_books():
    from src.tools.hadith import BOOKS
    assert "bukhari" in BOOKS
    assert BOOKS["bukhari"] == "صحيح البخاري"


def test_islamic_events():
    from src.tools.hijri import ISLAMIC_EVENTS
    assert len(ISLAMIC_EVENTS) >= 10
    names = [e[2] for e in ISLAMIC_EVENTS]
    assert "عيد الفطر" in names
    assert "عيد الأضحى" in names


def test_arab_currencies():
    from src.tools.currency import ARAB_CURRENCIES
    assert "SAR" in ARAB_CURRENCIES
    assert "AED" in ARAB_CURRENCIES
    assert ARAB_CURRENCIES["SAR"] == "ريال سعودي"


def test_currency_rates():
    from src.tools.currency import USD_RATES
    assert USD_RATES["SAR"] == 3.75
    assert USD_RATES["USD"] == 1.0
    assert "AED" in USD_RATES


def test_arabizi_conversion():
    """Test that Arabizi converts correctly — short vowels dropped, no Latin output."""
    from src.tools.translate import _arabizi_to_arabic

    # 7abibi -> حبيبي (short vowels between consonants dropped)
    result = _arabizi_to_arabic("7abibi")
    assert result == "حبيبي", f"Expected حبيبي, got {result}"

    # No Latin letters should remain in any conversion
    result = _arabizi_to_arabic("marhaba")
    assert not any("a" <= c <= "z" for c in result), f"Latin chars in: {result}"

    # yalla -> يلا (doubled L = shadda = single ل, final a = ا)
    result = _arabizi_to_arabic("yalla")
    assert result == "يلا", f"Expected يلا, got {result}"


def test_names_db():
    from src.tools.names import NAMES_DB
    assert "محمد" in NAMES_DB
    assert NAMES_DB["محمد"]["gender"] == "ذكر"
    assert NAMES_DB["مريم"]["quran"] is True
    assert len(NAMES_DB) >= 20


def test_server_imports():
    from src.server import mcp
    assert mcp.name == "wasl"
