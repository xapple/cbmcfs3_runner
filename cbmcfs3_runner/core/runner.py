#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Written by Lucas Sinclair and Paul Rougieux.

JRC biomass Project.
Unit D1 Bioeconomy.
"""

# Built-in modules #
import os

# First party modules #
from autopaths            import Path
from autopaths.auto_paths import AutoPaths
from plumbing.cache       import property_cached
from plumbing.git         import GitRepo
from plumbing.logger      import create_file_logger

# Third party modules #

# Internal modules #
import cbmcfs3_runner
from cbmcfs3_runner.graphs import runner_graphs, load_graphs_from_module
from cbmcfs3_runner.pre_processor                  import PreProcessor
from cbmcfs3_runner.pump.middle_process            import MiddleProcessor
from cbmcfs3_runner.post_processor                 import PostProcessor
from cbmcfs3_runner.pump.input_data                import InputData
from cbmcfs3_runner.pump.pre_flight                import PreFlight
from cbmcfs3_runner.reports.runner                 import RunnerReport
from cbmcfs3_runner.stdrd_import_tool.launch_sit   import DefaultSIT, AppendSIT
from cbmcfs3_runner.external_tools.launch_cbm      import LaunchCBM

# Constants #
home = os.environ.get('HOME', '~') + '/'

###############################################################################
class Runner(object):
    """
    This object is capable of running a CBM simulation pipeline, starting
    from a few input tables, such as an inventory and a list of disturbances
    and to bring this data all the way to the predicted carbon stock.
    """

    all_paths = """
    /input/
    /input/csv/
    /input/xls/
    /input/json/
    /output/
    /logs/runner.log
    /graphs/
    /report/report.pdf
    """

    sit_calling = 'dual' or 'single'

    def __repr__(self):
        return '%s object on "%s"' % (self.__class__, self.data_dir)

    def __bool__(self): return self.paths.log.exists
    __nonzero__ = __bool__

    def __init__(self, scenario, country, num):
        # Base attributes #
        self.scenario = scenario
        self.country  = country
        self.num      = num
        # How to reference this runner #
        self.short_name  = self.scenario.short_name + '/'
        self.short_name += self.country.iso2_code + '/'
        self.short_name += str(self.num)
        # Where the data will be stored for this run #
        self.data_dir = self.scenario.scenarios_dir + self.short_name + '/'
        # Automatically access paths based on a string of many subpaths #
        self.paths = AutoPaths(self.data_dir, self.all_paths)

    @property_cached
    def log(self):
        """
        Each runner will have its own logger.
        By default we clear the log file when you start logging.
        """
        return create_file_logger(self.short_name, self.paths.log)

    def __call__(self, interrupt_on_error=True, verbose=False):
        try:
            self.run(verbose=verbose)
        except Exception:
            message = "Runner '%s' encountered an exception. See log file."
            self.log.error(message % self.short_name)
            self.log.exception("Exception", exc_info=1)
            if interrupt_on_error: raise

    def run(self, verbose=False):
        """
        Run the full modelling pipeline for a given country,
        a given scenario and a given step.
        """
        # Send messages to console #
        if verbose: self.log.handlers[0].setLevel("DEBUG")
        # Messages #
        self.log.info("Using module at '%s'." % Path(cbmcfs3_runner))
        self.log.info("Runner '%s' starting." % self.short_name)
        # Record the hash of the other library "cbm3_python" e.g. 4dc12af #
        cbm3py_repos = GitRepo(home + "repos/cbm3_python/")
        self.log.info("Using cbm3_python at '%s'." % cbm3py_repos.hash)
        # Clean everything from previous run #
        self.remove_directory()
        # Modify input data before copying it #
        self.pre_processor()
        # Pre-flight check #
        self.pre_flight()
        # Just check we are on Windows #
        if os.name == "posix":
            raise Exception("Can't go any further (only on Windows).")
        # Switch archive index #
        self.country.aidb.switch()
        # Standard import tool #
        self.default_sit()
        if self.sit_calling == 'dual': self.append_sit()
        # Final steps #
        self.middle_processor()
        self.launch_cbm()
        # Save hash #
        db = self.post_processor.database
        self.log.info("Database '%s' md5 hash '%s'." % (db, db.md5))
        # Post-processing #
        self.post_processor()
        # Reporting #
        #self.log.info("Creating runner report.")
        #for graph in self.graphs: graph()
        #self.report()
        # Messages #
        self.log.info("Done.")

    def remove_directory(self):
        """
        Removes the directory that will be recreated by running this runner.
        Note: we need to keep the log we are writing to currently.
        """
        # Message #
        self.log.info("Removing directory '%s'." % self.data_dir)
        # The output directory #
        self.paths.input_dir.remove(safe=False)
        self.paths.output_dir.remove(safe=False)
        # Empty all the other logs #
        for element in self.paths.logs_dir.flat_contents:
            if element != self.paths.log:
                element.remove()

    @property_cached
    def input_data(self):
        return InputData(self)

    @property_cached
    def pre_processor(self):
        return PreProcessor(self)

    @property_cached
    def pre_flight(self):
        return PreFlight(self)

    @property_cached
    def default_sit(self): return DefaultSIT(self)
    @property_cached
    def append_sit(self):  return AppendSIT(self)

    @property_cached
    def middle_processor(self):
        return MiddleProcessor(self)

    @property_cached
    def launch_cbm(self):
        return LaunchCBM(self)

    @property_cached
    def post_processor(self):
        return PostProcessor(self)

    @property
    def tail(self):
        """A short summary showing just the end of the log file."""
        msg  = "\n## Runner `%s`\n" % self.short_name
        msg += "\nTail of the log file at `%s`\n" % self.paths.log
        msg += self.paths.log.pretty_tail
        return msg

    @property
    def map_value(self):
        """
        Return a float that indicates how far this country is running
        within the pipeline. This can be used to plot the country on a
        color scale map.
        """
        if not self.paths.log.exists: return 0.0
        if   'run is completed' in self.paths.log.contents: return 1.0
        elif 'SIT created'      in self.paths.log.contents: return 0.5
        else:                                               return 0.0

    @property_cached
    def graphs(self):
        return load_graphs_from_module(self, runner_graphs)

    @property_cached
    def report(self):
        return RunnerReport(self)
