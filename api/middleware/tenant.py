"""Tenant resolution middleware."""

from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

_PUBLIC_PATHS = frozenset({"/health", "/docs", "/openapi.json", "/redoc"})


class TenantMiddleware(BaseHTTPMiddleware):
    """Resolves the tenant for every incoming request and stores it in request.state."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.url.path not in _PUBLIC_PATHS:
            resolver = request.app.state.tenant_resolver
            request.state.tenant_context = await resolver.resolve(request)
        return await call_next(request)
