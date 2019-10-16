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
class DisturbanceTypesMod(object):
    """
    Lorem ipsum.
    """

    all_paths = """
    /input/csv/disturbance_types.csv
    /input/csv/disturbance_types_extended.csv
    """

    def __call__(self):
        # Disturbance types #
        # Unsure this is actually needed. Related to renaming of dist ids.
        source = self.paths.disturbance_types
        destin = self.paths.disturbance_types_extended
        self.extend_dist_types(source, destin)

    #------------------------- Disturbance types -----------------------------#
    def extend_dist_types(self, old_path, new_path):
        """
        This method takes the file "disturbance_types.csv" and
        modifies it, by duplicating some entries with a new ID.
        Saving the result under "disturbance_types_extended.csv".
        Why do we have to do this? Because of some arcane CBM-CFS3
        requirements.
        CBM-CFS3 accepts only one measurement type per disturbance.
        We want to express historical disturbances in terms of area and
        future disturbances in terms of biomass.
        Future disturbances won't be applied by CBM if we don't
        change their id.
        See https://webgate.ec.europa.eu/CITnet/jira/browse/BIOECONOMY-228
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
        dist_to_dup = silv.query("man_nat == 'Man'")['dist_type_name'].unique()
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

