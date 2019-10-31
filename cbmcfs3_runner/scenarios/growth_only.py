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
class GrowthOnly(Scenario):
    """
    Run CBM without any disturbances events for the future period.
    The disturbances for the historical period remain.
    This can then be used as a benchmark to start reproducing results
    with separate models.
    """

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
            # Prolong the simulation until base_year + 15
            base_year       = runner.country.base_year
            inv_start_year  = runner.country.inventory_start_year
            step_2015       =  base_year - inv_start_year + 1
            # Change attribute #
            runner.middle_processor.num_steps_to_extend = step_2015 + 15
        # Return #
        return result
