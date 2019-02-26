# Built-in modules #

# Third party modules #

# First party modules #
from autopaths.auto_paths import AutoPaths
from plumbing.cache       import property_cached

# Internal modules #
from cbm_runner.orig.calibration import CalibrationParser

###############################################################################
class OrigToCSV(object):
    """
    This class takes as input the four "original" files.
    And produces the CSV files for the next step (CSVToXLS).
    """

    all_paths = """
    /orig/silviculture.sas
    /orig/calibration.mdb
    /orig/aidb_eu.mdb
    /orig/associations.xlsx
    """

    def __init__(self, parent):
        # Default attributes #
        self.parent = parent
        # Automatically access paths based on a string of many subpaths #
        self.paths = AutoPaths(self.parent.data_dir, self.all_paths)

    def __call__(self):
        pass

    @property_cached
    def calibration_parser(self):
        return CalibrationParser(self)

    @property_cached
    def xxxxxx(self):
        pass