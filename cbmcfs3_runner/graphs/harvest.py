#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Written by Lucas Sinclair and Paul Rougieux.

JRC biomass Project.
Unit D1 Bioeconomy.
"""

# First party modules #
from plumbing.graphs import Graph

# Third party modules #
import seaborn

###############################################################################
class HarvestedWoodProducts(Graph):
    def plot(self, **kwargs):
        pass

###############################################################################
class HarvestExpectedProvided(Graph):
    def plot(self, **kwargs):
        # Data #
        self.df = (self.parent.post_processor.harvest.expected_provided
                    .query('DistTypeName != "Annual Processes"')
                    .groupby(['TimeStep', 'forest_type'])
                    .agg({'expected':'sum',
                          'provided':'sum'})
                    .reset_index())
        # Plot #
        fig = seaborn.FacetGrid(data=self.df, col='forest_type', sharey=False, col_wrap=4)
        fig.map(seaborn.scatterplot, 'TimeStep', 'expected', color='g')
        fig.map(seaborn.scatterplot, 'TimeStep', 'provided', color='r')
        # Save #
        self.save_plot(**kwargs)
