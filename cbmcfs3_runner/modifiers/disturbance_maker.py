#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Written by Lucas Sinclair and Paul Rougieux.

JRC biomass Project.
Unit D1 Bioeconomy.
"""

# Built-in modules #

# Third party modules #

# First party modules #
from autopaths.auto_paths import AutoPaths

# Internal modules #

###############################################################################
class DisturbanceMaker(object):
    """
    Will create new disturbances for the simulation period
    and modify the file input file "disturbance_events.csv".
    """

    all_paths = """
    /input/csv/disturbance_events.csv
    """

    def __init__(self, parent):
        # Default attributes #
        self.parent  = parent
        self.country = parent.country
        # Directories #
        self.paths = AutoPaths(self.parent.data_dir, self.all_paths)

    def __call__(self):
        self.add_events()

    @property
    def new_events(self):
        """Lorem ipsum."""
        # Load data #
        df = self.country.demand.df
        # Do it #
        pass
        # Return #
        return df

    def add_events(self):
        """Append the new disturbances to the disturbance file."""
        # Load data #
        df = self.new_events
        # Write the result #
        df.to_csv(str(self.paths.csv), mode='a', index=False)

