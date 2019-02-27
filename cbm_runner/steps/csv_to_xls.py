# Built-in modules #

# Third party modules #
import pandas, pyexcel

# First party modules #
from autopaths.auto_paths import AutoPaths

# Internal modules #

###############################################################################
class CSVToXLS(object):
    """
    This class takes care of bundeling the seven input CSV files into
    one binary Excel file with seven tables for consumption by
    the tool "StandardImportTool".
    """

    all_paths = """
    /input/csv/ageclass.csv
    /input/csv/classifiers.csv
    /input/csv/disturbance_events.csv
    /input/csv/disturbance_types.csv
    /input/csv/inventory.csv
    /input/csv/transition_rules.csv
    /input/csv/yields.csv
    /input/xls/inv_and_dist.xlsx
    /input/xls/inv_and_dist.xls
    """

    sheet_name_to_file_name = {
        'AgeClasses':      'ageclass',
        'Classifiers':     'classifiers',
        'DistEvents':      'disturbance_events',
        'DistType':        'disturbance_types',
        'Inventory':       'inventory',
        'Growth':          'yields',
        'Transitions':     'transition_rules',
    }

    def __init__(self, parent):
        # Default attributes #
        self.parent = parent
        # Automatically access paths based on a string of many subpaths #
        self.paths = AutoPaths(self.parent.data_dir, self.all_paths)
        # Reverse the dictionary #
        self.file_name_to_sheet_name = {v:k for k,v in self.sheet_name_to_file_name.items()}
        # Check there are CSV files present #
        for name in self.file_name_to_sheet_name: assert self.paths[name].exists

    def __call__(self):
        # Create an Excel Writer #
        writer = pandas.ExcelWriter(self.paths.inv_xlsx, engine='xlsxwriter')
        # Add each DataFrame to a different sheet #
        for file_name, sheet_name in self.file_name_to_sheet_name.items():
            self.df = pandas.read_csv(self.paths[file_name])
            self.df.to_excel(writer, sheet_name=sheet_name, index=False)
        # Save changes #
        writer.save()
        # Convert from XLSX to XLS #
        source = str(self.paths.inv_xlsx)
        dest   = str(self.paths.inv_xls)
        pyexcel.save_book_as(file_name=source, dest_file_name=dest)

    def reverse_generation(self):
        """If you ever want to generate the CSVs from the Excel
         (other way round) for testing purposes only."""
        self.xls = pandas.ExcelFile(str(self.paths.inv_xls))
        for sheet in self.xls.sheet_names:
            df   = self.xls.parse(sheet)
            path = str(self.paths[self.sheet_name_to_file_name[sheet]])
            df.to_csv(path, index=False)