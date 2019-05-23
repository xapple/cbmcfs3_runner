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
    sep = ('y')
    y_grid = True

    @property
    def static(self):
        """The last step in the static_demand scenario for the same country"""
        return self.parent.scenarios['static_demand'][-1].post_processor

    @property
    def calibr(self):
        """The last step in the calibration scenario for the same country"""
        return self.parent.scenarios['calibration'][-1].post_processor

    @property
    def main_title(self):
        return ('Comparison of merchantable stock between static demand'
                '\n and calibration at year %i' % self.year_to_plot)

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
        # Filter for year #
        self.year_to_plot = self.year_selection(df['year'].unique())
        selector          = df['year'] == self.year_to_plot
        df                = df.loc[selector].copy()
        # Filter for positive mass #
        selector = df['mass'] > 0.0
        df       = df.loc[selector].copy()
        # Switch to million of tons #
        df['mass'] = df['mass'] / 1e6
        # Return #
        return df

    def plot(self, **kwargs):
        # Plot #
        g = seaborn.catplot(x="forest_type", y="mass", hue="scenario",
                           data=self.data, kind="bar", palette="muted")
        # Adjust #
        g.despine(left=True)
        g.set_ylabels("Merchantable mass [million tons of carbon]")
        # Title #
        pyplot.subplots_adjust(top =0.90)
        pyplot.subplots_adjust(left=0.30)
        pyplot.gcf().suptitle(self.main_title)
        # Save #
        self.save_plot(**kwargs)
        # Return for display in notebooks for instance #
        return g

###############################################################################
class MerchStockAtStart(MerchStock):
    caption = "Total merchantable stock at the beginning of the simulation."
    year_selection = lambda self, years: min(years)

class MerchStockAtEnd(MerchStock):
    caption = "Total merchantable stock at the end of the simulation."
    year_selection = lambda self, years: max(years)
