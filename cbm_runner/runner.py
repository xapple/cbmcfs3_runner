#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
Written by Lucas Sinclair and Paul Rougieux.

JRC biomass Project.
Unit D1 Bioeconomy.
"""

# Built-in modules #
import os, glob

# Third party modules #
from autopaths.dir_path   import DirectoryPath
from autopaths.auto_paths import AutoPaths
from plumbing.cache       import property_cached

# Internal modules #
from cbm_runner.orig.orig_to_csv           import OrigToCSV
from cbm_runner.steps.csv_to_xls           import CSVToXLS
from cbm_runner.steps.switch_aidb          import AIDBSwitcher
from cbm_runner.steps.input_data           import InputDataXLS, InputDataTXT
from cbm_runner.steps.standard_import_tool import ImportWithXLS, ImportWithTXT
from cbm_runner.steps.compute_model        import ComputeModel
from cbm_runner.steps.post_process         import PostProcessor
from cbm_runner.graphs.graphs              import Graphs
from cbm_runner.reports                    import Reports

###############################################################################
class Runner(object):
    """This object is capable of running the full pipeline, starting
    from a few input tables, such as an inventory and a list of disturbances
    and to bring this data all the way to visualizations of the predicated
    carbon stock."""

    all_paths = """
    /input/
    /input/csv/
    /input/xls/
    /input/txt/
    /output/
    /logs/plot.pdf
    """

    def __init__(self, data_dir=None):
        """Store the data directory paths where everything will start from."""
        # If the data_dir is not specified, get it from the environment vars #
        if data_dir is None: data_dir = os.environ.get('CBM_IO_DIR')
        # Main directory #
        self.data_dir = DirectoryPath(data_dir)
        # Check it exists #
        self.data_dir.must_exist()
        # Automatically access paths based on a string of many subpaths #
        self.paths = AutoPaths(self.data_dir, self.all_paths)
        # Snif if this is an excel input #

    def __call__(self):
        self.clear_all_outputs()
        self.orig_to_csv.calibration_parser()
        if not self.paths.csv_dir.empty: self.csv_to_xls()
        self.standard_import_tool()
        self.compute_model()
        self.graphs()
        self.reports.inventory_report()

    def clear_all_outputs(self):
        """Removes the directories that will be recreated by running the pipeline."""
        self.paths.output_dir.remove()
        self.paths.logs_dir.remove()

    @property_cached
    def switcher(self):
        return AIDBSwitcher(self)

    @property_cached
    def csv_to_xls(self):
        return CSVToXLS(self)

    @property_cached
    def orig_to_csv(self):
        return OrigToCSV(self)

    @property
    def is_excel_input(self):
        return not self.paths.xls_dir.empty

    @property_cached
    def input_data(self):
        if self.is_excel_input: return InputDataXLS(self)
        else:                   return InputDataTXT(self)

    @property_cached
    def standard_import_tool(self):
        if self.is_excel_input: return ImportWithXLS(self)
        else:                   return ImportWithTXT(self)

    @property_cached
    def compute_model(self):
        return ComputeModel(self)

    @property_cached
    def post_processor(self):
        return PostProcessor(self)

    @property_cached
    def graphs(self):
        return Graphs(self)

    @property_cached
    def reports(self):
        return Reports(self)
