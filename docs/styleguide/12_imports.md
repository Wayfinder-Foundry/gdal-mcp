# 12️⃣ `12_imports.md`

# Imports

### Principle
Keep imports clean, explicit, and ordered.

### Order
1. Standard library  
2. Third-party packages  
3. Local modules  

Separate groups with a blank line.

### ✅ Example
```python
# Standard library
import os
import math

import numpy as np
import pandas as pd

from lask.core import workflow
````

### Rules

* Avoid wildcard imports (`from x import *`)
* Use absolute imports when possible
* Sort alphabetically within groups

---

### 🤝 Our Philosophy

Clean imports make a codebase feel calm.
They’re the first impression every reader gets.