# 14️⃣ `14_logging_and_errors.md`

# Logging & Errors

### Principle
Use structured logging and meaningful exceptions.

### ✅ Prefer
```python
import logging
logger = logging.getLogger(__name__)

try:
    process(data)
except DataError as e:
    logger.error("Data processing failed: %s", e)
    raise
````

### Rules

* Use `logging`, not `print`
* Create custom exception classes for domain errors
* Include context in messages

---

### 🤝 Our Philosophy

Logs are for humans and machines alike.
Make them informative, not noisy.
