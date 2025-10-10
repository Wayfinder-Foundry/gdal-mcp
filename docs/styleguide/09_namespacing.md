# 9️⃣ `09_namespacing.md`

# Namespacing

### Principle
Let module paths convey context.  
Avoid repeating domain names in classes.

### ✅ Prefer
```
pipeline/status.py  →  class Status
pipeline/result.py  →  class Result
```

```python
import pipeline

# Use hierarchal namespacing to avoid noisy imports and identifiers
status = pipeline.Status()
result = pipeline.Result()
```

### ❌ Avoid
```
pipeline.py          → class PipelineStatus, PipelineResult
```

```python
import pipeline

# Avoid noisy imports and identifiers
status = pipeline.PipelineStatus()
result = pipeline.PipelineResult()
```

### Tips
- Use `_` prefix for abstract base classes (`class _Base:`)
- Split when 3+ classes share a prefix

---

### 🤝 Our Philosophy
Namespaces are narrative.  
They should tell the reader where they are and what belongs there.