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
    Provides access to the CBM pool and fluxes aggregated according to the
    IPCC pool mapping.
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

        * pool name of a cbm pool, used as column name
        * ipcc_pool_name long name for an ipcc pool
        * ipcc_pool short name for an ipcc pool, used as column name

        The ipcc_pool names are not exactly the ipcc pools available
        in table 4.A of the National Inventory Submissions to the IPCC:

        #TODO put this in tinyurl
        https://unfccc.int/process-and-meetings/transparency-and-reporting/reporting-and-review-under-the-convention/greenhouse-gas-inventories-annex-i-parties/national-inventory-submissions-2019

        The difference is that we distinguished below ground
        from above ground biomass while the living biomass net change reported
        to NIS contains both above ground and below ground biomass.

        | IPCC NIS Table 4.A                    | Pool as mentionned here  |
        |---------------------------------------|--------------------------|
        | Carbon stock change in living biomass | NA                       |
        |     Gains                             | NA                       |
        |     Losses                            | NA                       |
        |     Net change                        | abgr_bmass + belgr_bmass |
        | Carbon stock change in dead wood      | dead_wood                |
        | Net carbon stock change in litter     | litter                   |
        | Net carbon stock change in soils      | soil_dom                 |
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
        classifiers_names = self.parent.classifiers_names
        # Load pools #
        df = self.parent.pool_indicators_long
        # Load output inventory area #
        columns_of_interest = classifiers_names + ['time_step', 'area']
        inv = self.parent.inventory.age_indicators[columns_of_interest]
        # Add the 5 IPCC pools to the table #
        df = df.left_join(self.ipcc_pool_mapping, on=['pool'])
        # Explicitly name NA values before grouping #
        df['ipcc_pool'] = df['ipcc_pool'].fillna('not_available')
        # Aggregate total carbon weight along the 5 IPCC pools #
        # Change ipcc_pool column to a factor variable
        df['ipcc_pool'] = df['ipcc_pool'].astype('category')
        index = classifiers_names + ['ipcc_pool', 'time_step', 'year']
        # Group by and aggregate #
        df = (df
              .groupby(index, observed=True)
              .agg({'tc':sum})
              .reset_index()
              )
        # Aggregate the inventory
        # i.e. sum the area for all ages
        index = classifiers_names + ['time_step']
        inv_agg = (inv
                   .groupby(index, observed=True)
                   .agg({'area':sum})
                   .reset_index())
        # Add the area column to the pool table
        df = df.left_join(inv_agg, on=index)
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
        # Aggregate over pools and time #
        index = ['ipcc_pool', 'time_step', 'year']
        df = (df
              .groupby(index, observed=True)
              .agg({'tc':sum})
              .reset_index()
              )
        # Total carbon per hectare #
        df['tc_ha'] = df['tc'] / df['area']
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
