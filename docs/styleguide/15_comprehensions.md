# 15️⃣ `15_comprehensions.md`

# Comprehensions & Generators

### Principle
Use comprehensions when they improve clarity — avoid them when they obscure intent.

### ✅ Prefer
```python
squares = [x**2 for x in range(10)]
````

### ❌ Avoid

```python
result = [f(x) for x in range(10) if x > 2 if x % 3 == 0 if x < 100]
```

### Tips

* Break across lines if complex
* Generators (`(x for x in ...)`) are ideal for streaming
* Avoid nesting beyond two levels

---

### 🤝 Our Philosophy

Comprehensions are tools for elegance, not puzzles.
Readability always wins.
