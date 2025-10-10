# 5️⃣ `05_math_readability.md`

# Math Readability

### Principle
Break complex formulas into small, named parts.

### ✅ Prefer
```python
base = 2 * x + 0.1 * y
logv = math.log(base)
coef = 5 if limit == HIGH else 3
result = logv * coef
````

### Why

* Easier to verify correctness
* Simplifies unit testing
* Improves traceability

---

### 🤝 Our Philosophy

Mathematics should read like prose: clean, precise, and easy to follow.