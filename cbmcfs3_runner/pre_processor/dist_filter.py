#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Written by Lucas Sinclair and Paul Rougieux.

JRC biomass Project.
Unit D1 Bioeconomy.
"""

# Built-in modules #

# Third party modules #
import numpy
import pandas

# First party modules #
from autopaths.auto_paths import AutoPaths
from plumbing.cache import property_cached

# Internal modules #

###############################################################################
class DisturbanceFilter(object):
    """
    Will remove some disturbances according to a condition.
    """

    def __init__(self, parent):
        # Default attributes #
        self.parent  = parent
        self.runner  = parent.parent
        self.country = parent.parent.country

    @property_cached
    def df(self):
        """The calibration database is configured to run over a period of
         100 years. We would like to limit the simulation to the historical
         period. Currently Year < 2015.

         Filtering M types on Sort Type 6 is necessary to avoid the famous error:

            Error:  Illegal target type for RANDOM sort in timestep 3, action number 190,
                    in disturbance group 1, sort type 6, target type 2.
            Error:  Invalid disturbances found in .\\input\\disturb.lst.  Aborting.
         """
        # Load the original data frame #
        df = self.country.orig_data.disturbance_events_raw
        # Filter rows based on years #
        base_year      = self.country.base_year
        inv_start_year = self.country.inventory_start_year
        period_max     = base_year - inv_start_year + 1
        df = df.query("step <= %s" % period_max)
        # Filtering M types #
        row_indexer = (df['sort_type'] == 6) & (df['measurement_type'] == 'M')
        df = df.loc[row_indexer, 'sort_type']
        # Return #
        return df