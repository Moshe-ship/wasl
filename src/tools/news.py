"""Arabic news tools — DuckDuckGo (free, no key)."""

from __future__ import annotations

from src.errors import api_error, safe_json
from src.http import client
from fastmcp import FastMCP

DDG_API = "https://api.duckduckgo.com/"


def register_news_tools(mcp: FastMCP) -> None:

    @mcp.tool()
    async def search_arabic_news(query: str) -> str:
        """Search for Arabic news using DuckDuckGo with Arabic region bias."""
        if not query.strip():
            return api_error("invalid_input")
        try:
            async with client() as c:
                resp = await c.get(
                    DDG_API,
                    params={
                        "q": query,
                        "format": "json",
                        "kl": "xa-ar",
                        "no_html": 1,
                    },
                    timeout=10.0,
                )
                data = safe_json(resp)

            if data is None:
                return api_error("parse")

            # Extract results
            results = []

            # Abstract (main answer)
            if data.get("Abstract"):
                results.append({
                    "title": data.get("Heading", ""),
                    "text": data["Abstract"],
                    "source": data.get("AbstractSource", ""),
                })

            # Related topics
            for topic in data.get("RelatedTopics", [])[:5]:
                if "Text" in topic:
                    results.append({
                        "title": topic.get("Text", "")[:80],
                        "text": topic.get("Text", ""),
                        "url": topic.get("FirstURL", ""),
                    })

            if not results:
                return f"لم أجد نتائج لـ: {query}\n\nجرب البحث عبر: duckduckgo.com/?q={query}&kl=xa-ar"

            output = f"نتائج البحث عن «{query}»:\n\n"
            for r in results:
                output += f"  {r['title']}\n"
                if r.get("text"):
                    output += f"  {r['text'][:150]}\n"
                if r.get("url"):
                    output += f"  {r['url']}\n"
                output += "\n"

            return output
        except Exception:
            return api_error("connection")
