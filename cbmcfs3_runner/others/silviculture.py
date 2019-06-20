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
    This class gives access to information contained in the file
    "silviculture.sas".
    This information will be used to allocate the harvest across the spatial
    units and species when creating disturbances.
    Thanks to these tables, using the demand from an economic model,
    one can create a list of specific disturbances that include where
    to harvest and what species to harvest at which year.
    """

    all_paths = """
    /orig/silv_treatments.csv
    /orig/harvest_corr_fact.csv
    /orig/harvest_prop_fact.csv
    """

    def __init__(self, parent):
        # Default attributes #
        self.parent = parent
        # Automatically access paths based on a string of many subpaths #
        self.paths = AutoPaths(self.parent.data_dir, self.all_paths)

    @property_cached
    def treatments(self):
        """Load the CSV that is 'silv_treatments.csv'."""
        return pandas.read_csv(str(self.paths.treatments))

    @property_cached
    def corr_fact(self):
        """Load the CSV that is 'harvest_corr_fact.csv'."""
        return pandas.read_csv(str(self.paths.corr_fact))

    @property_cached
    def harvest_prop_fact(self):
        """Load the CSV that is 'harvest_prop_fact.csv'."""
        return pandas.read_csv(str(self.paths.prop_fact))

