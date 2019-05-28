#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This scenarios is the same as static_demand.py except that we use the
current yield for the historical period
We are not supposed to do this.
It is just for comparison purposes, to see what effect has this change of yield.
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
        result = {c.iso2_code: [Runner(self, c, 0)] for c in self.continent}
        for c in self.continent:
            # Get runner #
            runner = result[c.iso2_code][0]
            # Copy the class attribute into the instance of the class #
            xls = runner.default_sit.create_xls
            xls.file_name_to_sheet_name = xls.file_name_to_sheet_name.copy()
            # Switch the relevent key #
            runner.default_sit.create_xls.file_name_to_sheet_name.pop('historical_yields')
            runner.default_sit.create_xls.file_name_to_sheet_name['yields'] = 'Growth'
        # Return #
        return result
