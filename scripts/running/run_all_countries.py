#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
A script to run all the countries.

Typically you would run this file from a command line like this:

     ipython3.exe -i -- /deploy/cbmcfs3_runner/scripts/running/run_all_countries.py

The last times the script was run it took this much time to run:
100%|████████████████████| 26/26 [9:49:52<00:00, 998.86s/it]
100%|██████████████████| 26/26 [10:36:00<00:00, 1329.48s/it]
"""

# Built-in modules #

# Third party modules #

# First party modules #

# Internal modules #
from cbmcfs3_runner.core.continent import continent

###############################################################################
scenario = continent.scenarios['static_demand']
scenario()

###############################################################################
#continent()
