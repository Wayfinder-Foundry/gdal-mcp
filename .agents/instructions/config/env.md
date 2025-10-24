---
Project environment reference.
---

```yaml
name: env
context:
  workspace_id: Lask

  project:
    id: Lask
    root_path: /home/jgodau/work/personal/Lask
    source_path: {.root_path}/lask
    tests_path: {.root_path}/tests
    docs_path: {.root_path}/docs

  # ---------------------------------------------------
  # Language / framework
  # ---------------------------------------------------
  language: python
  framework: uv

  # ---------------------------------------------------
  # Generic tool categories (high-level only)
  # ---------------------------------------------------
  tools:
    package_manager: uv

  # ---------------------------------------------------
  # Explicit executables available in this workspace
  # ---------------------------------------------------
  executables:
    python: 
    
  # ---------------------------------------------------
  # Local Environment
  # ---------------------------------------------------
  system:
    platform: linux
    OS: posix
    distro:
      name: ubuntu
      version: 24.10
      codename: jammy

  # ----------------------------------------------------
  # Language-specific metadata (kept minimal)
  # ----------------------------------------------------
  profiles:
    python:
      version: 3.12.3
      implementation: 
      executable: 
      pyproject_path: 
      venv_path: 
      package_manager: 
      build_tool: 
      test_runner: pytest
      test_args: ["-v", "--tb=short"]
```
