#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Written by Lucas Sinclair and Paul Rougieux.

JRC biomass Project.
Unit D1 Bioeconomy.
"""

# Built-in modules #

# Third party modules #
import pandas

# First party modules #

# Internal modules #

###############################################################################
class PreFlight(object):
    """
    This class will check the input data for inconsistencies.
    """

    def __init__(self, parent):
        # Default attributes #
        self.parent = parent
        self.runner = parent

    def __call__(self):
        self.check_for_nan()

    def check_for_nan(self):
        """This method will catch any 'NaN' presents in the input."""
        # The object that will run next #
        create_xls = self.runner.default_sit.create_xls
        # Check there are CSVs #
        if create_xls.paths.csv_dir.empty:
            raise Exception("No CSVs present to generate the XLS.")
        # Go over each file #
        for file_name in create_xls.file_name_to_sheet_name:
            assert create_xls.paths[file_name].exists
            df = pandas.read_csv(create_xls.paths[file_name])
            assert not df.isna().any().any()