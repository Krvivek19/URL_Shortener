# ----- tests/test_shorten.py -----
# Tests for POST /shorten endpoint.

import pytest


class TestShortenURL:
    """Tests for creating short URLs."""

    def test_shorten_valid_url(self, client):
        """✅ Should create a short URL for a valid long URL."""
        response = client.post("/shorten", json={
            "long_url": "https://www.google.com/search?q=python"
        })
        assert response.status_code == 201
        data = response.json()
        assert "short_url" in data
        assert "short_code" in data
        assert data["long_url"] == "https://www.google.com/search?q=python"

    def test_shorten_with_custom_alias(self, client):
        """✅ Should accept and use a custom alias."""
        response = client.post("/shorten", json={
            "long_url": "https://www.github.com",
            "custom_alias": "github"
        })
        assert response.status_code == 201
        data = response.json()
        assert data["short_code"] == "github"

    def test_shorten_duplicate_url_returns_existing(self, client):
        """✅ Same long_url submitted twice → should return the same short code."""
        payload = {"long_url": "https://www.example.com"}

        resp1 = client.post("/shorten", json=payload)
        resp2 = client.post("/shorten", json=payload)

        assert resp1.status_code == 201
        assert resp2.status_code == 201
        assert resp1.json()["short_code"] == resp2.json()["short_code"]

    def test_shorten_custom_alias_conflict(self, client):
        """✅ Duplicate custom alias → should return 409."""
        payload1 = {"long_url": "https://www.google.com", "custom_alias": "goog"}
        payload2 = {"long_url": "https://www.bing.com", "custom_alias": "goog"}

        resp1 = client.post("/shorten", json=payload1)
        resp2 = client.post("/shorten", json=payload2)

        assert resp1.status_code == 201
        assert resp2.status_code == 409

    def test_shorten_invalid_url(self, client):
        """✅ Invalid URL → should return 422 (Pydantic validation)."""
        response = client.post("/shorten", json={
            "long_url": "not-a-valid-url"
        })
        assert response.status_code == 422

    def test_shorten_empty_body(self, client):
        """✅ Empty body → should return 422."""
        response = client.post("/shorten", json={})
        assert response.status_code == 422

    def test_shorten_with_expiry(self, client):
        """✅ Should accept an expiry_date."""
        response = client.post("/shorten", json={
            "long_url": "https://www.example.com/temp",
            "expiry_date": "2030-12-31T23:59:59"
        })
        assert response.status_code == 201
        data = response.json()
        assert data["expiry_date"] is not None
