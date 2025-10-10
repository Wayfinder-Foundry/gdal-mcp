# syntax=docker/dockerfile:1.7

# =========================================================================
# Base image with GDAL runtime (used by both stages)
# =========================================================================
FROM ghcr.io/osgeo/gdal:ubuntu-small-3.8.0 AS base

# -----------------------------------------------------------------
# Production-friendly defaults
# -----------------------------------------------------------------
ENV PYTHONDONTWRITEBYTECODE=1   \
    PYTHONUNBUFFERED=1          \
    UV_LINK_MODE=copy           \
    UV_SYSTEM_PYTHON=1          \
    GDAL_CACHEMAX=512           \
    CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif,.tiff,.vrt,.geojson,.json,.shp"

# -----------------------------------------------------------------
# Keep Python runtime lean; no pip needed when using uv
# -----------------------------------------------------------------
RUN \
    apt-get update && \
    apt-get install -y --no-install-recommends     \
      curl python3 python3-venv ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# -----------------------------------------------------------------
# uv installer adds binaries to ~/.local/bin
# -----------------------------------------------------------------
ENV PATH="/root/.local/bin:${PATH}"

# =========================================================================
# Builder: compile deps, build wheel with uv
# =========================================================================
FROM base AS builder

# -----------------------------------------------------------------
# Toolchain and GDAL headers for building Python wheels 
# that link to GDAL
# -----------------------------------------------------------------
RUN \
    apt-get update && \
    apt-get install -y --no-install-recommends \
      python3-dev build-essential libgdal-dev \
    && rm -rf /var/lib/apt/lists/*

# -----------------------------------------------------------------
# Install uv (single-file installer)
# -----------------------------------------------------------------
ARG UV_INSTALL_URL="https://astral.sh/uv/install.sh"
RUN \
    curl -LsSf "$UV_INSTALL_URL" | \
    sh -s -- -y

WORKDIR /app

# -----------------------------------------------------------------
# Copy only files that affect dependency resolution FIRST
# (helps cache wheel/dep layers across source changes)
# -----------------------------------------------------------------
COPY pyproject.toml README.md LICENSE ./
COPY uv.lock ./

# -----------------------------------------------------------------
# Prime UV cache by attempting a wheel build before adding src/
# BuildKit cache mount keeps this layer fast on subsequent builds.
# -----------------------------------------------------------------
ARG BUILD_DIR="/dist"
ARG UV_CACHE_DIR="/root/.cache/uv"
RUN \
    --mount=type=cache,target=$UV_CACHE_DIR \
    uv build     \
      --wheel    \
      --no-sdist \
      --out-dir $BUILD_DIR \
    || true

# -----------------------------------------------------------------
# Now bring in the source and build the final wheel
# -----------------------------------------------------------------
COPY src/ ./src/
RUN \
    --mount=type=cache,target=$UV_CACHE_DIR \
    uv build     \
      --wheel    \
      --no-sdist \
      --out-dir $BUILD_DIR

# =========================================================================
# Runtime: minimal image with GDAL and wheel installed
# =========================================================================
FROM base AS runtime

# -----------------------------------------------------------------
# Install uv in runtime too so we can install the wheel 
# cleanly without pip
# -----------------------------------------------------------------
ARG UV_INSTALL_URL="https://astral.sh/uv/install.sh"
RUN \
    curl -LsSf "$UV_INSTALL_URL" | \
    sh -s -- -y

# -----------------------------------------------------------------
# Create a non-root user for safer defaults
# -----------------------------------------------------------------
ARG APP_USER=app
RUN \
    useradd -m -u 10001 -s /usr/sbin/nologin ${APP_USER}

WORKDIR /app

# -----------------------------------------------------------------
# Copy the built wheel and install into the system Python
# -----------------------------------------------------------------
COPY --from=builder /dist/*.whl /tmp/pkg.whl
RUN \
    --mount=type=cache,target=/root/.cache/uv \
    uv pip install --system --no-cache /tmp/pkg.whl && \
    rm -f /tmp/pkg.whl

# -----------------------------------------------------------------
# Switch to a data directory and non-root user
# -----------------------------------------------------------------
WORKDIR /data
USER ${APP_USER}

# -----------------------------------------------------------------
# Expose HTTP port for optional server mode
# -----------------------------------------------------------------
EXPOSE 8000

# -----------------------------------------------------------------
# Lightweight healthcheck; customize if you add an 
# HTTP transport
# -----------------------------------------------------------------
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python3 -c "import sys; sys.exit(0)"

# -----------------------------------------------------------------
# Default: run stdio transport (MCP default). Override 
# at runtime as needed:
#   docker run ... gdal-mcp --transport http --port 8000
# -----------------------------------------------------------------
ENTRYPOINT ["gdal-mcp"]
CMD ["--transport", "stdio"]
