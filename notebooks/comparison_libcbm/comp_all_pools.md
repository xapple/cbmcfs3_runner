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
dist_comp['diff'] = dist_comp.amount_cbm3 - dist_comp.amount_libcbm
print("\nNote how the disturbance amout differs from time step 12 onwards")
dist_comp#.iloc[[0,1,2,3,4,5,-3,-2,-1]]
```

## Run libcbm to get its output

This running step is needed because libcbm doesn't store the output. It is not needed for cbmcfs3 because the output is storred in the Access output database and reused from there. 

```python
# run
runner_libcbm.run()
```

## Retrieve pools for both model versions

```python
pools_libcbm_wide = runner_libcbm.simulation.results.pools
display(pools_libcbm_wide.iloc[[1,-1]])
print(f"Number of rows in the wide table {len(pools_libcbm_wide)}")
```

```python
# Reshape to long format #
pools_libcbm = pools_libcbm_wide.melt(id_vars=['identifier', 'timestep', 'Input'],
                                    var_name='pool',
                                    value_name='tc')
display(pools_libcbm.iloc[[1,-1]])
print(f"Number of rows in the long table {len(pools_libcbm)}")
```

```python
pools_cbm3 = runner_cbm3.post_processor.pool_indicators_long
display(pools_cbm3.iloc[[1,-1]])
print(f"Number of rows in the long format table {len(pools_cbm3)}")
```

<!-- #region -->
## Pool names and mapping table


Pool names differ between the 2 model versions, load a mapping table.
<!-- #endregion -->

```python
pools_libcbm.columns
```

```python
pools_cbm3.pool.unique()
```

```python
from cbmcfs3_runner.pump.libcbm_mapping import libcbm_mapping
print(libcbm_mapping)
# Remove the unnecessary ipcc pool names
libcbm_mapping = libcbm_mapping[['libcbm', 'cbmcfs3']]
```

# Compare all pools at t0

Aggregate with a sum, then compare all carbon pools at time step zero. 


Aggregate libcbm by pool

```python
pools_libcbm_t0 = pools_libcbm.query("timestep == 0")

pools_libcbm_t0_sum = (pools_libcbm_t0
                       .groupby(['pool'])
                       .agg(tc_libcbm = ('tc', sum))
                      )
```

Aggregate cbmcfs3 by pool

```python
pools_cbm3_t0 = pools_cbm3.query("time_step == 0")
pools_cbm3_t0_sum =  (pools_cbm3_t0
 .groupby(['pool'])
 .agg(tc_cbmcfs3 = ('tc', sum))
)
```

Merge and compare the difference 

```python
pools_t0_comp = (pools_cbm3_t0_sum
 .merge(libcbm_mapping, 'left', left_index = True, right_on = 'cbmcfs3')
 .merge(pools_libcbm_t0_sum, 'outer', left_on = 'libcbm', right_index = True)
 .reset_index(drop = True))
pools_t0_comp['diff'] = pools_t0_comp['tc_libcbm'] - pools_t0_comp['tc_cbmcfs3']
pools_t0_comp['diff_prop'] = (pools_t0_comp['tc_libcbm'] / pools_t0_comp['tc_cbmcfs3']) - 1
# Query to remove NA values 
pools_t0_comp.query("libcbm == libcbm")
```

# Compare all pools at all time steps
