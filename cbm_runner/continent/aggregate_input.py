# Built-in modules #

# Third party modules #
import pandas

# First party modules #
from autopaths.auto_paths import AutoPaths
from plumbing.cache import property_cached

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

    @property_cached
    def all_dict(self):
        """A dictionary of data frames, with country iso 2 code as keys."""
        return dist_all = {c.country_code: c.sdasd.df for c in self.parent.all_countries}

    @property_cached
    def concat_df(self):
        """A concatenated data frame containing all ."""
        return pandas.concat(self.contact_dict)

