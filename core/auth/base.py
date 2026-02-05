"""Authentication abstractions."""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass(frozen=True)
class User:
    id: uuid.UUID
    email: str
    tenant_id: uuid.UUID
    roles: list[str] = field(default_factory=list)


class AbstractAuthProvider(ABC):
    @abstractmethod
    async def authenticate(self, token: str) -> User:
        """Validate a token and return the authenticated User."""

    @abstractmethod
    async def create_token(self, user: User) -> str:
        """Issue a new token for the given User."""

    @abstractmethod
    async def hash_password(self, password: str) -> str:
        """Hash a plaintext password."""

    @abstractmethod
    async def verify_password(self, password: str, hashed: str) -> bool:
        """Verify a plaintext password against a hash."""
