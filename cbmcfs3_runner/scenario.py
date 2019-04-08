#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
Written by Lucas Sinclair and Paul Rougieux.

JRC biomass Project.
Unit D1 Bioeconomy.
"""

# Built-in modules #

# First party modules #
from autopaths.dir_path import DirectoryPath
from autopaths.auto_paths import AutoPaths

# Internal modules #
from cbmcfs3_runner.runner import Runner

###############################################################################
class Scenario(object):
    """This object is represents a harvest and economic scenario. It will contain
    a copy of every country."""

    def __init__(self, scenario_dir=None):
        """Store the data directory paths where everything will start from."""
        # Main directory #
        self.scenario_dir = DirectoryPath(scenario_dir)
        # Check it exists #
        self.scenario_dir.must_exist()
        # Automatically access paths based on a string of many subpaths #
        self.paths = AutoPaths(self.scenario_dir, self.all_paths)
