#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
A script to run the current feature that is being developed and test it.

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
for c in tqdm(continent.countries.values()):
    # Get scenarios #
    statc = c.scenarios['static_demand'][-1]
    # Filter runners #
    if statc.map_value < 1.0: continue
    # Purge runners #
    statc.paths.graphs_dir.remove()
    # Purge country #
    c.paths.graphs_dir.remove()
    # Runner report #
    statc.report()
    # Country report #
    c.report()
    c.report.copy_to_outbox()
