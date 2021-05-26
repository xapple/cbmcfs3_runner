#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Written by Lucas Sinclair and Paul Rougieux.

JRC biomass Project.
Unit D1 Bioeconomy.
"""

# Built-in modules #

# Third party modules #
import pandas, numpy

# Internal modules #
from .bin_discretizer import aggregator, binner

# First party modules #
from plumbing.cache import property_cached
from autopaths.auto_paths import AutoPaths

###############################################################################
class Inventory(object):
    """
    See notebook "simulated_inventory.ipynb" for more details.
    """

    all_paths = """
    /output/inventory/
    """

    def __init__(self, parent):
        # Default attributes #
        self.parent = parent
        # Directories #
        self.paths = AutoPaths(self.parent.parent.data_dir, self.all_paths)
        # Shortcut #
        self.country = self.parent.parent.country

    #-------------------------------------------------------------------------#
    @property_cached
    def age_indicators(self):
        """
        CBM output table containing the forest area by age class.

        Interesting values:
            * Classifiers.
            * 'ave_age' the average age of a stand.
            * 'area' the area in hectares.
            * 'biomass' in **tons of carbon per hectare**, includes above
            and below ground biomass.

        Columns of the data frame:
            ['user_defd_class_set_id', 'age_ind_id', 'time_step', 'spuid',
             'age_class_id', 'land_class_id', 'kf2', 'kf3', 'kf4', 'kf5', 'kf6',
             'area', 'biomass', 'dom', 'ave_age', 'forest_type', 'status', 'region',
             'management_type', 'management_strategy', 'climatic_unit',
             'conifers_broadleaves', 'id', 'density', 'harvest_gr']
        """
        # Load table #
        age_indicators = self.parent.database["tblAgeIndicators"]
        classifr_coefs = self.parent.classifiers_coefs
        # Join
        df = (age_indicators
              .left_join(classifr_coefs, on='user_defd_class_set_id')
              )
        # Place classifiers first
        df = df.set_index(self.parent.classifiers_names).reset_index()
        return df

    #-------------------------------------------------------------------------#
    @property_cached
    def bef_ft(self):
        """
        Stands for "Biomass Expansion Factor, by Forest Type", we think.
        This is translated from an SQL query authored by RP.
        It calculates the ratio of
        (total above and below ground biomass) / total above ground biomass.

        TODO: replace sums by a reshape in long format and the use of
        grouping variables.
        """
        # Join #
        df = self.parent.pool_indicators
        # Sum for everyone #
        cols_sum = {'sw_merch'  : 'sum',
                    'sw_foliage': 'sum',
                    'sw_other'  : 'sum',
                    'hw_merch'  : 'sum',
                    'hw_foliage': 'sum',
                    'hw_other'  : 'sum',
                    'sw_coarse' : 'sum',
                    'sw_fine'   : 'sum',
                    'hw_coarse' : 'sum',
                    'hw_fine'   : 'sum'}
        # Group and aggregate #
        df = df.groupby("forest_type").agg(cols_sum).reset_index()
        # Make new columns #
        df['tot_merch']  = df.sw_merch   + df.hw_merch
        df['tot_abg']    = df.sw_merch   + df.hw_merch   + \
                           df.sw_foliage + df.hw_foliage + \
                           df.hw_other   + df.sw_other
        df['bg_biomass'] = df.sw_coarse  + df.sw_fine    + \
                           df.hw_coarse  + df.hw_fine
        # Calculate the biomass expansion factor
        # Ratio of (total above and below ground) / total above ground
        df['bef_tot']    = (df.tot_abg   + df.bg_biomass) / df.tot_abg
        # Return #
        return df

    #-------------------------------------------------------------------------#
    @property_cached
    def simulated(self):
        """
        Update the inventory based on the simulation output contained in
        table 'tblPoolIndicators'.

        Columns of the output are:

            ['status', 'forest_type', 'region', 'management_type',
             'management_strategy', 'climatic_unit', 'conifers_broadleaves', 'ave_age',
             'time_step', 'area', 'biomass', 'bef_tot', 'db', 'merch_c_ha',
             'Merch_Vol_ha']
        """
        # Join #
        df = self.age_indicators.left_join(self.bef_ft, on='forest_type')
        # Select only some columns #
        columns_of_interest  = ['ave_age', 'time_step', 'area', 'biomass', 'bef_tot', 'density']
        columns_of_interest += list(self.parent.classifiers.columns)
        # Drop the other columns #
        df = df[columns_of_interest].copy()
        # Divide biomass by the expansion factor #
        df['merch_c_ha']   = df['biomass']    / df['bef_tot']
        df['merch_vol_ha'] = df['merch_c_ha'] / df['density']
        # Return #
        return df

    #-------------------------------------------------------------------------#
    # Columns we will keep and group on #
    group_cols = ['time_step', 'forest_type']
    # Column we will keep and sum on #
    sum_col = 'area'
    # Column we will use for the summing, this will never change #
    bin_col = 'ave_age'
    # The bin width we will use when recreating bins #
    bin_width = 20.0

    @property
    def grouped_vectors(self):
        """
        Group the simulated inventory data frame and collapse columns
        by vectorizing according to the AveAge.

        The dataframe will look like this:

                 TimeStep forest_type                           Area
            0           0          DF  [0.0, 5.0, 0.0, 0.0, 8.0, ...
            1           0          FS  [0.0, 6.0, 0.0, 0.0, 7.0, ...
            2           0          OB  [0.0, 0.2, 4.0, 0.0, 6.0, ...
            3           0          OC  [0.0, 0.2, 0.0, 0.0, 5.0, ...
            4           0          PA  [0.0, 0.2, 0.0, 0.0, 4.0, ...
            5           0          QR  [0.0, 0.2, 0.0, 0.0, 0.0, ...
            6           1          DF  [0.0, 0.0, 0.3, 0.0, 0.0, ...
            7           1          FS  [1.0, 1.0, 2.3, 0.0, 3.0, ...
            8           1          OB  [1.0, 0.0, 0.3, 0.0, 0.0, ...
            9           1          OC  [1.0, 0.0, 0.3, 0.0, 0.0, ...
            ...         ...        ... ...
        """
        # Group #
        grouped = self.simulated.groupby(self.group_cols)
        # Iterate #
        result = []
        for col_values, df in grouped:
            # Keep the current values of the group columns #
            current = dict(zip(self.group_cols, col_values))
            # Compute a discrete numpy vector #
            current[self.sum_col] = aggregator(df, self.sum_col, self.bin_col)
            # Make a series and append #
            result.append(pandas.Series(current))
        # Put all series into a data frame #
        result = pandas.DataFrame(result)
        # Return #
        return result

    #-------------------------------------------------------------------------#
    @property_cached
    def grouped_bins(self):
        """Using the vectorized version, recreate bins and average values.

         The data frame will look like this:

                                      age_start  age_end         Area
                TimeStep forest_type
                0        DF                 0.0     20.0   792.530945
                         DF                20.0     40.0   663.677941
                         DF                40.0     60.0   618.225475
                         DF                60.0     80.0   524.963490
                         FS                 0.0     20.0  1390.616846
                         FS                20.0     40.0  1549.103840
                         FS                40.0     60.0   979.168979
                ...     ...                 ...      ...          ...
        """
        # Load the vector version #
        df = self.grouped_vectors
        # Empty data frame to contain result #
        result  = pandas.DataFrame()
        # Iterate #
        for i, row in df.iterrows():
            # Compute a data frame containing the recreated bins #
            current = binner(row[self.sum_col], self.sum_col, self.bin_width)
            # Keep the current values of the group columns as an index #
            col_values = [row[col] for col in self.group_cols]
            current = current.assign(**dict(zip(self.group_cols, col_values)))
            current = current.set_index(self.group_cols)
            # Append #
            result = result.append(current)
        # Return #
        return result

    #-------------------------------------------------------------------------#
    def check_conservation(self):
        """Assert that total area of forest is conserved after
        successive steps of discretization and rebinning."""
        # Compute #
        df1 = self.simulated
        df2 = self.grouped_bins
        all_close = numpy.testing.assert_allclose
        # Check #
        all_close(df1[self.sum_col].sum(), df2[self.sum_col].sum())

    #-------------------------------------------------------------------------#
    @property_cached
    def bins_per_year(self):
        """Same as grouped_bins but with the TimeStep swtiched to years.
        The four important class attributes are:
            * group_cols, sum_col, bin_col, bin_width
        Adapting these variables will modify the behavior of this final data frame.
        """
        # Load the vector version #
        df = self.grouped_bins.reset_index()
        # Add year and remove TimeStep #
        df['year'] = self.country.timestep_to_year(df['time_step'])
        df = df.drop('time_step', axis=1)
        # Only if we are in the calibration scenario #
        if self.parent.parent.scenario.short_name == 'calibration':
            # Patch the harvest data frame to stop at the simulation year #
            selector = df['year'] <= self.parent.parent.country.base_year
            df = df.loc[selector].copy()
        # Return #
        return df

    #-------------------------------------------------------------------------#
    @property_cached
    def sum_merch_stock(self):
        """
        Total biomass *stock* in tons of carbon directly from the
        pool indicators table distinguished by forest type.
        Also contains the volume in cubic meters over bark.

        It's an indication of the overall evolution of the growing stock
        (not yet disturbed). This is useful for making a high level check avoiding
        intermediate queries which could be sources of errors.

        Columns are: ['year', 'forest_type', 'conifers_broadleaves', 'mass']
        """
        # Load data #
        df    = self.parent.database['tblPoolIndicators']
        clifr = self.parent.classifiers.set_index("user_defd_class_set_id")
        # Our index #
        index = ['time_step', 'forest_type', 'conifers_broadleaves']
        # Join #
        df = (df
              .set_index('user_defd_class_set_id')
              .join(clifr)
              .groupby(index)
              .agg({'hw_merch': 'sum',
                    'sw_merch': 'sum'})
              .reset_index())
        # Add year and remove TimeStep #
        df['year'] = self.country.timestep_to_year(df['time_step'])
        df = df.drop('time_step', axis=1)
        # Check for mixed species that would produce both hard and soft #
        import warnings
        for i, row in df.iterrows():
            if row['hw_merch'] > 0.0 and row['sw_merch'] > 0.0:
                warnings.warn("There is a mixed species at row %i.\n%s" % (i,row))
        df['mass'] = df['hw_merch'] + df['sw_merch']
        # calculate the volume in cubic meters over bark #
        # join density
        df = df.left_join(self.country.coefficients, 'forest_type')
        df['volume'] = df['mass'] / df['density']
        # Only if we are in the calibration scenario #
        if self.parent.parent.scenario.short_name == 'calibration':
            # Patch the harvest data frame to stop at the simulation year #
            selector = df['year'] <= self.country.base_year
            df = df.loc[selector].copy()
        # Return #
        return df
    
# addedd 18/05/2021   
    @property_cached
    def sum_agb_stock(self):
        # Load data #
        df    = self.parent.database['tblPoolIndicators']
        clifr = self.parent.classifiers.set_index("user_defd_class_set_id")
        # Our index #
        index = ['time_step', 'forest_type', 'conifers_broadleaves']
        # Join #
        df = (df
              .set_index('user_defd_class_set_id')
              .join(clifr)
              .groupby(index)
              .agg({'hw_merch': 'sum',
                    'sw_merch': 'sum',
                    'hw_other': 'sum',
                    'sw_other': 'sum',
                    'hw_foliage': 'sum',
                    'sw_foliage': 'sum'})
              .reset_index())
        # Add year and remove TimeStep #
        df['year'] = self.country.timestep_to_year(df['time_step'])
        df = df.drop('time_step', axis=1)
        # Check for mixed species that would produce both hard and soft #
        import warnings
        for i, row in df.iterrows():
            if row['hw_merch'] > 0.0 and row['sw_merch'] > 0.0:
                warnings.warn("There is a mixed species at row %i.\n%s" % (i,row))
        df['mass'] = df['hw_merch'] + df['sw_merch']+df['hw_other'] + df['sw_other']+df['hw_foliage'] + df['sw_foliage']
        # calculate the volume in cubic meters over bark #
        # join density
        #df = df.left_join(self.country.coefficients, 'forest_type')
        #df['volume'] = df['mass'] / df['density']
        # Only if we are in the calibration scenario #
        if self.parent.parent.scenario.short_name == 'calibration':
            # Patch the harvest data frame to stop at the simulation year #
            selector = df['year'] <= self.country.base_year
            df = df.loc[selector].copy()
        # Return #
        return df