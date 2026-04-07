"""Shared HTTP client for all tools."""

from __future__ import annotations

import httpx

TIMEOUT = 15.0


def client() -> httpx.AsyncClient:
    """Create a configured async HTTP client."""
    return httpx.AsyncClient(
        follow_redirects=True,
        timeout=TIMEOUT,
    )
