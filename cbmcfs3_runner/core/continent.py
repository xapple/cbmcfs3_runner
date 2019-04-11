#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
Written by Lucas Sinclair and Paul Rougieux.

JRC biomass Project.
Unit D1 Bioeconomy.
"""

# Built-in modules #

# Third party modules #

# First party modules #
from autopaths            import Path
from autopaths.auto_paths import AutoPaths
from plumbing.cache       import property_cached
from plumbing.logger      import create_file_logger

# Internal modules #
from cbmcfs3_runner.core.country import Country
from cbmcfs3_runner.scenarios import scen_classes

# Constants #
cbm_data_repos = Path("/repos/cbmcfs3_data/")

###############################################################################
class Continent(object):
    """Aggregates countries together. Enables access to a dataframe containing
    concatenates data from all countries."""

    all_paths = """
    /countries/
    /scenarios/
    /logs/continent.log
    """

    def __init__(self, base_dir):
        """Store the directory paths where there is a directory for every
        country and for every scenario."""
        # The base directory #
        self.base_dir = base_dir
        # Automatically access paths based on a string of many subpaths #
        self.paths = AutoPaths(cbm_data_repos, self.all_paths)
        # Where the data will be stored for this run #
        self.countries_dir = self.paths.countries_dir
        self.scenarios_dir = self.paths.scenarios_dir

    def __iter__(self): return iter(self.countries.values())
    def __len__(self):  return len(self.countries.values())

    @property_cached
    def countries(self):
        """Return a list with country objects inside."""
        all_countries = [Country(d) for d in self.countries_dir.flat_directories]
        return {c.iso2_code: c for c in all_countries}

    @property_cached
    def scenarios(self):
        """Return a dictionary of scenario names to Scenario objects."""
        all_scenarios = [S(self) for S in scen_classes]
        return {s.short_name: s for s in all_scenarios}

    @property_cached
    def log(self):
        """Each runner will have its own logger."""
        return create_file_logger('continent', self.paths.log)

###############################################################################
# Create list of all countries #
continent = Continent(cbm_data_repos)

