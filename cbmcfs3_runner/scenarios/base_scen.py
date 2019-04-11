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
