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
from plumbing.cache       import property_cached

# Internal modules #
from cbmcfs3_runner.pre_processor.dist_filter import DisturbanceFilter
from cbmcfs3_runner.disturbances.maker        import DisturbanceMaker

###############################################################################
class PreProcessor(object):
    """
    Will modify a copy of the orig CSV files before handing them to SIT.
    """

    all_paths = """
    /csv/ageclass.csv
    /csv/inventory.csv
    /csv/classifiers.csv
    /csv/disturbance_events.csv
    /csv/disturbance_types.csv
    /csv/transition_rules.csv
    /csv/yields.csv
    /csv/historical_yields.csv
    """

    # Default case #
    unchanged = ['ageclass', 'inventory', 'classifiers', 'types',
                 'transition_rules', 'yields', 'historical_yields']

    # This can easily be changed by a scenario #
    use_dist_maker = True

    def __init__(self, parent):
        # Default attributes #
        self.parent  = parent
        self.country = parent.country
        # Directories #
        self.paths = AutoPaths(self.parent.data_dir, self.all_paths)

    def __call__(self):
        """Write every CSV to the input directory after changing them."""
        # Some are changed #
        self.disturbances_events.to_csv(str(self.paths.events))
        # Other files don't change so take them straight from orig_data #
        for file in self.unchanged:
            self.parent.country.orig_data.paths[file].copy(self.paths[file])

    @property_cached
    def disturbance_filter(self):
        # Filter existing disturbance events #
        return DisturbanceFilter(self)

    @property_cached
    def disturbance_maker(self):
        # Make new disturbance events #
        return DisturbanceMaker(self)

    @property_cached
    def disturbances_events(self):
        if self.use_dist_maker:  return self.disturbance_maker.df
        else:                    return self.disturbance_filter.df
