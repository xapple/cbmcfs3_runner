---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.1'
      jupytext_version: 1.2.4
  kernelspec:
    display_name: Python 3
    language: python
    name: python3
---

```python
import sys, pandas, seaborn, numpy
# Project modules
# Load the cbm_runner package from 'repos/' (instead of 'deploy/') #
sys.path.insert(0, "/repos/cbmcfs3_runner/")
from cbmcfs3_runner.core.continent import continent
scenario = continent.scenarios['static_demand']
runner = continent[('static_demand','AT',0)]
```

# Introduction 
The purpose of this notebook is to plot the change in carbon fluxes through time after the simulation run. 



# Input



## Disturbances

```python
# Load dist
dist = runner.input_data.disturbance_events
# Add hwp column
hwp_map = runner.country.silviculture.hwp_map
cols = list(set(hwp_map.columns) - set(['hwp']))
print(cols)
dist = dist.left_join( hwp_map, cols)
dist
```

```python
dist[['amount1000']] = dist[['amount']]/1e3
ax = dist[['amount1000', 'step']].groupby('step').sum().plot()
ax.set_ylabel("Amount in 1000 cubic meter")
ax 
```

```python
import seaborn
dist_agg = (dist
            .groupby(['hwp', 'step'])
            .agg({'amount':sum})
            .reset_index())
dist_agg['amount'] = dist_agg['amount']/1e3
ax = seaborn.scatterplot('step', 'amount', 'hwp', data=dist_agg)
ax.set_ylabel("Amount in 1000 tons of carbon")
display(ax)
```

# Flux indicators
Direct CBM output

```python
flux = runner.post_processor.flux_indicators
flux.head()
```

```python
print(flux.columns)
```

```python
production = ['soft_production', 'hard_production']
flux[['time_step']+production].groupby("time_step").sum().plot()
```

# Harvested wood products 

```python
hwp =runner.post_processor.products.hwp
hwp.head()
```

```python
cols = ['irw_c', 'irw_b', 'fw_c', 'fw_b']
hwp[cols] = hwp[cols]/1e3
```

```python
ax = hwp.set_index("time_step").drop(columns='year').plot(style="o", figsize=(10,10))
ax.set_ylabel("Amount in 1000 cubic meters")
```

```python

```
