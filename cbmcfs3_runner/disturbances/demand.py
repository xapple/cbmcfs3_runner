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
import numpy

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
        self.bark_correction_factor = 0.88

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

        GFTM gives a yearly demand over a 5 year interval.
        Before we can generate disturbances, we create a year indentifier
        for each year in the interval
        and we duplicate the yearly demand volume 5 times.

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
        df = (df.reset_index()
              .rename(columns = {0: 'variable',
                                 1: 'year',
                                 2: 'product'}))
        # Correct an inconsistency in the year range
        df['year'] = df['year'].replace('2016to 2020', '2016 to 2020')
        # Filter for years with data and select the variable of interest
        years_to_keep = ['2016 to 2020', '2021 to 2025', '2026 to 2030']
        variable      = 'Annual  production (m3ub) - from GFTM'
        df = df.query("variable==@variable & year in @years_to_keep").copy()
        # Convert under bark demand volumes to over bark using a correction factor
        df['value_ob'] = df['value'] / self.bark_correction_factor
        # Sum log and pulpwood
        # Create a little data frame to rename products to HWP
        gftm_irw_names = pandas.DataFrame({'product': ['C log', 'C pulpwood',
                                                       'N log', 'N pulpwood'],
                                           'hwp':     ['IRW_C', 'IRW_C',
                                                       'IRW_B', 'IRW_B']})
        df = (df
              # Rename products to HWP
              .set_index('product')
              .join(gftm_irw_names.set_index('product'))
              # Aggregate the value by HWP
              .groupby(['year', 'hwp'])
              .agg({'value_ob': sum})
              .reset_index())
        # Create a little data frame with expanded years
        year_min = numpy.concatenate([numpy.repeat(x,5) for x in range(2016, 2030, 5)])
        year_expansion = pandas.DataFrame({'year_min': year_min,
                                           'year':     range(2016, 2031, 1)})
        df['year_min'] = df['year'].str[:4].astype(int)
        df['year_max'] = df['year'].str[-4:].astype(int)
        # Repeat lines for each successive year within a range by
        # joining the year_expansion data frame
        df = (df
              .drop(columns=['year', 'year_max'])
              .set_index(['year_min'])
              .join(year_expansion.set_index(['year_min'])))
        # Convert year to time step
        df['step'] = self.parent.year_to_timestep(df['year'])
        # Return #
        return df

    @property_cached
    def historical_wide(self):
        """Historical harvest corrected manually by R.P. from the original
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
                                       var_name   = 'hwp',
                                       value_name = 'volume')
        # Make HWP uppercase to match the silviculture table
        df['hwp'] = df['hwp'].str.upper()
        # Check if the total column matches with the sum of the other columns
        # Set abs_tol=1 to one to allow for rounding errors in the input data
        sum_tot = df.query("hwp=='TOTAL'")['volume'].sum()
        sum_other = df.query("hwp!='TOTAL'")['volume'].sum()
        if not math.isclose(sum_tot, sum_other, abs_tol=1):
            msg = "The sum of the total column: %s "
            msg += "doesn't match the sum of the other columns: %s"
            raise Exception(msg % (sum_tot, sum_other))
        # Remove the total column from the table
        df = df.query("hwp!='TOTAL'").copy()
        # Sort #
        df = df.sort_values(by=['year', 'hwp'], ascending=[True, False])
        # Return #
        return df
