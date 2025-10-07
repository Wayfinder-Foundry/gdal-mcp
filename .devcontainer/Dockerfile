# Development container for GDAL MCP
# Based on official GDAL image with development tools

ARG PYTHON_VERSION=3.12
FROM ghcr.io/osgeo/gdal:ubuntu-small-3.8.0

# Install system dependencies for development
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        # Python development
        python3-dev \
        python3-pip \
        python3-venv \
        build-essential \
        libgdal-dev \
        # Development tools
        git \
        curl \
        wget \
        vim \
        nano \
        less \
        jq \
        # Useful utilities
        ca-certificates \
        software-properties-common \
        gnupg \
        lsb-release \
        sudo \
        && rm -rf /var/lib/apt/lists/*

# Create non-root user 'vscode' for development
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID

RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

# Install uv for Python package management
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

# Install uv for vscode user as well
USER $USERNAME
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/home/vscode/.cargo/bin:$PATH"

# Switch back to root for any remaining setup
USER root

# Environment variables for development
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    GDAL_CACHEMAX=512 \
    CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif,.tiff,.vrt,.geojson,.json,.shp"

# Set working directory
WORKDIR /workspace

# Switch to vscode user by default
USER $USERNAME

# Default command (overridden by devcontainer)
CMD ["/bin/bash"]
