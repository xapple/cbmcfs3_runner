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
class InventoryBarChart(Graph):
    caption = "Distribution of total area according to age"

    def plot(self, **kwargs):
        # Plot #
        seaborn.barplot(self.df.index, self.df['Area'])
        # Save #
        self.save_plot(**kwargs)

###############################################################################
class InputInventory(InventoryBarChart):
    def plot(self, **kwargs):
        self.df = self.parent.input_data.inventory
        self.df = self.df.set_index('Age').groupby('Age').sum()[['Area']]
        super(InputInventory, self).plot(**kwargs)

###############################################################################
class PredictedInventory(InventoryBarChart):
    def plot(self, **kwargs):
        self.timestep = self.parent.middle_processor.current_timestep
        self.df = self.parent.post_processor.inventory.simulated
        self.df = self.df.query('TimeStep == %i' % self.timestep)
        self.df = self.df.set_index('AveAge').groupby('AveAge').sum()[['Area']]
        super(PredictedInventory, self).plot(**kwargs)

###############################################################################
class InventoryScatter(Graph):
    def plot(self, **kwargs):
        # Data #
        self.df = self.parent.post_processor.inventory.simulated
        # Plot #
        seaborn.scatterplot(x='TimeStep', y='AveAge', hue='Area', data=self.df)
        # Save #
        self.save_plot(**kwargs)


