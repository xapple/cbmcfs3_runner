---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.1'
      jupytext_version: 1.1.7
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

# Choose a scenario, country and step
country = 'LU'
runner_calibration = continent[('calibration', country, 0)]
runner_static_demand = continent[('static_demand', country, 0)]

# Choose scenarios to compare
scenario_names = ['static_demand', 'calibration']
```

<!-- #region -->
# Introduction
Scenarios consists of python scripts storred in the `cbmcsf3_runner/cbmcsf3_runner/scenarios folder`.

* `historical` covers the historical period only up to 2015, it does not contain future disturbances.
* `static_demand` is a scenario with demand from the GFTM economic model taken in one single input file 
    from 2016 to 2030. In this scenario there is no feed-back from CBM to GFTM.
* `calibration` gives access to the CBM output of a manual GUI run performed during the calibration process
* `fake_yields` was a test of using current yields for the historical period
* `growh_only ` is a CBM run for the historical period without disturbances


## Scenario objects
In the `cbmcfs3_runner` pipeline, scenarios are continent scale objects that give access to CBM runners for many countries.

`continent.scenarios` is a dictionnary of

| keys          | values        |
|---------------|---------------|
| scenario name |scenario object|
<!-- #endregion -->

```python
continent.scenarios
```

Scenario information can also be accessed at the country level, albeit, only giving access to the list of runners for each country. 

`country.scenarios` is a dictionnary of 

| keys          | values                              |
|---------------|-------------------------------------|
| scenario name |list of runners for the given country|

```python
continent.countries[country].scenarios
```

# Creating a new scenario
To create a scenario:
1. Create a new file in the
    `cbmcsf3_runner/scenarios` folder, by copying an existing scenario.
2. Edit `cbmcsf3_runner/scenarios/new_scenario.py` 
   give the scenario a new class name and short scenario name

        class NewScenario(Scenario):
            short_name = 'new_scenario'
3. Edit `cbmcsf3_runner/scenarios/__init__.py` to 
    * import the new class `from cbmcfs3_runner.scenarios.fake_yields   import NewScenario` 
    * and add the `NewScenario` to the list of scenario classes `scen_classes`.
    

<!-- #region -->
# List of scenarios
`static_demand` is the first scenario we tried to run.


## calibration
Calibration is a scenario that did not run through the cbmcfs3_runner. 
It gives access to the original data givent by Roberto, output of his CBM calibration procedure. Roberto's data  also countains CBM output data. We wan to use Roberto's manual simulations with the CBM GUI, with the output of our automated scripts.
<!-- #endregion -->

## historical


[historical](historical.md) covers the historical period only before 2015


## static_demand
[static_demand](static_demand.md) is the default scenario. 


## fake_yields_hist

```python
# Here are the yield tables used in the static_demand scenario
print(runner_static_demand.default_sit.yield_table_name)
print(runner_static_demand.append_sit.yield_table_name)
```

```python
# The scenario fake_yields_hist used different yield tables
# print(runner_fake_yields_hist.default_sit.yield_table_name)
# print(runner_fake_yields_hist.append_sit.yield_table_name)
```

## fake_yields_cur
fake_yields_cur is a scenario used to compare the use of historical_yields and normal yields over the historical i.e. ~1998-2015 period.
Different yields

```python
# you can see that the fake_yields_cur uses different yield tables
# print(runner_fake_yields_cur.default_sit.yield_table_name)
# print(runner_fake_yields_cur.append_sit.yield_table_name)
```

Compare total merchantable biomass for all scenarios in one bar plot

```python
runner_static_demand.country.graphs.merch_stock_at_start(rerun=True, close=False)
```

```python
display(runner_fake_yields_hist.country.graphs.merch_stock_at_end(rerun=True, close=False))
```

## growth_only
`growth_only` is a scenario without disturbance, to prepare the reverse-engineering of CBM. 
It will enable us to see only the growth part of CBM.

See the other notebook: 
[growth_only.ipynb](growth_only.ipynb)

```python

```
