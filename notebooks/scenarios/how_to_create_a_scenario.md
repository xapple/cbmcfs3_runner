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
# Import main continent object #
from cbmcfs3_runner.core.continent import continent

# Pick a country #
country_code = "LU"
```

# Introduction

Scenarios consists of python modules storred in the `repos/cbmcsf3_runner/cbmcsf3_runner/scenarios` directory.

There are several existing scenarios:

* `historical` covers the historical period only (i.e. up to 2015) and it does not contain future disturbances.
* `static_demand` is a scenario with demand from the GFTM economic model taken in one single input file 
    from 2016 to 2030. In this scenario there is no feed-back loop between CBM-CFS3 and GFTM.
* `calibration` gives access to the CBM-CFS3 output of a manual GUI run performed during the calibration process via a dummy database mechanism. You can't actually run this scenario.
* `fake_yields_hist` is a scenario that tests using current yields for all period.
* `fake_yields_cur` is a scenario that tests using historical yields for all periods.
* `single_sit` is a scenario that does not perform a seperate carbon pool initialization with different yield curves.
* `growth_only` is a scenario where the historical period contains disturbances but the future period does not.
* `auto_allocation` is a scneario where the future disturances have question marks in all calssifiers (except con_broad).

## Scenario objects

In the `cbmcfs3_runner` pipeline, Scenario objects give access to one or several Runner object per Country object.

`continent.scenarios` is a dictionnary of

| keys          | values        |
|---------------|---------------|
| scenario name |scenario object|

```python
continent.scenarios
```

Scenario information can also be accessed at the country level, albeit, only giving access to the list of runners for each country. 

`country.scenarios` is a dictionnary of 

| keys          | values                              |
|---------------|-------------------------------------|
| scenario name |list of runners for the given country|

```python
continent.countries[country_code].scenarios
```

# Creating a new scenario
To create a scenario:
1. Create a new file in the
    `repos/cbmcsf3_runner/scenarios` directory, by copying an existing scenario.
    
2. Edit `repos/cbmcsf3_runner/scenarios/new_scenario.py` and
   give the scenario a new class name and short scenario name:

        class NewScenario(Scenario):
            short_name = 'new_scenario'
            
3. Edit `repos/cbmcsf3_runner/scenarios/__init__.py` to 
    * import the new class `from cbmcfs3_runner.scenarios.new_scenario import NewScenario` 
    * and add the `NewScenario` to the list of scenario classes `scen_classes`.
    

```python

```
