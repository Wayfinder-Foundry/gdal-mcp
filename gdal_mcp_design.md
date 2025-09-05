# GDAL MCP: A Design & Planning Document

## Introduction

The **Geospatial Data Abstraction Library (GDAL)** is an open‑source translator library for raster and vector geospatial data formats.  It provides a suite of command‑line utilities (`gdalinfo`, `gdal_translate`, `gdalwarp`, `gdalbuildvrt`, `gdal_rasterize`, `gdal2xyz`, `gdal_merge`, and `gdal_polygonize`) that allow data inspection, format conversion, reprojection, mosaicing and rasterization【666650857824669†L25-L33】.  Each utility exposes powerful geospatial operations that are widely used within the remote sensing and GIS communities.

The **Model Context Protocol (MCP)** is a standard protocol for connecting AI models to external systems.  It uses JSON‑RPC 2.0 to exchange messages between clients and servers.  A server exposes a set of **tools** (operations that the model can invoke) and **resources** (data that the model can access).  Tools are discoverable via `tools/list` and are defined by a name, title, description, `inputSchema`, optional `outputSchema`, and annotations【326596536680505†L84-L173】.  The MCP specification requires that any invocation of a tool must be explicitly authorised by a human user; servers must show confirmation prompts, protect sensitive data and ensure user consent【555906160256464†L154-L181】【326596536680505†L100-L107】.  Core design principles emphasise standardisation, modularity, security and reusability【319257362703485†L63-L95】.

This document proposes a **GDAL MCP** — an open‑source MCP server that wraps GDAL’s command‑line tools into MCP tools.  The goal is to allow agents or large‑language models (LLMs) to call geospatial operations in a safe and user‑authorised manner while following best practices for MCP server design and open‑source collaboration.

### Objectives

1. **Expose GDAL utilities as MCP tools.**  Each GDAL CLI command will be represented by a tool with a clear JSON input schema and output schema.  The design should hide complexity from the user while allowing advanced options when needed.
2. **Ensure secure and user‑centric design.**  The server must enforce human‑in‑the‑loop confirmations, limit file system access, and sanitise inputs.  It must implement the security principles described in the MCP spec【555906160256464†L154-L181】.
3. **Provide a modular, extensible architecture.**  The server should be written in Python, using a web framework (e.g. FastAPI) to handle JSON‑RPC, and should support adding new tools or resources easily.
4. **Create an open‑source repository.**  A GitHub repository will host the code, documentation, and community guidelines.  The project will use a permissive licence (MIT) and include a README, contribution guidelines and a code of conduct, as recommended by GitHub best practices【352695461642380†L160-L169】.

## Architecture Overview

### System Components

1. **JSON‑RPC Server:**  A Python web service implementing the MCP server API.  It will listen for JSON‑RPC requests and expose two namespaces:
   - `tools`: listing available tools and executing tool calls.
   - `resources`: exposing read‑only resources such as processed files or logs.
2. **Tool Wrappers:**  Each GDAL CLI command will have a Python wrapper that validates inputs against a JSON Schema, constructs a command‑line call, executes it via `subprocess.run`, captures the output, and returns a result.  Error handling will include timeouts and safe command‑line escaping.
3. **Resource Manager:**  A mechanism for storing output files.  Each output file will be registered as a resource with a unique URI.  The server will host these files via HTTP for retrieval.  The resource metadata will include file names, sizes and creation times, and may support subscription if extended later【763999239620954†L85-L134】.
4. **Confirmation UI:**  When a model requests a tool call, the server will produce a human‑readable description and require explicit user confirmation before executing it.  This ensures compliance with MCP’s user consent requirement【326596536680505†L100-L107】.

### Data Flow

1. A client (e.g. an LLM agent) calls `tools/list` to discover available GDAL tools, receiving the tool definitions.
2. The client constructs an action plan and requests to call a specific tool via `tools/call`.  The call includes the tool name and parameters conforming to the input schema.
3. The server renders a user confirmation prompt describing the action and awaits user approval.  If approved, the server executes the wrapper, producing output files or JSON results.
4. Output files are registered as resources and returned in the `result` field.  The client can subsequently fetch the files via their URIs.

### Security & Trust Considerations

The design will implement the following security measures drawn from the MCP specification【555906160256464†L154-L181】:

