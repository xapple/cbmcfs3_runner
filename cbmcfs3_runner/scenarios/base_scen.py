#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
Written by Lucas Sinclair and Paul Rougieux.

JRC biomass Project.
Unit D1 Bioeconomy.
"""

# Built-in modules #

# First party modules #

# Internal modules #

###############################################################################
class Scenario(object):
    """This object represents a harvest and economic scenario"""

    def __init__(self, continent):
        # Save parent #
        self.continent = continent

    @property
    def scenarios_dir(self):
        """Shortcut to the scenarios directory"""
        return self.continent.scenarios_dir

    def compile_log_tails(self, step=-1):
        runner = self.runners
        summary = cbm_data_repos + "logs_summary.md"
        summary.open(mode='w')
        summary.handle.write("# Summary of all log file tails\n\n")
        summary.handle.writelines(c.summary for c in continent.all_countries)
        summary.close()
