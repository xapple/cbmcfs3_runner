#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Written by Lucas Sinclair and Paul Rougieux.

JRC biomass Project.
Unit D1 Bioeconomy.
"""

# Built-in modules #

# First party modules #
from plumbing.cache import property_cached

# Internal modules #
from cbmcfs3_runner.scenarios.base_scen import Scenario
from cbmcfs3_runner.core.runner import Runner

###############################################################################
class FakeYieldsHist(Scenario):
    """
    This scenario is the same as `static_demand` except that we use the
    HISTORICAL yield tables for the current period simulation.

    Calling SIT both times with the same historical yield table.

    We are normally not supposed to do this. But, for comparison purposes,
    we are going to do so anyway to see what effect this change has on results..
    """

    short_name = 'fake_yields_hist'

    @property_cached
    def runners(self):
        """A dictionary of country codes as keys with a list of runners as values."""
        # Create all runners #
        result = {c.iso2_code: [Runner(self, c, 0)] for c in self.continent}
        # Modify these runners #
        for c in self.continent:
            # Get the runner of the last step #
            runner = result[c.iso2_code][-1]
            runner.default_sit.yield_table_name = "historical_yields.csv"
        # Return #
        return result
