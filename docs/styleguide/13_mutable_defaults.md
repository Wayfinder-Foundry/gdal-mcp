# 13️⃣ `13_mutable_defaults.md`

# Mutable Defaults

### Principle
Never use mutable objects (`[]`, `{}`) as default arguments.

### ✅ Prefer
```python
def add_item(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items
````

### ❌ Avoid

```python
def add_item(item, items=[]):  # shared state bug
    items.append(item)
    return items
```

### Why

* Prevents shared state between calls
* Avoids subtle, hard-to-debug behavior

---

### 🤝 Our Philosophy

Predictability beats cleverness.
Mutable defaults are almost never worth the surprise.