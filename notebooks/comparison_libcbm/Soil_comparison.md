---
jupyter:
  jupytext:
    formats: ipynb,md
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

# Introduction

The purpose of this notebook is to compare soil pools between libcbm and cbmcfs3.




## Create runner objects

```python
# Create a libcbm runner
from libcbm_runner.core.continent import continent
import pandas as pd
# TODO call it static demand and make sure it loads a disturbance file from the static demand scenario
scenario = continent.scenarios['historical']
runner_libcbm = scenario.runners['LU'][-1]

# Create a cbmcfs3 runner
from cbmcfs3_runner.core.continent import continent
runner_cbm3 = continent[('static_demand','LU',0)]
```

# Soil Organic Matter content at timestep 0


#  SOC by libcbm

```python
# run
runner_libcbm.run()

# Retrieve pools
pools_libcbm = runner_libcbm.simulation.results.pools
```

```python
# list the columns in the result file
pools_libcbm.columns
```

```python
# display each sub-pool on years
soil_pools_libcbm= pools_libcbm[['identifier', 'timestep', 'Input', 'AboveGroundVeryFastSoil',
       'BelowGroundVeryFastSoil', 'AboveGroundFastSoil', 'BelowGroundFastSoil',
       'MediumSoil', 'AboveGroundSlowSoil', 'BelowGroundSlowSoil',
       'SoftwoodStemSnag', 'SoftwoodBranchSnag', 'HardwoodStemSnag',
       'HardwoodBranchSnag']]
soil_pools_libcbm_ind= (soil_pools_libcbm 
                   .reset_index())
soil_pools_libcbm_ind_sum=soil_pools_libcbm_ind.sum(axis=1)
soil_pools_libcbm_ss=(soil_pools_libcbm_ind_sum
              .reset_index())
soil_aggreg_libcbm = pd.merge(soil_pools_libcbm_ind,soil_pools_libcbm_ss,
         how = 'left', on = 'index')
print(soil_aggreg_libcbm)
```

```python
# subset a dataframe with soil relevant columns, inclduing area ("=input") 
#in order to estimate initialized C stock per_ha in the timestep 0

soil_aggreg_libcbm=soil_aggreg_libcbm.rename(columns ={"Input":"Area", 0:"Total_dom"})
soil_libscbm_init= soil_aggreg_libcbm.loc[soil_aggreg_libcbm["timestep"]==0,["Area","Total_dom"]]

soil_libscbm_init['SOC_libcbm_per_ha']=soil_libscbm_init['Total_dom']/soil_libscbm_init['Area']

#print(soil_libscbm_init)
#from cbmcfs3_runner.pump.dataframes import csv_download_link
#csv_download_link(soil_timestep_0,"soil_timestep_0.csv")
#soc_libcbm_0 = soil_timestep_0["SOC_per_ha"].mean()
soil_libscbm_init.describe()
```

# SOC by cbmcfs3_runner


## First attempt at adding area

```python
pools_cbmcfs3 = runner_cbmcfs3.post_processor.database['tblPoolIndicators']
clifr = runner_cbmcfs3.post_processor.classifiers.set_index("user_defd_class_set_id")

# we need to add area which is missing in 'tblPoolIndicators', age_indicators have the same level of details as tblPoolIndicators 
area_init = runner_cbmcfs3.post_processor.inventory.age_indicators
area_init.set_index("user_defd_class_set_id")
area = area_init.loc[area_init["time_step"]==0,["time_step", "user_defd_class_set_id","area"]]
area_a = (area
    .reset_index())
area_aa = (area_a
      .groupby('user_defd_class_set_id')
      .agg({'area': 'sum'})
      .reset_index())
area_aa
```

```python
area_init.columns
```

