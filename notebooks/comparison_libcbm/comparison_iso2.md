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
from cbmcfs3_runner.core.continent import continent
runner = continent[('static_demand','LU',0)]
```

<!-- #region -->
# Compare LUX 

we compare the merch_stock for two models from CBMCFS3_runner ("runner", based on CBM3_python) to libcbm_runner ("runner_libcbm", based on libcbm_py). The last table ilustrates the issue, the ratio of merch in two models is almost 2, instead of 1, for both SW (sw_ratio) and HW (hw_ratio). 



## CBMCFS3 version
<!-- #endregion -->

```python
#merch stock by year only 
def merch_stock_by(runner,index):
    pools = runner.post_processor.database['tblPoolIndicators']
    clifr = runner.post_processor.classifiers.set_index("user_defd_class_set_id")
    # Our index #

    # Join #
    merch = (pools
      .set_index('user_defd_class_set_id')
      .join(clifr)
      .groupby(index)
      .agg({'hw_merch': 'sum',
            'sw_merch': 'sum'})
      .reset_index())
    # Add year and remove TimeStep #
    merch['year'] = runner.country.timestep_to_year(merch['time_step'])
    return merch
merch_cbmcfs3_by_year=merch_stock_by(runner,'time_step')
merch_cbmcfs3_by_year
```

```python
# Compare the input inventory area to the area available in the output pools table
```

```python
# input inventory 
inv_cbmcfs3 = runner.country.orig_data.inventory
inv_cbmcfs3['area'].sum()

```

```python
# output pools, area 
age_indic = runner.post_processor.database['tblageindicators']
age_indic0 = age_indic.query('time_step == 0')
age_indic0['area'].sum()

```

```python
#merch_stock_by(runner,['time_step', 'forest_type'])
```

```python
# pools = runner.post_processor.database['tblPoolIndicators']
pools0=pools.query('time_step==0')
#for c in pools0.columns:
#    print (c, sum(pools0[c]))
pools0
```

```python
import pandas
with pandas.option_context('display.max_rows', None, 'display.max_columns', None):
    display(pools.query('time_step == 0'))
```

## LIBCBM version

```python
# libcbm version 

from libcbm_runner.core.continent import continent as continent_libcbm
################################################################################
scenario = continent_libcbm.scenarios['historical']
runner_libcbm   = scenario.runners['LU'][-1]
runner_libcbm.run()
```

```python
runner_libcbm.simulation.classifiers.iloc[[0,1,-2,-1]]
```

```python
runner_libcbm.input_data['classifiers'].iloc[[0,1,-2,-1]]
```

import pandas
with pandas.option_context('display.max_rows', None, 'display.max_columns', None):
    display(pools_libcbm.query('timestep == 0'))
    
   

```python
inv = runner_libcbm.input_data['inventory']
pools0 = pools_libcbm.query('timestep == 0')
pools0['Input'].sum()

print(pools0['Input'].sum())
print(inv['area'].sum())

```

```python
#print(runner_libcbm.simulation.results)
#print(runner_libcbm.simulation.inventory)

pools_libcbm = runner_libcbm.simulation.results.pools

merch_libcbm_by_year = (pools_libcbm
  .groupby('timestep')
  .agg({'HardwoodMerch': 'sum',
        'SoftwoodMerch': 'sum'})
  .reset_index())

pools0_libcbm=pools_libcbm.query('timestep==0')
for c in pools0_libcbm.columns:
    print (c, sum(pools0_libcbm[c]))

#pools0_libcbm

```

```python
merch_libcbm_by_year.rename(columns ={'timestep':'time_step'})
print(merch_libcbm_by_year.columns)
print(merch_cbmcfs3_by_year.columns)
merch_comp=merch_cbmcfs3_by_year.merge(merch_libcbm_by_year, left_on='time_step', right_on='timestep')
merch_comp['hw_ratio']= merch_comp.HardwoodMerch/merch_comp.hw_merch
merch_comp['sw_ratio']= merch_comp.SoftwoodMerch/merch_comp.sw_merch
merch_comp

```

```python

```
