#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Written by Lucas Sinclair and Paul Rougieux.

JRC biomass Project.
Unit D1 Bioeconomy.

You can use this object like this:

    from cbmcfs3_runner.core.continent import continent
    print(continent)
"""

# Built-in modules #
import os

# Third party modules #
from tqdm import tqdm
import pandas

# First party modules #
from autopaths            import Path
from autopaths.auto_paths import AutoPaths
from plumbing.cache       import property_cached
from plumbing.logger      import create_file_logger

# Internal modules #
from cbmcfs3_runner.core.country import Country
from cbmcfs3_runner.scenarios import scen_classes

# Where is the data, default case #
cbm_data_repos = Path("~/repos/cbmcfs3_data/")

# But you can override that with an environment variable #
if os.environ.get("CBMCFS3_DATA"):
    cbm_data_repos = Path(os.environ['CBMCFS3_DATA'])

###############################################################################
class Continent(object):
    """Aggregates countries together. Enables access to a data frame containing
    concatenates data from all countries."""

    all_paths = """
    /countries/
    /scenarios/
    /reports/
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

    def __getitem__(self, key):
        """Return a runner based on a tuple of scenario, country and step."""
        return self.get_runner(*key)

    def __iter__(self): return iter(self.countries.values())
    def __len__(self):  return len(self.countries.values())

    def __call__(self):
        for country in tqdm(self, ncols=60):
            country()

    @property_cached
    def countries(self):
        """Return a dictionary of country iso2 code to country objects."""
        all_countries = [Country(self, d) for d in self.countries_dir.flat_directories]
        return {c.iso2_code: c for c in all_countries}

    @property_cached
    def scenarios(self):
        """Return a dictionary of scenario names to Scenario objects."""
        all_scenarios = [Scen(self) for Scen in scen_classes]
        return {s.short_name: s for s in all_scenarios}

    def run_scenarios(self, verbose=True):
        """Run all scenarios for all countries in continent"""
        for scenario in self.scenarios.values():
            print(scenario)
            scenario(verbose=verbose)

    @property_cached
    def log(self):
        """Each runner will have its own logger."""
        return create_file_logger('continent', self.paths.log)

    def get_runner(self, scenario, country, step):
        """Return a runner based on scenario, country and step."""
        return self.scenarios[scenario].runners[country][step]

    @property
    def first(self):
        key = next(iter(self.countries))
        return self.countries[key]

###############################################################################
# Create list of all countries #
continent = Continent(cbm_data_repos)

