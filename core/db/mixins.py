"""Reusable model mixins."""

from __future__ import annotations

import uuid

from sqlalchemy import Index
from sqlalchemy.orm import Mapped, mapped_column


class TenantMixin:
    """Mixin that adds a tenant_id column with an index."""

    tenant_id: Mapped[uuid.UUID] = mapped_column(index=True)

    @classmethod
    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        if hasattr(cls, "__tablename__"):
            cls.__table_args__ = (
                *getattr(cls, "__table_args__", ()),
                Index(f"ix_{cls.__tablename__}_tenant_id", "tenant_id"),
            )
