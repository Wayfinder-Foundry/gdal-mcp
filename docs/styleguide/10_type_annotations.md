# 🔟 `10_type_annotations.md`

# Type Annotations

### Principle
Annotate every function parameter and return value.

### ✅ Prefer
```python
def calculate(x: float, y: float) -> float:
    ...
````

### Why

* Enables static analysis and IDE hints
* Improves agent reasoning
* Makes contracts explicit

### Tips

* Use generics: `list[T]`, `dict[str, T]`
* Favor domain types (`WeatherResult`, not `Any`)
* Keep annotations up to date

---

### 🤝 Our Philosophy

Types are documentation that never drifts.
They clarify intent without words.
