#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Written by Lucas Sinclair and Paul Rougieux.

JRC biomass Project.
Unit D1 Bioeconomy.
"""

# Built-in modules #

# Third party modules #
import pandas

# First party modules #
from autopaths.auto_paths import AutoPaths
from plumbing.cache import property_cached

# Internal modules #

###############################################################################
class Silviculture(object):
    """
    This class takes the file "silviculture.sas" as input and generate a CSV
    from it.
    This information will be used to allocate the harvest across the spatial
    units and species.
    Thanks to this table, using the demand from an economic model,
    one can create a list of specific disturbances that include where
    to harvest and what species to harvest.
    """

    all_paths = """
    /orig/silviculture.csv
    """

    def __init__(self, parent):
        # Default attributes #
        self.parent = parent
        # Automatically access paths based on a string of many subpaths #
        self.paths = AutoPaths(self.parent.data_dir, self.all_paths)

    def __call__(self):
        pass

    @property_cached
    def df(self):
        """Load the CSV that is 'silviculture.csv'."""
        return pandas.read_csv(str(self.paths.csv))