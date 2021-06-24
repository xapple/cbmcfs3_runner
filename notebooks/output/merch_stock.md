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
# Force creation of a matplotlib device, so that plots can be viewed in this notebook
from matplotlib import pyplot
import matplotlib.pyplot as plt
import numpy
display(pyplot.plot(0,0))
import sys, seaborn
import pandas as pd
from cbmcfs3_runner.pump.dataframes import csv_download_link
from cbmcfs3_runner.core.continent import continent
from cbmcfs3_runner.pump.dataframes import concat_as_df_from_many_scenarios
import pandas # Used to return an empty data frame in the except statement of the get_ms_merch() function below
```

```python
# Project modules
# Choose scenarios to compare
# Load module (at the very first cell)

# extract volume and biomass in merch pool only for each country for each scenario
# Create a dictionary of all scenario objects
scenario_names = ['static_demand', 'demand_minus_20', 'demand_plus_20']
scenario_dict = {x: continent.scenarios[x] for x in scenario_names}
# Load the output merchantable stock for all countries in all scenarios
# Use a try and except statement to avoid countries where data is potentially missing
def get_ms_merch(runner):
    try:
        df = runner.post_processor.inventory.sum_merch_stock
    except Exception as e:
        print("no data in", runner.country.iso2_code)
        print('Error loading data: '+ str(e))
        df = pandas.DataFrame()
    return df
merch = concat_as_df_from_many_scenarios(scenario_dict, func = get_ms_merch)
df_ms_merch = merch [['year','scenario','country_iso2', 'conifers_broadleaves', 'density', 'forest_type', 'harvest_gr', 'hw_merch', 'id', 'mass', 'sw_merch', 'volume']]
df_ms_merch
```

```python
# Project modules
# Choose scenarios to compare
# Load module (at the very first cell)

# extract volume and biomass in merch pool only for each country for each scenario
# Create a dictionary of all scenario objects
scenario_names = ['static_demand', 'demand_minus_20', 'demand_plus_20']
scenario_dict = {x: continent.scenarios[x] for x in scenario_names}
# Load the output merchantable stock for all countries in all scenarios
# Use a try and except statement to avoid countries where data is potentially missing
def get_ms_merch(runner):
    try:
        df = runner.post_processor.inventory.sum_merch_stock_detailed
    except Exception as e:
        print("no data in", runner.country.iso2_code)
        print('Error loading data: '+ str(e))
        df = pandas.DataFrame()
    return df
merch = concat_as_df_from_many_scenarios(scenario_dict, func = get_ms_merch)
#df_ms_merch = merch [['year','scenario','country_iso2', 'conifers_broadleaves', 'density', 'forest_type', 'harvest_gr', 'hw_merch', 'id', 'mass', 'sw_merch', 'volume']]
#df_ms_merch
merch
```

```python
# A dictionnary of all runners in one scenario
runners_dict = scenario_dict['static_demand'].runners.items()

# Checking for which countries have finnished running or not
for c, r in scenario_dict['static_demand'].runners.items():
    print(c, r[-1].map_value)
```

```python
# Large data frame with merchantable stock of all countries where it is available #
def get_ms_merch(runner):
    try:
        df = runner.post_processor.inventory.sum_merch_stock
    except Exception as e:
        print("no data in ", runner.country.iso2_code)
        print('Error loading data: '+ str(e))
        df = pandas.DataFrame()
    return df

merch = pandas.DataFrame()
for scenario_name in scenario_names:
    print('Loading data from', scenario_name)
    merch_1 = scenario_dict[scenario_name].concat_as_df(func=get_ms_merch)
    merch_1['scenario'] = scenario_name
    merch = pandas.concat([merch, merch_1])

merch.iloc[[0,1,-2,-1]]
csv_download_link(merch,"merch_0.csv")
    
# scenario_dict['static_demand'].concat_as_df(func=get_ms_merch).
```

# Introduction

The goal is to plot the total merchantable biomass per forest type / species and compare scenarios. 
We obtain the total merchantable biomass from a query on the poolindicators table.


# Load and graph merch stock data for the scenarios



```python
merch_static.head(-1)
```

```python
# deveop a df with the data for each scenario for MERCH
sv_static = merch_static.groupby('year').agg({'volume':sum,
                                   'mass':sum})
sv_plus20 = merch_plus_20.groupby('year').agg({'volume':sum,
                                   'mass':sum})
