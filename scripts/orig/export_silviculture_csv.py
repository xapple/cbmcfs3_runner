#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
A script to create the CSV files called "silviculture.csv"
by extracting it from the "silviculture.sas" file.

Typically you would run this file from a command line like this:

     ipython3.exe -i -- /deploy/cbmcfs3_runner/scripts/orig/export_silviculture_csv.py
"""

# Built-in modules #
import re

# Third party modules #
from tqdm import tqdm
from six import StringIO
import pandas

# First party modules #
from autopaths.auto_paths import AutoPaths

# Internal modules #
from cbmcfs3_runner.core.continent import continent

# Constants #

###############################################################################
class ExportSilvicultureCSV(object):
    """
    This class takes the file "silviculture.sas" as input and generates a CSV
    from it.
    """

    all_paths = """
    /orig/silviculture.csv
    /orig/silviculture.sas
    """

    def __init__(self, country):
        # Default attributes #
        self.country = country
        # Automatically access paths based on a string of many subpaths #
        self.paths = AutoPaths(self.country.data_dir, self.all_paths)

    def __call__(self):
        """Search the SAS file for the CSV that is hidden inside and return a
        pandas DataFrame. Yes, you heard that correctly, the SAS file has
        a CSV hidden somewhere in the middle under plain text format."""
        # Our regular expression #
        query = '\n {3}input (.*?);\n {3}datalines;\n\n(.*?)\n;\nrun'
        # Search in the file #
        column_names, all_rows = re.findall(query, self.paths.sas.contents, re.DOTALL)[0]
        # Format the column_names #
        column_names = [name.strip('$') for name in column_names.split()]
        # Place the rows (content) into a virtual file to be read #
        all_rows = StringIO(all_rows)
        # Parse into a data frame #
        df = pandas.read_csv(all_rows, names=column_names, delim_whitespace=True)
        # Write back into a CSV #
        df.to_csv(str(self.paths.csv), index=False)

###############################################################################
if __name__ == '__main__':
    exporters = [ExportSilvicultureCSV(c) for c in continent]
    for exporter in tqdm(exporters): exporter()
