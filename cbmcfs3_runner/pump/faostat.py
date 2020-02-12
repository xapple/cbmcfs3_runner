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
import requests, zipfile

# Third party modules #
import pandas
from six import BytesIO

# First party modules #
from plumbing.cache import property_cached

# Internal modules #
from cbmcfs3_runner import module_dir
from tqdm import tqdm

###############################################################################
class Faostat(object):
    """
    Provides access to a forestry production and trade databases from
    http://www.fao.org/faostat/en/#data/FO

    The download method gets data from a bulk file specified in the
    url attribute of this class.

    The forestry method returns a data frame containing
    round wood and fuel wood harvest volumes.
    """

    products = ['Roundwood, coniferous (production)',
                'Roundwood, non-coniferous (production)',
                'Wood fuel, coniferous',
                'Wood fuel, non-coniferous']

    short_names = ['irw_c', 'irw_b', 'fw_c', 'fw_b']

    # Constants #
    faostat_fo_path = module_dir + 'extra_data/faostat_forestry.csv'
    url = 'http://fenixservices.fao.org/faostat/static/bulkdownloads/Forestry_E_Europe.zip'

    def download(self):
        """A method to automatically downloaded the needed CSV file.
        You should only need to run this once. Use it like this:

            >>> from cbmcfs3_runner.faostat import faostat
            >>> faostat.download()
        """
        # Download it #
        response = requests.get(self.url, stream=True)
        total_size = int(response.headers.get('content-length'))
        block_size = int(total_size/1024)
        # Do it #
        zip_file = BytesIO()
        for data in tqdm(response.iter_content(chunk_size=block_size), total=1024):
            zip_file.write(data)
        # Uncompress only one file #
        zip_archive = zipfile.ZipFile(zip_file)
        file_name = "Forestry_E_Europe_NOFLAG.csv"
        # We can't use zip_archive.extract() because it preserves directories #
        with open(self.faostat_fo_path, 'wb') as handle:
            handle.write(zip_archive.read(file_name))

    @property_cached
    def forestry(self):
        """
        Transform the raw data table to something adapted to our needs.
        For instance, We need to use DataFrame.stack() to place the
        years as rows instead of columns.

        The resulting data frame will have missing data, for instance
        in Belgium, the ref_year is 1999 but data only starts in 2000.

        Furthermore, we are only interested in these products mentioned
        in self.products

        The units are cubic meters under bark in the column 'value'.

        Columns in the output are: ???
        """
        # Import internal modules #
        from cbmcfs3_runner.core.country import all_codes, ref_years
        # Read #
        df = pandas.read_csv(str(self.faostat_fo_path))
        # Rename all columns to lower case #
        df = df.rename(columns=lambda name: name.replace(' ', '_').lower())
        # Areas are actually countries, items are products #
        df = df.rename(columns={'area': 'country', 'item': 'product'})
        # Columns we want to keep #
        cols_to_keep = ['area_code', 'country', 'item_code', 'product', 'element_code', 'element', 'unit']
        # Get rid of all the remaining columns by pivoting the table #
        df = df.set_index(cols_to_keep)
        df = df.stack()
        # For an unknown reason we get a Series instead of a DataFrame with a multilevel #
        df = pandas.DataFrame(df)
        # This will leave us with columns '0' and 'level_7' #
        df = df.reset_index()
        # Rename #
        df = df.rename(columns={'level_7': 'year', 0: 'value'})
        # Make the years true numerical values #
        df['year'] = df['year'].apply(lambda x: int(x[1:]))
        # Filter below year 1990 #
        min_year = ref_years['ref_year'].min()
        selector = df['year'] >= min_year
        df = df[selector].copy()
        # Remove countries we don't need #
        selector = df['country'].isin(all_codes['country'])
        df = df[selector].copy()
        # Add the correct iso2 code #
        df = df.replace({"country": all_codes.set_index('country')['iso2_code']})
        # Filter products #
        selector = df['product'].isin(self.products)
        df = df[selector].copy()
        # Rename the products to their shorter names #
        df = df.replace({'product': dict(zip(self.products, self.short_names))})
        # This corresponds to our "hwp" column elsewhere #
        df['hwp'] = df['product']
        # Split the column into two and keep hwp #
        df['product'], df['conifers_broadleaves'] = df['hwp'].str.split('_', 1).str
        # The value is under bark #
        df = df.rename(columns={'value': 'value_ub'})
        # Return #
        return df

###############################################################################
# Make a singleton #
faostat = Faostat()