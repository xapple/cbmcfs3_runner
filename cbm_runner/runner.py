#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
Written by Lucas Sinclair and Paul Rougieux.

JRC biomass Project.
Unit D1 Bioeconomy.
"""

# Built-in modules #
import os, logging

# First party modules #
from autopaths.dir_path   import DirectoryPath
from autopaths.auto_paths import AutoPaths
from plumbing.cache       import property_cached
from plumbing.common      import pad_extra_whitespace

# Internal modules #
from cbm_runner.orig.orig_to_csv           import OrigToCSV
from cbm_runner.steps.csv_to_xls           import CSVToXLS
from cbm_runner.steps.pre_process          import PreProcessor
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
    /orig/
    /input/
    /input/csv/
    /input/xls/
    /input/txt/
    /output/
    /logs/runner.log
    """

    def __repr__(self):
        return '%s object on "%s"' % (self.__class__, self.data_dir)

    def __init__(self, data_dir=None, country_code=None):
        """Store the data directory paths where everything will start from."""
        # If the data_dir is not specified, get it from the environment vars #
        if data_dir is None: data_dir = os.environ['CBM_IO_DIR']
        # Main directory #
        self.data_dir = DirectoryPath(data_dir)
        # Check it exists #
        self.data_dir.must_exist()
        # Automatically access paths based on a string of many subpaths #
        self.paths = AutoPaths(self.data_dir, self.all_paths)
        # Store the country code #
        self.country_code = country_code

    @property_cached
    def log(self):
        """Each runner will have its own logger."""
        # Create a custom logger #
        logger = logging.getLogger(self.country_iso2)
        # Console logger and file logger #
        s_handler = logging.StreamHandler()
        f_handler = logging.FileHandler(str(self.paths.log), mode="w")
        # Choose the level of information for each #
        s_handler.setLevel(logging.ERROR)
        f_handler.setLevel(logging.DEBUG)
        # Choose the format of each #
        c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
        f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        s_handler.setFormatter(c_format)
        f_handler.setFormatter(f_format)
        # No need to display Exceptions on the console #
        class NoExceptionFilter(logging.Filter):
            def filter(self, record):
                return not record.getMessage() == 'Exception'
        s_handler.addFilter(NoExceptionFilter())
        # Add handlers to the logger
        logger.addHandler(s_handler)
        logger.addHandler(f_handler)
        # Set the level of the logger itself #
        logger.setLevel(logging.DEBUG)
        # Return #
        return logger

    def __call__(self, silent=False):
        try:
            self.run()
        except Exception:
            message = "Country '%s' encountered an exception. See log file."
            self.log.error(message % self.country_iso2)
            self.log.exception("Exception", exc_info=1)
            if not silent: raise

    def run(self):
        #self.log.info("Regenerating CSV inputs for country '%s'." % self.country_iso2)
        #self.orig_to_csv()
        self.log.info("Running country '%s'." % self.country_iso2)
        self.pre_processor()
        self.clear_all_outputs()
        self.csv_to_xls()
        self.aidb_switcher()
        self.standard_import_tool()
        self.compute_model()
        #self.graphs()
        #self.reports.inventory_report()

    def clear_all_outputs(self):
        """Removes the directories that will be recreated by running the pipeline."""
        self.log.info("Clearing all outputs.")
        # The output directory #
        self.paths.output_dir.remove()
        # Empty the logs, but we need to keep the log we are writing to currently #
        for element in self.paths.logs_dir.flat_contents:
            if element != self.paths.log: element.remove()

    @property_cached
    def aidb_switcher(self):
        return AIDBSwitcher(self)

    @property_cached
    def orig_to_csv(self):
        return OrigToCSV(self)

    @property_cached
    def csv_to_xls(self):
        return CSVToXLS(self)

    @property
    def is_excel_input(self):
        return not self.paths.xls_dir.empty

    @property_cached
    def input_data(self):
        if self.is_excel_input: return InputDataXLS(self)
        else:                   return InputDataTXT(self)

    @property_cached
    def pre_processor(self):
        return PreProcessor(self)

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

    @property
    def tail(self):
        """View the end of the log file"""
        return self.paths.log.tail()

    @property
    def summary(self):
        """A short summary including the end of the log file"""
        msg  = "\n## Country `%s`\n" % self.country_iso2
        msg += "\nTail of the log file at `%s`\n" % self.paths.log
        msg += "\n" + pad_extra_whitespace(self.tail, 4) + "\n"
        return msg
