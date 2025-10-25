---
trigger: glob
description: 
globs: *.py
---

# Docstring Style Rule — Numpy Standard

**ID:** `rule.docstring_numpy_style`
**Scope:** All Python source files (`.py`, `.pyi`)
**Priority:** Medium
**Intent:** Enforce a consistent, structured documentation style for functions, classes, and modules.

---

## Principle

All Python **docstrings must follow the Numpy documentation style**.

This ensures clarity, consistency, and compatibility with automated documentation tools such as **Sphinx (Napoleon)**, **pdoc**, or **Docstring-Parser**.

---

## ✅ Requirements

* Each **public function**, **class**, and **module** must include a Numpy-style docstring.
* Include sections in this order (omit only if truly not applicable):

  ```
  """Short summary line.

  Extended summary paragraph explaining the context and purpose.

  Parameters
  ----------
  name : type
      Description of the parameter.
  other : type, optional
      Description of optional parameter. Default is None.

  Returns
  -------
  type
      Explanation of return value(s).

  Raises
  ------
  ErrorType
      Explanation of when the error is raised.

  Examples
  --------
  >>> result = func(x=5)
  >>> print(result)
  10
  """
  ```

---

## Anti-Patterns

Missing sections or inconsistent formatting
Google-style or reST-style docstrings
Misaligned indentation or missing blank lines between sections
Type hints in the signature *and* again in parentheses (`param (int):`) — redundant under Numpy style

---

## Implementation Hints

* Use **triple double quotes** (`"""`) for all docstrings.
* Keep summary lines ≤ 80 characters.
* Leave a blank line after the short summary and before “Parameters”.
* For one-liners (e.g. small helpers), summary-only docstrings are acceptable.

---

## 🔍 Verification

Static linting tools that can enforce this rule:

* `pydocstyle` with configuration:

  ```ini
  [pydocstyle]
  convention = numpy
  ```
* `ruff`:

  ```toml
  [tool.ruff.pydocstyle]
  convention = "numpy"
  ```

CI or agent checks should fail if `pydocstyle` reports violations.

---

## TL;DR

> Every public symbol must have a **Numpy-style docstring**
> — concise summary, full parameter/return sections, and examples where useful.