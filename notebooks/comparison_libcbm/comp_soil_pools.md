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

# Introduction

The purpose of this notebook is to compare soil pools between libcbm and cbmcfs3.




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

```python
# run
runner_libcbm.run()
```

# Compare the input

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
yield_libcbm = pd.read_csv(runner_libcbm.input_data.paths["growth_curves"])
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

# Compare soil and merch pools at t0


## libcbm

```python
pools_libcbm = runner_libcbm.output.load('pools')
pools_libcbm.iloc[[1,-1]]
```

```python
pools_libcbm.columns
```

```python
so_me_pools_libcbm = pools_libcbm[['identifier', 'timestep', 'area', 'above_ground_very_fast_soil', 'below_ground_very_fast_soil',
       'above_ground_fast_soil', 'below_ground_fast_soil', 'medium_soil',
       'above_ground_slow_soil', 'below_ground_slow_soil',
       'softwood_stem_snag', 'softwood_branch_snag', 'hardwood_stem_snag',
       'hardwood_branch_snag', 'softwood_merch', 'hardwood_merch']]

so_me_pools_libcbm_t0 = so_me_pools_libcbm.query("timestep == 0")
tot_libcbm = so_me_pools_libcbm_t0.set_index(['identifier', 'timestep', 'area']).sum().reset_index()
libcbm = tot_libcbm.rename(columns={'index':'libcbm_pools', 'Unnamed:0':'tC'})
libcbm
```

## cbmcfs3 

```python
pools_cbm3 = runner_cbm3.post_processor.database['tblPoolIndicators']
clifr = runner_cbm3.post_processor.classifiers.set_index("user_defd_class_set_id")
pools_cbm3.iloc[[1,-1]]
```

```python
pools_cbm3.columns
```

```python
so_me_pools_cbm3 = pools_cbm3[['time_step', 'spuid', 'user_defd_class_set_id',
       'v_fast_ag', 'v_fast_bg', 'fast_ag', 'fast_bg', 'medium', 'slow_ag',
       'slow_bg', 'sw_stem_snag', 'sw_branch_snag', 'hw_stem_snag',
       'hw_branch_snag','sw_merch', 'hw_merch' ]]
so_me_pools_cbm3_t0 = so_me_pools_cbm3.query("time_step == 0")
#so_me_pools_cbm3_t0
```

```python
so_me_pools_cbm3 = pools_cbm3[['time_step', 'spuid', 'user_defd_class_set_id',
       'v_fast_ag', 'v_fast_bg', 'fast_ag', 'fast_bg', 'medium', 'slow_ag',
       'slow_bg', 'sw_stem_snag', 'sw_branch_snag', 'hw_stem_snag',
       'hw_branch_snag','sw_merch', 'hw_merch' ]]
so_me_pools_cbm3_t0 = so_me_pools_cbm3.query("time_step == 0")
so_me_pools_cbm3_t0.set_index(['time_step', 'spuid','user_defd_class_set_id']).sum()
tot_cbm3 = so_me_pools_cbm3_t0.set_index(['time_step', 'spuid','user_defd_class_set_id']).sum().reset_index()
cbm3=tot_cbm3.rename(columns={'index':'cbm3_pools'})
cbm3
```

```python
frames=[cbm3, libcbm]
result = pd.concat(frames, axis=1)
result
```

```python

```

```python

```
