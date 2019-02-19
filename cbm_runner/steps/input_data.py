# Built-in modules #

# Third party modules #
import pandas

# First party modules #
from autopaths.auto_paths import AutoPaths
from plumbing.cache import property_cached

# Internal modules #

###############################################################################
class InputData(object):
    """
    This class will provide access to the input data as pandas dataframes.
    """

    def __init__(self, parent):
        # Default attributes #
        self.parent = parent
        # Directories #
        self.paths = AutoPaths(self.parent.data_dir, self.all_paths)

###############################################################################
class InputDataXLS(InputData):

    all_paths = """
    /input/inv_and_dist.xls
    """

    @property_cached
    def xls(self): return pandas.ExcelFile(str(self.paths.xls))

    @property_cached
    def inventory(self): return self.xls.parse("Inventory")

###############################################################################
class InputDataTXT(InputData):

    all_paths = """
    /input/ageclass.txt
    /input/classifiers.txt
    /input/disturbance_events.txt
    /input/disturbance_types.txt
    /input/inventory.txt
    /input/transition_rules.txt
    /input/yields.txt
    """

    @property_cached
    def inventory(self):
        raise NotImplemented("We cannot read this custom format yet.")

###############################################################################
class InputDataCSV(InputData):
    """This is not currently possible."""
    pass