#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
Written by Lucas Sinclair and Paul Rougieux.

JRC biomass Project.
Unit D1 Bioeconomy.
"""

# Built-in modules #
import os

# Third party modules #
from autopaths.dir_path   import DirectoryPath
from autopaths.auto_paths import AutoPaths
from plumbing.cache       import property_cached

# Internal modules #
from cbm_runner.steps.switch_aidb          import AIDBSwitcher
from cbm_runner.steps.standard_import_tool import StandardImportTool
from cbm_runner.steps.compute_model        import ComputeModel
from cbm_runner.steps.post_process         import PostProcessor
from cbm_runner.graphs.graphs              import Graphs

###############################################################################
class Runner(object):
    """This object is capable of running the full pipeline, starting
    from a few input tables, such as an inventory and a list of disturbances
    and to bring this data all the way to visualizations of the predicated
    carbon stock."""

    all_paths = """
    /input/
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

    def __call__(self):
        self.clear_all_outputs()
        self.standard_input_tool()
        self.compute_model()

    def clear_all_outputs(self):
        """Removes the directories that will be recreated by running the pipeline."""
        self.paths.output_dir.remove()
        self.paths.logs_dir.remove()

    @property_cached
    def switcher(self):
        return AIDBSwitcher(self)

    @property_cached
    def standard_input_tool(self):
        return StandardImportTool(self)

    @property_cached
    def compute_model(self):
        return ComputeModel(self)

    @property_cached
    def post_processor(self):
        return PostProcessor(self)

    @property_cached
    def graphs(self):
        return Graphs(self)
