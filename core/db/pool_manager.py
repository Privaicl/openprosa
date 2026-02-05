"""Tenant pool manager — LRU engine cache for database-per-tenant isolation."""

from __future__ import annotations

import asyncio
import uuid
from collections import OrderedDict

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine


class TenantPoolManager:
    """Manages a cache of async engines keyed by tenant_id."""

    def __init__(self, max_size: int = 32) -> None:
        self._engines: OrderedDict[uuid.UUID, AsyncEngine] = OrderedDict()
        self._max_size = max_size
        self._shared_engine: AsyncEngine | None = None
        self._background_tasks: set[asyncio.Task[None]] = set()

    def set_shared_engine(self, database_url: str) -> AsyncEngine:
        """Create and cache the shared (default) engine."""
        self._shared_engine = create_async_engine(database_url, echo=False)
        return self._shared_engine

    def get_engine(
        self,
        tenant_id: uuid.UUID,
        database_url: str | None = None,
    ) -> AsyncEngine:
        """Return the engine for a tenant, creating one if necessary.

        If *database_url* is ``None``, the shared engine is returned.
        """
        if database_url is None:
            if self._shared_engine is None:
                raise RuntimeError("Shared engine not initialised — call set_shared_engine first")
            return self._shared_engine

        if tenant_id in self._engines:
            self._engines.move_to_end(tenant_id)
            return self._engines[tenant_id]

        engine = create_async_engine(database_url, echo=False)
        self._engines[tenant_id] = engine

        if len(self._engines) > self._max_size:
            _, evicted = self._engines.popitem(last=False)
            task = asyncio.create_task(evicted.dispose())
            self._background_tasks.add(task)
            task.add_done_callback(self._background_tasks.discard)

        return engine

    async def dispose(self) -> None:
        """Dispose all cached engines."""
        for engine in self._engines.values():
            await engine.dispose()
        self._engines.clear()
        if self._shared_engine:
            await self._shared_engine.dispose()
            self._shared_engine = None
