"""Tenant resolution middleware."""

from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response


class TenantMiddleware(BaseHTTPMiddleware):
    """Resolves the tenant for every incoming request and stores it in request.state."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        resolver = request.app.state.tenant_resolver
        request.state.tenant_context = await resolver.resolve(request)
        return await call_next(request)
