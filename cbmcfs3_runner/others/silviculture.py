# Built-in modules #
import re
from six import StringIO

# Third party modules #
import pandas

# First party modules #
from autopaths.auto_paths import AutoPaths
from plumbing.cache import property_cached

# Internal modules #

###############################################################################
class Silviculture(object):
    """
    This class takes the file "silviculture.sas" as input and generate a CSV
    from it.
    This information will be used to allocate the harvest across the spatial
    units and species.
    Thanks to this table, using the demand from an economic model,
    one can create a list of specific disturbances that include where
    to harvest and what species to harvest.
    """

    all_paths = """
    /orig/silviculture.sas
    """

    def __init__(self, parent):
        # Default attributes #
        self.parent = parent
        # Automatically access paths based on a string of many subpaths #
        self.paths = AutoPaths(self.parent.data_dir, self.all_paths)

    def __call__(self):
        pass

    @property_cached
    def df(self):
        """Search the SAS file for the CSV that is hidden inside and return a
        pandas DataFrame. Yes, the SAS file has a CSV hidden somewhere in the middle."""
        # Search #
        query = '\n {3}input (.*?);\n {3}datalines;\n\n(.*?)\n;\nrun'
        column_names, all_rows = re.findall(query, self.paths.sas.contents, re.DOTALL)[0]
        # Format #
        all_rows     = StringIO(all_rows)
        column_names = [name.strip('$') for name in column_names.split()]
        # Parse into table #
        df = pandas.read_csv(all_rows, names=column_names, delim_whitespace=True)
        # Return #
        return df

    @property_cached
    def csv(self):
        """Create a new disturbance table from `df` by matching columns
        and filling empty cells with information from the original disturbances
        (match rows that have the same classifiers together)."""
        # Original disturbance table from input XLS #
        orig_dist = self.parent.parent.input_data.disturbance_events
        # Columns #
        common_columns  = set(self.df.columns) & set(orig_dist.columns)
        # TODO #
        # TODO #
        # TODO #
        missing_columns = set(self.df.columns) - set(orig_dist.columns)
        classifier_columns = ['_2', '_4', '_5', '_7']
        # Drop columns #
        classifier_columns = ['Dist_Type_ID', '', '_2', '_4', '_5', '_7']
        scenario_dist = self.df[common_columns]
        # Join #
        return pandas.merge(scenario_dist, orig_dist, how='left')
