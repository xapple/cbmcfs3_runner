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

The purpose of this notebook is to compare carbon pools between libcbm and cbmcfs3 for the historical scenario or the historical part of the static_demand scenario (which should have identical disturbances for the part before 2015).




## Create runner objects

Create a runner object for each model.


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

## Run libcbm to get output

This running step is needed because libcbm doesn't store the output. It is not needed for cbmcfs3 because the output is storred in the Access output database and reused from there. 

```python
# run
runner_libcbm.run()
```

## Compare the input to check it is identical

Make sure that the cbmcfs3 and libcbm runners use the same input inventory, disturbances and yields.

```python
# Compare the Input inventory
print(f"cbmcfs3 input inventory area: {runner_cbm3.input_data.get_sheet('Inventory').area.sum()}")
libcbminv = pd.read_csv(runner_libcbm.input_data.paths.inventory)
print(f"libcbm input inventory area: {libcbminv.area.sum()}")
```

```python
# Compare the yields
yield_cbm3 = runner_cbm3.input_data.get_sheet('Growth')
yield_libcbm = pd.read_csv(runner_libcbm.input_data.paths["yield"])
```

```python
# Compare the disturbances
dist_cbm3 = runner_cbm3.input_data.disturbance_events
dist_libcbm = pd.read_csv(runner_libcbm.input_data.paths.events)
dist_cbm3_agg = (dist_cbm3
                 .groupby(['measurement_type', 'step'])
                 .agg(amount_cbm3 = ('amount',sum))
                )
dist_libcbm_agg = (dist_libcbm
                   .groupby(['measurement_type', 'step'])
                   .agg(amount_libcbm = ('amount', sum))
                  )

dist_comp = dist_cbm3_agg.merge(dist_libcbm_agg, "left", left_index = True, right_index = True)
dist_comp.iloc[[0,1,2,3,4,5,-3,-2,-1]]
```

## Retrieve pools for both model versions

```python
pools_libcbm = runner_libcbm.simulation.results.pools
pools_libcbm.iloc[[1,-1]]
```

```python
pools_cbm3 = runner_cbm3.post_processor.database['tblPoolIndicators']
```

## Load pool names mapping table

Pool names differ between the 2 model versions, load a mapping table.

```python

```

# Compare all pools at t0


## libcbm

```python
pools_libcbm.columns
```

```python
so_me_pools_libcbm = pools_libcbm[['identifier', 'timestep', 'Input', 'AboveGroundVeryFastSoil',
       'BelowGroundVeryFastSoil', 'AboveGroundFastSoil', 'BelowGroundFastSoil',
       'MediumSoil', 'AboveGroundSlowSoil', 'BelowGroundSlowSoil',
       'SoftwoodStemSnag', 'SoftwoodBranchSnag', 'HardwoodStemSnag',
       'HardwoodBranchSnag', 'SoftwoodMerch', 'HardwoodMerch']]

so_me_pools_libcbm_t0 = so_me_pools_libcbm.query("timestep == 0")
so_me_pools_libcbm_t0.set_index(['identifier', 'timestep', 'Input']).sum()
```

## cbmcfs3 

```python
pools_cbm3.pool.unique()
```

```python
soil_pools = ['fast_ag', 'fast_bg', 'hw_branch_snag', 'hw_stem_snag', 'medium', 'slow_ag', 'slow_bg', 'sw_branch_snag','sw_stem_snag', 'v_fast_ag', 'v_fast_bg']
soil_and_merch_pools = soil_pools + ['hw_merch', 'sw_merch']
so_me_pools_cbm3 = pools_cbm3.query("pool in @soil_and_merch_pools") 
so_me_pools_cbm3_t0 = so_me_pools_cbm3.query("time_step == 0")
so_me_pools_cbm3_t0_sum =  (so_me_pools_cbm3_t0
 .groupby(['pool'])
 .agg(total_new_name = ('tc', sum))
)
so_me_pools_cbm3_t0_sum
```

```python

```
