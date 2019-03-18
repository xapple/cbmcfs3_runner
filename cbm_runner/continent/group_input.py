# Built-in modules #
from collections import OrderedDict

# Third party modules #
import pandas

# First party modules #
from autopaths.auto_paths import AutoPaths

# Internal modules #

###############################################################################
class GroupInput(object):
    """
    Concatenate input table in one single table for all countries available. 
    Also provide a dictionary of data frames to investigate inconsistent conlumn names between the different countries. 
    The compare_column_names method can be used to print differences in column names compared to a reference country
    (defaults to AT).
    """

    def __init__(self, parent):
        # Default attributes #
        self.parent = parent

    def as_dict(self, name):
        """A dictionary of data frames, with country iso 2 code as keys."""
        dist_all = [(r.country_iso2, r.csv_to_xls.read_csv(name)) for r in self.parent.all_countries]
        return OrderedDict(dist_all)

    def as_concat_df(self, name):
        """A concatenated data frame containing disturbance tables for all countries."""
        return pandas.concat(self.as_dict(name))

    def compare_column_names(self, name, country_ref = 'AT'):
        """Print differences in column names, compared to a reference country"""
        dict_of_df = self.as_dict(name) 
        for country, table in dict_of_df.items():
            print("\n"+country)
            print(dict_of_df[country_ref].columns.difference(table.columns))
            print(table.columns.difference(dict_of_df[country_ref].columns))
