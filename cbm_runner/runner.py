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

###############################################################################
class Runner(object):
    """Lorem."""

    all_paths = """
    /input/
    /output/
    /logs/
    """

    def __init__(self, data_dir=None):
        """Store the data directory paths."""
        # If the data_dir is not specified, get it from the environment vars #
        if data_dir is None: data_dir = os.environ.get('CBM_IO_DIR')
        # Main directory #
        self.data_dir = DirectoryPath(data_dir)
        # Check it exists #
        self.data_dir.must_exist()
        # Automatically access paths #
        self.paths = AutoPaths(self.data_dir, self.all_paths)

    def clear_all_outputs(self):
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
