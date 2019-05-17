#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Written by Lucas Sinclair and Paul Rougieux.

JRC biomass Project.
Unit D1 Bioeconomy.
"""

# Futures #
from __future__ import division

# Built-in modules #

# Internal modules #
from cbmcfs3_runner.reports.base_template import ReportTemplate

# First party modules #
from plumbing.cache    import property_cached
from pymarktex         import Document
from pymarktex.figures import ScaledFigure

###############################################################################
class RunnerReport(Document):
    """A report generated in PDF describing a single CBM-CFS3 simulation
    and its results."""

    builtin_template = 'sinclair_bio'

    def __init__(self, parent):
        # Attributes #
        self.parent = parent
        self.runner = parent
        # Paths #
        self.output_path = self.parent.paths.pdf

    @property_cached
    def template(self): return RunnerTemplate(self)

    def load_markdown(self):
        self.params = {'title': 'Runner report'}
        self.markdown = str(self.template)

###############################################################################
class RunnerTemplate(ReportTemplate):
    """All the parameters to be rendered in the markdown template."""

    delimiters = (u'{{', u'}}')

    def __repr__(self): return '<%s object on %s>' % (self.__class__.__name__, self.parent)

    def __init__(self, parent):
        # Attributes #
        self.parent = parent
        self.report = parent
        self.runner = self.report.parent
        self.graphs = self.runner.graphs
        self.scenario = self.report.parent

    def short_name(self):
        return self.runner.short_name

    def is_calibration(self):
        return self.runner.scenario.short_name == 'calibration'

    def log_tail(self):
        if not self.runner.paths.log: return ""
        return self.runner.paths.log.pretty_tail

    #------------------------------ Inventory --------------------------------#
    def inventory_at_start(self):
        graph   = self.graphs.inventory_at_start
        return str(ScaledFigure(graph=graph, caption=graph.caption))

    def inventory_at_end(self):
        graph   = self.graphs.inventory_at_end
        return str(ScaledFigure(graph=graph, caption=graph.caption))

    #------------------------------ Harvest ----------------------------------#
    def harvested_wood_prodcuts(self):
        return 0

    def harvest_expected_provided(self):
        caption = "Comparision of expected against provided harvest"
        graph   = self.graphs.harvest_expected_provided
        return str(ScaledFigure(graph=graph, caption=caption))


