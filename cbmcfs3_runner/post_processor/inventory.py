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

# First party modules #
from plumbing.cache import property_cached
from autopaths.auto_paths import AutoPaths

###############################################################################
# This value is in years and needs to be confimed with Scott
CBM_BIN_WIDTH = 20.0

# This value is in years and can be changed to adjust the precision of the discretisation
CBM_PRECISION = 0.01

def categorical_to_discrete(bin_center, bin_height, bin_width, precision):
    """This function is more or less the inverse of the pandas.cut method.
    Starting with binned data, we will assume a uniform distribution and
    transform it back to discrete data with a given precision.

    Given the center and width of a bin we will create a numpy vector
    with conservation of total mass (i.e. bin_height).

    We will check that we left bound cannot exceed zero.

    >>> categorical_to_discrete(4, 5, 6, 1)
    array([0., 0., 0., 5., 5.])
    >>> categorical_to_discrete(1, 6, 10, 1)
    array([1., 1., 1., 1., 1., 1.])
    """
    # Round to precision #
    bin_radius = bin_width / 2
    bin_radius = int(numpy.round(bin_radius / precision))
    bin_center = int(numpy.round(bin_center / precision))
    # Edges #
    bin_left   = bin_center - bin_radius
    bin_right  = bin_center + bin_radius
    # Check that the left edge is never negative #
    bin_left = max(bin_left, 0)
    # Build vector like this: 0,0,0,0,1,1,1,1,1,1,1,1 #
    vector = numpy.append(numpy.zeros(bin_left), numpy.ones(bin_right - bin_left))
    # Multiply by the matching height #
    vector *= bin_height / (bin_right - bin_left)
    # Check mass is conserved #
    numpy.testing.assert_allclose(vector.sum(),  bin_height)
    # Return #
    return vector

def apply_discretizer(row, key):
    """Given a row from our dataframe, return the discretized vector."""
    return categorical_to_discrete(row['AveAge'], row[key], CBM_BIN_WIDTH, CBM_PRECISION)

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

    @property_cached
    def grouped(self):
        """
        Group the simulated inventory data frame and collapse columns.
        """
        def aggregator(df):
            """The input df is a data frame with multiple rows and
            the grouping columns still present. One must return a
            series (i.e. only one row) with the grouping columns absent."""
            # Get the discretized version of all rows #
            all_vectors = df.apply(apply_discretizer, axis=1, key='Area')
            all_vectors = pandas.DataFrame(v for v in all_vectors).fillna(0.0)
            # Sum them up #
            final_vector = all_vectors.sum()
            # Return #
            return pandas.Series(dict(area_per_age=final_vector))
        # Columns we will keep #
        group_cols = ['TimeStep', 'forest_type']
        # Do it #
        df = (self.simulated
              .groupby(group_cols)
              .agg(aggregator)
              .reset_index())
        # Return #
        return df

###############################################################################
