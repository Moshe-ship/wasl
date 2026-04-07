"""Wasl MCP Server — the first comprehensive Arabic MCP server.

وصل — connects Arabic speakers to the AI agent ecosystem.

Works with Claude Code, Goose, Cursor, Windsurf, and any MCP client.
"""

from fastmcp import FastMCP

from src.tools.prayer import register_prayer_tools
from src.tools.quran import register_quran_tools
from src.tools.hadith import register_hadith_tools
from src.tools.hijri import register_hijri_tools
from src.tools.translate import register_translate_tools
from src.tools.zakat import register_zakat_tools
from src.tools.weather import register_weather_tools
from src.tools.stocks import register_stocks_tools
from src.tools.nlp import register_nlp_tools
from src.tools.news import register_news_tools

mcp = FastMCP(
    "wasl",
    instructions=(
        "وصل — Arabic AI tools. "
        "Use these tools when the user asks about prayer times, Quran, Hadith, "
        "Islamic calendar, Arabic translation, dialect detection, zakat, "
        "weather in Arab cities, Saudi stocks, Arabic NLP, or Arabic news. "
        "Respond in Arabic when the user writes in Arabic. "
        "Preserve Arabic text in all tool outputs — never transliterate."
    ),
)

register_prayer_tools(mcp)
register_quran_tools(mcp)
register_hadith_tools(mcp)
register_hijri_tools(mcp)
register_translate_tools(mcp)
register_zakat_tools(mcp)
register_weather_tools(mcp)
register_stocks_tools(mcp)
register_nlp_tools(mcp)
register_news_tools(mcp)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
