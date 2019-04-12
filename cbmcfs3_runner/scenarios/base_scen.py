#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
Written by Lucas Sinclair and Paul Rougieux.

JRC biomass Project.
Unit D1 Bioeconomy.
"""

# Built-in modules #

# First party modules #
from autopaths            import Path
from autopaths.auto_paths import AutoPaths

# Internal modules #

###############################################################################
class Scenario(object):
    """This object represents a harvest and economic scenario"""

    all_paths = """
    /logs_summary.md
    """

    def __init__(self, continent):
        # Save parent #
        self.continent = continent
        # This scenario dir #
        self.base_dir = Path(self.scenarios_dir + self.short_name + '/')
        # Automatically access paths based on a string of many subpaths #
        self.paths = AutoPaths(self.base_dir, self.all_paths)

    @property
    def scenarios_dir(self):
        """Shortcut to the scenarios directory"""
        return self.continent.scenarios_dir

    def compile_log_tails(self, step=-1):
        summary = self.paths.summary
        summary.open(mode='w')
        summary.handle.write("# Summary of all log file tails\n\n")
        summary.handle.writelines(r[step].summary for r in self.runners.values() if r[step])
        summary.close()
