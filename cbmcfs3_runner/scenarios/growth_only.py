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
class GrowthOnly(Scenario):
    short_name = 'growth_only'

    @property_cached
    def runners(self):
        """A dictionary of country codes as keys with a list of runners as values."""
        # Create all runners #
        result = {c.iso2_code: [Runner(self, c, 0)] for c in self.continent}
        # Modify these runners #
        for country in self.continent:
            runner = result[country.iso2_code][-1]
            pre_pro = runner.pre_processor
            # Deactivate the disturbance maker #
            # i.e. use only historical disturbances #
            pre_pro.disturbance_events = pre_pro.events_hist
            # Prolong the simulation until 2030
            step_2015 = runner.country.base_year - runner.country.inventory_start_year 
            runner.middle_processor.years_to_extend = step_2015 + 15
        # Return #
        return result
