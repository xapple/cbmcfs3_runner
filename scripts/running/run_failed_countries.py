#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
A script to rerun only the countries that didn't pass.

Typically you would run this file from a command line like this:

     ipython3.exe -i -- /deploy/cbmcfs3_runner/scripts/running/run_failed_countries.py
"""

# Built-in modules #

# Third party modules #
from tqdm import tqdm

# First party modules #

# Internal modules #
from cbmcfs3_runner.core.continent import continent

###############################################################################
scenario       = continent.scenarios['static_demand']
runners        = [r[-1] for k,r in scenario.runners.items()]
failed_runners = [r for r in runners if r.map_value < 1.0]
for r in tqdm(failed_runners):
    if r.country.iso2_code == "LU": continue
    if r.country.iso2_code == "SI": continue
    r(interrupt_on_error=False)

###############################################################################
for r in failed_runners:
    if r.country.iso2_code == "LU": continue
    if r.country.iso2_code == "SI": continue
    print("---------------")
    print(r.country.iso2_code)
    print(r.tail)