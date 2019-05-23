#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Written by Lucas Sinclair and Paul Rougieux.

JRC biomass Project.
Unit D1 Bioeconomy.
"""

# Built-in modules #
import math

# First party modules #
from plumbing.graphs import Graph

# Third party modules #
import seaborn, brewer2mpl, matplotlib
from matplotlib import pyplot

###############################################################################
class MerchStock(Graph):

    @property
    def color(self):
        return brewer2mpl.get_map('Dark2', 'qualitative', 3).mpl_colors[1]

    @property
    def data(self):
        # Load tables #
        index = ['year', 'forest_type', 'conifers_bradleaves']
        static = self.static.inventory.sum_merch_stock.copy()
        calibr = self.calibr.inventory.sum_merch_stock.copy()
        # Append #
        static['scenario'] = 'static_demand'
        calibr['scenario'] = 'calibration'
        df = static.append(calibr)
        # Filter #
        self.year_to_plot = self.year_selection(df['year'].unique())
        selector          = df['year'] == self.year_to_plot
        df                = df.loc[selector].copy()
        # Return #
        return df

    @property
    def main_title(self):
        return 'Comparison of merchantable stock between static demand and calibration' % self.year_to_plot

    def plot(self, **kwargs):
        df = kwargs.pop("data")
        start, end  = df[self.age_cols[0]], df[self.age_cols[1]]
        center = start + (end - start) / 2
        height = df[self.value_col]
        pyplot.bar(x=center, height=height, width=self.width, **kwargs)

###############################################################################
class MerchStockAtStart(MerchStock):
    caption = "Merchantable stock at the beginning of the simulation."
    year_selection = lambda self, years: min(years)

class MerchStockAtEnd(MerchStock):
    caption = "Merchantable stock at the end of the simulation."
    year_selection = lambda self, years: max(years)
