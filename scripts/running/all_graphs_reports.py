#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
A script to regenerate all the graphs for every country object and every runner object as well (of the static demand scenario).

Typically you would run this file from a command line like this:

     ipython3.exe -i -- /deploy/cbmcfs3_runner/scripts/running/all_graphs_reports.py
"""

# Built-in modules #

# Third party modules #
from tqdm import tqdm

# First party modules #

# Internal modules #
from cbmcfs3_runner.core.continent import continent

################################################################################
for country in tqdm(continent.countries.values()):
    # Get scenarios #
    runner = country.scenarios['static_demand'][-1]
    # Optionally, filter runners #
    #if runner.map_value < 1.0: continue
    # Purge runners #
    runner.paths.graphs_dir.remove()
    # Purge country #
    country.paths.graphs_dir.remove()
    # Runner report #
    runner.report()
    # Country report #
    country.report()
    country.report.copy_to_outbox()