sv_minus20 = merch_minus_20.groupby('year').agg({'volume':sum,
                                   'mass':sum})
join_merch_0 = pd.merge(sv_plus20,sv_minus20,
          how = 'left', on = 'year', suffixes = ("_plus_20", "_minus_20"))
join_merch = pd.merge(sv_static,join_merch_0,
          how = 'left', on = 'year')

tot_standing_merch=join_merch.rename(columns={"volume":"volume_static", "mass": "mass_static"})
standing_abg_merch = tot_standing_merch[['mass_static','mass_plus_20','mass_minus_20']]
```

```python
# Graph with standing MERCH volume and biomass 
merch=tot_standing_merch.reset_index()
merch.plot(x='year',y= ['volume_static','mass_static' , 'volume_plus_20', 'mass_plus_20', 'volume_minus_20', 'mass_minus_20'], 
                            title = "Standing volume and biomass",xlabel='years', ylabel='m3 & ton of drymass', color=["b", "r", "g"])

#plt.savefig("C:/CBM/figure.png") # save as png
```

```python
# deveop a df with the data for each scenario for merch and total AGB
agb_merch = standing_abg_merch.rename(columns={"mass_static":"merch_static", "mass_plus_20":"merch_plus_20","mass_minus_20":"merch_minus_20"})

sb_static = agb_static.groupby('year').agg({'mass':sum})
sb_plus20 = agb_plus_20.groupby('year').agg({'mass':sum})
sb_minus20 = agb_minus_20.groupby('year').agg({'mass':sum})

join_sb_0 = pd.merge(sb_plus20,sb_minus20,
          how = 'left', on = 'year', suffixes = ("_agb_plus_20", "_agb_minus_20"))
join_sb = pd.merge(sb_static,join_sb_0,
          how = 'left', on = 'year')
agb_total = join_sb.rename(columns={"mass":"agb_static", "mass_agb_plus_20":"agb_plus_20","mass_agb_minus_20":"agb_minus_20"})
agb_tot=pd.merge(agb_merch,agb_total, how ='left', on ='year')
agb=agb_tot.reset_index()
```

```python
# Graph with standing biomass in merh and ABG
agb.plot(x='year',y= ['merch_static', 'merch_plus_20', 'merch_minus_20', 'agb_static', 'agb_plus_20', 'agb_minus_20'], 
        title = "Biomass in merch and total aboveground standing stock",xlabel='years', ylabel='tons of drymass', color=["blue", "red", "green", "pink", "olive", "brown"])

#plt.savefig("C:/CBM/figure.png") # save as png
```

```python
# round to two decimals all values in this table
pd.options.display.float_format = '{:,.2f}'.format

runner.country.coefficients.T
```
```python

```




## Development scrap


### post_processor/inventory method
This gives access to the merchangable stock table for a single scenario


```python
runner.post_processor.inventory.sum_merch_stock.head()
```

### Reshape pool indicators
This query was used to generate the table above

```python
# tblpoolindicators
# display(runner_static.post_processor.database['tblpoolindicators'].head(2))
```

```python
def sum_owc_stock(self):
        # Load data #
        df    = self.parent.database['tblPoolIndicators']
        clifr = self.parent.classifiers.set_index("user_defd_class_set_id")
        # Our index #
        index = ['time_step', 'forest_type', 'conifers_broadleaves']
        # Join #
        df = (df
              .set_index('user_defd_class_set_id')
              .join(clifr)
              .groupby(index)
              .agg({'hw_other': 'sum',
                    'sw_other': 'sum'})
              .reset_index())
        # Add year and remove TimeStep #
        df['year'] = self.country.timestep_to_year(df['time_step'])
        df = df.drop('time_step', axis=1)
        # Check for mixed species that would produce both hard and soft #
        import warnings
        for i, row in df.iterrows():
            if row['hw_other'] > 0.0 and row['sw_other'] > 0.0:
                warnings.warn("There is a mixed species at row %i.\n%s" % (i,row))
        df['mass'] = df['hw_other'] + df['sw_other']
        # calculate the volume in cubic meters over bark #
        # join density
        df = df.left_join(self.country.coefficients, 'forest_type')
        df['volume'] = df['mass'] / df['density']
        # Only if we are in the calibration scenario #
        if self.parent.parent.scenario.short_name == 'calibration':
            # Patch the harvest data frame to stop at the simulation year #
            selector = df['year'] <= self.country.base_year
            df = df.loc[selector].copy()
        # Return #
        return df





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
