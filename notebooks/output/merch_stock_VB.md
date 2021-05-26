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

```python
# Force creation of a matplotlib device, so that plots can be viewed in this notebook
from matplotlib import pyplot
import matplotlib.pyplot as plt
display(pyplot.plot(0,0))
```

```python
import sys, pandas, seaborn
import pandas as pd
# Project modules
# Load the cbm_runner package from 'repos/' (instead of 'deploy/') #
sys.path.insert(0, "/repos/cbmcfs3_runner/") 
from cbmcfs3_runner.core.continent import continent

# Choose  a country
country_iso2 = 'LT'
runner_static = continent[('static_demand', country_iso2, 0)]
runner_minus_20 = continent[('demand_minus_20', country_iso2, 0)]
runner_plus_20 = continent[('demand_plus_20', country_iso2, 0)]

# Choose scenarios to compare
scenario_names = ['static_demand','demand_minus_20', 'demand_plus_20']

def get_merch(scenario):
    runner = continent[(scenario, country_iso2, 0)]
    df =  runner.post_processor.inventory.sum_merch_stock
    return df
scenario_dict = {x: get_merch(x) for x in scenario_names}

# for a particular country
df = pandas.concat(scenario_dict, sort=True)
df = df.reset_index(level=0)
df = df.rename(columns={'level_0': 'scenario'})
merch = df
#merch[merch.scenario == 'static_demand'])
merch_static=merch[merch.scenario=='static_demand']
merch_minus_20 = merch[merch.scenario=='demand_minus_20']
merch_plus_20 = merch[merch.scenario=='demand_plus_20']

#display(runner_static)
#use pd.concat()
#scenario = continent.scenarios['demand_minus_20']

# round to integer all values
pandas.options.display.float_format = '{:,.0f}'.format

from cbmcfs3_runner.pump.dataframes import csv_download_link
```

# Introduction

The goal is to plot the total merchantable biomass per forest type / species and compare scenarios. 
We obtain the total merchantable biomass from a query on the poolindicators table.


# Load merch stock data



```python
v= runner_minus_20.post_processor.inventory.sum_merch_stock
#v.head(10)
#v.loc[:,['hw_merch']]
#vv = v[v['sw_merch']>0]
#vv.head()
#v.describe()
#vv=pd.melt(v)
#vv=v.pivot(columns='conifers_broadleaves', values='sw_merch')
#vv.head(-10)
#vvv = pd.concat([v,vv], axis =1)
#vvv.describe()
#vvv.rename(columns={'year':'time_step'})
#vvv.drop(columns=['year'])
#v[v.mass > 2000000]
#v.drop_duplicates()
#v.iloc[10:15]
#v.loc[:,'hw_merch':'year']
v.filter(regex = '\_')
#v.iloc[:,[1,3,6]]
#v.loc[v['sw_merch']<1500000, ['sw_merch', 'hw_merch', 'mass']]
#t=v.groupby(by = "forest_type")
#t.head()
#v.query("forest_type == 'PT'")
#len(v)
#v.info()
#t=v.dropna()
#v.plot.scatter(x ='year', y='sw_merch')
```

```python
runner_plus_20.post_processor.inventory.sum_merch_stock
```

```python
#represent Merch. Stock for the three sceanrios 
#merch_static = runner_static.post_processor.inventory.sum_merch_stock
#merch_plus_20 = runner_plus_20.post_processor.inventory.sum_merch_stock
#merch_minus_20 = runner_minus_20.post_processor.inventory.sum_merch_stock
# for 2018 only: .query("year == 2018")

ms = merch_static.groupby('year').agg({'volume':sum,
                                   'mass':sum})
mp20 = merch_plus_20.groupby('year').agg({'volume':sum,
                                   'mass':sum})
mm20 = merch_minus_20.groupby('year').agg({'volume':sum,
                                   'mass':sum})

#join_merch_0 = pd.merge(mp20,mm20,
#         how = 'left', on = 'year', suffixes = ("plus_20", "minus_20"))
#join_merch = pd.merge(ms,join_merch_0,
#         how = 'left', on = 'year')

#join_merch_0 = mp20.merge(mm20,
#         how = 'left', on = 'year', suffixes = ("plus_20", "minus_20"))
#join_merch = ms.merge(join_merch_0,
#         how = 'left', on = 'year')


#join_merch 
#SumTable=join_merch.rename(columns={"volume":"Volume_static", "mass": "Mass_static", "volume_x":"Volume_p20", "mass_x": "Mass_p20","volume_y":"Volume_m20", "mass_y": "Mass_m20"})
#display(SumTable)

#display(join_merch)

#csv_download_link(SumTable,"SumTable.csv")
```

```python
#year Volume_p20 Mass_p20 Volume_m20 Mass_m20
#SumTable.reset_index().plot(x='year',y=['Volume_static','Volume_p20','Volume_m20','Mass_static','Mass_p20','Mass_m20' ], 
#                            title = "Standing volume and biomass", color=["b", "r", "g", "g", "f", "o"])
#plt.savefig("C:/CBM/figure.png") # save as png
```

