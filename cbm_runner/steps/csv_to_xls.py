# Built-in modules #

# Third party modules #
import pandas

# First party modules #
from autopaths.auto_paths import AutoPaths

# Internal modules #

###############################################################################
class CSVToXLS(object):
    """
    This class takes care of bundeling the seven input CSV files into
    one binary Excel file with seven tables for consumption by
    the illnamed "StandardImportTool".
    """

    all_paths = """
    /input/csv/ageclass.csv
    /input/csv/classifiers.csv
    /input/csv/disturbance_events.csv
    /input/csv/disturbance_types.csv
    /input/csv/inventory.csv
    /input/csv/transition_rules.csv
    /input/csv/yields.csv
    /input/xls/inv_and_dist.xls
    """

    def __init__(self, parent):
        # Default attributes #
        self.parent = parent
        # Automatically access paths based on a string of many subpaths #
        self.paths = AutoPaths(self.parent.data_dir, self.all_paths)
        # Check there are CSV files present #
        pass

    def __run__(self, parent):
        pass

    sheet_name_to_file_name = {
        'AgeClasses':      'ageclass',
        'Classifiers':     'classifiers',
        'DistEvents':      'disturbance_events',
        'DistType':        'disturbance_types',
        'Inventory':       'inventory',
        'Growth':          'yields',
        'Transitions':     'transition_rules',
    }

    def reverse_generation(self):
        """If you ever want to generate the CSVs from the Excel
         (other way round) for testing purposes only."""
        self.xls = pandas.ExcelFile(str(self.paths.inv_xls))
        for sheet in self.xls.sheet_names:
            df   = self.xls.parse(sheet)
            path = str(self.paths[self.sheet_name_to_file_name[sheet]])
            df.to_csv(path, index=False)