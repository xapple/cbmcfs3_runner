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

```python
# Create a cbmcfs3 runner
from cbmcfs3_runner.core.continent import continent
runner_cbm3 = continent[('static_demand','LU',0)]
```

# Output inventory


```python
inv_cbm3 = runner_cbm3.post_processor.inventory.age_indicators#[columns_of_interest]
```


## Checks on inventory aggregation


```python
# Colummns available as aggregation variables
print(inv_cbm3.columns)
# Number of rows
inv_cbm3.iloc[[1,2,-2,-1]]
```

```python
# Aggregate by classifiers and time step
(inv_cbm3
    .groupby(classifiers_names + ['time_step'], observed=True)
    .agg({'area':sum})
    .reset_index()
    .iloc[[1,2,-2,-1]]
)
```

```python
# When we aggregate by classifiers and age id we get the maximum number of rows
(inv_cbm3
    .groupby(classifiers_names + ['time_step', 'age_ind_id'], observed=True)
    .agg({'area':sum})
    .reset_index()
    .iloc[[1,2,-2,-1]]
)
```

```python
# Aggregate by time step and user_defd_class_set_id is the same as aggregating by classifiers.
# In o ther words, one user_defd_class_set_id maps to a unique set of classifiers, without the age.
(inv_cbm3
    .groupby(['time_step', 'user_defd_class_set_id'], observed=True)
    .agg({'area':sum})
    .reset_index()
    .iloc[[1,2,-2,-1]]
)
```

```python
# Add the area to the pools table
#pools_cbm3 = pools_cbm3
```
