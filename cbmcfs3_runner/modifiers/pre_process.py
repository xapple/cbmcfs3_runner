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
    /input/csv/disturbance_types.csv
    /input/csv/disturbance_types_extended.csv
    """

    def __init__(self, parent):
        # Default attributes #
        self.parent  = parent
        self.country = parent.country
        # Directories #
        self.paths = AutoPaths(self.parent.data_dir, self.all_paths)

    def __call__(self):
        # Disturbance events #
        source = self.paths.disturbance_events
        destin = self.paths.disturbance_events_filtered
        self.filter_dist_events(source, destin)
        # Disturbance types #
        source = self.paths.disturbance_types
        destin = self.paths.disturbance_types_extended
        self.extend_dist_types(source, destin)

    #------------------------- Disturbance events ----------------------------#
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
        """Takes the old event data frame and returns the new filtered one."""
        # Filter rows based on years #
        period_max = base_year - inv_start_year + 1
        return df.query("step <= %s" % period_max)

    #------------------------- Disturbance types -----------------------------#
    def extend_dist_types(self, old_path, new_path):
        """
        This method takes the file "disturbance_types.csv" and
        modifies it, by duplicating some entries with a new ID.
        Saving the result under "disturbance_types_extended.csv".
        Why do we have to do this? Because of some arcane CBM-CFS3
        requirements.
        """
        # Convenience shortcut #
        col_name = 'disturbance_type_id'
        # Parse #
        orig = pandas.read_csv(str(old_path))
        # Make into a string and index it #
        orig[col_name] = orig[col_name].astype(str)
        orig = orig.set_index(col_name)
        # Get disturbances to duplicate from silv #
        silv        = self.country.silviculture.treatments
        dist_to_dup = silv.query("man_nat == 'Man'")['dist_type_id'].unique()
        # Make a new data frame #
        dists = [orig.loc[dist][0] for dist in dist_to_dup]
        dup   = pandas.DataFrame(zip(dist_to_dup, dists), columns=[col_name, 'name'])
        # Add large numerical suffix #
        dup[col_name] = dup[col_name].apply(lambda x: '999' + x)
        # Add 'Future' #
        pass
        # Put the two data frames together #
        orig = orig.reset_index()
        orig = pandas.concat([orig, dup])
        # Write back to disk #
        orig.to_csv(str(new_path), index=False)

