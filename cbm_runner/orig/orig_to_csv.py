# Built-in modules #

# Third party modules #

# First party modules #
from autopaths.auto_paths import AutoPaths
from plumbing.cache       import property_cached

# Internal modules #
from cbm_runner.orig.associations import AssociationsParser
from cbm_runner.orig.calibration  import CalibrationParser
from cbm_runner.orig.silviculture import SilvicultureParser

###############################################################################
class OrigToCSV(object):
    """
    This class takes as input the three "original" files.
    And produces the CSV files for the next step (CSVToXLS).
    """

    all_paths = """
    /orig/silviculture.sas
    /orig/calibration.mdb
    /orig/aidb_eu.mdb
    """

    def __init__(self, parent):
        # Default attributes #
        self.parent = parent
        # Automatically access paths based on a string of many subpaths #
        self.paths = AutoPaths(self.parent.data_dir, self.all_paths)

    def __call__(self):
        self.calibration_parser()
        self.silviculture_parser()
        self.associations_parser.regenerate_csv()

    @property_cached
    def calibration_parser(self):
        return CalibrationParser(self)

    @property_cached
    def silviculture_parser(self):
        return SilvicultureParser(self)

    @property_cached
    def associations_parser(self):
        return AssociationsParser(self)
