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
class InventoryFacet(Graph):
    facet_var = 'forest_type'
    value_col = 'Area'
    age_cols  = ['age_start', 'age_end']

    year_selection = lambda self, years: max(years)
    color = brewer2mpl.get_map('Dark2', 'qualitative', 3).mpl_colors[0]

    @property
    def data(self):
        return self.parent.post_processor.inventory.bins_per_year

    @property
    def width(self):
        return self.parent.post_processor.inventory.bin_width

    @property
    def main_title(self):
        return 'Predicted inventory at year %i' % self.year_to_plot

    def plot(self, **kwargs):
        # Load data #
        self.df = self.data

        # Get the right year #
        self.year_to_plot = self.year_selection(self.df['year'].unique())
        selector     = self.df['year'] == self.year_to_plot
        self.df      = self.df.loc[selector].copy()

        # Facet grid #
        col_wrap = math.ceil(len(self.df[self.facet_var].unique()) / 8.0)+1
        p = seaborn.FacetGrid(data     = self.df,
                              col      = self.facet_var,
                              sharey   = False,
                              col_wrap = col_wrap,
                              height   = 6.0)

        # Functions #
        def bar_plot(**kwargs):
            df = kwargs.pop("data")
            start, end  = df[self.age_cols[0]], df[self.age_cols[1]]
            center = start + (end - start) / 2
            height = df[self.value_col]
            pyplot.bar(x=center, height=height, width=self.width, **kwargs)

        # Make the bars #
        p.map_dataframe(bar_plot, color=self.color)

        # Set the x ticks to the same width as the bins in years #
        def tick_freq(freq=self.width, **kw):
            func = pyplot.gca().xaxis.set_major_locator
            func(matplotlib.ticker.MultipleLocator(freq))
        p.map(tick_freq)

        # Add a thousands separator on the y axis #
        def formatter(**kw):
            from plumbing.common import split_thousands
            func     = lambda x,pos: split_thousands(x)
            splitter = matplotlib.ticker.FuncFormatter(func)
            pyplot.gca().yaxis.set_major_formatter(splitter)
        p.map(formatter)

        # Add horizontal lines on the y axis #
        grid_on = lambda **kw: pyplot.gca().yaxis.grid(True, linestyle=':')
        p.map(grid_on)

        # Check the auto-scale y axis limits aren't too small #
        def autoscale_y(**kw):
            axes        = pyplot.gca()
            bottom, top = axes.get_ylim()
            if top < 5.0: axes.set_ylim(0.0, 5.0)
        p.map(autoscale_y)

        # Change the labels #
        p.set_axis_labels("Age of forest in %i year bins" % self.width,
                          self.value_col + " in [hectares]") # TODO check units

        # Main plot main_title #
        pyplot.gcf().suptitle(self.main_title)

        # Change the titles for each facet #
        p.set_titles(self.facet_var.replace('_', ' ').title() + " : {col_name}")

        # Leave some space for the main main_title #
        pyplot.subplots_adjust(top=0.95)

        # Save #
        self.save_plot(**kwargs)

        # Return for display in notebooks for instance #
        return p

###############################################################################
class InventoryAtStart(InventoryFacet):
    caption = "Inventory at the beginning of the simulation."
    year_selection = lambda self, years: min(years)

class InventoryAtEnd(InventoryFacet):
    caption = "Inventory at the end of the simulation."
    pass

###############################################################################
class InventoryDiscrepancy(InventoryFacet):
    caption = ("Sum of total absolute discrepancy of predicted inventory at the"
               " end of the simulation between the two aforementioned scenarios.")

    color = brewer2mpl.get_map('Dark2', 'qualitative', 3).mpl_colors[1]

    @property
    def width(self):
        return self.parent.scenarios['static_demand'][0].post_processor.inventory.bin_width

    @property
    def data(self):
        # Columns #
        cols = self.age_cols+[self.facet_var]+['year']
        # Data #
        static = self.parent.scenarios['static_demand'][0].post_processor
        calibr = self.parent.scenarios['calibration'][0].post_processor
        static = static.inventory.bins_per_year.set_index(cols)
        calibr = calibr.inventory.bins_per_year.set_index(cols)
        # Subtract #
        return abs(static - calibr).reset_index()

    @property
    def main_title(self):
        return 'Absolute delta at year %i between static demand and calibration' % self.year_to_plot
