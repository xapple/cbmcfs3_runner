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

# Internal modules #
from cbmcfs3_runner import module_dir

# Constants #
gftm_demand_path        = module_dir + 'extra_data/gftm_forest_model.csv'
historical_demand_path = module_dir + 'historical_harvest_corrected.csv'

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
        """Get the row corresponding to this country."""
        selector = self.gftm_content[0] == self.parent.iso2_code
        return self.gftm_content.loc[selector]

    @property_cached
    def df(self):
        """Create the data frame in long format.
        Columns: ['values']"""
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
    def historical(self):
        """Historical harvest corrected from original FAOSTAT data 
           for the purpose of CBM calibration"""
        return self.historical_demand
