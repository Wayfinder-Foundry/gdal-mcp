---
type: product_context
title: MCP Guidelines
tags: [mcp, compliance, guidelines]
---

# Guide to Building an MCP Server (Model Context Protocol)

## Introduction

The **Model Context Protocol (MCP)** is an open standard that allows AI applications (called *hosts*) such as Claude Desktop or ChatGPT to discover context data and safely call functions exposed by external systems.  The protocol decouples AI clients from specific data sources and tools by defining a JSON‑RPC–based interface for exchanging context and invoking actions.  An MCP **server** is a program that provides tools, resources and prompts to a host through an **MCP client**.  A **client** is a connector embedded in the host which maintains a dedicated connection to a single server and translates between JSON‑RPC messages and host‑specific APIs:contentReference[oaicite:0]{index=0}.  Multiple clients can be active within a host to communicate with different servers:contentReference[oaicite:1]{index=1}.

This guide synthesises the official documentation and specification to provide server developers with a concise reference.  It covers the architecture, lifecycle, primitives, message flows and best practices needed to build a compliant server.

## Architecture and Participants

MCP follows a **client‑server architecture** with three actors:contentReference[oaicite:2]{index=2}:

| Actor | Role |
|---|---|
| **Host** | The AI application (e.g., IDE, chat‑assistant) that spawns clients and orchestrates interactions. |
| **Client** | A connection manager running inside the host that talks to exactly one server.  It negotiates capabilities, translates user interactions into JSON‑RPC requests and enforces user permissions. |
| **Server** | A separate program that provides context and functionality via MCP.  It may run locally or remotely and communicates only through JSON‑RPC messages. |

MCP splits functionality into two **layers**:contentReference[oaicite:3]{index=3}:

1. **Data layer** – a JSON‑RPC 2.0 exchange protocol that defines message structures for connection lifecycle, primitives (tools, resources and prompts), client‑initiated features (sampling, elicitation, logging) and notifications.  This layer defines what messages exist and when they are valid:contentReference[oaicite:4]{index=4}.
2. **Transport layer** – responsible for moving JSON‑RPC messages between participants.  The two official transports are **stdio** (for local processes) and **streamable HTTP** (for remote servers).  StdIO is faster and uses process pipes; HTTP uses POST requests and optional Server‑Sent Events for streaming responses, with support for bearer tokens, API keys or OAuth:contentReference[oaicite:5]{index=5}.

### Scope and Projects

The protocol comprises a specification, SDKs in multiple languages, development tools (e.g., an **MCP Inspector**) and reference servers:contentReference[oaicite:6]{index=6}.  The standard only defines how context and tool calls are exchanged; how the host uses this context (e.g., summarising long documents) is out of scope:contentReference[oaicite:7]{index=7}.

## Lifecycle Management

MCP connections are **stateful**; therefore server and client must negotiate capabilities and protocol version before any operation.  The lifecycle consists of three phases:contentReference[oaicite:8]{index=8}:

1. **Initialisation** – The client sends an `initialize` request specifying the protocol version it understands, its capabilities (e.g., ability to handle elicitation or sampling) and client metadata:contentReference[oaicite:9]{index=9}.  The server responds with its supported protocol version, capabilities and server metadata:contentReference[oaicite:10]{index=10}.  Once agreed, the client sends a `notifications/initialized` message to signal readiness:contentReference[oaicite:11]{index=11}.  During this phase clients and servers **must not** send other requests apart from pings or logging messages:contentReference[oaicite:12]{index=12}.
2. **Operation** – After initialization, both parties can send requests or notifications defined by the capabilities negotiated.  They must use the same protocol version throughout the session:contentReference[oaicite:13]{index=13}.
3. **Shutdown** – The connection terminates gracefully.  There are no special shutdown messages; the transport (closing stdio streams or HTTP connections) signals termination:contentReference[oaicite:14]{index=14}.

### Version Negotiation

Protocol revisions are strings like `YYYY‑MM‑DD` and indicate the last date of backward‑incompatible changes:contentReference[oaicite:15]{index=15}.  During initialisation the client proposes a version; if the server supports it, it responds with the same version; otherwise it can reply with the latest version it supports:contentReference[oaicite:16]{index=16}.  If a common version cannot be found, the connection should be closed:contentReference[oaicite:17]{index=17}.  For HTTP transports, every request must include an `MCP‑Protocol‑Version` header with the negotiated version:contentReference[oaicite:18]{index=18}.

### Capability Negotiation

