#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Written by Lucas Sinclair and Paul Rougieux.

JRC biomass Project.
Unit D1 Bioeconomy.
"""

# Built-in modules #
import warnings, math

# First party modules #
from plumbing.graphs import Graph

# Third party modules #
import seaborn
import matplotlib
from matplotlib import pyplot

###############################################################################
class HarvestedWoodProducts(Graph):
    def plot(self, **kwargs):
        pass

###############################################################################
class HarvestExpectedProvided(Graph):
    def plot(self, **kwargs):
        # Columns #
        grp_cols = ['DistTypeName',
                    'year']

        agg_cols = {'expected': 'sum',
                    'provided': 'sum'}

        facet_col = 'DistTypeName'

        # Data #
        self.df = self.parent.post_processor.harvest.exp_prov_by_year
        self.df = self.df.groupby(grp_cols).agg(agg_cols).reset_index()

        # Colors #
        import brewer2mpl
        colors = brewer2mpl.get_map('Pastel1', 'qualitative', 3).mpl_colors
        name_to_color = {'Expected':   colors[1],
                         'Provided':   colors[0],
                         'Difference': 'blue'}

        # Facet grid #
        col_wrap = math.ceil(len(self.df[facet_col].unique()) / 8.0) + 1
        p = seaborn.FacetGrid(data     = self.df,
                              col      = facet_col,
                              sharey   = False,
                              col_wrap = col_wrap,
                              height   = 6.0)

        # Functions #
        def line_plot(x, y, **kwargs):
            axes = pyplot.gca()
            df = kwargs.pop("data")
            pyplot.plot(df[x], df[y], marker=".", markersize=10.0, **kwargs)

        def bar_plot(**kwargs):
            axes = pyplot.gca()
            df = kwargs.pop("data")
            delta = (df.expected - df.provided)
            pyplot.bar(x=df['year'], height=delta, bottom=df.provided, **kwargs)

        # Make the two skinny lines #
        p.map_dataframe(line_plot, 'year', 'provided', color=name_to_color['Provided'])
        p.map_dataframe(line_plot, 'year', 'expected', color=name_to_color['Expected'])

        # Make the fat bars #
        p.map_dataframe(bar_plot, color=name_to_color['Difference'])

        # Add a thousands separator #
        def formatter(**kw):
            from plumbing.common import split_thousands
            splitter = lambda x,pos: split_thousands(x)
            pyplot.gca().yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(splitter))
        p.map(formatter)

        # Change the axis limits for x #
        x_axis_min = self.df.year.min() - 1
        x_axis_max = self.df.year.max() + 1
        p.set(xlim=(x_axis_min , x_axis_max))

        # Check the auto-scale axis limits aren't too small for y #
        def autoscale_y(minimum=5.0, **kw):
            axes        = pyplot.gca()
            bottom, top = axes.get_ylim()
            delta       = top - bottom
            if delta < minimum:
                center = bottom + delta/2
                axes.set_ylim(center - minimum/2, center + minimum/2)
        p.map(autoscale_y)

        # Add a legend #
        patches = [matplotlib.patches.Patch(color=v, label=k) for k,v in name_to_color.items()]
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            p.add_legend(handles=patches)

        # Change the labels #
        p.set_axis_labels("Year (simulated)", "Volume in [m^3]") # TODO check units

        # Change the titles #
        p.set_titles(facet_col + " : {col_name}")

        # Save #
        self.save_plot(**kwargs)

###############################################################################
class HarvestDiscrepancy(Graph):
    def plot(self, **kwargs):
        # Columns #
        idx_cols = ['DistTypeName',
                    'year',
                    'forest_type',
                    'status', 'management_type', 'management_strategy']

        grp_cols = ['DistTypeName',
                    'year']

        agg_cols = {'delta': 'sum'}

        facet_col = 'DistTypeName'

        # Data #
        static = self.parent.scenarios['static_demand'][0].post_processor.harvest.exp_prov_by_year
        calibr = self.parent.scenarios['calibration'][0].post_processor.harvest.exp_prov_by_year

        # Filter the years that we don't use from the calibration scenario #
        max_year = static.year.max()
        selector = calibr['year'] <= max_year
        calibr   = calibr.loc[selector].copy()

        # Set index #
        static = static.set_index(idx_cols)
        calibr = calibr.set_index(idx_cols)

        # Difference #
        discrepancy = (calibr - static)
        discrepancy.delta = abs(discrepancy.delta)

        # Data frame #
        self.df = discrepancy.groupby(grp_cols).agg(agg_cols).reset_index()

        # Facet grid #
        col_wrap = math.ceil(len(self.df[facet_col].unique()) / 8.0) + 1
        p = seaborn.FacetGrid(data     = self.df,
                              col      = facet_col,
                              sharey   = False,
                              col_wrap = col_wrap,
                              height   = 6.0)

        # Functions #
        def bar_plot(x, y, **kw): pyplot.bar(x=x, height=y, **kw)

        # Make the bars #
        p.map_dataframe(bar_plot, 'year', 'delta', color='red')

        # Add a thousands separator #
        def formatter(**kwargs):
            from plumbing.common import split_thousands
            splitter = lambda x,pos: split_thousands(x)
            pyplot.gca().yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(splitter))
        p.map(formatter)

        # Change the axis limits for x #
        x_axis_min = self.df.year.min() - 1
        x_axis_max = self.df.year.max() + 1
        p.set(xlim=(x_axis_min , x_axis_max))

        # Check the auto-scale axis limits aren't too small for y #
        def autoscale_y(**kw):
            axes        = pyplot.gca()
            bottom, top = axes.get_ylim()
            if top < 2.0: axes.set_ylim(bottom, 2.0)
        p.map(autoscale_y)

        # Change the labels #
        p.set_axis_labels("Year (simulated)", "Volume in [m^3]")

        # Change the titles #
        p.set_titles("Type: {col_name}")

        # Save #
        self.save_plot(**kwargs)