# 3️⃣ `03_module_scope.md`
# Module Scope

### Principle
Each file should serve one clear purpose.  
If a module handles multiple unrelated concerns, split it up.

### ✅ Example Structure
```
map/
├── workflow/orchestrator.py
├── workflow/stages/spatial.py
└── workflow/validation.py
```

### Smells
- Very long files
- Mixed concerns (I/O, logic, visualization)
- Reused prefixes everywhere (`PipelineStatus`, `PipelineResult`)
    - **Note:** Prefer `pipeline.Status` over `PipelineStatus`

### Why
- Improves discoverability
- Enables reuse and testing
- Keeps imports meaningful

> 💡 *Rule of thumb:* if a file has more than one “reason to change,” it’s time to split.

---

### 🤝 Our Philosophy
Structure follows understanding.  
We value files that read like chapters: focused and cohesive.