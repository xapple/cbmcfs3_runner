#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This scenario is the same as `static_demand` except that we use the
current yield tables for the historical period simulation.
We are normally not supposed to do this. But, for comparison purposes,
we are going to do so anyway to see what effect has this change of yield.
"""

# Built-in modules #

# First party modules #
from plumbing.cache import property_cached

# Internal modules #
from cbmcfs3_runner.scenarios.base_scen import Scenario
from cbmcfs3_runner.core.runner import Runner

###############################################################################
class FakeYields(Scenario):
    short_name = 'fake_yields'

    @property_cached
    def runners(self):
        """A dictionary of country codes with a list of runners (for each country)."""
        # Create all runners #
        result = {c.iso2_code: [Runner(self, c, 0)] for c in self.continent}
        # Modify these runners #
        for c in self.continent:
            # Get the runner of the last step #
            runner = result[c.iso2_code][-1]
            # Copy the class attribute into the instance of the class #
            xls = runner.default_sit.create_xls
            xls.file_name_to_sheet_name = xls.file_name_to_sheet_name.copy()
            # Switch the relevant key #
            growth = xls.file_name_to_sheet_name.pop('historical_yields')
            xls.file_name_to_sheet_name['yields'] = growth
        # Return #
        return result
