---
jupyter:
  jupytext:
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

```python
%matplotlib inline
```

# Introduction

The purpose of this document is to analyze inventory area from the calibration database. 

It also compares the inventory areas modified by FUSION.


```python
# Modules #
import sys
import numpy
import pandas
import seaborn

# Optionally import from repos instead of deploy #
sys.path.insert(0, "/repos/cbmcfs3_runner/")
#sys.path.insert(0, "/home/sinclair/repos/bioeconomy_notes/src/")

from cbmcfs3_runner.pump.dataframes import csv_download_link
# Monkey patch because this method was removed from the scenario
from cbmcfs3_runner.pump.dataframes import concat_as_df
from cbmcfs3_runner.scenarios.base_scen import Scenario
Scenario.concat_as_df = concat_as_df

# Internal modules #
from cbmcfs3_runner.core.continent import continent
# Other imports #
from cbmcfs3_runner.pump.dataframes import multi_index_pivot
from plumbing.dataframes import count_unique_index

# Constants #
scenario     = continent.scenarios['static_demand']
runner_AT    = continent[('static_demand', 'AT', 0)]
runner_LU    = continent[('static_demand', 'LU', 0)]
runner_HU    = continent[('static_demand', 'HU', 0)]
# Inventories #
inv_AT = runner_AT.country.orig_data.inventory
inv_LU = runner_LU.country.orig_data.inventory
```

## Load data

### Inventory
Load inventory tables for all countries.

- The default scenario inventory runs on country.orig_data.inventory
- There is another inventory with different classifier for the availability for wood supply running on 
    country.fustion_data.inventory_aws


```python
# Large data frame with all yields of all countries #
def get_yields(runner): return runner.country.orig_data.yields
yields = scenario.concat_as_df(func=get_yields)
yields.iloc[[0,1,-2,-1]]
```

Inv AWS is the Availability for Wood supply inventory used in an exchange with FUSION.

```python

```
