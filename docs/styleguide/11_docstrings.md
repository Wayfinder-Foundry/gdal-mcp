# 11️⃣ `11_docstrings.md`

# Docstrings (Numpy Style)

### Principle
Public classes, methods, and functions use [Numpy-style docstrings](https://numpydoc.readthedocs.io/en/latest/format.html).

### ✅ Example
```python
def area(radius: float) -> float:
    """Compute area of a circle.

    Parameters
    ----------
    radius : float
        Circle radius in meters.

    Returns
    -------
    float
        Area in square meters.
    """
```

### Why

* Works with Sphinx/Napoleon, pdoc, and static tools
* Consistent with scientific conventions
* Encourages structured documentation

> 💡 For private helpers, a short one-line summary is fine.

---

### 🤝 Our Philosophy

Docstrings explain *why*, not just *what*.
Write them for your future self.