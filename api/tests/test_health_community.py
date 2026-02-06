"""Health endpoint tests for the community edition."""

from __future__ import annotations

import httpx
import pytest

from api.main import app


@pytest.fixture
def client() -> httpx.AsyncClient:
    transport = httpx.ASGITransport(app=app)
    return httpx.AsyncClient(transport=transport, base_url="http://test")


async def test_health_returns_ok(client: httpx.AsyncClient) -> None:
    async with client:
        resp = await client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data == {"status": "ok", "edition": "community"}
