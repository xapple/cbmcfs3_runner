# Built-in modules #

# Third party modules #

# First party modules #
from autopaths.auto_paths import AutoPaths

# Internal modules #

###############################################################################
class SilvicultureParser(object):
    """
    This class takes as input the "original" files:
        - silviculture.sas
        - calibration.mdb
        - aidb_eu.mdb
        - associations.xlsx
    And produces the CSV files for the next step (CSVToXLS).
    """

    all_paths = """
    /input/orig/silviculture.sas
    /input/orig/calibration.mdb
    /input/orig/aidb_eu.mdb
    /input/orig/associations.xlsx
    """

    def __init__(self, parent):
        # Default attributes #
        self.parent = parent
        # Automatically access paths based on a string of many subpaths #
        self.paths = AutoPaths(self.parent.data_dir, self.all_paths)

    def __call__(self):
        pass
