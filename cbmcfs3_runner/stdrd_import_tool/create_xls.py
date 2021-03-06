#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Written by Lucas Sinclair and Paul Rougieux.

JRC biomass Project.
Unit D1 Bioeconomy.
"""

# Built-in modules #

# Third party modules #
import pandas, pyexcel

# First party modules #
from autopaths.auto_paths import AutoPaths

# Internal modules #

###############################################################################
class CreateXLS(object):
    """
    This class takes care of bundling the seven input CSV files into
    one binary Excel file with seven tables for consumption by
    the tool "StandardImportTool".
    """

    all_paths = """
    /input/csv/ageclass.csv
    /input/csv/inventory.csv
    /input/csv/classifiers.csv
    /input/csv/disturbance_events.csv
    /input/csv/disturbance_types.csv
    /input/csv/transition_rules.csv
    /input/csv/yields.csv
    /input/csv/historical_yields.csv
    """

    file_name_to_sheet_name = {
        'ageclass':             'AgeClasses',
        'classifiers':          'Classifiers',
        'disturbance_events':   'DistEvents',
        'disturbance_types':    'DistType',
        'inventory':            'Inventory',
        'transition_rules':     'Transitions',
    }

    def __init__(self, parent):
        # Default attributes #
        self.parent = parent
        self.runner = parent.parent
        # Automatically access paths based on a string of many subpaths #
        self.paths = AutoPaths(self.runner.data_dir, self.all_paths + self.parent.all_paths)

    def __call__(self):
        # Create an Excel Writer #
        writer = pandas.ExcelWriter(self.paths.tables_xlsx, engine='xlsxwriter')
        # Add each DataFrame to a different sheet #
        for file_name, sheet_name in self.file_name_to_sheet_name.items():
            # Read the CSV and put it in the excel file #
            self.df = pandas.read_csv(self.paths[file_name])
            self.df.to_excel(writer, sheet_name=sheet_name, index=False)
        # Special case for the yield table that can vary between current and hist #
        self.df = pandas.read_csv(self.paths[self.parent.yield_table_name.replace('.','_')])
        self.df.to_excel(writer, sheet_name='Growth', index=False)
        # Save changes #
        writer.save()
        # Convert from XLSX to XLS #
        source = str(self.paths.tables_xlsx)
        dest   = str(self.paths.tables_xls)
        pyexcel.save_book_as(file_name=source, dest_file_name=dest)