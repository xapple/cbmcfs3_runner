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

# Internal modules #


###############################################################################
class PreProcessor(object):
    """
    Will modify the input CSV files before handing them to SIT.
    """

    all_paths = """
    /input/csv/disturbance_events.csv
    /input/csv/disturbance_events_filtered.csv
    """

    def __init__(self, parent):
        # Default attributes #
        self.parent  = parent
        self.country = parent.country
        # Directories #
        self.paths = AutoPaths(self.parent.data_dir, self.all_paths)

    def __call__(self):
        source = self.paths.disturbance_events
        destin = self.paths.disturbance_events_filtered
        self.filter_dist_events(source, destin)

    def filter_dist_events(self, old_path, new_path):
        """The calibration database is configured to run over a period of
         100 years. We would like to limit the simulation to the historical
         period. Currently Year < 2015.

         Filtering M types on Sort Type 6 is necessary to avoid the famous error:

            Error:  Illegal target type for RANDOM sort in timestep 3, action number 190,
                    in disturbance group 1, sort type 6, target type 2.
            Error:  Invalid disturbances found in .\input\disturb.lst.  Aborting.
         """
        # Load the original data frame #
        old_df = pandas.read_csv(str(old_path))
        # We make a copy because query() doesn't return a true new data frame #
        new_df = self.filter_df(old_df, self.country.base_year, self.country.inventory_start_year).copy()
        # Filtering M types #
        row_indexer = (new_df['sort_type'] == 6) & (new_df['measurement_type'] == 'M')
        new_df.loc[row_indexer, 'sort_type'] = 2
        # Write the result #
        new_df.to_csv(str(new_path), index=False)

    def filter_df(self, df, base_year, inv_start_year):
        """Takes the old event dataframe and returns the new filtered one."""
        # Filter rows based on years #
        period_max = base_year - inv_start_year + 1
        return df.query("step <= %s" % period_max)