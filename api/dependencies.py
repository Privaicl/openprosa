"""FastAPI dependency injection."""

from __future__ import annotations

from collections.abc import AsyncIterator

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from core.tenancy.base import TenantContext


async def get_tenant_context(request: Request) -> TenantContext:
    """Return the TenantContext set by TenantMiddleware."""
    ctx: TenantContext | None = getattr(request.state, "tenant_context", None)
    if ctx is None:
        raise RuntimeError("TenantContext not found — is TenantMiddleware enabled?")
    return ctx


async def get_session(
    request: Request,
    tenant: TenantContext = Depends(get_tenant_context),
) -> AsyncIterator[AsyncSession]:
    """Yield a tenant-scoped async session."""
    from core.db.scoped_session import TenantScopedSession

    factory = request.app.state.session_factory
    async with TenantScopedSession(
        tenant_id=tenant.tenant_id,
        bind=factory.kw["bind"],
        expire_on_commit=False,
    ) as session:
        yield session
