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
class ScenarioReport(Document):
    """A report generated in PDF describing a scenario."""
    builtin_template = 'sinclair_bio'

    def __init__(self, parent):
        # Attributes #
        self.parent = parent
        # Paths #
        self.output_path = self.parent.paths.inventory_pdf

    @property_cached
    def template(self): return ScenarioTemplate(self)

    def generate(self):
        # Dynamic templates #
        self.markdown = unicode(self.template)
        # Render to latex #
        self.make_body()
        self.make_latex({'title': 'Scenario report'})
        self.make_pdf(safe=False)

###############################################################################
class ScenarioTemplate(ReportTemplate):
    """All the parameters to be rendered in the markdown template."""
    delimiters = (u'{{', u'}}')

    def __repr__(self): return '<%s object on %s>' % (self.__class__.__name__, self.parent)

    def __init__(self):
        pass