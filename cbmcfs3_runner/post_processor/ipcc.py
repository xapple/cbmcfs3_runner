#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Written by Lucas Sinclair and Paul Rougieux.

JRC biomass Project.
Unit D1 Bioeconomy.

You can use this object like this:

    from cbmcfs3_runner.pump.faostat import faostat
    print(faostat.forestry)
"""

# Built-in modules #


# Third party modules #
import pandas

# First party modules #
from plumbing.cache import property_cached

# Internal modules #
from cbmcfs3_runner import module_dir

# Internal modules
from cbmcfs3_runner.pump.common import multi_index_pivot


###############################################################################
class Ipcc(object):
    """
    Provides access to the IPCC pool mapping
    """

    # Constants #
    ipcc_pools_path = module_dir + 'extra_data/ipcc_pools.csv'

    def __init__(self, parent):
        # Default attributes #
        self.parent = parent
        # Shortcut #
        self.country = self.parent.parent.country

    @property_cached
    def ipcc_pool_mapping(self):
        """
        Load a maping between IPCC pools and CBM pool names.

        Columns in the output are:
            pool	ipcc_pool_name	ipcc_pool

        The pool column contains the cbm pool.
        """
        # Read #
        df = pandas.read_csv(str(self.ipcc_pools_path))
        # Return #
        return df

    @property_cached
    def pool_indicators_long(self):
        """ Aggregate the pool indicators table along the 5 IPCC pools"""
        df = self.parent.pool_indicators_long
        # Add the 5 IPCC pools to the table
        df = df.left_join(self.ipcc_pool_mapping, on=['pool'])
        # Excplicity name NA values before grouping
        df['ipcc_pool'] = df['ipcc_pool'].fillna('not_available')
        # Aggregate total carbon weight along the 5 IPCC pools
        index = self.country.classifiers.names
        index = index + ['ipcc_pool', 'time_step', 'year']
        df = (df
              .groupby(index)
              .agg({'tc':sum})
              .reset_index()
              )
        return df


    @property_cached
    def pool_indicators_long_agg(self):
        """ Aggregate the pool indicators table for the whole country
        Calculate:
         * `tc` tons of carbon in IPCC pools
         * `tc_ha` tons of carbon per hectare in IPCC pools
        """
        # input
        df = self.pool_indicators_long
        inv = self.country.orig_data.inventory.copy()
        # Aggregate over pools and time
        index = ['ipcc_pool', 'time_step', 'year']
        df = (df
              .groupby(index)
              .agg({'tc':sum})
              .reset_index()
              )
        # Get the total forest area, ignore non forested areas
        total_area = (inv
                      .query("status not in 'NF'")
                      .agg({'area':sum}))
        # Make the pandas series into a scalar
        total_area = total_area[0]
        # Add total carbon per hectare
        df['tc_ha'] = df['tc'] / total_area
        # TODO add the stock change per hectare
        # first calculate the stock change
        # then the stock change per hectare
        #index = ['country_iso3', 'ipcc_pool']
        #pools_agg = pools_agg.sort_values(by=index + ['year'])
        #pools_agg['co2_stock_change'] = pools_agg.groupby(index)['co2_stock'].diff().fillna(0)

        # Add iso3 code
        df['country_iso3'] = self.country.country_iso3
        return df



    @property_cached
    def pool_indicators(self):
        """Pivot the pool indicators table to a wider format with
        pools in columns"""
        df = self.pool_indicators_long
        index = self.country.classifiers.names + ['time_step']
        df = multi_index_pivot(df.set_index(index),
                               columns = 'ipcc_pool', values='tc')
        return df