1. **Least privilege:**  Tools only accept file paths within designated project directories.  The server will enforce path whitelisting and disallow arbitrary shell arguments.
2. **User authorisation:**  Each tool call triggers a human confirmation step.  The server should display the command and description clearly and require explicit approval.
3. **Input validation:**  Parameters are validated against JSON Schemas.  Strings are sanitised to prevent shell injection.  Numeric parameters are range‑checked.
4. **Execution controls:**  Subprocess calls are executed with restricted environment variables and resource limits (e.g. CPU time, memory).  Timeouts prevent runaway processes.
5. **Data privacy:**  Resources include only data generated or explicitly provided by the user.  Sensitive data is not exposed to clients without authorisation.
6. **Logging & auditing:**  All tool invocations and user confirmations are logged for audit trails.  Logs should omit sensitive data when possible.

## Tool Definitions

Each GDAL tool will be defined with a `name`, `title`, `description`, an `inputSchema` describing parameters, and an `outputSchema` describing return types.  The descriptions draw from the GDAL documentation (with citations) to help users understand the tool’s purpose.

### Common Schema Components

To avoid repetition, we define several schema components:

```json
// Schema components (draft) for reuse
{
  "$defs": {
    "filePath": {
      "type": "string",
      "description": "Path to a raster or vector dataset accessible to the server"
    },
    "optionalFilePath": {
      "type": ["string", "null"],
      "description": "Optional path; null means the server will create a temporary file"
    },
    "boolean": { "type": "boolean" },
    "number": { "type": "number" },
    "string": { "type": "string" },
    "stringArray": {
      "type": "array",
      "items": { "type": "string" }
    }
  }
}
```

### gdalinfo

* **Description:**  Prints summary information about a raster dataset (metadata, geolocation, statistics)【183695331021388†L73-L94】.
* **InputSchema:**
  ```json
  {
    "type": "object",
    "properties": {
      "dataset": { "$ref": "#/$defs/filePath" },
      "json": {
        "type": "boolean",
        "description": "Return output in JSON format"
      },
      "stats": {
        "type": "boolean",
        "description": "Compute and include raster band statistics"
      }
    },
    "required": ["dataset"],
    "additionalProperties": false
  }
  ```
* **OutputSchema:**
  ```json
  {
    "type": "object",
    "properties": {
      "report": { "type": "string", "description": "Human‑readable or JSON formatted report" }
    },
    "required": ["report"]
  }
  ```

### gdal_translate

* **Description:**  Converts raster data between formats and can also subset, resample and rescale pixels【225900531694095†L123-L125】.
* **InputSchema:**
  ```json
  {
    "type": "object",
    "properties": {
      "src_dataset": { "$ref": "#/$defs/filePath" },
      "dst_dataset": { "$ref": "#/$defs/optionalFilePath" },
      "output_format": {
        "type": "string",
        "description": "GDAL output format (e.g. GTiff, COG, JPEG)"
      },
      "bands": {
        "$ref": "#/$defs/stringArray",
        "description": "List of band numbers to copy, as strings"
      },
      "projwin": {
        "type": "array",
        "items": { "type": "number" },
        "minItems": 4,
        "maxItems": 4,
        "description": "Subwindow in georeferenced coordinates: ulx, uly, lrx, lry"
      },
      "resample_alg": {
        "type": "string",
        "description": "Resampling algorithm (nearest, bilinear, cubic, etc.)"
      }
    },
    "required": ["src_dataset"],
    "additionalProperties": false
  }
  ```
* **OutputSchema:**
  ```json
  {
    "type": "object",
    "properties": {
      "output_uri": { "type": "string", "description": "URI of the converted raster" }
    },
    "required": ["output_uri"]
  }
  ```

### gdalwarp

* **Description:**  Reprojects and warps raster images; can mosaic multiple inputs and apply ground control points (GCPs)【513720626862592†L113-L116】.
* **InputSchema:**
  ```json
  {
    "type": "object",
    "properties": {
      "src_datasets": { "$ref": "#/$defs/stringArray", "description": "List of source raster files" },
      "dst_dataset": { "$ref": "#/$defs/optionalFilePath" },
      "t_srs": { "type": "string", "description": "Target spatial reference system (e.g. EPSG:4326)" },
      "r": { "type": "string", "description": "Resampling algorithm (near, bilinear, cubic)" },
      "overwrite": { "type": "boolean", "description": "Overwrite existing output file" }
    },
    "required": ["src_datasets", "t_srs"],
    "additionalProperties": false
  }
  ```
* **OutputSchema:**
  ```json
  {
    "type": "object",
    "properties": {
      "output_uri": { "type": "string", "description": "URI of the warped raster" }
    },
    "required": ["output_uri"]
  }
  ```

### gdalbuildvrt

