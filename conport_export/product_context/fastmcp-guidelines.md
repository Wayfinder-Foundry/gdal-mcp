---
type: product_context
title: FastMCP Guidelines
tags: [fastmcp, mcp, guidelines]
---

# FastMCP: A Pythonic Framework for the Model Context Protocol

## What is FastMCP?

FastMCP is a high-level, Pythonic framework for building servers and clients that implement the **Model Context Protocol (MCP)**. MCP is a standard that allows large language models (LLMs) to access external data and functions through structured endpoints.

FastMCP simplifies MCP implementation by handling protocol specifics—such as JSON-RPC message handling, schema generation, error reporting, and transport management—so developers can focus on business logic.

The **FastMCP 2.0** release is the actively maintained version. It provides a comprehensive toolkit that goes beyond the core protocol, including:

- Deployment tools
- Authentication
- Dynamic tool rewriting
- REST-API integration
- Testing utilities

FastMCP’s goal is to be **fast, simple, Pythonic, and complete**, giving you an easy path from development to production.

> **Website:** [gofastmcp.com](https://gofastmcp.com)

---

## Installation and Versioning

FastMCP can be installed via `uv` or `pip`:

```bash
# Recommended if using uv to manage dependencies
uv add fastmcp

# Alternative uv-based pip installation
uv pip install fastmcp

# Standard pip installation
pip install fastmcp
````

After installation, verify the installation and view the FastMCP and MCP versions:

```bash
fastmcp version
```

**Upgrading from FastMCP 1.0:**

* Update your import:

  ```python
  from fastmcp import FastMCP
  ```
* Pin exact versions to avoid breaking changes:

  ```bash
  pip install fastmcp==2.11.0
  ```

---

## Creating a FastMCP Server

A FastMCP server encapsulates tools, resources, and prompts.

### Example: Basic Server

```python
from fastmcp import FastMCP

mcp = FastMCP("My MCP Server")

@mcp.tool
def greet(name: str) -> str:
    return f"Hello, {name}!"

if __name__ == "__main__":
    mcp.run()
```

**Explanation:**

* `FastMCP()` instantiates a server.
* `@mcp.tool` registers the function as a tool.
* `mcp.run()` starts the server.
* Use `if __name__ == "__main__"` for CLI compatibility.

---

## Running and Transport Modes

FastMCP supports multiple transport modes:

| Transport | Description |
| --------- | --------------------------------------------------------------------------- |
| **stdio** | Default. Ideal for local development, each client gets a dedicated process. |
| **http**  | Exposes your server over HTTP for network access.                           |
| **sse**   | Server-Sent Events transport for legacy streaming clients.                  |

### Run via CLI:

```bash
fastmcp run my_server.py:mcp

# Specify transport and port
fastmcp run my_server.py:mcp --transport http --port 8000
```

---

## Self-Hosted Deployment

For remote deployments, you can:

1. **Start a standalone HTTP server**

   ```python
   mcp.run(transport="http", host="0.0.0.0", port=8000)
   ```

2. **Integrate with ASGI apps**
   Use `mcp.http_app()` with frameworks like **FastAPI** or **Uvicorn**.

3. **Configure with `fastmcp.json`**

   * Store environment variables and secrets.
   * Use interpolation with `${VAR_NAME}`.

---

## FastMCP Cloud

FastMCP offers a **hosted service** where you can deploy by linking a GitHub repository.
It will automatically **build and host your server** with minimal configuration.

> Learn more at [gofastmcp.com](https://gofastmcp.com)

---

## Tools

**Tools** are functions exposed to LLMs. When an LLM calls a tool:

1. Input is validated against the function signature.
2. The function executes.
3. Results are returned.

### Key Concepts

* **Creation:**
  Use `@mcp.tool`. Avoid `*args` or `**kwargs` (breaks schema generation).

* **Metadata:**
  Customize with name, description, tags, and safety hints (`readOnlyHint`, `destructiveHint`, etc.).

* **Async support:**
  Use `async def` for I/O-bound tasks.

* **Return values:**

  * Dicts/dataclasses → structured JSON.
  * Primitives → structured output only with an output schema.
  * Type annotations auto-generate schemas.

* **Error handling:**
  Use `ToolError` for user-facing messages.
  Set `mask_error_details=True` to hide internal details.

* **Context Access:**
  Add a `Context` parameter for logging, progress, resources, and state management.

---

## Resources and Resource Templates

**Resources** are read-only data endpoints.

### Example

```python
@mcp.resource("resource://files/{filename}")
def read_file(filename: str) -> str:
    return open(filename).read()
```

### Notes

* Strings → text response
* Dicts/lists → JSON
* Bytes → Base64-encoded
* Use `Context` for request metadata.
* Use `mcp.add_resource()` to register static files or directories.

---

## Prompts

Prompts are reusable message templates.

### Example

```python
@mcp.prompt
def summarize(text: str) -> str:
    """Summarizes a given block of text."""
    return f"Summary: {text[:50]}..."
```

* Typed arguments are automatically converted from strings.
* Prompts must have fixed parameter lists (no `*args` or `**kwargs`).

---

## Context Capabilities

The `Context` object provides powerful features for tools, resources, and prompts:

| Capability         | Description                                           |
| ------------------ | ----------------------------------------------------- |
| Logging            | Send debug, info, warning, error messages to clients. |
| Progress Reporting | `await ctx.report_progress(progress, total)`          |
| Resource Access    | `await ctx.read_resource(uri)`                        |
| LLM Sampling       | `ctx.sample(...)` for text generation.                |
| User Elicitation   | Prompt the user for structured input.                 |
| State Management   | `ctx.set_state()`, `ctx.get_state()`                  |
| Request Metadata   | `ctx.request_id`, `ctx.client_id`                     |

---

## Progress Reporting

For long-running tasks:

```python
await ctx.report_progress(progress=10, total=100)
```

* Supports absolute, percentage, and indeterminate progress.
* Requires the client to include a `progressToken`.

---

## Tool Transformation & Method Decoration

* Use `Tool.from_tool()` to modify tools without rewriting them.
* Transform individual arguments using `ArgTransform`.
* **Avoid decorating instance methods directly.**
  Instead, register them explicitly:

  ```python
  mcp.tool(obj.method)
  ```

---

## Best Practices

* **Pin versions** to prevent breaking changes.
* Use **async** for I/O-bound operations.
* Return **structured data** with schemas.
* Use **context logging and progress reporting** for UX improvements.
* Gracefully **handle errors** with `ToolError`.
* Secure HTTP servers with **authentication and secrets in `fastmcp.json`**.

---

## Conclusion

FastMCP offers an easy, extensible way to implement MCP servers and clients in Python.

By abstracting protocol complexity and providing features like schema generation and transport management, FastMCP allows you to focus on building meaningful tools, resources, and prompts.

With proper version pinning, environment management, and best practices, you can create **robust, production-ready integrations** that safely extend LLM capabilities.
