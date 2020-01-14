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
from plumbing.cache import property_cached

# Internal modules #
from cbmcfs3_runner import module_dir

# Internal modules
from cbmcfs3_runner.pump.common import multi_index_pivot

###############################################################################
class Ipcc(object):
    """
    Provides access to the IPCC pool mapping.
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
        Load a mapping between IPCC pools and CBM pool names.

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
        """
        Aggregate the pool indicators table along the 5 IPCC pools
        Keep the details of each stand separate
        i.e. each possible combination of classifiers remains in the data.
        """
        # Load the one from the post processor #
        df = self.parent.pool_indicators_long
        # Add the 5 IPCC pools to the table #
        df = df.left_join(self.ipcc_pool_mapping, on=['pool'])
        # Explicitly name NA values before grouping #
        df['ipcc_pool'] = df['ipcc_pool'].fillna('not_available')
        # Aggregate total carbon weight along the 5 IPCC pools #
        # Change ipcc_pool column to a factor variable
        df['ipcc_pool'] = df['ipcc_pool'].astype('category')
        index = self.parent.classifiers_names
        index = index + ['ipcc_pool', 'time_step', 'year']
        # Group by and aggregate #
        df = (df
              .groupby(index)
              .agg({'tc':sum})
              .reset_index()
              )
        # Return #
        return df

    @property_cached
    def carbon_stock_long(self):
        """
        Aggregate the pool indicators table over the whole country
        Calculate these variable for each IPCC pool at each time step:

         * `tc` tons of carbon
         * `tc_ha` tons of carbon per hectare
         * `tc_change` net change of carbon stock in tons of carbon
         * `tc_change_ha` in tons of carbon per hectare
         * `co2_em_ha` CO2 emissions per hectare

        Note on the conversion from carbon to CO2.
        The CBM output pools are expressed in tons of Carbon,
        while the IPCC emission values are expressed in CO2.
        energyeducation.ca
        [C_vs_CO2](https://energyeducation.ca/encyclopedia/C_vs_CO2):
        > "Carbon has an atomic mass of 12 and oxygen has an atomic mass of 16.
        > Therefore CO2 has an atomic mass of 44.
        > This means that one kilogram (kg) of carbon
        > will produce 44/12 × 1kg = 3.67 kg of CO2."
        """
        # Load pool indicators #
        df = self.pool_indicators_long
        # ignore non forested areas #
        df = df.query("status not in 'NF'")
        inv = self.country.orig_data.inventory.copy()
        # Aggregate over pools and time #
        index = ['ipcc_pool', 'time_step', 'year']
        df = (df
              .groupby(index)
              .agg({'tc':sum})
              .reset_index()
              )
        # Get the total forest area, ignore non forested areas #
        # TODO: use changing area as in post_processing non_forested
        total_area = (inv
                      .query("status not in 'NF'")
                      .agg({'area':sum}))
        # Make the pandas series into a scalar #
        total_area = total_area[0]
        # Total carbon per hectare #
        df['tc_ha'] = df['tc'] / total_area
        # Keep the area #
        df['area'] = total_area
        # Carbon stock change
        # and Carbon stock change per hectare
        index = ['ipcc_pool']
        df = df.sort_values(by = index + ['year'])
        df['tc_change'] = df.groupby(index)['tc'].diff()
        df['tc_change_ha'] = df.groupby(index)['tc_ha'].diff()
        # Add CO2 emissions per hectare #
        df['co2_em_ha'] = - df['tc_change_ha'] * 44/12
        # Add iso3 code #
        df['country_iso3'] = self.country.country_iso3
        # Return #
        return df

    @property_cached
    def net_co2_emissions_removals(self):
        """Net CO2 emissions/removals over the whole country."""
        df = self.carbon_stock_change
        index = ['time_step', 'year']
        df = (df
              .groupby(index)
              # Is it useful to compute the C02 emissions here ?
              )
        df['co2_stock'] = - df['tc'] * 44/12
        # Return #
        return df

    @property_cached
    def pool_indicators(self):
        """
        Pivot the pool indicators table to a wider format with
        pools in columns.
        """
        # Load pool indicators #
        df = self.pool_indicators_long
        index = self.parent.classifiers_names + ['time_step']
        df = multi_index_pivot(df.set_index(index),
                               columns = 'ipcc_pool', values='tc')
        # Return #
        return df
