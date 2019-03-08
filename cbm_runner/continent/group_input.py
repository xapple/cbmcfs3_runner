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

