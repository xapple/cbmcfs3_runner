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
    Also provide a dictionary of data frames
    to investigate inconsistent conlumn names between the different countries.
    The compare_column_names method can be used to print
    differences in column names compared to a reference country
    (defaults to AT).
    """

    def __init__(self, parent):
        # Default attributes #
        self.parent = parent

    def as_dict(self, name):
        """A dictionary of data frames, with country iso 2 code as keys."""
        dist_all = [(r.country_iso2,
                     r.csv_to_xls.read_csv(name))
                    for r in self.parent.all_countries]
        return OrderedDict(dist_all)

    def as_concat_df(self, name):
        """A concatenated data frame containing tables for all countries."""
        df = pandas.concat(self.as_dict(name)) 
        df = df.reset_index(level=0)
        df.rename(columns={'level_0': 'country_iso2'})
        return df

    def compare_column_names_in_dict_of_df(self, dict_of_df, key_ref='AT'):
        """Compare column names in a dictionnary of data frames
        to a reference data frame present under the key_ref"""
        print("(Specific to this country, present in reference country: " +
              key_ref + ")")
        comparison = OrderedDict()
        for country, table in dict_of_df.items():
            specific_to_this = list(table.columns.difference(dict_of_df[key_ref].columns))
            present_in_ref = list(dict_of_df[key_ref].columns.difference(table.columns))
            comparison[country] = (specific_to_this, present_in_ref)
        for country, table in comparison.items():
            if(table[0] or table[1]):
                print(country)
                print(table)

    def compare_column_names(self, table_name, country_ref='AT'):
        """Print differences in column names,
        compared to a reference country"""
        dict_of_df = self.as_dict(table_name)
        self.compare_column_names_in_dict_of_df(dict_of_df, country_ref)
