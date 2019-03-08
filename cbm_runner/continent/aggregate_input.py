# Built-in modules #

# Third party modules #
import pandas

# First party modules #
from autopaths.auto_paths import AutoPaths
from plumbing.cache import property_cached

# Internal modules #

###############################################################################
class AggregateInput(object):
    """
    A.
    """

    def __init__(self, parent):
        # Default attributes #
        self.parent = parent

    @property_cached
    def contact_dict(self):
        """A."""
        return silv_all = {c.country_code: c.sdasd.df for c in self.parent.all_countries}

    @property_cached
    def contact_df(self):
        """A."""
        return pandas.concat(self.contact_dict)
