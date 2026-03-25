# Bot Dockerfile - uses uv for dependency management
# See https://docs.astral.sh/uv/guides/integration/docker/

ARG REGISTRY_PREFIX=harbor.pg.innopolis.university/docker-hub-cache/
FROM ${REGISTRY_PREFIX}astral/uv:python3.14-bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
ENV UV_NO_DEV=1
ENV UV_PYTHON_DOWNLOADS=0

WORKDIR /app

# Sync dependencies from workspace root (bot uses root uv.lock)
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=bot/pyproject.toml,target=bot/pyproject.toml \
    uv sync --frozen --no-install-project

# Copy bot source code
COPY bot /app/bot
COPY pyproject.toml uv.lock /app/

# Sync again with the actual code
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen

# ---
# Runtime image
# ---

ARG REGISTRY_PREFIX=harbor.pg.innopolis.university/docker-hub-cache/
FROM ${REGISTRY_PREFIX}python:3.14.2-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV LANG=C.UTF-8

# Create non-root user
RUN groupadd --system --gid 999 nonroot \
    && useradd --system --gid 999 --uid 999 --create-home nonroot

# Copy application from builder
COPY --from=builder --chown=nonroot:nonroot /app /app

# Add virtual environment to PATH
ENV PATH="/app/.venv/bin:$PATH"

WORKDIR /app

USER nonroot

# Run the bot from bot directory
CMD ["python", "bot/bot.py"]
