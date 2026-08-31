"""Bounded public-page fetcher used as an ADK function tool."""

from __future__ import annotations

import asyncio
import ipaddress
import re
import socket
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

from app.core.config import settings
from app.core.version import SHIPCHECK_USER_AGENT

MAX_RESPONSE_BYTES = 750_000
MAX_CLEAN_TEXT_CHARS = 80_000
MAX_REDIRECTS = 3

_ALLOWED_CONTENT_TYPES = (
    "text/html",
    "text/plain",
    "application/xhtml+xml",
)


class RulesFetchError(RuntimeError):
    """Raised when Shipcheck cannot safely retrieve a public rules page."""


def _reject_obvious_local_host(hostname: str) -> None:
    host = hostname.strip().lower().rstrip(".")

    if host in {"localhost", "localhost.localdomain"} or host.endswith(".local"):
        raise RulesFetchError("Local/private hosts are not allowed.")

    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        return

    if (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_multicast
        or ip.is_reserved
        or ip.is_unspecified
    ):
        raise RulesFetchError("Private or non-routable IP addresses are not allowed.")


async def _validate_public_url(url: str) -> None:
    parsed = urlparse(url)

    if parsed.scheme not in {"http", "https"}:
        raise RulesFetchError("Only HTTP(S) rules URLs are supported.")

    if not parsed.hostname:
        raise RulesFetchError("Rules URL does not contain a valid hostname.")

    _reject_obvious_local_host(parsed.hostname)

    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    try:
        addr_info = await asyncio.to_thread(
            socket.getaddrinfo,
            parsed.hostname,
            port,
            type=socket.SOCK_STREAM,
        )
    except socket.gaierror as exc:
        raise RulesFetchError(f"Could not resolve rules hostname: {exc}") from exc

    for entry in addr_info:
        resolved_ip = entry[4][0]
        ip = ipaddress.ip_address(resolved_ip)
        if (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_multicast
            or ip.is_reserved
            or ip.is_unspecified
        ):
            raise RulesFetchError(
                "Rules hostname resolved to a private or non-routable address."
            )


def _clean_html(raw_html: str, source_url: str) -> dict[str, str | int | None]:
    soup = BeautifulSoup(raw_html, "html.parser")

    title = None
    if soup.title and soup.title.string:
        title = soup.title.string.strip()

    for selector in (
        "script",
        "style",
        "noscript",
        "svg",
        "canvas",
        "form",
        "nav",
        "header",
        "footer",
    ):
        for node in soup.select(selector):
            node.decompose()

    text = soup.get_text("\n", strip=True)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = text[:MAX_CLEAN_TEXT_CHARS]

    if not text.strip():
        raise RulesFetchError("Rules page did not contain extractable text.")

    return {
        "source_url": source_url,
        "page_title": title,
        "text": text,
        "text_chars": len(text),
    }


async def fetch_rules_page(url: str) -> dict[str, str | int | None]:
    """Fetch a public competition-rules page and return bounded readable text.

    Use this tool when Shipcheck needs to inspect a public rules, FAQ, or submission
    requirements page. Local/private targets are rejected.
    """
    current_url = url

    timeout = httpx.Timeout(
        float(settings.shipcheck_request_timeout_seconds),
        connect=min(10.0, float(settings.shipcheck_request_timeout_seconds)),
    )

    headers = {
        "User-Agent": f"{SHIPCHECK_USER_AGENT} (+submission preflight inspector)",
        "Accept": "text/html,text/plain,application/xhtml+xml;q=0.9,*/*;q=0.1",
    }

    async with httpx.AsyncClient(
        timeout=timeout,
        headers=headers,
        follow_redirects=False,
    ) as client:
        for redirect_index in range(MAX_REDIRECTS + 1):
            await _validate_public_url(current_url)

            async with client.stream("GET", current_url) as response:
                if 300 <= response.status_code < 400:
                    location = response.headers.get("location")
                    if not location:
                        raise RulesFetchError(
                            "Rules page returned a redirect without a location."
                        )
                    if redirect_index >= MAX_REDIRECTS:
                        raise RulesFetchError("Rules page exceeded redirect limit.")
                    current_url = urljoin(current_url, location)
                    continue

                if response.status_code >= 400:
                    raise RulesFetchError(
                        f"Rules page returned HTTP {response.status_code}."
                    )

                content_type = response.headers.get("content-type", "").lower()
                if content_type and not any(
                    allowed in content_type for allowed in _ALLOWED_CONTENT_TYPES
                ):
                    raise RulesFetchError(
                        f"Unsupported rules-page content type: {content_type}."
                    )

                payload = bytearray()
                async for chunk in response.aiter_bytes():
                    payload.extend(chunk)
                    if len(payload) > MAX_RESPONSE_BYTES:
                        raise RulesFetchError(
                            "Rules page exceeded Shipcheck's response-size limit."
                        )

                encoding = response.encoding or "utf-8"
                raw_text = bytes(payload).decode(encoding, errors="replace")

                if "text/plain" in content_type:
                    cleaned = raw_text[:MAX_CLEAN_TEXT_CHARS].strip()
                    if not cleaned:
                        raise RulesFetchError(
                            "Rules page did not contain extractable text."
                        )
                    return {
                        "source_url": current_url,
                        "page_title": None,
                        "text": cleaned,
                        "text_chars": len(cleaned),
                    }

                return _clean_html(raw_text, current_url)

    raise RulesFetchError("Rules page could not be retrieved.")