* **Description:**  Builds a virtual dataset (VRT) that mosaics a list of input rasters and ensures they share similar characteristics【361752259006829†L96-L123】.
* **InputSchema:**
  ```json
  {
    "type": "object",
    "properties": {
      "src_datasets": { "$ref": "#/$defs/stringArray" },
      "dst_vrt": { "$ref": "#/$defs/optionalFilePath" },
      "resolution": { "type": "string", "description": "Output resolution (highest, lowest, average)" },
      "separate": { "type": "boolean", "description": "Place each input file into a separate VRT band" }
    },
    "required": ["src_datasets"],
    "additionalProperties": false
  }
  ```
* **OutputSchema:**
  ```json
  {
    "type": "object",
    "properties": {
      "vrt_uri": { "type": "string", "description": "URI of the VRT file" }
    },
    "required": ["vrt_uri"]
  }
  ```

### gdal_rasterize

* **Description:**  Burns vector geometries into raster band(s)【764420655834748†L100-L106】.
* **InputSchema:**
  ```json
  {
    "type": "object",
    "properties": {
      "src_vector": { "$ref": "#/$defs/filePath" },
      "dst_raster": { "$ref": "#/$defs/optionalFilePath" },
      "burn_value": { "type": "number", "description": "Pixel value to burn into the raster" },
      "width": { "type": "integer", "description": "Output raster width in pixels" },
      "height": { "type": "integer", "description": "Output raster height in pixels" },
      "extent": {
        "type": "array",
        "items": { "type": "number" },
        "minItems": 4,
        "maxItems": 4,
        "description": "Spatial extent of the output raster: minX, minY, maxX, maxY"
      },
      "invert": { "type": "boolean", "description": "If true, burn all pixels except those covered by geometries" }
    },
    "required": ["src_vector", "width", "height", "extent", "burn_value"],
    "additionalProperties": false
  }
  ```
* **OutputSchema:**
  ```json
  {
    "type": "object",
    "properties": {
      "raster_uri": { "type": "string", "description": "URI of the rasterized output" }
    },
    "required": ["raster_uri"]
  }
  ```

### gdal2xyz

* **Description:**  Converts a raster dataset into x/y/z points; supports multiple bands and nodata handling【32545494894027†L88-L104】.
* **InputSchema:**
  ```json
  {
    "type": "object",
    "properties": {
      "dataset": { "$ref": "#/$defs/filePath" },
      "dst_csv": { "$ref": "#/$defs/optionalFilePath" },
      "skip_nodata": { "type": "boolean", "description": "Skip nodata values" },
      "bands": { "$ref": "#/$defs/stringArray", "description": "Bands to extract" },
      "output_format": { "type": "string", "description": "Output format: CSV or numpy" }
    },
    "required": ["dataset"],
    "additionalProperties": false
  }
  ```
* **OutputSchema:**
  ```json
  {
    "type": "object",
    "properties": {
      "xyz_uri": { "type": "string", "description": "URI of the CSV or array output" }
    },
    "required": ["xyz_uri"]
  }
  ```

### gdal_merge

* **Description:**  Mosaics a set of images that must have the same coordinate system and number of bands; overlapping areas are overwritten by later images【288164147086118†L90-L97】.
* **InputSchema:**
  ```json
  {
    "type": "object",
    "properties": {
      "src_datasets": { "$ref": "#/$defs/stringArray" },
      "dst_dataset": { "$ref": "#/$defs/optionalFilePath" },
      "n": { "type": "number", "description": "Nodata value to use when merging" },
      "separate": { "type": "boolean", "description": "Place each input file into separate bands" }
    },
    "required": ["src_datasets"],
    "additionalProperties": false
  }
  ```
* **OutputSchema:**
  ```json
  {
    "type": "object",
    "properties": {
      "merged_uri": { "type": "string", "description": "URI of the merged raster" }
    },
    "required": ["merged_uri"]
  }
  ```

### gdal_polygonize

* **Description:**  Creates vector polygons from connected regions of pixels sharing the same value【416908224402442†L87-L93】.
* **InputSchema:**
  ```json
  {
    "type": "object",
    "properties": {
      "src_dataset": { "$ref": "#/$defs/filePath" },
      "dst_vector": { "$ref": "#/$defs/optionalFilePath" },
      "band": { "type": "integer", "description": "Band number to polygonize" },
      "mask": { "$ref": "#/$defs/optionalFilePath", "description": "Optional mask dataset" },
      "field_name": { "type": "string", "description": "Name of attribute to store pixel value" }
    },
    "required": ["src_dataset"],
    "additionalProperties": false
  }
  ```
* **OutputSchema:**
  ```json
  {
    "type": "object",
    "properties": {
      "vector_uri": { "type": "string", "description": "URI of the polygonised vector file" }
    },
    "required": ["vector_uri"]
  }
  ```

## Implementation Plan

### 1. Repository Structure