```python
conv_coef=runner_static.country.coefficients.density
pandas.options.display.float_format = '{:,.2f}'.format
print(conv_coef)
#display(conv_coef)
```

## graphs/merch_stock
`graphs/merch_stock.py`  is the way the dataset used for the diagnostic plot is generated. 
It returns a dataset containing all summary tables for all scenarios, for the given country.

```python
#ORIGINAL
# Choose a list of scenario_names different from the default one
#runner_static.country.graphs.merch_stock_at_start.scenario_names = scenario_names
#merch = runner_static.country.graphs.merch_stock_at_start.data_raw
#merch = merch.query('mass > 0')
#merch

#scenario_minus_20 = runner_minus_20.country.scenarios.keys() # all available

#runner_static.country.graphs.merch_stock.scenario_names
merch = runner_static.country.graphs.merch_stock.data_raw
merch = scenario_minus_20.country.graphs.merch_stock.data_raw
#merch = merch.query('mass > 0')
#merch
```

## Development scrap


### post_processor/inventory method
This gives access to the merchangable stock table for a single scenario


```python
### reorder columns
data=runner_static.post_processor.inventory.sum_merch_stock
runner_static.post_processor.inventory.sum_merch_stock.head(2)
cols = data.columns.tolist()
cols
data_=data[['year','id', 'forest_type','conifers_broadleaves','hw_merch','sw_merch', 'mass', 'density', 'harvest_gr', 'volume']]
```

```python
#sum across years 
#Merch_static = merch_static.groupby('year').agg({'volume':sum,
#                                   'mass':sum})
Across_years = data.groupby('year').agg({'volume':sum,
                                   'mass':sum})
pandas.options.display.float_format = '{:,.0f}'.format

Across_years.reset_index()
```

### Reshape pool indicators
This query was used to generate the table above

```python
#tblpoolindicators
#display(runner_static.post_processor.database['tblpoolindicators'].head(2))
#display(runner_static.post_processor.classifiers)
#display(runner_static.post_processor.database['tblAdminBoundary'])
#display(runner_static.post_processor.coefficients)
#display(runner_static.input_data.disturbance_events)
#display(runner_static.input_data.disturbance_types)
display(runner_static.middle_processor.project_database['tblAdminBoundary'])
```

```python
def sum_merch(runner, index=['time_step', 'forest_type']): 
    df = (runner.post_processor.database['tblpoolindicators']
          .set_index('user_defd_class_set_id')
          .join(runner.post_processor.classifiers) #.set_index('user_defd_class_set_id') already done
          .groupby(index)
          .agg({'hw_merch':'sum',
                'sw_merch':'sum'})
          .reset_index()
          .melt(id_vars=['time_step', 'forest_type'],
                var_name='conifer_broadleaves', 
                value_name='quantity'))
    return df
```

```python
biomass_static = sum_merch(runner_static)
biomass_static.query('time_step>0 & quantity>0')
#biomass_static.query('time_step==0 & quantity>0')
```

```python
biomass_merch = sum_merch(runner_static)
biomass_merch.query('time_step==18 & quantity>0')
```

# Plot

## Bar plot based on loaded merch

```python
display(merch)
```

```python
#merch by species for 2030 
merch_by_species = (merch
                    .query('year==2030')
                    .groupby(['scenario', 'forest_type'])
                    .agg({'volume':sum})
                    .reset_index())
merch_by_species
```

```python
g = seaborn.barplot(x="forest_type", y="volume", hue="scenario",
                    palette='dark', data=merch_by_species)
```

```python
g = seaborn.barplot(x="forest_type", y="mass_1e6", hue="scenario",
                    palette='dark', data=merch.query('year==2015'))
```

```python
pyplot.close(axes.figure)
```

## Time series

```python
p = seaborn.FacetGrid(data=merch.query("scenario in ['static_demand', 'demand_minus_20','demand_plus_20']"),
                      col='forest_type', 
                      sharey=False,
                      col_wrap=3)
p.map(seaborn.scatterplot, 'year', 'mass_1e6', 'scenario')
p.add_legend()
```

## Use merchantable stock graphs method

```python
country = continent.countries[country_iso2]
graphs = [country.graphs.merch_stock_at_start, country.graphs.merch_stock_at_end]
# scenario_names = ['static_demand', 'calibration', 'fake_yields_hist', 'fake_yields_cur', 'single_sit','demand_minus_20']
scenario_names = ['static_demand', 'demand_plus_20', 'demand_minus_20']
for g in graphs:
    g.scenario_names = scenario_names
    start, end = graphs
axes = start.plot(close=False)
display(start)
```

```python
pyplot.close(axes.figure)
axes = end.plot(close=False)
display(end)
```

```python

```
