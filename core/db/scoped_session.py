"""Tenant-scoped session that auto-filters queries and sets tenant_id on inserts."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import ORMExecuteState

from core.db.mixins import TenantMixin


class TenantScopedSession(AsyncSession):
    """AsyncSession subclass that enforces tenant isolation."""

    def __init__(self, tenant_id: uuid.UUID, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._tenant_id = tenant_id
        event.listen(self.sync_session, "do_orm_execute", self._apply_tenant_filter)

    def _apply_tenant_filter(self, execute_state: ORMExecuteState) -> None:
        """Automatically add tenant_id filter to SELECT statements."""
        if execute_state.is_select:
            for mapper in execute_state.all_mappers:
                if issubclass(mapper.class_, TenantMixin):
                    execute_state.statement = execute_state.statement.filter_by(
                        tenant_id=self._tenant_id
                    )

    def add(self, instance: Any, _warn: bool = True) -> None:
        """Auto-set tenant_id on INSERT for TenantMixin models."""
        if isinstance(instance, TenantMixin) and not instance.tenant_id:
            instance.tenant_id = self._tenant_id
        super().add(instance, _warn=_warn)
