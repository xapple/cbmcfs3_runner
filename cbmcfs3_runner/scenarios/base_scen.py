#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Written by Lucas Sinclair and Paul Rougieux

JRC biomass Project.
Unit D1 Bioeconomy.
"""

# Built-in modules #

# First party modules #
from autopaths            import Path
from autopaths.auto_paths import AutoPaths
from plumbing.cache       import property_cached
from tqdm import tqdm

# Internal modules #
from cbmcfs3_runner.reports.scenario import ScenarioReport

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

    def __call__(self):
        for code, steps in tqdm(self.runners.items(), ncols=60):
            for r in steps:
                r(silent=True)
        self.compile_log_tails()

    @property
    def scenarios_dir(self):
        """Shortcut to the scenarios directory"""
        return self.continent.scenarios_dir

    def compile_log_tails(self, step=-1):
        summary = self.paths.summary
        summary.open(mode='w')
        summary.handle.write("# Summary of all log file tails\n\n")
        summary.handle.writelines(r[step].tail for r in self.runners.values() if r[step])
        summary.close()

    @property_cached
    def report(self):
        return ScenarioReport(self)
