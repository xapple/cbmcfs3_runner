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

    #-------------------------------------------------------------------------#
    @property_cached
    def bef_ft(self):
        """
        Stands for "Biomass Expansion Factor, by Forest Type", we think.
        This is translated from an SQL query authored by RP.
        It calculates merchantable biomass.
        """
        # Load tables #
        pool  = self.parent.database["tblPoolIndicators"].set_index('UserDefdClassSetID')
        clifr = self.parent.classifiers
        # Join #
        df = pool.join(clifr, on="UserDefdClassSetID")
        # Sum for everyone #
        cols_sum = {'SW_Merch'  : 'sum',
                    'SW_Foliage': 'sum',
                    'SW_Other'  : 'sum',
                    'HW_Merch'  : 'sum',
                    'HW_Foliage': 'sum',
                    'HW_Other'  : 'sum',
                    'SW_Coarse' : 'sum',
                    'SW_Fine'   : 'sum',
                    'HW_Coarse' : 'sum',
                    'HW_Fine'   : 'sum'}
        # Group and aggregate #
        df = df.groupby("forest_type").agg(cols_sum).reset_index()
        # Make new columns #
        df['Tot_Merch']  = df.SW_Merch   + df.HW_Merch
        df['Tot_ABG']    = df.SW_Merch   + df.HW_Merch   + \
                           df.SW_Foliage + df.HW_Foliage + \
                           df.HW_Other   + df.SW_Other
        df['BG_Biomass'] = df.SW_Coarse  + df.SW_Fine    + \
                           df.HW_Coarse  + df.HW_Fine
        df['BEF_Tot']    = (df.Tot_ABG   + df.BG_Biomass) / df.Tot_ABG
        # Return result #
        return df

    #-------------------------------------------------------------------------#
    @property_cached
    def simulated(self):
        """
        Update the inventory based on the simulation output contained in
        table 'tblPoolIndicators'.

        Columns of the output are:

            ['status', 'forest_type', 'region', 'management_type',
             'management_strategy', 'climatic_unit', 'conifers_bradleaves', 'AveAge',
             'TimeStep', 'Area', 'Biomass', 'BEF_Tot', 'db', 'Merch_C_ha',
             'Merch_Vol_ha']
        """
        # Load table #
        age_indicators = self.parent.database["tblAgeIndicators"]
        classifr_coefs = self.parent.classifiers_coefs
        # Set the same index #
        age_indicators = age_indicators.set_index('UserDefdClassSetID')
        classifr_coefs = classifr_coefs.set_index('UserDefdClassSetID')
        # Double join #
        df = (age_indicators
               .join(classifr_coefs)
               .reset_index()
               .set_index('forest_type')
               .join(self.bef_ft.set_index('forest_type'))
               .reset_index())
        # Select only some columns #
        columns_of_interest  = ['AveAge', 'TimeStep', 'Area', 'Biomass', 'BEF_Tot','db']
        columns_of_interest += list(self.parent.classifiers.columns)
        df = df[columns_of_interest].copy()
        # Divide #
        df['Merch_C_ha']   = df.Biomass    / df.BEF_Tot
        df['Merch_Vol_ha'] = df.Merch_C_ha / df.db
        # Return result #
        return df

    #-------------------------------------------------------------------------#
    @property_cached
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
        # Columns we will keep and group on #
        self.group_cols = ['TimeStep', 'forest_type']
        # Column we will keep and sum on #
        self.sum_col = 'Area'
        # Column we will use for the summing #
        self.bin_col = 'AveAge'
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
            bin_width = 20.0
            current = binner(row[self.sum_col], self.sum_col, bin_width)
            # Keep the current values of the group columns as an index #
            col_values = [row[col] for col in self.group_cols]
            current = current.assign(**dict(zip(self.group_cols, col_values)))
            current = current.set_index(self.group_cols)
            # Append #
            result = result.append(current)
        # Return #
        return result

    #-------------------------------------------------------------------------#
    def check_conservation(self, tolerance=0.005):
        """Assert that total area of forest is conserved."""
        # Compute #
        df1 = self.simulated
        df2 = self.grouped_bins
        all_close = numpy.testing.assert_allclose
        # Check #
        all_close(df1[self.sum_col].sum(), df2[self.sum_col].sum(), rtol=tolerance)
