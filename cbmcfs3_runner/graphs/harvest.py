#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Written by Lucas Sinclair and Paul Rougieux.

JRC biomass Project.
Unit D1 Bioeconomy.
"""

# Built-in modules #
import warnings

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
                    'TimeStep']
        agg_cols = {'expected': 'sum',
                    'provided': 'sum'}

        # Data #
        self.df = self.parent.post_processor.harvest.expected_provided
        self.df = self.df.groupby(grp_cols).agg(agg_cols).reset_index()

        # Colors #
        import brewer2mpl
        colors = brewer2mpl.get_map('Pastel1', 'qualitative', 3).mpl_colors
        name_to_color = {'Expected':   colors[1],
                         'Provided':   colors[0],
                         'Difference': 'blue'}

        # Facet grid #
        p = seaborn.FacetGrid(data=self.df, col='DistTypeName', sharey=False, col_wrap=2, height=6.0)

        # Functions #
        def line_plot(x, y, **kwargs):
            axes = pyplot.gca()
            df = kwargs.pop("data")
            df.plot.line(x=x, y=y, ax=axes, grid=False,  marker=".", markersize =10.0, **kwargs)

        def bar_plot(**kwargs):
            axes = pyplot.gca()
            df = kwargs.pop("data")
            delta = (df.expected - df.provided)
            pyplot.bar(x=df.TimeStep, height=delta, bottom=df.provided, **kwargs)

        # Make the two skinny lines #
        p.map_dataframe(line_plot, 'TimeStep', 'provided', color=name_to_color['Provided'])
        p.map_dataframe(line_plot, 'TimeStep', 'expected', color=name_to_color['Expected'])

        # Make the fat bars #
        p.map_dataframe(bar_plot, color=name_to_color['Difference'])

        # Add a thousands separator #
        def formatter(**kwargs):
            from plumbing.common import split_thousands
            splitter = lambda x,pos: split_thousands(x)
            pyplot.gca().yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(splitter))
        p.map(formatter)

        # Change the axis limits #
        p.set(xlim=(self.df.TimeStep.min() - 1 , self.df.TimeStep.max() + 1))

        # Add a legend #
        patches = [matplotlib.patches.Patch(color=v, label=k) for k,v in name_to_color.items()]
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            p.add_legend(handles=patches)

        # Change the labels #
        p.set_axis_labels("Time step", "Volume in [m^3]")

        # Change the titles #
        p.set_titles("Type: {col_name}")

        # Save #
        self.save_plot(**kwargs)
