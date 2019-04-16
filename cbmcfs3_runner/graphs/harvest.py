#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Written by Lucas Sinclair and Paul Rougieux.

JRC biomass Project.
Unit D1 Bioeconomy.
"""

# Third party modules #
import seaborn

# First party modules #
from plumbing.graphs import Graph

###############################################################################
class HarvestExpectedPredicted(Graph):
    def plot(self, **kwargs):
        seaborn.barplot(self.df.index, self.df['Area'])