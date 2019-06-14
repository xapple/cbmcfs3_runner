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
gftm_demand_path = module_dir + 'extra_data/gftm_forest_model.csv'

# Parse #
gftm_demand  = pandas.read_csv(str(gftm_demand_path), header=None)
gftm_header  = gftm_demand[0:3]
gftm_content = gftm_demand[3:]

# Fill #
gftm_header  = gftm_header.fillna(method='ffill', axis=1)
gftm_content = gftm_content.fillna(0.0)

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

    and have been deleted from the original file.
    """

    def __init__(self, parent):
        # Default attributes #
        self.parent = parent

    @property_cached
    def row(self):
        """Get the row corresponding to this country."""
        selector = gftm_content[0] == self.parent.iso2_code
        return gftm_content.loc[selector]

    @property_cached
    def df(self):
        """Create the data frame in long format."""
        # Get the headers #
        df = pandas.concat([gftm_header, self.row])
        return df
        # Melt #
        args = {
            'id_vars':    ['a'],
            'value_vars': ['a'],
            'var_name':   ['year'],
            'value_name': ['a'],
        }
        return self.row.melt(*args)
