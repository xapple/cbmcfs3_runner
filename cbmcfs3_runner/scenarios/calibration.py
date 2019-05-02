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
class Calibration(Scenario):
    short_name = 'calibration'

    @property_cached
    def runners(self):
        """A list of runners for each country"""
        result = {c.iso2_code: [Runner(self, c, 0)] for c in self.continent}
        # Get a second scenario #
        other_scen = self.continent.scenarios['static_demand']
        # Patch the input data for each country from that other scenario #
        for c in self.continent:
            this_runner  = result[c.iso2_code][0]
            other_runner = other_scen.runners[c.iso2_code][0]
            this_runner.input_data = other_runner.input_data
        # Return #
        return result