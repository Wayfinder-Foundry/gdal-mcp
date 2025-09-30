# Contributing to GDAL MCP

Thank you for considering contributing! We welcome bug reports, feature requests, documentation improvements, and code contributions.

## Getting started

1. Fork this repository and clone your fork.
2. Create a new branch (`git checkout -b feature/my-feature`).
3. Create a virtual environment and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

4. If you plan to work with GDAL CLI tools, ensure GDAL and the Python bindings are installed on your system.
5. Make your changes, following [PEP 8](https://peps.python.org/pep-0008/) coding style.
6. Write tests where applicable (we use pytest; run `pytest` to execute the test suite).
7. Commit your changes with a descriptive message and push to your fork.
8. Open a pull request against the `master` branch, describing what you’ve done and referencing any relevant issues.

## Adding a new MCP tool

New tools should follow the design described in [`docs/design/`](docs/design/index.md):

- Provide a Python wrapper around the GDAL CLI command in `src/tools/`.
- Define the tool’s metadata (name, title, description, inputSchema, outputSchema, annotations) in the server’s tool registry.
- Ensure inputs are validated and sanitized to prevent arbitrary command execution.
- Add unit tests demonstrating the tool’s use.
- Document the tool in the README and design document.

## Reporting issues

If you encounter a bug or have an idea for improvement, please open an issue on GitHub. Include:

- A clear and descriptive title.
- A summary of the problem or suggestion.
- Steps to reproduce, if reporting a bug.
- Expected and actual behaviour.
- Any relevant logs or error messages.

## Code review and merging

All pull requests require at least one approval from a maintainer. Please be responsive to feedback. Maintainers reserve the right to request changes or decline proposals that are out of scope.

Thank you for contributing!