Following GitHub’s best practices【352695461642380†L160-L169】, the repository will include:

```
gdal-mcp/
├── README.md            # Project overview, instructions and examples
├── LICENSE              # MIT licence
├── CONTRIBUTING.md      # Guidelines for contributors
├── CODE_OF_CONDUCT.md   # Conduct and reporting guidelines
├── docs/
│   └── design.md        # This planning document
├── src/
│   ├── server.py        # Entry point for the MCP server (FastAPI or similar)
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── gdalinfo.py
│   │   ├── gdal_translate.py
│   │   ├── gdalwarp.py
│   │   ├── gdalbuildvrt.py
│   │   ├── gdal_rasterize.py
│   │   ├── gdal2xyz.py
│   │   ├── gdal_merge.py
│   │   └── gdal_polygonize.py
│   └── resource_manager.py   # Manages files and URIs
├── tests/
│   └── test_tools.py     # Unit tests for tool wrappers
└── requirements.txt      # Python dependencies
```

### 2. Development Steps

1. **Project setup**
   - Initialise a Python project and repository.  Add a `requirements.txt` file specifying `fastapi`, `uvicorn`, `jsonschema`, `pydantic`, `gdal` (Python bindings), and testing packages like `pytest`.
   - Configure continuous integration (e.g. GitHub Actions) to run tests on pull requests.
   - Choose MIT License and add a `LICENSE` file.
2. **Implement server**
   - Use FastAPI (or another lightweight ASGI framework) to create endpoints at `/jsonrpc` to handle JSON‑RPC 2.0 requests.  Provide methods `tools/list`, `tools/call`, and `resources/read`.
   - Use `jsonschema` to validate input parameters against each tool’s schema.
   - Implement the human‑confirmation flow: when a `tools/call` request arrives, store the pending action in a queue and respond with a `requiresConfirmation` object.  Provide a simple HTML/REST interface for the user to review and approve or deny the action.
3. **Write tool wrappers**
   - For each GDAL command, create a Python module in `src/tools` with a class or function implementing an `execute(parameters)` method.
   - Validate parameters; build the command line with safe quoting; run via `subprocess.run` with resource limits.
   - Capture stdout/stderr and parse results when necessary (e.g. for `gdalinfo --json`).
   - Save output files to a designated workspace directory; register them with `resource_manager` and return URIs.
4. **Resource manager**
   - Implement a `ResourceManager` class to allocate unique identifiers, map them to file paths, and serve files via static HTTP endpoints.  Provide an optional `subscribe` mechanism for future expansion【763999239620954†L85-L134】.
5. **Testing**
   - Write unit tests to ensure each tool wrapper correctly constructs commands and handles typical scenarios (e.g. missing parameters, invalid paths, timeouts).
   - Add integration tests to simulate JSON‑RPC calls and user confirmations.
6. **Documentation**
   - Populate `README.md` with an overview of the project, installation instructions, usage examples, and a high‑level explanation of MCP.
   - Include this design document in the `docs/` folder.
   - Provide usage examples demonstrating how an agent could call `gdalinfo` or `gdalwarp` through the MCP server.
7. **Security Hardening**
   - Review server for path traversal vulnerabilities, injection risks, and improper file permissions.
   - Enable HTTPs if deploying publicly; consider containerising the application for reproducible environments.
8. **Community & Contributions**
   - Create a `CONTRIBUTING.md` describing how to report issues, submit pull requests, run tests, and follow coding standards.
   - Add a `CODE_OF_CONDUCT.md` to define expected behaviour in the community.
   - Consider enabling GitHub security features like Dependabot alerts and secret scanning【352695461642380†L171-L184】.

### 3. Release and Deployment

1. **Open‑Source release**: Once the initial implementation is complete and tested, tag a v0.1.0 release and publish the repository publicly.  Encourage feedback and contributions.
2. **Continuous deployment**: Provide a Dockerfile to build an image with GDAL and the MCP server.  Optionally publish to a container registry.
3. **Hosting**: Deploy on a cloud platform (e.g. AWS, Azure, or GCP) or run locally.  Use environment variables to configure workspace directories and port settings.

## Conclusion

The GDAL MCP will bridge advanced geospatial processing tools with AI agents through a standardised and secure interface.  By wrapping GDAL’s battle‑tested CLI utilities into MCP tools and adhering to the protocol’s principles (standardisation, modularity, security and reusability)【319257362703485†L63-L95】, the project empowers models to handle real‑world raster and vector data.  A thoughtful repository structure with clear documentation, open‑source licensing and contribution guidelines ensures that the community can adopt, improve and extend the server.  Through careful planning and adherence to best practices, this project will become a reliable foundation for geospatial AI workflows.