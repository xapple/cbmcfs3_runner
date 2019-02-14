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

    all_paths = """
    /input/inv_and_dist.xls
    """

    def __init__(self, parent):
        # Default attributes #
        self.parent = parent
        # Directories #
        self.paths = AutoPaths(self.parent.data_dir, self.all_paths)

    def test_xls_reading(self):
        import xlrd
        book = xlrd.open_workbook(self.paths.xls)
        print("The number of worksheets is", book.nsheets)
        print("Worksheet name(s):", book.sheet_names())
        return book.sheet_by_index(0)

    @property_cached
    def xls(self): return pandas.ExcelFile(str(self.paths.xls))

    @property_cached
    def inventory(self): return self.xls.parse("Inventory")
