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
class CountryReport(Document):
    """A report generated in PDF describing a country and
    results from several scenarios."""

    builtin_template = 'sinclair_bio'

    def __init__(self, parent):
        # Attributes #
        self.parent = parent
        self.runner = parent
        # Paths #
        self.output_path = self.parent.paths.pdf

    @property_cached
    def template(self): return CountryTemplate(self)

    def load_markdown(self):
        self.params = {'title': 'Country report'}
        self.markdown = str(self.template)

###############################################################################
class CountryTemplate(ReportTemplate):
    """All the parameters to be rendered in the markdown template."""

    delimiters = (u'{{', u'}}')

    def __repr__(self): return '<%s object on %s>' % (self.__class__.__name__, self.parent)

    def __init__(self, parent):
        # Attributes #
        self.parent = parent
        self.report = parent
        self.country = self.report.parent
        self.scenarios = self.country.scenarios

    def iso2_code(self):
        return self.country.iso2_code

    def short_name(self):
        return self.country.country_name

    def harvest_exp_pro_static(self):
        caption = "Comparision of expected against provided harvest in the static demand scenario."
        graph   = self.scenarios['static_demand'][0].graphs.harvest_expected_provided
        return str(ScaledFigure(graph=graph, caption=caption))

    def harvest_exp_pro_calib(self):
        caption = "Comparision of expected against provided harvest in the calibration scenario."
        graph   = self.scenarios['calibration'][0].graphs.harvest_expected_provided
        return str(ScaledFigure(graph=graph, caption=caption))
