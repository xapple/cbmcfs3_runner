#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Written by Lucas Sinclair and Paul Rougieux

JRC biomass Project.
Unit D1 Bioeconomy.
"""

# Built-in modules #
from collections import OrderedDict

# Third party modules #
import pandas

# First party modules #
from autopaths            import Path
from autopaths.auto_paths import AutoPaths
from plumbing.cache       import property_cached
from tqdm import tqdm

# Internal modules #
from cbmcfs3_runner.reports.scenario import ScenarioReport

###############################################################################
class Scenario(object):
    """This object represents a harvest and economic scenario."""

    all_paths = """
    /logs_summary.md
    """

    def __iter__(self): return iter(self.runners.values())
    def __len__(self):  return len(self.runners.values())

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

    #-------------------------------------------------------------------------#
    def concat_as_dict(self, step=-1, func=None):
        """A dictionary of data frames, with country iso2 code as keys."""
        # Default option, function that takes a runner, returns a data frame #
        if func is None:
            func = lambda r: r.input_data.disturbance_events
        # Retrieve data #
        result = [(iso2, func(runners[step]).copy()) for iso2,runners in self.runners.items()]
        # Return result #
        return OrderedDict(result)

    def concat_as_df(self, *args, **kwargs):
        """A data frame with many countries together."""
        # Get data #
        dict_of_df = self.concat_as_dict(*args, **kwargs)
        # When classifiers are present
        # add column '_8' for all countries except BG 
        if '_7' in dict_of_df['AT'].columns:
            for iso2, df in dict_of_df.items():
                if iso2 == "BG": continue
                loc = list(dict_of_df['BG'].columns).index('_8')
                df.insert(loc, '_8', '')
        # DataFrame #
        # option sort=True adds a column of NaN if the column is missing
        # for a particular country
        df = pandas.concat(dict_of_df, sort=True)
        df = df.reset_index(level=0)
        df = df.rename(columns={'level_0': 'country_iso2'})
        # Return result #
        return df

    def compare_col_names(self, *args, **kwargs):
        """Compare column names in a dictionnary of data frames
        to a reference data frame present under the key_ref"""
        # Reference key #
        key_ref = kwargs.get('key_ref')
        if key_ref is None: key_ref = "AT"
        # Message #
        print("Specific to this country, present in reference country: ", key_ref)
        # Get data #
        dict_of_df = self.concat_as_dict(*args, **kwargs)
        # Iterate #
        ref_columns = set(dict_of_df[key_ref].columns)
        comparison  = {iso2: set(df.columns) ^ ref_columns for iso2, df in dict_of_df.items()}
        # Print result #
        print(comparison)

