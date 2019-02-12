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
from cbm_runner.steps.model_execution      import ModelExecution

###############################################################################
class Runner(object):
    """Lorem."""

    all_paths = """
    /input/
    /output/
    /logs/
    """

    def __init__(self, io_dir=None):
        """Store the data directory paths."""
        # If the io_dir is not specified, get it from the environment vars #
        if io_dir is None: io_dir = os.environ.get('CBM_IO_DIR')
        # Main directory #
        self.io_dir = DirectoryPath(io_dir)
        # Check it exists #
        self.io_dir.must_exist()
        # Automatically access paths #
        self.p = AutoPaths(self.io_dir, self.all_paths)

    @property_cached
    def switcher(self):
        return AIDBSwitcher(path)

    @property_cached
    def standard_input_tool(self):
        return StandardImportTool(path)

    @property_cached
    def model_executer(self):
        return ModelExecution(self)

    def __call__(self):
        self.switcher.switch_to_europe()
        self.standard_input_tool.run()
        self.simulator.run()