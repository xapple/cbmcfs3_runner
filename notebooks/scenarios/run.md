---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.2'
      jupytext_version: 1.3.3
  kernelspec:
    display_name: Python 3
    language: python
    name: python3
---

```python
import sys, pandas, seaborn
# Project modules
# Load the cbm_runner package from 'repos/' (instead of 'deploy/') #
sys.path.insert(0, "/repos/cbmcfs3_runner/")
from cbmcfs3_runner.core.continent import continent

# Choose a scenario, country and step
runner = continent[('static_demand', 'LU', 0)]
```

# Introduction
The purpose of this notebook is to show python commands used to run the CBM-CFS3 model using our `cbmcfs3_runner` python module.

We also explain how to read the log output of the model.


# Run the model 


## For 1 country

This would be run typically at an `ipython` command prompt:

    runner.run(verbose=True)

By default, the runner is only printing error messages. 

To view more messages, you can:
1. set the verbose argument to TRUE 
   (note: this sets the log handler property to `"DEBUG"` so that the ongoing runner outputs more messages)
2. start another runner in another ipython console 
   and use `runner.tail` to view the tail of the log file


## View the log
While the model is running, you can call this instruction in another ipython console, with a runner started for the same country.
print(runner.tail)

 * Don't call the `run()` method on that other runner as that would conflict with the already running runner.
 * Don't call the `log` argument as that would delete the log.

```python
# ! Instruction in another ipython console, with a runner started for the same country
print(runner.tail)
```

## For many countries

Countries are grouped under a 'scenario' object. To run the model for many countries, one can run the default method of a scenario object as such:


    scenario = continent.scenarios['static_demand']
    scenario()


See also the script in the `cbmcfs3_runner` repository, under : `scripts/running/run_all_countries.py` which can be invoked like this from the windows machine:

         ipython3.exe -i -- /deploy/cbmcfs3_runner/scripts/running/run_all_countries.py



## View all logs

After all runs have completed (it can take several hours).
The file `logs_summary.md` located at the root of a scenario folder will contain log summaries for all countries.


```python
for key, runner in continent.scenarios['static_demand'].runners.items():
    print(key)
    print(runner[-1].tail)
```

# Post processor and diagnostic plots
Regenerate the country report. 

```python
# regenerate one plot
# runner.country.graphs.merch_stock_at_end(rerun=True)
# regenerate all plots
# runner.country.graphs(rerun=True)

# regenerate the report
# runner.country.report()
```

generate all country reports

