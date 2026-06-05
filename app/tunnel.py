"""Discover the app's public URL so Vapi can POST the call transcript back.

Vapi (cloud) can't reach `localhost`, so docker-compose runs an `ngrok` service that tunnels
to the app. ngrok exposes a local API listing its tunnels; we read the public https URL from
it and cache it. Set `PUBLIC_BASE_URL` to force a URL (e.g. a reserved ngrok domain) and skip
ngrok entirely. If nothing is reachable we return None and calls simply run without a
transcript callback.
"""

import logging

import httpx

from app.config import settings

LOG = logging.getLogger("app.tunnel")

# Cached after the first successful ngrok lookup (the tunnel URL is stable for the life of
# the ngrok container). Reset when the app process restarts.
_cached_base_url: str | None = None


async def public_base_url() -> str | None:
    """Return the app's public base URL (no trailing slash), or None if unavailable.

    Precedence: an explicit `PUBLIC_BASE_URL`, then the ngrok tunnel's https URL.
    """
    global _cached_base_url

    if settings.public_base_url:
        return settings.public_base_url.rstrip("/")

    if _cached_base_url is not None:
        return _cached_base_url

    try:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get(settings.ngrok_api_url)
            response.raise_for_status()
            tunnels = response.json().get("tunnels", [])
    except (httpx.HTTPError, ValueError) as exc:
        LOG.warning("Could not reach ngrok to discover a public URL", extra={"error": str(exc)})
        return None

    for tunnel in tunnels:
        url = tunnel.get("public_url", "")
        if url.startswith("https://"):
            _cached_base_url = url.rstrip("/")
            LOG.info("Discovered public URL via ngrok", extra={"public_url": _cached_base_url})
            return _cached_base_url

    LOG.warning("ngrok is reachable but has no https tunnel yet")
    return None
