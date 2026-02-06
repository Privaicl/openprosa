"""Alembic async environment configuration."""

from __future__ import annotations

import asyncio
import importlib
import os
import pkgutil

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from core.db.base import Base

# Auto-discover model modules from project packages.
# Defaults to community packages. Set MODEL_PACKAGES env var to include more.
_packages = os.environ.get("MODEL_PACKAGES", "core,products").split(",")

for _pkg_name in _packages:
    _pkg_name = _pkg_name.strip()
    try:
        _pkg = importlib.import_module(_pkg_name)
    except ImportError:
        continue
    for _, _mod_name, _ in pkgutil.walk_packages(
        _pkg.__path__, prefix=f"{_pkg_name}."
    ):
        if _mod_name.endswith(".models"):
            importlib.import_module(_mod_name)

target_metadata = Base.metadata

config = context.config

# Override sqlalchemy.url from env var if available
database_url = os.environ.get("DATABASE_URL")
if database_url:
    config.set_main_option("sqlalchemy.url", database_url)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in 'online' mode using async engine."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
