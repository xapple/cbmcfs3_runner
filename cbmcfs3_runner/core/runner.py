#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Written by Lucas Sinclair and Paul Rougieux.

JRC biomass Project.
Unit D1 Bioeconomy.
"""

# Built-in modules #

# First party modules #
from autopaths.auto_paths import AutoPaths
from plumbing.cache       import property_cached
from plumbing.common      import pad_extra_whitespace
from plumbing.logger      import create_file_logger

# Internal modules #
import cbmcfs3_runner
from cbmcfs3_runner.graphs                        import runner_graphs
from cbmcfs3_runner.modifiers.pre_process         import PreProcessor
from cbmcfs3_runner.modifiers.middle_process      import MiddleProcessor
from cbmcfs3_runner.post_processor                import PostProcessor
from cbmcfs3_runner.others.input_data             import InputData
from cbmcfs3_runner.reports.runner                import RunnerReport
from cbmcfs3_runner.stdrd_import_tool.launch_sit  import LaunchSIT
from cbmcfs3_runner.external_tools.launch_cbm     import LaunchCBM

###############################################################################
class Runner(object):
    """This object is capable of running a CBM simulation pipeline, starting
    from a few input tables, such as an inventory and a list of disturbances
    and to bring this data all the way to the predicted carbon stock."""

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
        """Each runner will have its own logger."""
        return create_file_logger(self.short_name, self.paths.log)

    def __call__(self, silent=False):
        try:
            self.run()
        except Exception:
            message = "Runner '%s' encountered an exception. See log file."
            self.log.error(message % self.short_name)
            self.log.exception("Exception", exc_info=1)
            if not silent: raise

    def run(self):
        self.log.info("Using module at '%s'" % cbmcfs3_runner)
        self.log.info("Runner '%s' starting" % self.short_name)
        self.remove_directory()
        self.input_data.copy_from_country()
        self.pre_processor()
        self.country.aidb.switch()
        self.launch_sit()
        self.middle_processor()
        self.launch_cbm()
        #self.post_processor()
        for graph in self.graphs: graph()
        self.report()

    def remove_directory(self):
        """Removes the directory that will be recreated by running this runner.
        Note: we need to keep the log we are writing to currently."""
        # Message
        self.log.info("Removing directory '%s'." % self.data_dir)
        # The output directory #
        self.paths.input_dir.remove()
        self.paths.output_dir.remove()
        # Empty all the other logs #
        for element in self.paths.logs_dir.flat_contents:
            if element != self.paths.log:
                element.remove()

    @property_cached
    def input_data(self):
        """Use the country object to copy the original input data."""
        return InputData(self)

    @property_cached
    def pre_processor(self):
        return PreProcessor(self)

    @property_cached
    def launch_sit(self):
        return LaunchSIT(self)

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
        """Shortcut: view the end of the log file."""
        return "\n" + pad_extra_whitespace("\n".join(self.paths.log.tail()), 4) + "\n"

    @property
    def summary(self):
        """A short summary showing just the end of the log file."""
        msg  = "\n## Runner `%s`\n" % self.short_name
        msg += "\nTail of the log file at `%s`\n" % self.paths.log
        msg += self.tail
        return msg

    @property_cached
    def graphs(self):
        """Sorry for the black magic. The result is an object whose attributes
        are all the graphs found in taxa_table_graphs.py initialized with this
        instance as only argument."""
        class Graphs(object): pass
        result = Graphs()
        for graph in runner_graphs.__all__:
            cls = getattr(runner_graphs, graph)
            setattr(result, cls.short_name, cls(self))
        return result

    @property_cached
    def report(self):
        return RunnerReport(self)
