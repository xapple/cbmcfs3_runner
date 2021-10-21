#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Written by Lucas Sinclair, Viorel Blujdea and Paul Rougieux.

JRC Biomass Project.
Unit D1 Bioeconomy.

    Typically you would run this file from a command line like this:

         ipython3 -i -- ~/repos/cbmcfs3_runner/scripts/libcbm_comparison/compare_aidb.py
"""
# Third party modules #
from tqdm import tqdm

# Internal modules
from cbmcfs3_runner.pump.aidb_comparison import CompareAIDB
# Continents #
from cbmcfs3_runner.core.continent import continent as cbmcfs3_continent

###############################################################################
if __name__ == '__main__':
    # Make comparison objects, one per country #
    comparisons = [CompareAIDB(c) for c in cbmcfs3_continent]
    # Run them all #
    for comp in tqdm(comparisons):
        comp()
