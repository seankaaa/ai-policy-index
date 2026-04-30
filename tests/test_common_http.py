"""Tests for src/common/http.py"""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
import httpx

from src.common.http import (
    _url_cache_path,
    _host,
    is_allowed,
    fetch_url,
    USER_AGENT,
)


class TestUrlCachePath:
    def test_returns_path_under_source_dir(self):
        path = _url_cache_path("oxford_readiness", "https://example.com/data.csv")
        assert path.parts[-3] == "raw"
        assert path.parts[-2] == "oxford_readiness"
        assert path.suffix == ".csv"

    def test_different_urls_give_different_paths(self):
        p1 = _url_cache_path("src", "https://example.com/a.csv")
        p2 = _url_cache_path("src", "https://example.com/b.csv")
        assert p1 != p2

    def test_same_url_gives_same_path(self):
        p1 = _url_cache_path("src", "https://example.com/data.csv")
        p2 = _url_cache_path("src", "https://example.com/data.csv")
        assert p1 == p2


class TestHost:
    def test_extracts_host(self):
        assert _host("https://example.com/path?q=1") == "example.com"
        assert _host("http://api.oecd.org/v1/data") == "api.oecd.org"


class TestFetchUrl:
    def test_returns_cached_file_without_network(self, tmp_path, monkeypatch):
        import src.common.http as m
        monkeypatch.setattr(m, "RAW_DATA_DIR", tmp_path)

        cached = tmp_path / "test_src" / "aabbccdd.csv"
        cached.parent.mkdir(parents=True)
        cached.write_bytes(b"cached content")

        # Patch _url_cache_path to return our fixture path
        with patch.object(m, "_url_cache_path", return_value=cached):
            result = fetch_url("https://example.com/data.csv", "test_src", refresh=False)

        assert result == cached
        assert result.read_bytes() == b"cached content"

    def test_raises_permission_error_when_robots_disallows(self, tmp_path, monkeypatch):
        import src.common.http as m
        monkeypatch.setattr(m, "RAW_DATA_DIR", tmp_path)

        # Make cache miss
        with patch.object(m, "_url_cache_path", return_value=tmp_path / "miss.csv"):
            with patch.object(m, "is_allowed", return_value=False):
                with pytest.raises(PermissionError, match="robots.txt"):
                    fetch_url("https://example.com/blocked.csv", "test_src", refresh=False)

    def test_user_agent_constant(self):
        assert "AI-Policy-Dataset-Research" in USER_AGENT
        assert "academic research" in USER_AGENT
