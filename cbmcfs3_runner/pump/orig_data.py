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
class OrigData(object):
    """
    This class will provide access to the original data of a `Country`
    as a pandas data frame. Not the input data of a Runner.
    """

    all_paths = """
    /export/ageclass.csv
    /export/inventory.csv
    /export/classifiers.csv
    /export/disturbance_events.csv
    /export/disturbance_types.csv
    /export/transition_rules.csv
    /export/yields.csv
    /export/historical_yields.csv
    """

    def __init__(self, parent):
        # Default attributes #
        self.parent = parent
        # Directories #
        self.paths = AutoPaths(self.parent.data_dir, self.all_paths)

    def __getitem__(self, item):
        return pandas.read_csv(str(self.paths[item]))

    #-------------------------- Inventory ------------------------------#
    @property_cached
    def inventory(self):
        """
        Inventory data loaded from the original calibration db through a csv file.
        Columns are:

            ['status', 'forest_type', 'region', 'management_type',
             'management_strategy', 'climatic_unit', 'conifers_broadleaves',
             'using_id', 'age', 'area', 'delay', 'unfcccl', 'hist_dist', 'last_dist',
             'age_class'],
        """
        # Load #
        df = self['inventory']
        # Create the age_class column so it can be
        # used as a join variable with a yields table
        df['age_class'] = (df['age']
                           .replace('AGEID', '', regex=True)
                           .astype('int'))
        # But this is only true where an age class is defined
        df['age_class'] = df['age_class'].mask(~df['using_id'])
        # Rename classifiers #
        df = df.rename(columns = self.parent.classifiers.mapping)
        # Return #
        return df

    #-------------------------- Yields ------------------------------#
    @property_cached
    def yields(self):
        """
        Columns are:

        ['_1', '_2', '_3', '_4', '_5', '_6', '_7', 'sp', 'Vol0', 'Vol1', 'Vol2',
         'Vol3', 'Vol4', 'Vol5', 'Vol6', 'Vol7', 'Vol8', 'Vol9', 'Vol10',
         'Vol11', 'Vol12', 'Vol13', 'Vol14', 'Vol15', 'Vol16', 'Vol17', 'Vol18',
         'Vol19', 'Vol20', 'Vol21', 'Vol22', 'Vol23', 'Vol24', 'Vol25', 'Vol26',
         'Vol27', 'Vol28', 'Vol29', 'Vol30']
        """
        # Load #
        df = self['yields']
        # Rename classifiers #
        df = df.rename(columns = self.parent.classifiers.mapping)
        # Return #
        return df

    @property_cached
    def historical_yields(self):
        """Historical yield taken from the original CSV file."""
        # Load #
        df = self['historical_yields']
        # Rename classifiers #
        df = df.rename(columns = self.parent.classifiers.mapping)
        # Return #
        return df

    def reshape_yields_long(self, yields_wide):
        """
        Reshape a wide data frame into a long one.

        Columns are:

        ['status', 'forest_type', 'region', 'management_type',
         'management_strategy', 'climatic_unit', 'conifers_broadleaves', 'sp',
         'age_class', 'volume']
         """
        # Index #
        index = ['status', 'forest_type', 'region', 'management_type',
                 'management_strategy', 'climatic_unit', 'conifers_broadleaves',
                 'sp']
        # Add classifier 8 for the specific case of Bulgaria #
        if 'yield_tables' in yields_wide.columns: index += ['yield_tables']
        # Melt #
        df = yields_wide.melt(id_vars    = index,
                              var_name   = "age_class",
                              value_name = "volume")
        # Remove suffixes and keep just the number #
        df['age_class'] = df['age_class'].str.lstrip("vol").astype('int')
        # Return #
        return df

    @property_cached
    def yields_long(self):
        return self.reshape_yields_long(self.yields)

    @property_cached
    def historical_yields_long(self):
        return self.reshape_yields_long(self.historical_yields)

    #-------------------------- Disturbances ------------------------------#
    @property_cached
    def disturbance_types(self):
        """
        Load disturbance types from the calibration database.
        Change dist_type_name to a string.
        """
        # Load #
        df = self['disturbance_types']
        # Cast to string #
        df['dist_type_name'] = df['dist_type_name'].astype('str')
        # Return #
        return df

    @property_cached
    def disturbance_events(self):
        """
        Same as below but add the year column.
        """
        # Load #
        df = self.disturbance_events_raw
        # Add year #
        df['year'] = self.parent.timestep_to_year(df['step'])
        # Return #
        return df

    @property_cached
    def disturbance_events_raw(self):
        """
        Load disturbance_events from the calibration database.
        Change dist_type_name to a string and step to an integer.
        """
        # Load #
        df = self['disturbance_events']
        # Change dist_type_name to a string to harmonize data types #
        df['dist_type_name'] = df['dist_type_name'].astype('str')
        # Make step an integer #
        df['step'] = df['step'].astype(int)
        # Rename classifiers #
        df = df.rename(columns = self.parent.classifiers.mapping)
        # Return #
        return df


    @property_cached
    def transition_rules(self):
        """
        Load transition_rules from the calibration database.
        Change dist_type_name to a string.

        Transition rules describe the transition between one particular set
        of classifiers and another set of classifiers. They are used for example
        for afforestation to move land area from status 'NF' non forested
        to status 'For' (or 'CC') forested.

        Note on column renaming:
        The transition rules table contains duplicated column names.
        By default pandas leaves the columns that appear first as-is:
            ['_1', '_2', '_3', '_4', '_5', '_6', '_7']
        and renames the duplicated columns that way:
            ['_1.1', '_2.1', '_3.1', '_4.1', '_5.1', '_6.1', '_7.1']
        """
        # Load #
        df = self['transition_rules']
        # Change dist_type_name to a string to harmonize data types #
        df['dist_type_name'] = df['dist_type_name'].astype('str')
        # Rename classifiers #
        # This will only rename the first incoming classifiers columns.
        # The outgoing classifiers '_1.1', '_2.1', ... will remain unchanged.
        df = df.rename(columns = self.parent.classifiers.mapping)
        # Return #
        return df
