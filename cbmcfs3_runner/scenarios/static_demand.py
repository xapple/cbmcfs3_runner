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
class StaticDemand(Scenario):
    """
    This scenario represents a demand that is pre-calculated and is not a
    function of the maximum wood supply (no interaction yet with the GFTM model).
    """

    short_name = 'static_demand'

    @property_cached
    def runners(self):
        """A dictionary of country codes as keys with a list of runners as values."""
        # Create all runners #
        result = {c.iso2_code: [Runner(self, c, 0)] for c in self.continent}
        # Don't modify these runners #
        return result
