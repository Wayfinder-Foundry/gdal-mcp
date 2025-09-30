```
mcp-gdal/
  docs/
    design/
      ...
    adr/
      ADR-0001-adopt-fastmcp-and-python-native-stack.md
      ADR-0002-mvp-scope-tools-and-primitives.md
      ...
  src/
    __init__.py
    server.py
    tools/
      __init__.py
      raster/
        __init__.py
        ...
      vector/
        __init__.py
        ...
    models/
      raster.py (or raster/ submodule, depending on the amount of models)
      vector.py  (or vector/ submodule, depending on the amount of models)
  tests/
    fixtures/
    test_raster.py
    test_vector.py
  fastmcp.json (declarative config used for fastMCP, not BaseSettings obj like fastAPI)
  pyproject.toml
  README.md
```

