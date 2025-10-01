# ADR-0017: Pydantic models for structured I/O

## Status

Accepted

## Context

ADR-0007 mandates structured outputs with schemas. FastMCP generates JSON schemas from type hints, and we need a robust modeling library for:
- Request/response validation
- Serialization (to/from JSON, dict)
- Clear API contracts for LLM clients
- Documentation via field descriptions
- Nested/complex structures (e.g., CRS, transform matrices, options dicts)

Python offers dataclasses and Pydantic. Dataclasses are lightweight but lack validation and advanced serialization. Pydantic v2 provides:
- Built-in validation with clear error messages
- Field constraints (ge, le, pattern, etc.) per ADR-0011
- JSON schema generation aligned with FastMCP
- `.model_dump()` and `.model_validate()` for clean serialization
- Compatibility with FastMCP tool signatures

## Decision

Use **Pydantic v2** for all request/response models.

### Structure
- **One model per file** in `src/models/raster/` and `src/models/vector/`
- **Shared/common models** in `src/models/common.py` (e.g., `ResourceRef`, enums)
- **Export from `__init__.py`** for clean imports: `from src.models.raster import RasterInfo`

### Naming conventions
- **Response models**: `<Operation>Result` (e.g., `RasterInfoResult`, `ConversionResult`)
- **Request models**: `<Operation>Options` or `<Operation>Params` (e.g., `ConversionOptions`, `ReprojectionParams`)
- **Info models**: `<Type>Info` (e.g., `RasterInfo`, `VectorInfo`)

### Field design
- Use `Field(...)` for descriptions, constraints, examples
- Leverage enums for controlled values (resampling, compression, CRS formats)
- Optional fields with `None` defaults where sensible
- Avoid mutable defaults (use `Field(default_factory=...)`)

### Serialization
- Return `.model_dump()` or the model instance directly from tools (FastMCP handles both)
- Accept Pydantic models as tool parameters for automatic validation

## Consequences

### Pro
- Strong contracts: LLM clients see precise schemas
- Validation: invalid inputs rejected with clear errors
- Maintainability: models document the API
- FastMCP alignment: native support for Pydantic
- Type safety: mypy/IDE support

### Con
- Slight runtime overhead (validation) vs raw dicts
- Pydantic v2 dependency (though already widely adopted)
- Must keep models in sync with tool implementations

## Implementation notes

### Example: raster info
```python
# src/models/raster/info.py
from pydantic import BaseModel, Field

class RasterInfo(BaseModel):
    path: str
    driver: str | None
    crs: str | None
    width: int = Field(ge=1)
    height: int = Field(ge=1)
    count: int = Field(ge=1, description="Number of bands")
    dtype: str | None
    transform: list[float] = Field(min_length=6, max_length=6)
    bounds: tuple[float, float, float, float]
    nodata: float | None = None
    overview_levels: list[int] = Field(default_factory=list)
    tags: dict[str, str] = Field(default_factory=dict)
```

### Example: tool usage
```python
from src.models.raster import RasterInfo

@mcp.tool
async def raster_info(uri: str) -> RasterInfo:
    with rasterio.open(uri) as ds:
        return RasterInfo(
            path=uri,
            driver=ds.driver,
            # ... populate fields
        )
```

FastMCP will serialize the `RasterInfo` instance to JSON with the generated schema.

## References

- ADR-0007 (structured outputs)
- ADR-0011 (CRS/resampling policy)
- FastMCP docs: structured outputs with Pydantic
- Pydantic v2 docs: https://docs.pydantic.dev/latest/
