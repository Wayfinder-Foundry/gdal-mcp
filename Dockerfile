# Multi-stage build for Python-native GDAL MCP
# Stage 1: builder with GDAL development libraries
FROM ghcr.io/osgeo/gdal:ubuntu-small-3.8.0 AS builder

# Install Python build tools and GDAL development headers
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3-dev \
        python3-pip \
        python3-venv \
        build-essential \
        libgdal-dev \
        && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy project files
COPY pyproject.toml README.md LICENSE ./
COPY src/ ./src/

# Build wheel with GDAL support
RUN pip3 install --upgrade pip build && \
    python3 -m build --wheel -n -o /dist

# Stage 2: runtime with GDAL libraries
FROM ghcr.io/osgeo/gdal:ubuntu-small-3.8.0

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    GDAL_CACHEMAX=512 \
    CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif,.tiff,.vrt,.geojson,.json,.shp"

# Install Python runtime
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3 \
        python3-pip \
        ca-certificates \
        && rm -rf /var/lib/apt/lists/*

# Copy and install prebuilt wheel
COPY --from=builder /dist/*.whl /tmp/
RUN pip3 install --no-cache-dir /tmp/*.whl && \
    rm -f /tmp/*.whl

# Create working directory for data
WORKDIR /data

# Expose HTTP port
EXPOSE 8000

# Health check (optional)
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python3 -c "import sys; sys.exit(0)"

# Default: run stdio transport (for MCP clients)
# Override with --transport http --port 8000 for HTTP
ENTRYPOINT ["gdal-mcp"]
CMD ["--transport", "stdio"]
