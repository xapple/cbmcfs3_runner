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
class Historical(Scenario):
    """
    This scenarios represents a demand that is pre-calculated and is not a function of the
    maximum wood supply (no interaction yet with the GFTM model).
    """

    short_name = 'historical'

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
        # Return #
        return result
