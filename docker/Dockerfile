FROM python:3.13-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files first for caching
COPY pyproject.toml uv.lock* ./

# Install production dependencies only
RUN uv sync --no-dev --frozen || uv sync --no-dev

# Copy application code (community edition only)
COPY settings.py ./
COPY core/ core/
COPY api/ api/
COPY dsar/ dsar/
COPY alembic.ini ./
COPY alembic/ alembic/

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
