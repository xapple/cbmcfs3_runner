#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
A script to run all the scenarios.

Typically you would run this file from a command line like this:

     ipython3.exe -i -- /deploy/cbmcfs3_runner/scripts/running/run_all_scenarios.py
"""

# Built-in modules #

# Third party modules #

# First party modules #

# Internal modules #
from cbmcfs3_runner.core.continent import continent

###############################################################################
for scenario in continent.scenarios.values():
    if scenario.short_name == 'calibration': continue
    print("*** Scenario: %s ***\n" % scenario.short_name)
    scenario(verbose=True)