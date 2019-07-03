#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Written by Lucas Sinclair and Paul Rougieux.

JRC biomass Project.
Unit D1 Bioeconomy.
"""

# Built-in modules #

# First party modules #
from plumbing.cache import property_cached

# Third party modules #
import pandas
import math

# Internal modules #
from cbmcfs3_runner import module_dir

# Constants #
gftm_demand_path       = module_dir + 'extra_data/gftm_forest_model.csv'
historical_demand_path = module_dir + 'extra_data/hist_harvest_corrected.csv'

# Parse #
gftm_demand       = pandas.read_csv(str(gftm_demand_path), header=None)
historical_demand = pandas.read_csv(str(historical_demand_path))

###############################################################################
class Demand(object):
    """
    This class takes care of parsing the file "gftm_forest_model.xlsx"
    received from Ragnar. It represents the harvesting projections of the
    GFTM economic models and should be used to create the disturbances
    in the simulation period.

    The cells for are empty for:

        * Annual production (m3ub) - from GFTM 2031 to 2035
        * Annual harvest 2036 to 2040
        * Annual production (m3ub) - from GFTM 2036 to 2040
        * Annual harvest 2041 to 2045
        * Annual production (m3ub) - from GFTM 2041 to 2045
        * Annual harvest 2046 to 2050
        * Annual production (m3ub) - from GFTM 2046 to 2050

    but have not been deleted from the original file because
    they are used in as reference in Excel formulas for some
    unknown reason.
    """

    def __init__(self, parent):
        # Default attributes #
        self.parent = parent

    @property
    def gftm_header(self):
       return gftm_demand[0:3]

    @property
    def gftm_content(self):
        return gftm_demand[3:]

    @property_cached
    def row(self):
        """Get the row corresponding to the current country."""
        selector = self.gftm_content[0] == self.parent.iso2_code
        return self.gftm_content.loc[selector].copy()

    @property_cached
    def future(self):
        """
        Future demands as predicted by GFTM.
        Create the data frame in long format.
        Columns are: ['values']
        """
        # Fill values #
        header = self.gftm_header.fillna(method='ffill', axis=1)
        # Get the headers #
        df = pandas.concat([header, self.row])
        # Transpose #
        df = df.transpose()
        # Drop country code and country name #
        df = df.drop([0,1])
        # New index #
        df = df.set_index([0,1,2])
        # New column name #
        df = df.rename(columns={df.columns[0]: 'value'})
        # Drop special characters #
        df['value'] = df['value'].str.strip('%')
        df['value'] = df['value'].str.replace("'", '')
        # Switch to number #
        df['value'] = pandas.to_numeric(df['value'])
        df['value'] = df['value'].fillna(0.0)
        # Return #
        return df

    @property_cached
    def historical_wide(self):
        """Historical harvest corrected manually by RP from the original
        FAOSTAT data for the purpose of CBM calibration.
        Expert estimates and knowledge is used to change the values as
        some values are clearly erroneous in the FAOSTAT."""
        # Get the rows corresponding to the current country #
        selector = historical_demand['country'] == self.parent.iso2_code
        df = historical_demand.loc[selector].copy()
        # Return #
        return df

    @property_cached
    def historical(self):
        """Reshape historical_wide demand to long format."""
        df = self.historical_wide.melt(id_vars    = ['country', 'step', 'year'],
                                       var_name   = 'HWP',
                                       value_name = 'volume')
        # Make HWP uppercase to match the silviculture table
        df['HWP'] = df['HWP'].str.upper()
        # Check if the total column matches with the sum of the other columns
        assert math.isclose(df.query("HWP=='TOTAL'")['volume'].sum(),
                            df.query("HWP!='TOTAL'")['volume'].sum())
        # Remove the total column from the table
        df = df.query("HWP!='TOTAL'").copy()
        # Return #
        return df
