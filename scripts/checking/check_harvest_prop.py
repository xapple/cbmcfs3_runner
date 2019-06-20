#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
A script to check stuff in our pipeline.

Typically you would run this file from a command line like this:

     ipython3.exe -i -- /deploy/cbmcfs3_runner/scripts/others/check_harvest_prop.py

There are 3 sources for the same numbers and we want to check constancy.
https://webgate.ec.europa.eu/CITnet/jira/browse/BIOECONOMY-206
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
    # Runner #
    r = continent[('static_demand', c.iso2_code, -1)]
    # First source #
    first  = r.country.silviculture.treatments[['DistTypeID', 'Perc_Merch_Biom_rem']]
    # Second source #
    second = r.country.silviculture.harvest_prop_fact
    # Third source #
    third  = r.input_data.disturnace_type
    selector = '%' in third['Name']
