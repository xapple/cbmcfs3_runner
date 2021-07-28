---
jupyter:
  jupytext:
    formats: ipynb,md
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.11.1
  kernelspec:
    display_name: Python 3
    language: python
    name: python3
---

## Running afforestation

```python
from libcbm_runner.core.continent import continent
import pandas as pd
scenario = continent.scenarios['afforestation']
ar = scenario.runners['AT'][-1]
ar.run()
```

```python

```
