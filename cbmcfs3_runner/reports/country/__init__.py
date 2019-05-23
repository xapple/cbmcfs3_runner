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
        self.parent  = parent
        self.country = parent
        # Paths #
        self.output_path = self.parent.paths.pdf
        # Basic export path #
        self.outbox  = self.country.continent.paths.reports_dir
        self.outbox += 'countries/' + self.country.iso2_code + '.pdf'

    @property_cached
    def template(self): return CountryTemplate(self)

    def load_markdown(self):
        self.params = {'main_title': 'cbmcfs3\_runner - Country report'}
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

    #------------------------------ Inventory --------------------------------#
    def inventory_at_end_static(self):
        caption = "Inventory at the end of the static demand simulation."
        graph   = self.scenarios['static_demand'][0].graphs.inventory_at_end
        return str(ScaledFigure(graph=graph, caption=caption))

    def inventory_at_end_calib(self):
        caption = "Inventory at the end of the calibration simulation."
        graph   = self.scenarios['calibration'][0].graphs.inventory_at_end
        return str(ScaledFigure(graph=graph, caption=caption))

    def inventory_discrepancy(self):
        graph   = self.country.graphs.inventory_discrepancy
        return str(ScaledFigure(graph=graph, caption=graph.caption))

    #------------------------------ Stock --------------------------------#
    def merch_stock_at_start(self):
        graph   = self.country.graphs.merch_stock_at_start
        return str(ScaledFigure(graph=graph, caption=graph.caption))

    def merch_stock_at_end(self):
        graph   = self.country.graphs.merch_stock_at_end
        return str(ScaledFigure(graph=graph, caption=graph.caption))

    #------------------------------ Harvest ----------------------------------#
    def harvest_exp_pro_static(self):
        caption = ("Comparison of expected against provided harvest in the static demand scenario."
                   " Values are grouped into one plot for each disturbance type.")
        graph   = self.scenarios['static_demand'][0].graphs.harvest_expected_provided
        return str(ScaledFigure(graph=graph, caption=caption))

    def harvest_exp_pro_calib(self):
        caption = ("Comparison of expected against provided harvest in the calibration scenario."
                   " Values are grouped into one plot for each disturbance type.")
        graph   = self.scenarios['calibration'][0].graphs.harvest_expected_provided
        return str(ScaledFigure(graph=graph, caption=caption))

    def harvest_discrepancy(self):
        graph   = self.country.graphs.harvest_discrepancy
        return str(ScaledFigure(graph=graph, caption=graph.caption))

