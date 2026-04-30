"""Shared HTTP session with rate limiting, caching, retries, and robots.txt checking."""

from __future__ import annotations

import hashlib
import logging
import time
import urllib.robotparser
from pathlib import Path
from urllib.parse import urljoin, urlparse

import httpx
from tenacity import (
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)

logger = logging.getLogger(__name__)

USER_AGENT = "AI-Policy-Dataset-Research/0.1 (academic research; contact: researcher@example.com)"

RAW_DATA_DIR = Path("data/raw")

# Per-host last-request timestamp for rate limiting
_last_request: dict[str, float] = {}
_MIN_INTERVAL = 1.0  # seconds between requests to the same host

# robots.txt cache
_robots_cache: dict[str, urllib.robotparser.RobotFileParser] = {}


def _host(url: str) -> str:
    return urlparse(url).netloc


def _rate_limit(url: str) -> None:
    host = _host(url)
    last = _last_request.get(host, 0.0)
    elapsed = time.monotonic() - last
    if elapsed < _MIN_INTERVAL:
        time.sleep(_MIN_INTERVAL - elapsed)
    _last_request[host] = time.monotonic()


def _get_robots(url: str, client: httpx.Client) -> urllib.robotparser.RobotFileParser:
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    if robots_url in _robots_cache:
        return _robots_cache[robots_url]

    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(robots_url)
    try:
        _rate_limit(robots_url)
        resp = client.get(robots_url, timeout=10)
        if resp.status_code == 200:
            rp.parse(resp.text.splitlines())
        else:
            # No robots.txt or inaccessible — assume allowed
            rp.parse([])
    except Exception as e:
        logger.debug("Could not fetch robots.txt for %s: %s", robots_url, e)
        rp.parse([])

    _robots_cache[robots_url] = rp
    return rp


def is_allowed(url: str, client: httpx.Client) -> bool:
    rp = _get_robots(url, client)
    return rp.can_fetch(USER_AGENT, url)


def _url_cache_path(source_name: str, url: str) -> Path:
    url_hash = hashlib.sha256(url.encode()).hexdigest()[:16]
    parsed = urlparse(url)
    filename = Path(parsed.path).name or "index"
    suffix = Path(filename).suffix or ".bin"
    return RAW_DATA_DIR / source_name / f"{url_hash}{suffix}"


def _is_retryable(exc: BaseException) -> bool:
    if isinstance(exc, httpx.HTTPStatusError):
        return exc.response.status_code in (429, 500, 502, 503, 504)
    if isinstance(exc, (httpx.ConnectError, httpx.ReadTimeout, httpx.RemoteProtocolError)):
        return True
    return False


def make_client() -> httpx.Client:
    return httpx.Client(
        headers={"User-Agent": USER_AGENT},
        follow_redirects=True,
        timeout=30.0,
    )


@retry(
    retry=retry_if_exception(_is_retryable),
    wait=wait_exponential(multiplier=1, min=2, max=60),
    stop=stop_after_attempt(5),
    reraise=True,
)
def _do_get(client: httpx.Client, url: str) -> httpx.Response:
    _rate_limit(url)
    resp = client.get(url)
    resp.raise_for_status()
    return resp


def fetch_url(
    url: str,
    source_name: str,
    client: httpx.Client | None = None,
    refresh: bool = False,
) -> Path:
    """Fetch URL, cache response to data/raw/<source_name>/, return local path.

    On re-run without refresh=True, returns cached file without hitting the network.
    Respects robots.txt; raises PermissionError if disallowed.
    """
    cache_path = _url_cache_path(source_name, url)

    if cache_path.exists() and not refresh:
        logger.debug("Cache hit: %s -> %s", url, cache_path)
        return cache_path

    _client = client or make_client()

    if not is_allowed(url, _client):
        raise PermissionError(f"robots.txt disallows fetching {url}")

    logger.info("Fetching %s", url)
    resp = _do_get(_client, url)

    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_bytes(resp.content)
    logger.info("Saved %d bytes -> %s", len(resp.content), cache_path)
    return cache_path


def fetch_bytes(
    url: str,
    source_name: str,
    client: httpx.Client | None = None,
    refresh: bool = False,
) -> bytes:
    path = fetch_url(url, source_name, client=client, refresh=refresh)
    return path.read_bytes()


def fetch_text(
    url: str,
    source_name: str,
    client: httpx.Client | None = None,
    refresh: bool = False,
    encoding: str = "utf-8",
) -> str:
    return fetch_bytes(url, source_name, client=client, refresh=refresh).decode(encoding, errors="replace")
