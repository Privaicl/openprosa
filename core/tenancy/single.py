"""Single-tenant resolver for community edition."""

from __future__ import annotations

import uuid

from starlette.requests import Request

from core.tenancy.base import IsolationMode, TenantContext, TenantResolver

_DEFAULT_TENANT_ID = uuid.UUID("00000000-0000-0000-0000-000000000000")


class SingleTenantResolver(TenantResolver):
    """Always resolves to a fixed tenant — used in community edition."""

    async def resolve(self, request: Request) -> TenantContext:
        return TenantContext(
            tenant_id=_DEFAULT_TENANT_ID,
            isolation_mode=IsolationMode.SINGLE,
        )
