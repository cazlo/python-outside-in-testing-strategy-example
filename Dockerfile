FROM docker.io/python:3.13-alpine3.21 AS runtime
ENV PYTHONUNBUFFERED=1
ENV PIP_DEFAULT_TIMEOUT=100

# Create non-root user and group
RUN addgroup -g 1000 -S appgroup && adduser -u 1000 -S appuser -G appgroup

# Create app directory and set permissions
RUN mkdir -p /opt/app && chown -R appuser:appgroup /opt/app

# Set working directory
WORKDIR /opt/app

# Install uv
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#installing-uv
COPY --from=ghcr.io/astral-sh/uv:0.8.15@sha256:1eca97b33175f9c0896ec34f30e03ba0227efd8e38a9a0f6d12c6003eacb6faa /uv /uvx /bin/

# Ensure venv binaries are on PATH for runtime
ENV PATH="/opt/app/.venv/bin:$PATH"

# Compile bytecode
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#compiling-bytecode
ENV UV_COMPILE_BYTECODE=1

# uv Cache
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#caching
ENV UV_LINK_MODE=copy

USER appuser

# Install dependencies
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#intermediate-layers
RUN --mount=type=bind,source=app/uv.lock,target=uv.lock \
    --mount=type=bind,source=app/pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

ENV PYTHONPATH=/opt/app

# Copy application code
COPY --chown=appuser:appgroup app/alembic.ini app/pyproject.toml /opt/app/
COPY --chown=appuser:appgroup app/alembic /opt/app/alembic
COPY --chown=appuser:appgroup app/app /opt/app/app

# Sync the project
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#intermediate-layers
RUN --mount=type=bind,source=app/uv.lock,target=uv.lock \
  uv sync --frozen --no-dev

#RUN chown -R appuser:appgroup /opt/app/.venv

#ENV PYTHONPATH=/opt/app
EXPOSE 8000

# Switch to non-root user
#USER appuser

FROM runtime AS test
USER root

# renovate: datasource=repology depName=alpine_3_21/gcc versioning=loose
ENV GCC_VERSION="14.2.0-r4"
# renovate: datasource=repology depName=alpine_3_21/musl-dev versioning=loose
ENV MUSL_DEV_VERSION="1.2.5-r9"
# renovate: datasource=repology depName=alpine_3_21/linux-headers versioning=loose
ENV LINUX_HEADERS_VERSION="6.6-r1"

# Install dependencies needed for testing
RUN apk add --no-cache  \
    gcc="${GCC_VERSION}" \
    musl-dev="${MUSL_DEV_VERSION}" \
    linux-headers="${LINUX_HEADERS_VERSION}"

# allow coverage to write here for tests
RUN chown appuser:appgroup /opt/app

USER appuser

# Install all dependencies including dev dependencies
RUN --mount=type=bind,source=app/uv.lock,target=uv.lock \
  uv sync --frozen --group dev

COPY --chown=appuser:appgroup app/test /opt/app/test

ENV PATH="/opt/app/.venv/bin:$PATH"

# Switch back to non-root user for running tests
USER appuser
