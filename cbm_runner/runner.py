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

###############################################################################
class Runner(object):
    """Lorem."""

    all_paths = """
    /input/
    /output/
    /logs/
    """

    def __init__(self, io_dir=None):
        """Store the data directory path."""
        # If the io_dir is not specified, get it from the environment vars #
        if io_dir is None: io_dir = os.environ.get('CBM_IO_DIR')
        # Main directory #
        self.io_dir = DirectoryPath(io_dir)
        # Check it exists #
        self.io_dir.must_exist()
        # Automatically access paths #
        self.p = AutoPaths(self.io_dir, self.all_paths)

    @property_cached
    def lorem(self):
        return "ipsum"