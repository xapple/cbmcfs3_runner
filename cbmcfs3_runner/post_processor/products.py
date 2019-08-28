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
import re

# First party modules #
from plumbing.cache import property_cached
from autopaths.auto_paths import AutoPaths

# Internal modules #

###############################################################################
class Products(object):
    """
    See notebook "xxxxxxxxxxx.ipynb" for more details about the methods below.
    """

    all_paths = """
    /output/products/
    """

    def __init__(self, parent):
        # Default attributes #
        self.parent = parent
        # Directories #
        self.paths = AutoPaths(self.parent.parent.data_dir, self.all_paths)

    #-------------------------------------------------------------------------#
    @property_cached
    def silviculture(self):
        """Prepare the silviculture treatments data frame
        for joining operations with harvest tables."""
        # Load file #
        df = self.parent.parent.country.silviculture.treatments
        # Rename classifiers from _1 to forest etc. #
        df = df.rename(columns = self.parent.classifiers_mapping)
        # Rename a column #
        df = df.rename(columns = {'Dist_Type_ID': 'DistTypeName'})
        # Change the type of DistTypeName to string so that it has the same type as
        # the `harvest_check` DistTypeName column
        df['DistTypeName'] = df['DistTypeName'].astype(str)
        # Change the type of management_strategy to string (for SI)
        df['management_strategy'] = df['management_strategy'].astype(str)
        # Return #
        return df

    #-------------------------------------------------------------------------#
    @property_cached
    def hwp_intermediate(self):
        """
        Intermediate table based on `post_processor.harvest.check`.
        Joins disturbance id from the silviculture table
        to allocate specific disturbances to specific wood products.
        """
        join_index = ['DistTypeName',
                      'forest_type',
                      'management_type',
                      'management_strategy']
        # Take only a few columns #
        silv = self.silviculture[join_index + ['HWP']]
        silv = silv.set_index(join_index)
        # Join #
        df = (self.parent.harvest.check
              .reset_index()
              .set_index(join_index)
              .join(silv))
        # We want the columns with NaNs to be thrown away
        # Because they represent disturbances that do not produce any harvest
        # Otherwise we would do: assert not df[join_index].isna().any().any()
        # Group #
        df = (df.groupby(['TimeStep', 'HWP'])
                .agg({'Vol_Merch':    'sum',
                      'Vol_SubMerch': 'sum',
                      'Vol_Snags':    'sum',
                      'TC':           'sum'})
                .reset_index())
        # Return #
        return df

    #-------------------------------------------------------------------------#
    @property_cached
    def irw_b(self):
        """Harvest volumes of Industrial Round Wood Broadleaves."""
        df = (self.hwp_intermediate
              .query('HWP == "IRW_B"')
              .rename(columns={'Vol_Merch':    'Vol_Merch_IRW_B',
                               'Vol_SubMerch': 'Vol_SubMerch_IRW_B',
                               'Vol_Snags':    'Vol_Snags_IRW_B',
                               'TC':           'TC_IRW_B'}))
        # Drop HWP column
        # because it doesn't make sense anymore below when we join different products together
        df = df.drop('HWP', axis = 1)
        return df

    #-------------------------------------------------------------------------#
    @property_cached
    def irw_c(self):
        """Harvest volumes of Industrial Round Wood Coniferous."""
        df = (self.hwp_intermediate
              .query('HWP == "IRW_C"')
              .rename(columns={'Vol_Merch':    'Vol_Merch_IRW_C',
                               'Vol_SubMerch': 'Vol_SubMerch_IRW_C',
                               'Vol_Snags':    'Vol_Snags_IRW_C',
                               'TC':           'TC_IRW_C'}))
        df = df.drop('HWP', axis = 1)
        return df

    #-------------------------------------------------------------------------#
    @property_cached
    def fw_b(self):
        """Harvest volumes of Fuel Wood Broadleaves."""
        df = (self.hwp_intermediate
              .query('HWP == "FW_B"')
              .rename(columns={'Vol_Merch':    'Vol_Merch_FW_B',
                               'Vol_SubMerch': 'Vol_SubMerch_FW_B',
                               'Vol_Snags':    'Vol_Snags_FW_B',
                               'TC':           'TC_FW_B'}))
        return df

    #-------------------------------------------------------------------------#
    @property_cached
    def fw_b_total(self):
        """
        Harvest volumes of Fuel Wood Broadleaves
        Join Industrial Round Wood co-products: 'Vol_SubMerch_IRW_B' and 'Vol_Snags_IRW_B'
        into the fuel wood total.
        """
        df = (self.fw_b
              .set_index('TimeStep')
              .join(self.irw_b.set_index(['TimeStep']))
              .reset_index())
        df['TOT_Vol_FW_B'] = sum([df.Vol_Merch_FW_B,
                                  df.Vol_SubMerch_FW_B,
                                  df.Vol_Snags_FW_B,
                                  df.Vol_SubMerch_IRW_B,
                                  df.Vol_Snags_IRW_B])
        df = df[['TimeStep',
                 'Vol_Merch_FW_B', 'Vol_SubMerch_FW_B', 'Vol_Snags_FW_B',
                 'Vol_SubMerch_IRW_B', 'Vol_Snags_IRW_B',
                 'TOT_Vol_FW_B']]
        return df

    #-------------------------------------------------------------------------#
    @property_cached
    def fw_c(self):
        """Harvest volumes of Fuel Wood Coniferous."""
        df = (self.hwp_intermediate
              .query('HWP == "FW_C"')
              .rename(columns={'Vol_Merch':    'Vol_Merch_FW_C',
                               'Vol_SubMerch': 'Vol_SubMerch_FW_C',
                               'Vol_Snags':    'Vol_Snags_FW_C',
                               'TC':           'TC_FW_C'}))
        return df

    #-------------------------------------------------------------------------#
    @property_cached
    def fw_c_total(self):
        """
        Harvest volumes of Fuel Wood Coniferous
        Join Industrial Round Wood co-products.
        """
        df = (self.fw_c
                  .set_index('TimeStep')
                  .join(self.irw_c.set_index(['TimeStep']))
                  .reset_index())
        df['TOT_Vol_FW_C'] = numpy.where(df['Vol_Merch_FW_C'] >= 0,
                                      sum([df.Vol_Merch_FW_C,
                                           df.Vol_SubMerch_FW_C,
                                           df.Vol_Snags_FW_C,
                                           df.Vol_SubMerch_IRW_C,
                                           df.Vol_Snags_IRW_C]),
                                      sum([df.Vol_SubMerch_IRW_C,
                                           df.Vol_Snags_IRW_C]))
        df = df[['TimeStep',
                 'Vol_Merch_FW_C','Vol_SubMerch_FW_C','Vol_Snags_FW_C',
                 'Vol_SubMerch_IRW_C','Vol_Snags_IRW_C',
                 'TOT_Vol_FW_C']]
        return df

    #-------------------------------------------------------------------------#
    @property_cached
    def hwp(self):
        """
        Volumes of Harvested Wood Products (HWP)
        Matching the product description available in the economic model
        and in the FAOSTAT historical data.

        Join "Vol_Merch" columns from "irw_b" and "irw_c"
        to the total columns from "fw_b_total" and "fw_c_total",
        using the time step as an index.
        """
        df = (self.irw_c
              .set_index('TimeStep')[['Vol_Merch_IRW_C']]
              .join(self.irw_b.set_index('TimeStep')[['Vol_Merch_IRW_B']])
              .join(self.fw_c_total.set_index('TimeStep')[['TOT_Vol_FW_C']])
              .join(self.fw_b_total.set_index('TimeStep')[['TOT_Vol_FW_B']])
              .reset_index())
        # Add year
        df['year'] = self.parent.parent.country.timestep_to_years(df['TimeStep'])
        # Rename columns to standard IRW and FW product names
        df.rename(columns=lambda x: re.sub(r'Vol_Merch_|TOT_Vol_',r'', x))
        return df