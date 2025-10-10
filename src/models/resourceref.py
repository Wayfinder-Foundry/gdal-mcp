"""Resource reference model for MCP resource URIs."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ResourceRef(BaseModel):
    """Reference to a generated resource (file, URI, embedded data)."""

    uri: str = Field(description="Resource URI (file://, s3://, http://, etc.)")
    path: str | None = Field(None, description="Local filesystem path if applicable")
    size: int | None = Field(None, ge=0, description="Size in bytes")
    checksum: str | None = Field(None, description="Checksum (e.g., SHA256)")
    driver: str | None = Field(None, description="GDAL driver name")
    meta: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
