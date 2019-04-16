#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This scenarios represent a demand that is pre-calculated and is not a function of the
maximum wood supply.
"""

# Built-in modules #

# First party modules #
from plumbing.cache import property_cached

# Internal modules #
from cbmcfs3_runner.scenarios.base_scen import Scenario
from cbmcfs3_runner.core.runner import Runner

###############################################################################
class StaticDemand(Scenario):
    short_name = 'static_demand'

    @property_cached
    def runners(self):
        """A list of runners for each country"""
        result = {c.iso2_code: [Runner(self, c, 0)] for c in self.continent}
        return result