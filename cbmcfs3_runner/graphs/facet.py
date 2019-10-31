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
class FacetPlot(Graph):
    # Graph variables #
    facet_height = 6.0
    share_y      = False
    col_wrap     = 1
    auto_max_y   = 5.0

    @property
    def static(self):
        """The last step in the static_demand scenario for the same country."""
        return self.parent.scenarios['static_demand'][-1].post_processor

    @property
    def calibr(self):
        """The last step in the calibration scenario for the same country."""
        return self.parent.scenarios['calibration'][-1].post_processor

    def subplot(self, **kwargs):
        raise NotImplementedError()

    #-------------------------------------------------------------------------#
    def plot(self, **kwargs):
        # How many columns #
        if not hasattr(self, 'col_wrap'):
            self.col_wrap = math.ceil(len(self.df[self.facet_var].unique()) / 8.0)+1

        # The Facet Grib #
        p = seaborn.FacetGrid(data     = self.df,
                              col      = self.facet_var,
                              sharey   = self.share_y,
                              col_wrap = self.col_wrap,
                              height   = self.facet_height)

        # Make the subplots #
        p.map_dataframe(self.subplot)

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
        def auto_scale_y(**kw):
            axes        = pyplot.gca()
            bottom, top = axes.get_ylim()
            if top < self.auto_max_y: axes.set_ylim(0.0, self.auto_max_y)
        p.map(auto_scale_y)

        # Leave some space for the main main_title #
        pyplot.subplots_adjust(top=0.95)

        #--------------------------#
        # Change the labels #
        p.set_axis_labels("Age of forest in %i year bins" % self.width,
                          self.value_col + " in [hectares]") # TODO check units

        # Main plot main_title #
        if hasattr(self, 'main_title'):  pyplot.gcf().suptitle(self.main_title)

        # Change the titles for each facet #
        p.set_titles(self.facet_var.replace('_', ' ').title() + " : {col_name}")
        #----------------------------#

        # Save #
        self.save_plot(**kwargs)

        # Convenience: return for display in notebooks for instance #
        return p