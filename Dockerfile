# Multi-stage build to keep the final image small
# Stage 1: builder for the Python wheel (optional)
FROM python:3.12-slim AS builder
WORKDIR /app
COPY pyproject.toml README.md LICENSE ./
COPY src/ ./src/
RUN \
    pip install \
      --upgrade pip build && \
    python -m build \
      --wheel -n -o /dist

# Stage 2: runtime with GDAL CLI installed
# Use official GDAL image so the CLI is available without host deps
FROM osgeo/gdal:ubuntu-small-latest

# System prep
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install Python runtime and our wheel
RUN \
    apt-get update && \
    apt-get install \
      -y --no-install-recommends \
      python3 \
      python3-venv \
      python3-pip \
      ca-certificates &&  \
    rm -rf /var/lib/apt/lists/*

# Copy prebuilt wheel and install
COPY --from=builder /dist/*.whl /tmp/
RUN pip3 install --no-cache-dir /tmp/*.whl \
    && rm -f /tmp/*.whl

# Expose HTTP port (optional)
EXPOSE 8000

# Default: run HTTP transport on port 8000
ENTRYPOINT ["gdal-mcp"]
CMD ["--transport", "http", "--port", "8000"]
