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
    /input/xls/inv_and_dist.xls
    """

    @property_cached
    def xls(self): return pandas.ExcelFile(str(self.paths.xls))

    @property_cached
    def inventory(self): return self.xls.parse("Inventory")

    @property_cached
    def disturbance_events(self): return self.xls.parse("DistEvents")

    @property_cached
    def disturbance_types(self): return self.xls.parse("DistType")

    @property_cached
    def classifiers(self):
        df = self.xls.parse("Classifiers")
        return df.sort_values(by=['ClassifierNumber', 'ClassifierValueID'],
                              ascending=[True, False])

###############################################################################
class InputDataTXT(InputData):

    all_paths = """
    /input/txt/ageclass.txt
    /input/txt/classifiers.txt
    /input/txt/disturbance_events.txt
    /input/txt/disturbance_types.txt
    /input/txt/inventory.txt
    /input/txt/transition_rules.txt
    /input/txt/yields.txt
    """

    @property_cached
    def inventory(self):
        raise NotImplemented("We cannot read this custom format yet.")

###############################################################################
class InputDataCSV(InputData):
    """This is not currently possible."""
    pass