# wasl

**The first comprehensive Arabic MCP server**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-green.svg)](https://python.org)
[![Tools: 30](https://img.shields.io/badge/Tools-30-orange.svg)](#tools)

> One server. 30 Arabic tools. Every MCP client.

## Install

```bash
pip install wasl-mcp
```

## Configure

### Claude Code

```bash
claude mcp add wasl -- python -m src.server
```

### Goose

```bash
goose configure
# Add: command: python -m src.server
```

### Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "wasl": {
      "command": "python",
      "args": ["-m", "src.server"]
    }
  }
}
```

Works with Cursor, Windsurf, IntelliJ, and any MCP client.

## Tools

30 tools across 10 categories. All free APIs. Arabic-first.

### Prayer (2 tools)

| Tool | What it does | API |
|---|---|---|
| get_prayer_times | Prayer times for any city worldwide | Aladhan (free) |
| get_qibla_direction | Qibla direction from coordinates | Aladhan (free) |

### Quran (3 tools)

| Tool | What it does | API |
|---|---|---|
| search_quran | Search Quran by keyword | AlQuran Cloud (free) |
| get_verse | Get specific verse by surah:ayah | AlQuran Cloud (free) |
| get_surah | Get surah metadata and verses | AlQuran Cloud (free) |

### Hadith (2 tools)

| Tool | What it does | API |
|---|---|---|
| search_hadith | Search hadith by keyword across 6 collections | fawazahmed0 (free) |
| get_hadith | Get specific hadith by book and number | fawazahmed0 (free) |

### Hijri Calendar (3 tools)

| Tool | What it does | API |
|---|---|---|
| hijri_today | Get today's Hijri date | Aladhan (free) |
| convert_date | Convert Gregorian to Hijri and back | Aladhan (free) |
| islamic_events | List major Islamic events | Built-in |

### Translation and Dialect (3 tools)

| Tool | What it does | API |
|---|---|---|
| detect_dialect | Identify Gulf/Egyptian/Levantine/Maghrebi/MSA | Built-in |
| detect_language | Detect Arabic/English/mixed | Built-in |
| convert_arabizi | Convert Franco-Arabic to Arabic script | Built-in |

### Zakat and Finance (2 tools)

| Tool | What it does | API |
|---|---|---|
| calculate_zakat | Calculate zakat on wealth (2.5% with nisab) | Built-in |
| get_gold_price | Live gold price for nisab calculation | Gold API (free) |

### Weather (2 tools)

| Tool | What it does | API |
|---|---|---|
| get_weather | Current weather for any city | Open-Meteo (free) |
| get_forecast | Multi-day forecast | Open-Meteo (free) |

### Stocks (2 tools)

| Tool | What it does | API |
|---|---|---|
| get_stock_price | Saudi stock price from Tadawul | Twelve Data (free tier) |
| list_saudi_tickers | Common Saudi stock tickers | Built-in |

### NLP (4 tools)

| Tool | What it does | API |
|---|---|---|
| normalize_arabic | Standardize alef forms, taa marbuta, tatweel | Built-in |
| remove_diacritics | Strip tashkeel from Arabic text | Built-in |
| count_arabic_stats | Word/character/sentence counts | Built-in |
| check_bidi | Detect invisible BiDi Unicode characters (CVE-2021-42574) | Built-in |

### News (1 tool)

| Tool | What it does | API |
|---|---|---|
| search_arabic_news | Search Arabic news via DuckDuckGo | DuckDuckGo (free) |

## Dialect Support

Every language tool handles 5 Arabic dialects:

| Dialect | Example | Code |
|---|---|---|
| Gulf | ابي احجز فندق | gulf |
| Egyptian | عايز احجز فندق | egyptian |
| Levantine | بدي احجز فندق | levantine |
| Maghrebi | بغيت نحجز فندق | maghrebi |
| MSA | أريد حجز فندق | msa |

## Environment Variables

Most tools need no configuration. Optional:

| Variable | For | Required? |
|---|---|---|
| TWELVE_DATA_KEY | Saudi stocks | Optional (demo key works) |

## Development

```bash
git clone https://github.com/Moshe-ship/wasl.git
cd wasl
python -m venv .venv
source .venv/bin/activate
pip install -e .
python -m pytest tests/ -v
```

## Architecture

```
src/
  server.py          # FastMCP entry point
  tools/
    prayer.py        # Aladhan API
    quran.py         # AlQuran Cloud API
    hadith.py        # fawazahmed0 API
    hijri.py         # Aladhan API
    translate.py     # Built-in dialect detection
    zakat.py         # Gold API + built-in calculation
    weather.py       # Open-Meteo API
    stocks.py        # Twelve Data API
    nlp.py           # Built-in Arabic NLP
    news.py          # DuckDuckGo API
```

## Related Projects

| Project | Platform | Skills |
|---|---|---|
| Mkhlab | OpenClaw | 60 Arabic skills |
| Hurmoz | Hermes Agent | 63 Arabic skills |
| Wasl | MCP (everywhere) | 30 Arabic tools |

## Community

Built with input from the Saudi AI Community.

## License

MIT -- Musa the Carpenter (@Mosescreates)
