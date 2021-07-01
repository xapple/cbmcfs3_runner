---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.11.3
  kernelspec:
    display_name: Python 3
    language: python
    name: python3
---

```python
%matplotlib inline
```

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

# Introduction

The purpose of this document is to analyze inventory area from the calibration database. 

It also compares the inventory areas modified by FUSION.



# Load data

## Inventory for all countries
Load inventory tables for all countries.

- The default scenario inventory runs on country.orig_data.inventory
- There is another inventory with different classifier for the availability for wood supply running on 
    country.fustion_data.inventory_aws


```python
# Large data frame with all inventory of all countries #
def get_inv(runner): return runner.country.orig_data.inventory
inv = scenario.concat_as_df(func=get_inv)
inv.iloc[[0,1,-2,-1]]
```

## Inventory AWS for countries where it is available

Inv AWS is the **Availability for Wood Supply** inventory used in an exchange with FUSION.

```python
# Large data frame with inventory aws of all countries where it is available #
def get_inv_aws(runner):
    try:
        df = runner.country.fusion_data.inventory_aws
    except:
        print("no data in ", runner.country.iso2_code)
        df = pandas.DataFrame()
    return df
inv_aws = scenario.concat_as_df(func=get_inv_aws)
inv_aws.iloc[[0,1,-2,-1]]
```

```python
# # Export all combined inventories data to CSV
#csv_download_link(inv, 'inventory.csv')
```

# Forest Area

## By country
Total forest area in hectares by country

```python
invc = (inv
        # Exclude non forest area
        .query("status not in 'NF'")
        .groupby(['country_iso2'])
        .agg({'area': sum})
        .reset_index())

invc['area_m'] = invc['area'] / 1e6

display(invc)
```

## By country and age class


```python
pandas.options.display.max_columns = None
display(inv
        .groupby(['country_iso2', 'age_class'])
        .agg({'area': sum})
        .reset_index()
        .pivot(index='country_iso2', columns='age_class', values='area')
        .replace(numpy.nan, '', regex=True))
```

## By country and status
Note: this data should be updated in the FUSION dataset. 
This is not part of the CBM calibrated dataset but a later addition based on fusion's work on FAWS, FRAWS, FNAWS areas. 


### inventory calibration

```python
inv_by_status = (inv
                 .groupby(['country_iso2', 'status'])
                 .agg({'area': sum})
                 .reset_index()
                 .pivot(index='country_iso2', columns='status', values='area'))
inv_by_status['tot'] = inv_by_status.drop(columns='NF').sum(axis=1)

def style_thousand_grey_na(df):
    """Style a dataframe with thousand separators and grey NA values"""
    return (df.style.format("{:,.0f}")
             .applymap(lambda x: '' if x == x else 'color:grey'))

# Format the text display value of cells.
display(inv_by_status
        .round()
        .style.format("{:,.0f}")
        .applymap(lambda x: '' if x == x else 'color:grey')
        )
```

### Inventory FUSION
First step of FUSION to have better details on availability for wood supply. 

```python
inv_aws_by_status = (inv_aws
       .groupby(['country_iso2', 'status'])
       .agg({'area': sum})
       .reset_index()
       .pivot(index='country_iso2', columns='status', values='area')
       .replace(numpy.nan, 0, regex=True))
inv_aws_by_status['tot'] = inv_aws_by_status.sum(axis=1)
inv_aws_by_status['CC_prop'] = inv_aws_by_status['CC'] / inv_aws_by_status['tot']
inv_aws_by_status['Th_prop'] = inv_aws_by_status['Th'] / inv_aws_by_status['tot']
inv_aws_by_status['Un_prop'] = inv_aws_by_status['Un'] / inv_aws_by_status['tot']
display(inv_aws_by_status.round(2))
# Remove proportion columns useless for subsequent calculations
columns_of_interest = ['CC', 'Th', 'Un', 'tot']
inv_aws_by_status = inv_aws_by_status[columns_of_interest]
```

### Comparison inv calib vs fusion

```python
inv_aws_by_status = inv_aws_by_status.rename(columns=dict(zip(columns_of_interest, 
                                          [s + '_fusion' for s in columns_of_interest])))
inv_aws_by_status
inv_comp = (inv_by_status
            .reset_index()
            .left_join(inv_aws_by_status.reset_index(), 'country_iso2'))
inv_comp['tot_change_pc'] = (inv_comp['tot'] - inv_comp['tot_fusion']) / inv_comp['tot'] *100

display(inv_comp
        .set_index('country_iso2')
        .round()
        .style.format("{:,.0f}")
        .applymap(lambda x: '' if x == x else 'color:grey')
        )
```

```python
# Add country name
country_map = pandas.DataFrame({'country_name' : [r[0].country.country_name for r in scenario],
                                'country_iso2' : [r[0].country.iso2_code for r in scenario]})
inv_comp = (inv_comp
            .left_join(country_map, 'country_iso2')
            .set_index('country_name').reset_index() #place country name first
            .sort_values('country_name')
           )
```

