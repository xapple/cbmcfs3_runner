#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Run CBM without any disturbances even for the historical period.
This can then be used as a benchmark to start reproducing results
with separate models.
"""

# Built-in modules #

# First party modules #
from plumbing.cache import property_cached

# Internal modules #
from cbmcfs3_runner.scenarios.base_scen import Scenario
from cbmcfs3_runner.core.runner import Runner

###############################################################################
def filter_df(df, base_year, inv_start_year):
    """Takes the old event data frame and returns only disturbances for 2020."""
    only_this_year = base_year - inv_start_year + 5
    return df.query("Step == %s" % only_this_year)

###############################################################################
class GrowthOnly(Scenario):
    short_name = 'growth_only'

    @property_cached
    def runners(self):
        """A dictionary of country codes as keys with a list of runners as values."""
        # Create all runners #
        result = {c.iso2_code: [Runner(self, c, 0)] for c in self.continent}
        # Modify these runners #
        for c in self.continent:
            # Get the runner of the last step #
            runner = result[c.iso2_code][-1]
            # Monkey patch the pre-processor filter method #
            runner.pre_processor.filter_df = filter_df
        # Return #
        return result
