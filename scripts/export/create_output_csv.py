#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
A script to create all useful export CSVs.

Typically you would run this file from a command line like this:

     ipython3 -i -- ~/deploy/cbmcfs3_runner/scripts/export/create_output_csv.py

Or on the windows machine:

    ipython3.exe -i -- /deploy/cbmcfs3_runner/scripts/export/create_output_csv.py

"""

# Built-in modules #

# Third party modules #
from tqdm import tqdm

# First party modules #

# Internal modules #
from cbmcfs3_runner.core.continent import continent

###############################################################################
# Many scenarios #
scenarios = ['historical', 'static_demand', 'demand_plus_20', 'demand_minus_20']

# Go through every runner #
for scen_name in scenarios:
    # Load scenario #
    scenario = continent.scenarios[scen_name]
    # Loop runners #
    for runners in tqdm(scenario.runners.values()):
        r = runners[-1]
        r.post_processor.csv_maker()
    # Make zip file #
    scenario.make_csv_zip('ipcc_pools', '~/exports/for_sarah/' + scen_name + '/')