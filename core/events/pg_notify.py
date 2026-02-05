"""PostgreSQL LISTEN/NOTIFY event bus."""

from __future__ import annotations

import json
from collections.abc import Callable, Coroutine
from typing import Any

import asyncpg

from core.events.base import AbstractEventBus


class PgNotifyEventBus(AbstractEventBus):
    def __init__(self, database_url: str) -> None:
        # asyncpg uses its own DSN format (no +asyncpg suffix)
        self._dsn = database_url.replace("postgresql+asyncpg://", "postgresql://")
        self._conn: asyncpg.Connection | None = None

    async def _ensure_connection(self) -> asyncpg.Connection:
        if self._conn is None or self._conn.is_closed():
            self._conn = await asyncpg.connect(self._dsn)
        return self._conn

    async def publish(self, channel: str, payload: dict[str, Any]) -> None:
        conn = await self._ensure_connection()
        await conn.execute(f"NOTIFY {channel}, $1", json.dumps(payload))

    async def subscribe(
        self,
        channel: str,
        handler: Callable[[dict[str, Any]], Coroutine[Any, Any, None]],
    ) -> None:
        conn = await self._ensure_connection()

        async def _listener(
            _conn: asyncpg.Connection,
            _pid: int,
            _channel: str,
            payload: str,
        ) -> None:
            await handler(json.loads(payload))

        await conn.add_listener(channel, _listener)

    async def close(self) -> None:
        if self._conn and not self._conn.is_closed():
            await self._conn.close()
