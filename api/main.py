"""FastAPI application — community edition."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from core.auth.local import LocalAuthProvider
from core.db.session import build_session_factory
from core.storage.local import LocalStorageBackend
from core.tenancy.single import SingleTenantResolver
from settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Wire up community implementations on startup."""
    app.state.auth = LocalAuthProvider(
        secret=settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
        expire_minutes=settings.jwt_expiration_minutes,
    )
    app.state.tenant_resolver = SingleTenantResolver()
    app.state.storage = LocalStorageBackend(root=settings.storage_local_root)
    app.state.session_factory = build_session_factory(settings.database_url)

    yield


app = FastAPI(
    title="Privai Platform",
    version="0.1.0",
    lifespan=lifespan,
)

# ── Middleware ──────────────────────────────────────────────────────────
from api.middleware.tenant import TenantMiddleware  # noqa: E402

app.add_middleware(TenantMiddleware)

# ── Routes ─────────────────────────────────────────────────────────────
from api.routes import dsar  # noqa: E402

app.include_router(dsar.router, prefix="/api/dsar", tags=["DSAR"])


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "edition": settings.edition}
