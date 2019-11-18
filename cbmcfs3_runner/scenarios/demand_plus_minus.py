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
class DemandPlusMinus(Scenario):
    """
    This scenario is similar to the `static_demand` scenario. Except that it
    multiples said demand by a variable ratio before running the model.
    Either increasing the demand or reducing it.
    """

    demand_ratio = 1.0

    @property_cached
    def runners(self):
        """A dictionary of country codes as keys with a list of runners as values."""
        # Create all runners #
        result = {c.iso2_code: [Runner(self, c, 0)] for c in self.continent}
        # Modify these runners #
        for country in self.continent:
            # Get the maker #
            runner     = result[country.iso2_code][-1]
            dist_maker = runner.pre_processor.disturbance_maker
            # Adjust the artificial ratios #
            dist_maker.irw_artificial_ratio = self.demand_ratio
            dist_maker.fw_artificial_ratio  = self.demand_ratio
        # Don't modify these runners #
        return result

###############################################################################
class DemandPlus20(DemandPlusMinus):
    short_name   = 'demand_plus_20'
    demand_ratio = 1.2

###############################################################################
class DemandMinus20(DemandPlusMinus):
    short_name   = 'demand_minus_20'
    demand_ratio = 0.8
