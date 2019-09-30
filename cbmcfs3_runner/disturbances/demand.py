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
import pandas, math, numpy

# Internal modules #
from cbmcfs3_runner import module_dir

# Constants #
historical_demand_path = module_dir + 'extra_data/hist_harvest_corrected.csv'
gftm_irw_demand_path   = module_dir + 'extra_data/gftm_forest_model.csv'
gftm_fw_demand_path    = module_dir + 'extra_data/gftm_fuel_wood_bau.csv'

# Parse #
historical_demand = pandas.read_csv(str(historical_demand_path))
gftm_irw_demand   = pandas.read_csv(str(gftm_irw_demand_path), header=None)
gftm_fw_demand    = pandas.read_csv(str(gftm_fw_demand_path))

# Fix some country names #
old_names = ['LUX', 'SW', 'SL']
new_names = ['LU',  'SE', 'SI']
fixed_names = gftm_fw_demand['country_iso2'].replace(old_names, new_names)
gftm_fw_demand['country_iso2'] = fixed_names

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

    bark_correction_factor = 0.88

    def __init__(self, parent):
        # Default attributes #
        self.parent = parent

    @property_cached
    def year_expansion(self):
        """Create a little data frame to expand years
        from a 5 year time frame to a yearly time frame.

        GFTM gives a yearly demand over a 5 year interval.
        We will use this data frame to duplicate the yearly demand
        volume 5 times. This will then be used to generate disturbances.

        Columns are: ['year_min', 'year']
        """
        year_min = numpy.concatenate([numpy.repeat(x,5) for x in range(2016, 2030, 5)])
        df = pandas.DataFrame({'year_min': year_min,
                               'year':     range(2016, 2031, 1)})
        df['year'] = df['year'].astype(int)
        # Convert year to time step #
        df['step'] = self.parent.year_to_timestep(df['year'])
        return df

    @property
    def gftm_header(self):
       return gftm_irw_demand[0:3]

    @property
    def gftm_content(self):
        return gftm_irw_demand[3:]

    @property_cached
    def gftm_row(self):
        """Get the row corresponding to the current country."""
        selector = self.gftm_content[0] == self.parent.iso2_code
        return self.gftm_content.loc[selector].copy()

    @property_cached
    def gftm_irw(self):
        """Future IRW demand as predicted by GFTM.
        Load and reshape the data frame in long format."""
        # Fill values #
        header = self.gftm_header.fillna(method='ffill', axis=1)
        # Get the headers #
        df = pandas.concat([header, self.gftm_row])
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
        # Correct an inconsistency in the year range #
        df['year'] = df['year'].replace('2016to 2020', '2016 to 2020')
        # Filter for years with data and select the variable of interest #
        years_to_keep = ['2016 to 2020', '2021 to 2025', '2026 to 2030']
        variable      = 'Annual  production (m3ub) - from GFTM'
        df = df.query("variable==@variable & year in @years_to_keep").copy()
        # Convert under bark demand volumes to over bark using a correction factor #
        df['value_ob'] = df['value'] / self.bark_correction_factor
        # Sum log and pulpwood #
        # Create a little data frame to rename products to HWP #
        gftm_irw_names = pandas.DataFrame({'product': ['C log', 'C pulpwood',
                                                       'N log', 'N pulpwood'],
                                           'hwp':     ['irw_c', 'irw_c',
                                                       'irw_b', 'irw_b']})
        df = (df
              # Rename products to HWP #
              .set_index('product')
              .join(gftm_irw_names.set_index('product'))
              # Aggregate the log and pulpwood values by HWP #
              .groupby(['year', 'hwp'])
              .agg({'value_ob': sum})
              .reset_index())
        df['year_min'] = df['year'].str[:4].astype(int)
        df['year_max'] = df['year'].str[-4:].astype(int)
        # Rename year column, because a new year column will be created later
        # when expanding the years
        df = df.rename(columns={'year':'year_text'})
        # Repeat lines for each successive year within a range by
        # joining the year_expansion data frame
        df = df.left_join(self.year_expansion, 'year_min')
        return df

    @property_cached
    def gftm_fw(self):
        """Future FW demand as predicted by GFTM. Using the historical
        proportion of fuel wood with respect to industrial round wood.
        Load and reshape the data frame in long format."""
        # Get the row corresponding to the current country #
        selector = gftm_fw_demand['country_iso2'] == self.parent.iso2_code
        # Check there is something to find for this country #
        if not any(selector):
            msg = f'No fuel wood data for {self.parent.iso2_code} ' \
                  f'in "{gftm_fw_demand_path}".'
            raise pandas.errors.EmptyDataError(msg)
        # Copy only the current country #
        fw_wide = gftm_fw_demand.loc[selector].copy()
        # Reshape to long format #
        df = fw_wide.melt(id_vars='country_iso2', var_name='product_year',
                          value_name='value')
        # Separate the hwp and year_min columns  #
        df['hwp'], df['year_min'] = df['product_year'].str.split('_', 1).str
        # Rename #
        df['hwp'] = df['hwp'].replace(['coniferous', 'broadleaved'],
                                      ['fw_c', 'fw_b'])
        df['year_min'] = df['year_min'].astype(int) + 1
        # Limit fw year to 2026 equal to the maximum of irw years #
        df = df.query('year_min<2030').copy()
        # Convert demand value to over bark #
        df['value_ob'] = df['value'] / self.bark_correction_factor
        # Repeat lines for each successive year within a range by
        # joining the year_expansion data frame
        df = df.left_join(self.year_expansion, 'year_min')
        # Return #
        return df

    def gftm(self,
             columns_of_interest = ('hwp', 'value_ob', 'year', 'step')):
        """Concatenation of gftm_irw and gftm_fw, used only for
        diagnostics and analysis.
        Actual demand allocation is made from gftm_irw and gftm_fw."""
        return pandas.concat([self.gftm_irw[columns_of_interest],
                              self.gftm_fw[columns_of_interest]])

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
        # Make HWP uppercase to match the silviculture table #
        df['hwp'] = df['hwp'].str.upper()
        # Check if the total column matches with the sum of the other columns
        # Set abs_tol=1 to one to allow for rounding errors in the input data
        sum_tot   = df.query("hwp=='TOTAL'")['volume'].sum()
        sum_other = df.query("hwp!='TOTAL'")['volume'].sum()
        if not math.isclose(sum_tot, sum_other, abs_tol=1):
            msg = "The sum of the total column: %s "
            msg += "doesn't match the sum of the other columns: %s"
            raise Exception(msg % (sum_tot, sum_other))
        # Remove the total column from the table #
        df = df.query("hwp!='TOTAL'").copy()
        # Sort #
        df = df.sort_values(by=['year', 'hwp'], ascending=[True, False])
        # Return #
        return df
