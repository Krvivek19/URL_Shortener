# ----- tests/test_stats.py -----
# Tests for GET /stats/{short_code} endpoint.

import pytest


class TestStats:
    """Tests for the stats endpoint."""

    def test_stats_valid_code(self, client):
        """✅ Should return stats for a valid short code."""
        # Create a URL
        client.post("/shorten", json={
            "long_url": "https://www.google.com",
            "custom_alias": "stats1"
        })

        # Get stats
        response = client.get("/stats/stats1")
        assert response.status_code == 200
        data = response.json()
        assert data["short_code"] == "stats1"
        assert data["long_url"] == "https://www.google.com/"
        assert data["click_count"] == 0
        assert "created_at" in data

    def test_stats_not_found(self, client):
        """✅ Non-existent short code → should return 404."""
        response = client.get("/stats/doesnotexist")
        assert response.status_code == 404

    def test_stats_shows_click_count(self, client):
        """✅ Stats should reflect actual click count."""
        # Create
        client.post("/shorten", json={
            "long_url": "https://www.example.org",
            "custom_alias": "track"
        })

        # Click 5 times
        for _ in range(5):
            client.get("/track", follow_redirects=False)

        # Verify
        response = client.get("/stats/track")
        assert response.json()["click_count"] == 5
