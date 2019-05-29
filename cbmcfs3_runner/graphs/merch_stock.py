#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Written by Lucas Sinclair and Paul Rougieux.

JRC biomass Project.
Unit D1 Bioeconomy.
"""

# Built-in modules #

# First party modules #
from plumbing.graphs import Graph

# Third party modules #
import seaborn
from matplotlib import pyplot
import pandas

###############################################################################
class MerchStock(Graph):
    sep = ('y',)
    y_grid = True
    y_label = "Merchantable mass [million tons of carbon]"

    @property
    def title(self):
        return ('Comparison of merchantable stock between all scenarios'
                '\n at year %i' % self.year_to_plot)

    def get_sum_merch_stock(self, scenario):
        """ Extract the total merchantable stock for a given scenario"""
        # Here self.parent is a country
        p = self.parent.scenarios[scenario][-1].post_processor
        df = p.inventory.sum_merch_stock.copy()
        df['scenario'] = scenario
        return df

    @property
    def data(self):
        """Extract the total merchantable stock for all scenarios 
           and filter data for the plot.
           By default data is returned for all scenarios. 
           User can specify a list of scenarios as a property."""
        if not hasattr(self, 'scenario_names'):
            self.scenario_names = self.parent.scenarios.keys()
        merch = [self.get_sum_merch_stock(scen) for scen in self.scenario_names]
        df = pandas.concat(merch)
        df['mass_1e6'] = df['mass']/1e6
        # Filter for year #
        self.year_to_plot = self.year_selection(df['year'].unique())
        selector          = df['year'] == self.year_to_plot
        df                = df.loc[selector].copy()
        # Filter for positive mass #
        selector = df['mass'] > 0.0
        df       = df.loc[selector].copy()
        # Switch to million of tons #
        df['mass_1e6'] = df['mass'] / 1e6
        # Return #
        return df

    def plot(self, **kwargs):
        # Plot #
        g = seaborn.barplot(x="forest_type", y="mass_1e6", hue="scenario",
                            palette='dark', data=self.data)
        # Lines #
        pyplot.gca().yaxis.grid(True, linestyle=':')
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
