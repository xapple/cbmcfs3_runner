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

# Choose a country #
country_code = 'LU'
db = continent.countries[country_code].aidb.database

# Constants #
list_all_column_names = True
```

# Introduction





## List all tables

```python
db.tables
```

## List all column names

```python
if list_all_column_names:
    for table in db.tables:
        print("")
        print(table)
        try:
            print(db[table].columns)
        except (Error, DatabaseError) as error:
            print(error)
```

# Display



## tbladminboundarydefault


```python
db['tbladminboundarydefault'].query("admin_boundary_name=='Luxembourg'")
```


## tblsimulation

```python
db['tblsimulation']
```

## Disturbance Matrix
The following tables contain information relevant to the disturbance matrix.
### tbldm

```python
db['tbldm']
```

### tbldisturbancetypedefault

```python
db['tbldisturbancetypedefault']
```

### tbldmassociationdefault

```python
db['tbldmassociationdefault']
```

### tbldmassociationspudefault

```python
db['tbldmassociationspudefault']
```

### tbldmvalueslookup

```python
db['tbldmvalueslookup']
```

### tblsinkname

```python
db['tblsinkname']
```

### tblsourcename

```python
db['tblsourcename']
```

## tbluserimportconfig

```python
db['tbluserimportconfig']
```
