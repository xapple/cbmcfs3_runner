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
import sys, pandas
# Catch database related errors
from pyodbc import Error
from pandas.io.sql import DatabaseError

# Project modules
# Load the cbm_runner package from 'repos/' (instead of 'deploy/') #
sys.path.insert(0, "/repos/cbmcfs3_runner/")
from cbmcfs3_runner.core.continent import continent

# Choose  a country
country = 'LU'
runner = continent[('static_demand', country, 0)]
```

# Introduction

Plot the total biomass per forest type / species. 


# List all tables 

```python
db = runner.post_processor.database
db.tables
```

# List all column names
The list above contains tables and stored queries. 
From the ODBC driver perspectives tables and queries are the same. It's just that queries take a longuer time to load (especially if there are nested queries underneath).

The following code is a little bit innefficient since it loads the content of all tables, 
just to display the column name. 
But most time is spend in the queries anyway, not in fetching the tables. 

```python
for table in db.tables:
    print("")
    print(table)
    try:
        print(db[table].columns)
    except (Error, DatabaseError) as error:
        print(error)
```

## Catch errors
The following is only needed in case we have trouble figuring out 
from which module the error is coming from. 
For example some errors come from the pyodbc module while other come from pandas. 


```python
import inspect
try:
    db['harvest fire']
except Exception as e:
    frm = inspect.trace()[-1]
    mod = inspect.getmodule(frm[0])
    modname = mod.__name__ if mod else frm[1]
    print('Thrown from', modname)
```

# Display


## tblsimulation

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
