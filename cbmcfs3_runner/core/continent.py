#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Written by Lucas Sinclair and Paul Rougieux.

JRC biomass Project.
Unit D1 Bioeconomy.

You can use this object like this:

    >>> from cbmcfs3_runner.core.continent import continent
    >>> print(continent)
"""

# Built-in modules #
import os

# Third party modules #
from tqdm import tqdm

# First party modules #
from autopaths            import Path
from autopaths.auto_paths import AutoPaths
from plumbing.cache       import property_cached

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
    """
    Continent is a singleton i.e. an object of which there is a single instance.
    Continent contains many countries and many scenarios.

     * Country objects give access to the original data used
         as simulation input to CBM.
     * Scenarios objects give access to various simulation runs,
         i.e. modifications of the input data to create scenarios and
         the ensuing post processing to analyse simulation results.
    """

    all_paths = """
    /countries/
    /scenarios/
    /reports/
    """

    def __init__(self, base_dir):
        """
        Store the directory paths where there is a directory for every
        country and for every scenario.
        """
        # The base directory #
        self.base_dir = base_dir
        # Automatically access paths based on a string of many subpaths #
        self.paths = AutoPaths(cbm_data_repos, self.all_paths)
        # Where the data will be stored for this run #
        self.countries_dir = self.paths.countries_dir
        self.scenarios_dir = self.paths.scenarios_dir

    def __repr__(self):
        return '%s object with %i countries' % (self.__class__, len(self))

    def __getitem__(self, key):
        """Return a runner based on a tuple of scenario, country and step."""
        return self.get_runner(*key)

    def __iter__(self): return iter(self.countries.values())
    def __len__(self):  return len(self.countries.values())

    def __call__(self):
        for country in tqdm(self):
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
        """Run all scenarios for all countries in continent."""
        for scenario in self.scenarios.values():
            print(scenario)
            scenario(verbose=verbose)

    def get_runner(self, scenario, country, step):
        """
        Return a runner based on scenario, country and step.

            >>> from cbmcfs3_runner.core.continent import continent
            >>> runner = continent[('historical', 'AT', 0)]
        """
        return self.scenarios[scenario].runners[country][step]

###############################################################################
# Create a singleton #
continent = Continent(cbm_data_repos)