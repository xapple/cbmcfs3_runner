---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.1'
      jupytext_version: 1.1.7
  kernelspec:
    display_name: Python 3
    language: python
    name: python3
---

```python
# Modules #
import sys, pandas

# Optionally import from repos instead of deploy #
#sys.path.insert(0, "/repos/cbmcfs3_runner/")

# Internal modules #
from cbmcfs3_runner.core.continent import continent

# Catch database related errors
from pyodbc import Error
from pandas.io.sql import DatabaseError

# Constants #
scenario     = continent.scenarios['static_demand']
country_code = 'LU'
runner       = continent[('static_demand', country_code, 0)]

# The database #
db = runner.middle_processor.project_database
```

# Introduction





## List all tables

```python
db.tables
```

# Display



## tblsimulation

```python
db['tblsimulation']
```

# Table random seed

```python
db['tblrandomseed']
```

```python

```
