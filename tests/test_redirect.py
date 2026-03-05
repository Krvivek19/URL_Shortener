# ----- tests/test_redirect.py -----
# Tests for GET /{short_code} redirect endpoint.

import pytest


class TestRedirect:
    """Tests for the redirect endpoint."""

    def test_redirect_valid_code(self, client):
        """✅ Valid short code → should redirect (302)."""
        # First create a short URL
        resp = client.post("/shorten", json={
            "long_url": "https://www.google.com",
            "custom_alias": "goog"
        })
        assert resp.status_code == 201

        # Now try to redirect (don't follow redirects)
        redirect_resp = client.get("/goog", follow_redirects=False)
        assert redirect_resp.status_code == 302
        assert redirect_resp.headers["location"] == "https://www.google.com/"

    def test_redirect_not_found(self, client):
        """✅ Non-existent short code → should return 404."""
        response = client.get("/nonexistent")
        assert response.status_code == 404

    def test_redirect_increments_clicks(self, client):
        """✅ Each redirect should increment click_count."""
        # Create a short URL
        client.post("/shorten", json={
            "long_url": "https://www.example.com",
            "custom_alias": "clicks"
        })

        # Redirect 3 times
        for _ in range(3):
            client.get("/clicks", follow_redirects=False)

        # Check stats
        stats_resp = client.get("/stats/clicks")
        assert stats_resp.status_code == 200
        assert stats_resp.json()["click_count"] == 3

    def test_redirect_expired_url(self, client):
        """✅ Expired URL → should return 410 Gone."""
        # Create with a past expiry date
        client.post("/shorten", json={
            "long_url": "https://www.expired.com",
            "custom_alias": "expired",
            "expiry_date": "2020-01-01T00:00:00"  # already expired
        })

        response = client.get("/expired", follow_redirects=False)
        assert response.status_code == 410
