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
class InventoryBarChart(Graph):
    def plot(self, **kwargs):
        seaborn.barplot(self.df.index, self.df['Area'])

###############################################################################
class InputInventory(InventoryBarChart):
    def plot(self, **kwargs):
        self.df = self.parent.parent.input_data.inventory
        self.df = self.df.set_index('Age').groupby('Age').sum()[['Area']]
        super(InputInventory, self).plot(**kwargs)

###############################################################################
class PredictedInventory(InventoryBarChart):
    def plot(self, **kwargs):
        self.df = self.parent.parent.post_processor.predicted_inventory
        self.df = self.df.query('TimeStep == 89')
        self.df = self.df.set_index('AveAge').groupby('AveAge').sum()[['Area']]
        super(PredictedInventory, self).plot(**kwargs)

###############################################################################
class InventoryScatter(Graph):
    def plot(self, **kwargs):
        self.df = self.parent.parent.post_processor.predicted_inventory
        seaborn.scatterplot(x='TimeStep', y='AveAge', hue='Area', data=self.df)

