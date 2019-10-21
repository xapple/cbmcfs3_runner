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
from cbmcfs3_runner.core.continent import continent
# Choose a scenario, country and step
country = 'LU'
runner_static_demand = continent[('static_demand', country, 0)]
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
    
