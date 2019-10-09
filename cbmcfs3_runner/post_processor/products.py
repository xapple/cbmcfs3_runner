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
from cbmcfs3_runner.pump.common import outer_join

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
        df = df.rename(columns = {'dist_type_name': 'dist_type_name'})
        # Change the type of dist_type_name to string so that it has the same type as
        # the `harvest_check` dist_type_name column
        df['dist_type_name'] = df['dist_type_name'].astype(str)
        # Change the type of management_strategy to string (for SI)
        df['management_strategy'] = df['management_strategy'].astype(str)
        # Return #
        return df

    #-------------------------------------------------------------------------#
    @property_cached
    def hwp_intermediate(self):
        """
        Intermediate table based on `post_processor.harvest.check`.
        Joins disturbance id from the silviculture table.
        to allocate specific disturbances to specific wood products.
        TODO: make this work for historical disturbances as well.
        'hwp' rows that have a Na value represent either:
          1. disturbances of type natural processes that do not produce
             any harvest
          2. historical disturbances that have a difference disturbance id
             and are therefore not available in the silviculture table.
        """
        join_index = ['dist_type_name',
                      'forest_type',
                      'management_type',
                      'management_strategy']
        # Take only a few columns #
        silv = self.silviculture[join_index + ['hwp']]
        silv = silv.set_index(join_index)
        # Join #
        df = (self.parent.harvest.check
              .reset_index()
              .set_index(join_index)
              .join(silv))
        # 'hwp' rows with NaNs will be thrown away by the aggregation below
        # Otherwise to prevent any rows to be NA,
        # i.e. to force all rows to have a value,
        # we would do: assert not df[join_index].isna().any().any()
        # Group #
        df = (df.groupby(['time_step', 'hwp'])
                .agg({'vol_merch':     'sum',
                      'vol_sub_merch': 'sum',
                      'vol_snags':     'sum',
                      'tc':            'sum'})
                .reset_index())
        # Return #
        return df

    #-------------------------------------------------------------------------#
    @property_cached
    def irw_b(self):
        """Harvest volumes of Industrial Round Wood Broadleaves."""
        df = (self.hwp_intermediate
              .query('hwp == "irw_b"')
              .rename(columns={'vol_merch':     'vol_merch_irw_b',
                               'vol_sub_merch': 'vol_sub_merch_irw_b',
                               'vol_snags':     'vol_snags_irw_b',
                               'tc':            'tc_irw_b'}))
        # Drop HWP column
        # because it doesn't make sense anymore below when we join different products together
        df = df.drop('hwp', axis = 1)
        return df

    #-------------------------------------------------------------------------#
    @property_cached
    def irw_c(self):
        """Harvest volumes of Industrial Round Wood Coniferous."""
        df = (self.hwp_intermediate
              .query('hwp == "irw_c"')
              .rename(columns={'vol_merch':     'vol_merch_irw_c',
                               'vol_sub_merch': 'vol_sub_merch_irw_c',
                               'vol_snags':     'vol_snags_irw_c',
                               'tc':            'tc_irw_c'}))
        df = df.drop('hwp', axis = 1)
        return df

    #-------------------------------------------------------------------------#
    @property_cached
    def fw_b(self):
        """Harvest volumes of Fuel Wood Broadleaves."""
        df = (self.hwp_intermediate
              .query('hwp == "fw_b"')
              .rename(columns={'vol_merch':     'vol_merch_fw_b',
                               'vol_sub_merch': 'vol_sub_merch_fw_b',
                               'vol_snags':     'vol_snags_fw_b',
                               'tc':            'tc_fw_b'}))
        return df

    #-------------------------------------------------------------------------#
    @property_cached
    def fw_b_total(self):
        """
        Harvest volumes of Fuel Wood Broadleaves
        Join Industrial Round Wood co-products: 'vol_sub_merch_irw_b' and 'vol_snags_irw_b'
        into the fuel wood total.
        """
        df = outer_join(self.irw_b, self.fw_b, 'time_step')
        df['tot_vol_fw_b'] = sum([df['vol_merch_fw_b'],
                                  df['vol_sub_merch_fw_b'],
                                  df['vol_snags_fw_b'],
                                  df['vol_sub_merch_irw_b'],
                                  df['vol_snags_irw_b']])
        df = df[['time_step',
                 'vol_merch_fw_b', 'vol_sub_merch_fw_b', 'vol_snags_fw_b',
                 'vol_sub_merch_irw_b', 'vol_snags_irw_b',
                 'tot_vol_fw_b']]
        return df

    #-------------------------------------------------------------------------#
    @property_cached
    def fw_c(self):
        """Harvest volumes of Fuel Wood Coniferous."""
        df = (self.hwp_intermediate
              .query('hwp == "fw_c"')
              .rename(columns={'vol_merch':     'vol_merch_fw_c',
                               'vol_sub_merch': 'vol_sub_merch_fw_c',
                               'vol_snags':     'vol_snags_fw_c',
                               'tc':            'tc_fw_c'}))
        return df

    #-------------------------------------------------------------------------#
    @property_cached
    def fw_c_total(self):
        """
        Harvest volumes of Fuel Wood Coniferous
        Join Industrial Round Wood co-products.
        """
        df = outer_join(self.irw_c, self.fw_c, 'time_step')
        df['tot_vol_fw_c'] = numpy.where(df['vol_merch_fw_c'] >= 0,
                                         sum([df['vol_merch_fw_c'],
                                              df['vol_sub_merch_fw_c'],
                                              df['vol_snags_fw_c'],
                                              df['vol_sub_merch_irw_c'],
                                              df['vol_snags_irw_c']]),
                                         sum([df['vol_sub_merch_irw_c'],
                                              df['vol_snags_irw_c']]))
        df = df[['time_step',
                 'vol_merch_fw_c','vol_sub_merch_fw_c','vol_snags_fw_c',
                 'vol_sub_merch_irw_c','vol_snags_irw_c',
                 'tot_vol_fw_c']]
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
              .set_index('time_step')[['vol_merch_irw_c']]
              .join(self.irw_b.set_index('time_step')[['vol_merch_irw_b']])
              .join(self.fw_c_total.set_index('time_step')[['tot_vol_fw_c']])
              .join(self.fw_b_total.set_index('time_step')[['tot_vol_fw_b']])
              .reset_index())
        # Add year
        df['year'] = self.parent.parent.country.timestep_to_year(df['time_step'])
        # Rename columns to standard IRW and FW product names
        df = df.rename(columns=lambda x: re.sub(r'vol_merch_|tot_vol_',r'', x))
        return df