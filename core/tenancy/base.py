"""Tenancy abstractions."""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import StrEnum

from starlette.requests import Request


class IsolationMode(StrEnum):
    SINGLE = "single"
    SHARED = "shared"
    ISOLATED = "isolated"


@dataclass(frozen=True)
class TenantContext:
    tenant_id: uuid.UUID
    isolation_mode: IsolationMode
    database_url: str | None = None  # None → use shared DB


class TenantResolver(ABC):
    @abstractmethod
    async def resolve(self, request: Request) -> TenantContext:
        """Resolve the current request to a TenantContext."""
