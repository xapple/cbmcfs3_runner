#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Written by Lucas Sinclair and Paul Rougieux.

JRC biomass Project.
Unit D1 Bioeconomy.
"""

# Built-in modules #

# Third party modules #

# First party modules #
from autopaths.auto_paths import AutoPaths
from plumbing.cache       import property_cached

# Internal modules #
from cbmcfs3_runner.pre_processor.dist_filter import DisturbanceFilter
from cbmcfs3_runner.pre_processor.dist_maker  import DisturbanceMaker

###############################################################################
class PreProcessor(object):
    """
    Will modify a copy of the orig CSV files before handing them to SIT.
    """

    all_paths = """
    /input/csv/ageclass.csv
    /input/csv/inventory.csv
    /input/csv/classifiers.csv
    /input/csv/disturbance_events.csv
    /input/csv/disturbance_types.csv
    /input/csv/transition_rules.csv
    /input/csv/yields.csv
    /input/csv/historical_yields.csv
    """

    # Default case #
    unchanged = ['ageclass', 'inventory', 'classifiers', 'types',
                 'yields', 'historical_yields']

    def __init__(self, parent):
        # Default attributes #
        self.parent  = parent
        self.country = parent.country
        # Directories #
        self.paths = AutoPaths(self.parent.data_dir, self.all_paths)
        # These attributes might be overwritten by scenarios #
        self.disturbance_events = self.events_static_demand

    def __call__(self):
        """Write every CSV to the input directory after changing them."""
        # Some files don't change so take them straight from orig_data #
        for file in self.unchanged:
            self.parent.country.orig_data.paths[file].copy(self.paths[file])
        # Other files are special and need changing #
        # Generate disturbances (dynamic function) and write those #
        dist = self.disturbance_events()
        dist.to_csv(str(self.paths.events), index=False)
        # Rename columns of the transition rules 
        # To prevent a SIT error on import 
        # Unhandled Exception: System.Data.DuplicateNameException:
        #    A column named '_1' already belongs to this DataTable.
        transition = self.parent.country.orig_data.transition_rules
        transition.to_csv(str(self.paths.transition), index=False)

    #--------------------------- Different events ----------------------------#
    def events_hist(self):
        """Only historical disturbances."""
        return self.disturbance_filter.df

    def events_static_demand(self):
        """Static demand disturbances."""
        return self.disturbance_maker.df

    def events_auto_allocation(self):
        """Auto allocation disturbances."""
        return self.disturbance_maker.df_auto_allocation

    #----------------------------- Properties --------------------------------#
    @property_cached
    def disturbance_maker(self):
        """All information for making new disturbance events."""
        return DisturbanceMaker(self)

    @property_cached
    def disturbance_filter(self):
        """Filter existing disturbance events."""
        return DisturbanceFilter(self)


