#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
A script to create the CSV files called "silviculture.csv"
by extracting it from the "silviculture.sas" file.

Typically you would run this file from a command line like this:

     ipython3.exe -i -- /deploy/cbmcfs3_runner/scripts/orig/export_silviculture.py
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
class ExportFromSilviculture(object):
    """
    This class takes the file "silviculture.sas" as input and generates a CSV
    from it.
    """

    all_paths = """
    /orig/silviculture.sas
    /orig/silv_treatments.csv
    /orig/harvest_corr_fact.csv
    """

    def __init__(self, country):
        # Default attributes #
        self.country = country
        # Automatically access paths based on a string of many subpaths #
        self.paths = AutoPaths(self.country.data_dir, self.all_paths)

    def __call__(self):
        self.treatments()
        self.harvest_corr_fact()

    def treatments(self):
        """Search the SAS file for the CSV that is hidden inside and return a
        pandas DataFrame. Yes, you heard that correctly, the SAS file has
        a CSV hidden somewhere in the middle under plain text format.
        This data frame will be used to generate disturbances from the economic demand.
        """
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
        df.to_csv(str(self.paths.treatments), index=False)

    def harvest_corr_fact(self):
        """There is actually an other hard coded info inside the SAS file
        that we need.

        This method will extract a list of "harvest correction factors"
        in CSV format. We can spot the location in the file by searching for
        the string <if _2='>

        These corrections factors will be applied when creating new
        disturbances to adjust which forest type is harvest first.
        Obviously, coefficients are different in the different countries.

              if _2='FS' then CF=1.2;
              if _2='QR' then CF=0.9;
              ...
        """
        # Our regular expression #
        query = "\n(if _2='.*?)\n.*?run;\n"
        # Search in the file #
        found = re.findall(query, self.paths.sas.contents, re.DOTALL)
        if not found: return
        blob = found[0]
        # See if we can parse lines inside of it #
        query = "if _2='([A-Z][A-Z])' then CF=([0-9].[0-9]+);"
        found = re.findall(query, blob)
        if not found: return
        # Do each line #
        extract = lambda line: re.findall(query, line)[0]
        lines   = [line for line in blob.split('\n') if line]
        result  = list(map(extract,lines))
        # Make a data frame #
        df = pandas.DataFrame(result, columns=['forest_type', 'corr_fact'])
        # Write back into a CSV #
        df.to_csv(str(self.paths.corr_fact), index=False)

###############################################################################
if __name__ == '__main__':
    exporters = [ExportFromSilviculture(c) for c in continent]
    for exporter in tqdm(exporters): exporter()