```python
soil_pools_cbmcfs3= pools_cbmcfs3[['pool_ind_id', 'time_step', 'spuid', 'user_defd_class_set_id',
       'v_fast_ag', 'v_fast_bg', 'fast_ag', 'fast_bg', 'medium', 'slow_ag',
       'slow_bg', 'sw_stem_snag', 'sw_branch_snag', 'hw_stem_snag',
       'hw_branch_snag']]
soil_pools_cbmcfs3_ind= (soil_pools_cbmcfs3 
                   .reset_index())
soil_pools_cbmcfs3_ind_sum=soil_pools_cbmcfs3_ind.sum(axis=1)
soil_pools_cbmcfs3_ind_sss=(soil_pools_cbmcfs3_ind_sum
              .reset_index())
soil_aggreg_cbmcfs3 = pd.merge(soil_pools_cbmcfs3_ind,soil_pools_cbmcfs3_ind_sss,
            how = 'left')
soil_aggreg_cbmcfs3=soil_aggreg_cbmcfs3.rename(columns ={0:"Total_dom"})
soil_cbmcfs3_time_step_0= soil_aggreg_cbmcfs3.loc[soil_aggreg_cbmcfs3["time_step"]==0,["user_defd_class_set_id","Total_dom"]]
soil_cbmcfs3_time_step_0
soil_cbmcfs3_time_step_00=soil_cbmcfs3_time_step_0.sort_values(by=['user_defd_class_set_id'])
soil_cbmcfs3_time_step_00
```

```python
# subset a dataframe with soil relevant columns, inclduing area ("input") 
#in order to estimate initialized C stock per_ha in the timestep 0

area_aa
soil_cbmcfs3_time_step_00

soil_cbmcfs3_init = pd.merge(soil_cbmcfs3_time_step_00, area_aa,
            how = 'left', on = 'user_defd_class_set_id')

soil_cbmcfs3_init['SOC_cbmcfs3_ha']=soil_cbmcfs3_init['Total_dom']/soil_cbmcfs3_init['area']
print(soil_cbmcfs3_init)
```

```python
soil_libscbm_init.describe()
```

```python
soil_cbmcfs3_init.describe()
```

## Second attempt at adding the area


```python
pools_cbm3 = runner_cbm3.post_processor.pool_indicators_long
# classifiers = runner_cbm3.post_processor.classifiers.set_index("user_defd_class_set_id")

# We need to add area which is missing in 'tblPoolIndicators', 
classifiers_names = runner_cbm3.post_processor.classifiers_names
#columns_of_interest = classifiers_names + ['time_step', 'area', 'biomass', 'dom']
inv_cbm3 = runner_cbm3.post_processor.inventory.age_indicators#[columns_of_interest]
```

```python
pools_cbm3.iloc[[1,2,-2,-1]]
```

```python
inv_cbm3.iloc[[1,2,-2,-1]]
```

```python
# Aggregate by classifier, time step and join
index = classifiers_names + ['pool', 'time_step', 'year']
# Aggregate the pools #
pools_cbm3_agg = (pools_cbm3
    .groupby(index, observed=True)
    .agg({'tc':sum})
    .reset_index()
    )
# Aggregate the inventory area
# i.e. sum the area for all ages
index = classifiers_names + ['time_step']
inv_cbm3_agg = (inv_cbm3
         .groupby(index, observed=True)
         .agg({'area':sum})
         .reset_index())
# Add the area column to the pool table
pools_cbm3_agg = pools_cbm3_agg.left_join(inv_cbm3_agg, on=index)

pools_cbm3_agg.iloc[[1,2,-2,-1]]
```

```python
inv_cbm3_agg.iloc[[1,2,-2,-1]]
```

# Compare libcbm and cbm3

```python
pools_cbm3_t0 = pools_cbm3_agg.query("time_step == 0").reset_index(drop=True)
pools_cbm3_t0.iloc[[1,2,-2,-1]]
```

```python
pools_cbm3_t0.pool.unique()
```

```python
soil_pools = ['v_fast_ag', 'v_fast_bg', 'fast_ag', 'fast_bg', 'medium', 'slow_ag',
 'slow_bg', 'sw_stem_snag', 'sw_branch_snag', 'hw_stem_snag', 'hw_branch_snag']
pools_cbm3_t0.query("pool in @soil_pools")
```

```python

```

```python

```
