#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
A script to run all the countries.

The first step is to create the CSV files from the calibration database for every country.
The last step is generating a report with the outcome of the simulation.

Typically you would run this file from a command line like this:

     ipython3.exe -i -- /deploy/cbmcfs3_runner/scripts/running/run_all_countries.py
"""

# Built-in modules #

# Third party modules #
from tqdm import tqdm

# First party modules #

# Internal modules #
from cbmcfs3_runner.core.continent import continent

###############################################################################
# Run each country and send errors to the log #
scenario = continent.scenarios['static_demand']
runners  = [r[0] for k,r in scenario.runners.items()]
runners  = [r for r in runners if r.iso2_code in ('GB', 'GR', 'HR', 'LT', 'LV')]

for r in tqdm(runners, ncols=60):
    try:
        r(silent=True)
    except Exception:
        pass

###############################################################################
# Update the log summary #
scenario.compile_log_tails()
