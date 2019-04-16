#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
A script to check that the years add up.

Typically you would run this file from a command line like this:

     ipython3.exe -i -- /deploy/cbmcfs3_runner/scripts/others/check_end_years.py
"""

# Futures #
from __future__ import print_function

# Built-in modules #

# Third party modules #

# First party modules #

# Internal modules #
from cbmcfs3_runner.core.continent import continent

###############################################################################
for c in continent:
    r = continent[('static_demand', c.iso2_code, 0)]
    print("---Country %s (%s)---" % (c.iso2_code, c.country_name))
    print('Timesteps: ', r.middle_processor.current_timestep)
    print('Start year:', c.inventory_start_year)
    print('End year:  ', c.inventory_start_year + r.middle_processor.current_timestep)