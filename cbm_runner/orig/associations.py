# Built-in modules #

# Third party modules #

# First party modules #
from autopaths.auto_paths import AutoPaths

# Internal modules #

###############################################################################
class AssociationsParser(object):
    """
    This class takes the file "associations.xls" and parses it.
    """

    all_paths = """
    /orig/associations.xlsx
    """

    def __init__(self, parent):
        # Default attributes #
        self.parent = parent
        # Automatically access paths based on a string of many subpaths #
        self.paths = AutoPaths(self.parent.data_dir, self.all_paths)

    def __call__(self):
        pass
