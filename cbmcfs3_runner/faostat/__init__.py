#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Written by Lucas Sinclair and Paul Rougieux.

JRC biomass Project.
Unit D1 Bioeconomy.
"""

# Built-in modules #
import requests, zipfile

# Third party modules #
import pandas
from six import BytesIO

# First party modules #
from plumbing.cache       import property_cached

# Internal modules #
from cbmcfs3_runner import module_dir
from tqdm import tqdm

# Constants #
faostat_fo_path = module_dir + 'extra_data/faostat_forestry.csv'
url = 'http://fenixservices.fao.org/faostat/static/bulkdownloads/Forestry_E_Europe.zip'

###############################################################################
class Faostat(object):
    """
    Provides access to the databases from http://www.fao.org/.
    """

    @classmethod
    def download(cls):
        """A method to automatically downloaded the needed CSV file.
        You should only need to run this once. Use it like this:
        >>> from cbmcfs3_runner.faostat import Faostat
        >>> Faostat.download()
        """
        # Download it #
        response = requests.get(url, stream=True)
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
        with open(faostat_fo_path, 'wb') as handle:
            handle.write(zip_archive.read(file_name))

    @property_cached
    def fo(self):
        """We need to use DataFrame.stack() to place the
        years as rows instead of columns."""
        # Read #
        df = pandas.read_csv(str(faostat_fo_path))
        # Columns we want to keep #
        cols_to_keep = ['Area Code', 'Area', 'Item Code', 'Item', 'Element Code', 'Element', 'Unit']
        df = df.set_index(cols_to_keep)
        # Get rid of all the remaining columns by pivoting the table #
        df = df.stack()
        # For an unknown reason we get a Series instead of a DataFrame with a multilevel #
        df = pandas.DataFrame(df)
        # This will leave us with columns '0' and 'level_7' #
        df = df.reset_index()
        # Rename #
        df = df.rename(columns={'level_7': 'year', 0: 'value'})
        # Add the correct iso2 code #
        #TODO
        # Return #
        return df

###############################################################################
# Make a singelton #
faostat = Faostat()