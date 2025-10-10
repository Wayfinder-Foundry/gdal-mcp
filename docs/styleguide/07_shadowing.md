# 7️⃣ `07_shadowing.md`

# Shadowing

### Principle
Avoid name collisions between locals and imports.

### ✅ Prefer
```python
import config

def run(cfg: Config):
    ...
````

### Also Fine

Prefix locals with `_` or rename (`config_`, `cfg`).

---

### 🤝 Our Philosophy

Avoid clever naming collisions.
Choose clarity every time.
