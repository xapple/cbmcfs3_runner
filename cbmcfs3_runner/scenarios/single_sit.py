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
class SingleSIT(Scenario):
    """
    Call SIT only once.
    """

    short_name = 'single_sit'

    @property_cached
    def runners(self):
        """A dictionary of country codes as keys with a list of runners as values."""
        # Create all runners #
        result = {c.iso2_code: [Runner(self, c, 0)] for c in self.continent}
        # Modify these runners #
        for c in self.continent:
            # Get the runner of the last step #
            runner = result[c.iso2_code][-1]
            runner.sit_calling = 'single'
            runner.default_sit.yield_table_name = "historical_yields.csv"
        # Return #
        return result
