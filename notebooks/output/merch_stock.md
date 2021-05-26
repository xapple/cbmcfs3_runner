---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.2'
      jupytext_version: 1.3.3
  kernelspec:
    display_name: Python 3
    language: python
    name: python3
---

```python
# Force creation of a matplotlib device, so that plots can be viewed in this notebook
from matplotlib import pyplot
display(pyplot.plot(0,0))
```

```python
import sys, pandas, seaborn
# Project modules
# Load the cbm_runner package from 'repos/' (instead of 'deploy/') #
sys.path.insert(0, "/repos/cbmcfs3_runner/") 
from cbmcfs3_runner.core.continent import continent

# Choose  a country
country_iso2 = 'AT'
runner_static = continent[('static_demand', country_iso2, 0)]
runner_calib = continent[('calibration', country_iso2, 0)]

# Choose scenarios to compare
scenario_names = runner_static.country.scenarios.keys() # all available
scenario_names = ['static_demand', 'calibration', 'growth_only']
```

# Introduction

The goal is to plot the total merchantable biomass per forest type / species and compare scenarios. 
We obtain the total merchantable biomass from a query on the poolindicators table.


# Load merch stock data



```python
runner_static.post_processor.inventory.sum_merch_stock
```

```python
merch_2015 = runner_static.post_processor.inventory.sum_merch_stock.query("year == 2015")
display(merch_2015)

merch_2015['volume'].sum()

merch_stock = runner_static.post_processor.inventory.sum_merch_stock
merch_stock.groupby('year').agg({'volume':sum,
                                 'mass':sum})
```

```python
runner_static.country.coefficients.T
```



## graphs/merch_stock
`graphs/merch_stock.py`  is the way the dataset used for the diagnostic plot is generated. 
It returns a dataset containing all summary tables for all scenarios, for the given country.

```python
# Choose a list of scenario_names different from the default one
runner_static.country.graphs.merch_stock_at_start.scenario_names = scenario_names
merch = runner_static.country.graphs.merch_stock_at_start.data_raw
merch = merch.query('mass > 0')
merch
```

## Development scrap


### post_processor/inventory method
This gives access to the merchangable stock table for a single scenario


```python
runner_static.post_processor.inventory.sum_merch_stock.head()
```

### Reshape pool indicators
This query was used to generate the table above

```python
# tblpoolindicators
# display(runner_static.post_processor.database['tblpoolindicators'].head(2))
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
biomass_static.query('time_step==18 & quantity>0')
```

```python
biomass_calib = sum_merch(runner_calib)
biomass_calib.query('time_step==18 & quantity>0')
```

# Plot

## Bar plot based on loaded merch

```python
g = seaborn.barplot(x="forest_type", y="mass_1e6", hue="scenario",
                    palette='dark', data=merch.query('year==1998'))
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
p = seaborn.FacetGrid(data=merch.query("scenario in ['static_demand', 'calibration']"),
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
# scenario_names = ['static_demand', 'calibration', 'fake_yields_hist', 'fake_yields_cur', 'single_sit']
scenario_names = ['static_demand', 'calibration']
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
