# 4️⃣ `04_variable_extraction.md`

# Variable Extraction

### Principle
Avoid inline complexity.  
Extract nested calls or chained expressions into named variables.

### ✅ Prefer
```python
val = obj.a.b(c).d
if val > 5:
    ...
````

### ❌ Avoid

```python
if obj.a.b(c).d > 5:
    ...
```

### Exceptions

Simple built-ins (`len(x)`, `str(y)`, `int(z)`)

### Why

* Improves step-by-step reasoning
* Simplifies debugging
* Aids static analysis and agent comprehension

---

### 🤝 Our Philosophy

Readable code narrates its logic.
Don’t hide the story in a single line.
