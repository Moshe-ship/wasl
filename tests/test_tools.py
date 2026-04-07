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
