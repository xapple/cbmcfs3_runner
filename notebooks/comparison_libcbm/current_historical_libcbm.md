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

# Run cbm_defaults script

The script is located at the following link.  This is currently a private fork from our cat-cfs github organization, but it's up-to-data and both Paul and Lucas should have access
[https://github.com/smorken/cbm_defaults](https://github.com/smorken/cbm_defaults)

In retrospect this could be packaged in a better way but it should work with the following script. The following python just assumes that the notebook is in the git clone dir

```python
# Import
from libcbm_runner.core.continent import continent
 
# Init
scenario = continent.scenarios['historical']
runner_libcbm = scenario.runners['LU'][-1]
runner_libcbm.run()


# Show results
#print(runner_libcbm.simulation.results)
#print(runner_libcbm.simulation.inventory)
 

# Retrieve pools
pools_libcbm = runner_libcbm.simulation.results.pools

# Make dataframe
merch_libcbm_by_year = (pools_libcbm
  .groupby('timestep')
  .agg({'HardwoodMerch': 'sum',
        'SoftwoodMerch': 'sum'})
  .reset_index())

# Show
print(merch_libcbm_by_year)
```

```python
#mmm = merch_libcbm_by_year.iloc[0:33,]
#from cbmcfs3_runner.pump.dataframes import csv_download_link
#csv_download_link(mmm,"mmm.csv")
```

# Historical and Contemporary Growth curves


## Option 1: use a historic/contemporary classifier
* This would involve preparing SIT input data with both the historic and contemporary yields included in the sit_yield input
* The other SIT inputs need to be updated to carry the other classifier, and the sit_inventory needs to be set to use the "historic" value initially
* Immediately after spinup you then update the classifier value to "contemporary" in the simulation state variables


```python
from libcbm.input.sit import sit_cbm_factory
from libcbm.model.cbm import cbm_simulator

libcbm_config_path = os.path.abspath(r"./data/libcbm_config.json")
sit = sit_cbm_factory.load_sit(libcbm_config_path)
classifiers, inventory = sit_cbm_factory.initialize_inventory(sit)
cbm = sit_cbm_factory.initialize_cbm(sit)

def get_classifier_id(classifier_name, classifier_value):
    classifier_info = sit_cbm_factory.get_classifiers(
        sit.sit_data.classifiers, sit.sit_data.classifier_values)
    # needs to be filled in a bit more to fetch the appropriate value from 
    # "classifier_info" whose format is documented here:
    # https://github.com/cat-cfs/libcbm_py/blob/e9e37ce5a91cb2bcb07011812a7d49c859d88fa4/libcbm/model/cbm/cbm_config.py#L130

results, reporting_func = cbm_simulator.create_in_memory_reporting_func()
rule_based_processor = sit_cbm_factory.create_sit_rule_based_processor(sit, cbm)

def pre_dynamics_func(timestep, cbm_vars):
    if timestep == 1:
        # see:
        # https://github.com/cat-cfs/libcbm_py/blob/e9e37ce5a91cb2bcb07011812a7d49c859d88fa4/libcbm/model/cbm/cbm_simulator.py#L148
        # if t=1 we know this is the first timestep, and nothing has yet been done to the post-spinup pools
        # it is here that you want to change the yields, and this can be done by changing the classifier set of each inventory record
        # the name "period_classifier" is just a hypothetical example: 
        cbm_vars["period_classifier"] = get_classifier_id("period_classifier", "contemporary")
        
    return rule_based_processor.pre_dynamic_func(timestep, cbm_vars)

cbm_simulator.simulate(
    cbm,
    n_steps              = 102,
    classifiers          = classifiers,
    inventory            = inventory,
    pool_codes           = sit.defaults.get_pools(),
    flux_indicator_codes = sit.defaults.get_flux_indicators(),
    pre_dynamics_func    = pre_dynamics_func, # note we are now calling the above function here
    reporting_func       = reporting_func
)
```

## Option 2: make a custom simulation loop
* assemble the cbm and sit objects 2 times: once for the historic yields and once for the contemporary
* using multiple copies of the same objects
* run spinup with the historic cbm object, and the simulation period with the contemporary object

```python
import os
from libcbm.model.cbm import cbm_variables
from libcbm.model.cbm import cbm_simulator
from libcbm.input.sit import sit_cbm_factory
from libcbm import resources
n_steps = 100

config_path_historic = os.path.join(resources.get_test_resources_dir(), "cbm3_tutorial2", "sit_config.json")
config_path_contemp = os.path.join(resources.get_test_resources_dir(), "cbm3_tutorial2", "sit_config.json")
sit_historic = sit_cbm_factory.load_sit(config_path_historic)
sit_contemp = sit_cbm_factory.load_sit(config_path_contemp)
classifiers_historic, inventory_historic = sit_cbm_factory.initialize_inventory(sit_historic)
classifiers_contemp, inventory_contemp = sit_cbm_factory.initialize_inventory(sit_historic)
cbm_historic = sit_cbm_factory.initialize_cbm(sit_historic)
cbm_contemp = sit_cbm_factory.initialize_cbm(sit_contemp)
results, reporting_func = cbm_simulator.create_in_memory_reporting_func()
rule_based_processor = sit_cbm_factory.create_sit_rule_based_processor(
    sit_contemp, cbm_contemp)
pool_codes = sit_historic.defaults.get_pools()
flux_indicator_codes = sit_historic.defaults.get_flux_indicators()

n_stands = inventory_historic.shape[0]

spinup_params = cbm_variables.initialize_spinup_parameters(n_stands)
spinup_variables = cbm_variables.initialize_spinup_variables(n_stands)

cbm_vars = cbm_variables.initialize_simulation_variables(
    classifiers_historic, inventory_historic, pool_codes, flux_indicator_codes)
cbm_historic.spinup(
    cbm_vars.classifiers, cbm_vars.inventory, cbm_vars.pools,
    spinup_variables, spinup_params)
cbm_historic.init(cbm_vars.inventory, cbm_vars.pools, cbm_vars.state)
reporting_func(0, cbm_vars)

# replace the classifiers with the contemporary classifiers, this is the sole 
# linkage with the yield curves
cbm_vars.classifers = classifiers_contemp

for time_step in range(1, n_steps + 1):
    cbm_vars = rule_based_processor.pre_dynamic_func(time_step, cbm_vars)
    cbm_vars = cbm_variables.prepare(cbm_vars)
    cbm_contemp.step(
        cbm_vars.classifiers, cbm_vars.inventory, cbm_vars.pools,
        cbm_vars.flux_indicators, cbm_vars.state, cbm_vars.params)
    reporting_func(time_step, cbm_vars)

```

```python

```
