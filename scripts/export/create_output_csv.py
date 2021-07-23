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
for scen_name in tqdm(scenarios, desc='Scenarios'):
    # Load scenario #
    scenario = continent.scenarios[scen_name]
    # Loop runners #
    for runners in tqdm(scenario.runners.values(), desc='Countries', leave=False):
        r = runners[-1]
        # Do not recreate the csv file if it already exists
        if r.post_processor.csv_maker.paths.inventory_simulated.exists:
            print(f"Skipping {r.country.iso2_code}")
            continue
        print(f"Processing {r.country.iso2_code}")
        try:
            r.post_processor.csv_maker()
        except Exception as e:
            print("no data in ", r.country.iso2_code)
            print('Error loading data: '+ str(e))
    # Make zip files #
    scenario.make_csv_zip('inventory_simulated', '~/exports/for_sarah/' + scen_name + '/')
    scenario.make_csv_zip('ipcc_pools', '~/exports/for_sarah/' + scen_name + '/')

