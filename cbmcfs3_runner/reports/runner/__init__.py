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

    def short_name(self):
        return self.runner.data_dir.directory.name

    def log_tail(self):
        return self.runner.summary

    def aaaaa(self):
        caption = "Distribution of total area according to age"
        path    = self.graphs.input_inventory.path
        label   = "input_inventory"
        return str(ScaledFigure(path, caption, label))

    def input_inventory(self): return 0

    def predicted_inventory(self): return 0