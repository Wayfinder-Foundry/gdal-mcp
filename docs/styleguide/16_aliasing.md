# 16️⃣ `16_aliasing.md`

# Aliasing for Clarity and Efficiency

### Principle
Create **local aliases** for long or frequently accessed objects to improve readability and reduce repeated lookups.

Aliasing helps code read cleanly, avoid excessive dot chains, and, in some cases, improve runtime performance.

---

### ✅ Prefer

```python
grid = dataset.weather_model.grid
length = grid.temporal.bounds.length

for i in range(length):
    process(grid, i)
````

### ❌ Avoid

```python
for i in range(dataset.weather_model.grid.temporal.bounds.length):
    process(dataset.weather_model.grid, i)
```

---

### Why

* **Readability** — shorter, semantically meaningful references
* **Maintainability** — clearer local context and intent
* **Performance** — fewer repeated attribute lookups in tight loops
* **Line length** — avoids horizontal sprawl and cognitive clutter

---

### Example: Reusing Bound Methods

```python
get = cache.get  # reuse inside loop
for key in keys:
    value = get(key)
```

### Example: Semantic Clarity

```python
pipeline = context.workflow.pipeline
for stage in pipeline.stages:
    cfg = stage.config
    run_stage(cfg)
```

---

### ⚠️ Avoid Overuse

* Don’t alias imports like `import numpy as np → n` — follow community norms
* Don’t shorten meaningful names into cryptic ones (`c = config`)
* Don’t alias something used only once

---

### 🤝 Our Philosophy

Aliasing isn’t “lazy naming”, it’s narrative optimization.
Use it to make code flow naturally, reduce noise, and guide the reader’s eye to what matters.