```python
# Download the file to csv
#csv_download_link(inv_comp, 'inventory_comp_calib_fusion.csv')
```

## By country and species


```python
display(inv
       .groupby(['country_iso2', 'forest_type'])
       .agg({'area': sum})
       .reset_index()
       .pivot(index='country_iso2', columns='forest_type', values='area')
       .replace(numpy.nan, '', regex=True)
       )
```

## By species

```python
invs = (inv
        .groupby(['forest_type'])
        .agg({'area': sum})
        .reset_index()
        .sort_values('area', ascending=False))
display(invs)
```

# Make a graph

```python
invc = invc.sort_values('area', ascending=False)
```

```python

# Plot #
axes = invc.plot.bar(x='country_iso2', y='area_m', width=0.9)
fig = axes.figure

# Legends #
axes.set_xlabel("")
axes.set_ylabel("Area in millions of hectares")
axes.set_xlabel("ISO2 country code of EU member state")
axes.get_legend().remove()
fig.suptitle("Total forest area per country in RP's dataset")

# Save #
fig.savefig("inventory_by_country.pdf")

# Show #
display(fig)
```

```python
from IPython.display import FileLink, FileLinks
FileLink('inventory_by_country.pdf')
```

```python
import os
os.remove('inventory_by_country.pdf')
```

# Analyse classifiers
 * All possible values taken by classifiers 
 * Then all possible classifiers variations accross countries. 
     * count
     * Area

```python
# print("Unique values taken by the various classifiers used in the disturbance table:")
classifiers = ['status', 'forest_type', 'region', 'management_type',
               'management_strategy', 'climatic_unit', 'conifers_broadleaves']
# for x in classifiers + ['country_iso2']:
#     print("%s %s" % (x, dist[x].unique()))
```

Analyse all possible classifiers variations accross countries.

```python
for this_classifier in classifiers:
    inv2 = inv.copy()
    # convert to string for concatenation
    inv2[this_classifier] = inv2[this_classifier].astype(str)
    display(inv2
            .groupby(['country_iso2'])
            .agg({this_classifier: lambda x: ','.join(pandas.Series.unique(x))}))
```

```python
# Area by species in the inventory
(runner_LU.country.orig_data.inventory
 .groupby(['forest_type', 'conifers_broadleaves'])
 .agg({'area':sum}))
```

```python
runner_LU.country.orig_data.inventory.query("forest_type=='PA'")
```

## Summary tables

```python
#import pandas_profiling
#inv_LU.profile_report()
```

# What can be disturbed ?

```python
silv = runner_LU.country.silviculture.hwp_map.drop_duplicates()
silv
```

```python
classifiers = ['status', 'forest_type', 'management_type',
               'management_strategy', 'conifers_broadleaves']

# Compare with all #
for country in continent:
    print('--------------------')
    print(country.iso2_code)

    # Load #
    silv1 = country.silviculture.treatments
    silv1 = silv[classifiers].drop_duplicates()

    # Load #
    inv1  = country.orig_data.inventory

    # Join #
    df = inv1.inner_join(silv, classifiers)

    total_treats = df['area'].sum()
    total_inv    = inv1['area'].sum()

    print("Proportion that can be disturbed: %g" % (total_treats / total_inv))
```

# Issues


## Hungary
Inventory area higher than expected in Hungary.

The fact is that there is a lot of non forested area in the input inventory. 
These stand having a status 'NF' should be excluded from the area calculation. 


### Load inv and silv

```python
inv_hu = runner_HU.country.orig_data.inventory.copy()
inv_hu.sort_values('area', ascending=False).head(10)
```

```python
classifiers = ['status', 'forest_type', 'management_type',
               'management_strategy', 'conifers_broadleaves']
silv_hu = runner_HU.country.silviculture.treatments.copy()
silv_hu.loc[[0,1,len(silv_hu)-2,len(silv_hu)-1],['status','forest_type', 'dist_type_name']]
```

```python
silv_hu_map = silv_hu[classifiers].drop_duplicates()
silv_hu_map.iloc[[0,1,-2,-1]]
```

### Area that cannot be disturbed

```python
# Join inv and silv using the merge() method on the classifiers 
# indicator=True adds a '_merge' columns with information about 
# where the given row is present: 'left_only', 'right_only' or 'both'
df = (inv_hu
      .merge(silv_hu_map, how='left', on=classifiers, indicator=True))
df.iloc[[0,1,-2,-1], [0,1,-7,-1]]
```

```python
# The issue is that there is a very large area of NF: not forested land. 
display(df.groupby(['_merge','status']).agg({'area':sum}))
display(df.groupby(['status']).agg({'area':sum}))
# This NF area is represented by only 24 rows in the input inventory 
# Compared to 500 rows for the forested areas
display(count_unique_index(df, ['_merge', 'status']))
```
