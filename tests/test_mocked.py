"""Mocked HTTP tests for all networked tools.

Calls the actual tool functions directly with mocked HTTP responses.
"""

import json
import os
import pytest
from unittest.mock import AsyncMock, patch, MagicMock


def _mock_response(data: dict, status_code: int = 200):
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = data
    return resp


def _mock_client(*responses):
    cm = AsyncMock()
    cm.get = AsyncMock(side_effect=list(responses))
    cm.__aenter__ = AsyncMock(return_value=cm)
    cm.__aexit__ = AsyncMock(return_value=False)
    return cm


# Load all tools by importing the register functions and calling them
# The decorated functions are accessible as regular async functions

from src.tools.prayer import register_prayer_tools
from src.tools.quran import register_quran_tools
from src.tools.hadith import register_hadith_tools
from src.tools.weather import register_weather_tools
from src.tools.stocks import register_stocks_tools
from fastmcp import FastMCP

_mcp = FastMCP("test")
register_prayer_tools(_mcp)
register_quran_tools(_mcp)
register_hadith_tools(_mcp)
register_weather_tools(_mcp)
register_stocks_tools(_mcp)


# ============================================================
# Prayer
# ============================================================

@pytest.mark.asyncio
async def test_prayer_success():
    mock_data = {
        "code": 200,
        "data": {
            "timings": {"Fajr": "04:30", "Sunrise": "06:00", "Dhuhr": "12:00",
                        "Asr": "15:30", "Maghrib": "18:30", "Isha": "20:00"},
            "date": {"hijri": {"day": "1", "month": {"ar": "رمضان"}, "year": "1447"},
                     "gregorian": {"date": "07-04-2026"}},
        },
    }
    with patch("src.tools.prayer.client", return_value=_mock_client(_mock_response(mock_data))):
        # Call the tool function directly via mcp.call_tool
        result = await _mcp.call_tool("get_prayer_times", {"city": "Riyadh"})
        text = result.content[0].text
        assert "الفجر" in text
        assert "04:30" in text


@pytest.mark.asyncio
async def test_prayer_api_fail():
    with patch("src.tools.prayer.client", return_value=_mock_client(_mock_response({}, 500))):
        result = await _mcp.call_tool("get_prayer_times", {"city": "Riyadh"})
        text = result.content[0].text
        assert "خطأ" in text


# ============================================================
# Quran
# ============================================================

@pytest.mark.asyncio
async def test_quran_search():
    mock_data = {
        "code": 200,
        "data": {
            "count": 1,
            "matches": [{"text": "بسم الله الرحمن الرحيم",
                         "surah": {"name": "الفاتحة"}, "numberInSurah": 1}],
        },
    }
    with patch("src.tools.quran.client", return_value=_mock_client(_mock_response(mock_data))):
        result = await _mcp.call_tool("search_quran", {"query": "بسم"})
        text = result.content[0].text
        assert "الفاتحة" in text


@pytest.mark.asyncio
async def test_surah_no_english():
    mock_data = {
        "code": 200,
        "data": {
            "name": "الفاتحة", "englishName": "Al-Fatiha",
            "numberOfAyahs": 7, "revelationType": "Meccan",
            "ayahs": [{"text": "بسم الله", "numberInSurah": 1}],
        },
    }
    with patch("src.tools.quran.client", return_value=_mock_client(_mock_response(mock_data))):
        result = await _mcp.call_tool("get_surah", {"surah_number": 1})
        text = result.content[0].text
        assert "مكية" in text
        assert "Meccan" not in text
        assert "Al-Fatiha" not in text


# ============================================================
# Hadith
# ============================================================

@pytest.mark.asyncio
async def test_hadith_get():
    mock_data = {
        "code": 200,
        "data": {"number": 1, "contents": {"arab": "إنما الأعمال بالنيات"}, "arab": ""},
    }
    with patch("src.tools.hadith.client", return_value=_mock_client(_mock_response(mock_data))):
        result = await _mcp.call_tool("get_hadith", {"book": "bukhari", "number": 1})
        text = result.content[0].text
        assert "الأعمال" in text


@pytest.mark.asyncio
async def test_hadith_invalid_book():
    result = await _mcp.call_tool("get_hadith", {"book": "fake", "number": 1})
    text = result.content[0].text
    assert "غير معروف" in text


# ============================================================
# Weather
# ============================================================

@pytest.mark.asyncio
async def test_weather_502():
    geo = _mock_response({"results": [{"latitude": 24.7, "longitude": 46.7, "name": "الرياض"}]})
    bad = MagicMock()
    bad.status_code = 502

    with patch("src.tools.weather.client", return_value=_mock_client(geo, bad)):
        result = await _mcp.call_tool("get_weather", {"city": "Riyadh"})
        text = result.content[0].text
        assert "خطأ" in text


# ============================================================
# Stocks
# ============================================================

@pytest.mark.asyncio
async def test_stocks_no_key():
    with patch.dict(os.environ, {}, clear=True):
        result = await _mcp.call_tool("get_stock_price", {"symbol": "أرامكو"})
        text = result.content[0].text
        assert "خطأ" in text or "TWELVE_DATA_KEY" in text


# ============================================================
# Contract
# ============================================================

def test_all_errors_arabic():
    from src.errors import ERRORS
    for key, msg in ERRORS.items():
        has_latin = any("a" <= c.lower() <= "z" for c in msg)
        assert not has_latin, f"Error '{key}' has Latin: {msg}"
