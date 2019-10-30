---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.1'
      jupytext_version: 1.2.4
  kernelspec:
    display_name: Python 3
    language: python
    name: python3
---

```python
# Modules #
import sys, pandas

# Catch database related errors #
from pyodbc import Error
from pandas.io.sql import DatabaseError

# Optionally, load the cbm_runner package from 'repos/' (instead of 'deploy/') #
#sys.path.insert(0, "/repos/cbmcfs3_runner/")

# Import the main continent #
from cbmcfs3_runner.core.continent import continent

# Choose  a country #
runner_AT = continent[('static_demand', 'AT', 0)]
runner_CZ = continent[('static_demand', 'CZ', 0)]
runner_LU = continent[('static_demand', 'LU', 0)]
runner_IT = continent[('static_demand', 'IT', 0)]
runner_BE = continent[('static_demand', 'BE', 0)]
runner_SE = continent[('static_demand', 'SE', 0)]
runner_FR = continent[('static_demand', 'FR', 0)]
runner_ZZ = continent[('static_demand', 'ZZ', 0)]

# Pick a specific runner #
runner = runner_CZ

# Load the database object #
db = runner.post_processor.database
```

# List all tables 

```python
db.tables
```

# List all column names

```python
for table in db.tables:
    print("")
    print(table)
    try:
        print(db[table].columns)
    except (Error, DatabaseError) as error:
        print(error)
```

# Display


## tbldisturbancetype

```python
db['tbldisturbancetype']
```

## tblsimulation (doesn't exist?)

```python
db['tblsimulation']
```

## tblfluxindicators

```python
db['tblfluxindicators'].head(2)
```

## tblpoolindicators

```python
db['tblpoolindicators'].head(2)
```

## tblspeciestype


```python
db['tblspeciestype']
```