Capabilities define optional features of the protocol.  During initialisation, the client advertises capabilities it supports (roots, sampling, elicitation, etc.), and the server advertises the features it offers (tools, resources, prompts, logging, completions, etc.):contentReference[oaicite:19]{index=19}.  Each capability can include sub‑capabilities like `listChanged` (server will send update notifications) or `subscribe` (client can subscribe to resource changes).  Only capabilities that both sides declare are allowed during the session:contentReference[oaicite:20]{index=20}.

## MCP Primitives – Server Side

A server exposes **three core primitives**:contentReference[oaicite:21]{index=21}:

1. **Tools** – Executable functions that perform actions, such as database queries or API calls.  Tools are model‑controlled; the language model decides when to call them based on user prompts.  Each tool is described using JSON Schema (input parameters and optional output schema) and is uniquely named:contentReference[oaicite:22]{index=22}.  Tools can be invoked via the `tools/call` method.  Servers may also send `notifications/tools/list_changed` to inform clients when tools are added or removed:contentReference[oaicite:23]{index=23}.  The specification requires that tools be safe – the host must always seek explicit user approval before executing a tool:contentReference[oaicite:24]{index=24}.

2. **Resources** – Read‑only data that provide context to AI models.  Resources may represent file contents, database records, or API responses.  Each resource has a URI (e.g., `file:///path/to/file.md`) and MIME type.  There are **direct resources**, which have fixed URIs, and **resource templates**, which include parameters (e.g., `travel://activities/{city}/{category}`) to allow flexible queries:contentReference[oaicite:25]{index=25}.  Resources are discovered via `resources/list` or `resources/templates/list` and read via `resources/read`:contentReference[oaicite:26]{index=26}.  Optional `resources/subscribe` allows clients to subscribe to changes:contentReference[oaicite:27]{index=27}.  Servers can use resources to supply context to the model, but the host decides how to select and deliver the data:contentReference[oaicite:28]{index=28}.

3. **Prompts** – Pre‑built templates that guide the model through tasks.  Prompts can have structured arguments and may reference tools and resources to create domain workflows:contentReference[oaicite:29]{index=29}.  They are discovered via `prompts/list` and retrieved with `prompts/get`; they are never auto‑invoked by the model and always require explicit user initiation:contentReference[oaicite:30]{index=30}.  Parameter completion helps users discover valid argument values:contentReference[oaicite:31]{index=31}.

### Tool Definition and Usage

Each tool is defined by a unique `name`, `title`, `description` and an `inputSchema` (JSON Schema describing expected parameters):contentReference[oaicite:32]{index=32}.  Tools may optionally specify an `outputSchema` in the specification.  Clients list available tools via `tools/list` and then call a tool using `tools/call` with the tool name and arguments:

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "weather_current",
    "arguments": {
      "location": "San Francisco",
      "units": "imperial"
    }
  }
}
````

A tool returns an array of **content objects** that may include text, images, audio or structured data.  Responses also indicate whether an error occurred.  Tools must be idempotent and safe; hosts require user confirmation before execution.

### Notifications

Servers that declared `listChanged: true` may proactively send a notification when their tool list changes:

```json
{
  "jsonrpc": "2.0",
  "method": "notifications/tools/list_changed"
}
```

Clients should then send `tools/list` again to refresh their registry.  Notifications are one‑way messages and **must not** include an `id`.  They help maintain real‑time synchronisation without polling.

## MCP Primitives – Client Side (For Awareness)

Although server developers primarily focus on server primitives, understanding client features helps design richer interactions:

* **Elicitation** – Allows a server to request additional user input when needed.  The server sends an `elicitation/requestInput` message containing a prompt and JSON Schema of expected fields.  The user responds through the host UI and the client relays the data back.  Use elicitation to confirm bookings or gather additional parameters (e.g., seat preference) during long workflows.

* **Roots** – The client exposes filesystem boundaries to the server via `roots/list`.  Each root is a `file://` URI with a name, indicating directories where the server may operate.  Roots help servers understand project boundaries while clients retain access control.

* **Sampling** – Lets a server ask the client’s LLM to run a completion with a set of messages and model preferences.  Sampling is useful for tasks that require AI reasoning (e.g., choosing the best flight) without embedding an LLM in the server.  The client always seeks user approval and may reveal or redact sensitive data.

## Message Structure and JSON‑RPC Rules

MCP relies on the **JSON‑RPC 2.0** message format for all requests, responses and notifications.  Important rules include:

* **Requests** must include a `jsonrpc` field with value `"2.0"`, a non‑null `id` unique within the session, a `method` string and optional `params` object.
* **Responses** must use the same `id` as the corresponding request and include either a `result` or `error` object, but not both.  Errors must include a numeric code and message.
* **Notifications** are messages without an `id`; they never expect a response.
* The `_meta` field allows attaching additional metadata.  Keys may be namespaced and certain prefixes (`modelcontextprotocol`, `mcp`) are reserved for protocol use.

## Developing a Server

### Choosing an SDK

Official SDKs exist in TypeScript, Python, Go, Kotlin, Swift, Java, C#, Ruby, Rust and PHP.  Each SDK supports server features (tools, resources, prompts), client features, local/remote transports and type‑safe protocol implementations.  Choose an SDK that matches your language preferences and environment.

### Example: Python Weather Server (using `mcp.server.fastMCP`)

1. **Environment setup** – The quickstart suggests installing the `uv` packaging tool and creating a virtual environment.  On macOS/Linux:

   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   uv init weather
   cd weather
   uv venv && source .venv/bin/activate
   uv add "mcp[cli]" httpx
   touch weather.py
   ```
2. **Create the server instance** – Import required modules and create a `FastMCP` server instance.  Define constants such as API endpoints and user agent:
   ```python
   from typing import Any
   import httpx
   from mcp.server.fastmcp import FastMCP

   mcp = FastMCP("weather")
   NWS_API_BASE = "https://api.weather.gov"
   USER_AGENT   = "weather-app/1.0"
   ```
3. **Helper functions** – Write helper functions to fetch and format data.  For example, call the National Weather Service (NWS) API using `httpx`, handle errors and format responses into strings.

4. **Define tools** – Decorate asynchronous functions with `@mcp.tool()` to automatically register them as MCP tools.  Provide docstrings and type annotations; the SDK uses them to generate the tool description and input schema.  For example, implement `get_alerts(state: str) -> str` to fetch weather alerts for a U.S. state and `get_forecast(latitude: float, longitude: float) -> str` to return the forecast for a location.

5. **Run the server** – Start the server using the stdio transport.  The `mcp.run(transport='stdio')` call will listen for JSON‑RPC messages on stdin and write responses to stdout.  **Important:** never write to standard output directly (e.g., using `print()`), as this corrupts the message stream.  Instead, use a logging library that writes to stderr.

6. **Testing** – For hosts like Claude Desktop, update the configuration file to specify the command needed to start your server (e.g., `uv run weather.py`) and the server name.  Restart the host to pick up the configuration, and then verify that the tools appear in the UI.

### Best Practices and Guidelines

* **Logging:** For stdio transports, all logs must be sent to *stderr* to avoid mixing with JSON‑RPC output.  Use structured logging so clients can display logs effectively.
* **Error handling:** Use `None`/null returns or raise exceptions to return user‑friendly error messages.  Provide clear descriptions in error responses.
* **Security:** Implement robust consent flows; hosts must always ask users before executing tools or sending data.  Follow privacy and trust‑and‑safety principles: user consent, data privacy, tool safety, and sampling controls.  Do not request or transmit passwords or other sensitive information; rely on host‑provided credentials.
* **Capability declaration:** During initialization, accurately declare your server’s capabilities and sub‑capabilities (e.g., set `listChanged: true` if you intend to send change notifications).  Undeclared capabilities cannot be used in the session.
* **Tool design:** Use descriptive names, titles and descriptions.  Provide complete JSON Schemas for inputs (and outputs when appropriate).  Tools should be idempotent and minimize side effects.  Avoid exposing functions that can cause harm or leak sensitive data without explicit user confirmation.
* **Resource design:** When exposing resources, use clear and intuitive URI schemes.  Provide MIME types and support templates for dynamic queries.  Use `resources/subscribe` if resource data can change frequently.
* **Prompt design:** Keep prompts simple and parameterised.  Use them to orchestrate multi‑step workflows by combining resources and tools.  Provide descriptions and argument definitions to enable UI validation.
* **Notifications:** Use notifications sparingly to inform clients of changes.  Ensure that clients have subscribed (via capability negotiation) before sending notifications.

## Conclusion

Building an MCP server involves understanding the protocol’s lifecycle, message formats and primitives.  Servers expose tools, resources and prompts; negotiate capabilities with clients; and respect user consent and security guidelines.  The official SDKs simplify much of the boilerplate, allowing developers to focus on business logic.  By following the principles outlined in the documentation—such as proper version negotiation, logging practices, capability declaration, and trust‑and‑safety considerations—you can create powerful integrations that seamlessly extend AI applications while keeping users in control.

