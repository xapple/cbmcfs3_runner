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

# Third party modules #
from tabulate import tabulate

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

    @property
    def static_runner(self):
        return self.scenarios['static_demand'][-1]

    @property
    def calibr_runner(self):
        return self.scenarios['calibration'][-1]

    #------------------------------ Inventory --------------------------------#
    def inventory_at_end_static(self):
        caption = "Inventory at the end of the static demand simulation."
        graph   = self.static_runner.graphs.inventory_at_end
        return str(ScaledFigure(graph=graph, caption=caption))

    def inventory_at_end_calib(self):
        caption = "Inventory at the end of the calibration simulation."
        graph   = self.calibr_runner.graphs.inventory_at_end
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
    def harvest_exp_pro_vol_static(self):
        caption = ("Comparison of expected against provided harvest in the static demand scenario."
                   " Values are in volumes grouped into one plot for each disturbance type.")
        graph   = self.scenarios['static_demand'][0].graphs.harvest_exp_prov_vol
        return str(ScaledFigure(graph=graph, caption=caption))

    def harvest_exp_pro_area_static(self):
        caption = ("Comparison of expected against provided harvest in the static demand scenario."
                   " Values are in area grouped into one plot for each disturbance type.")
        graph   = self.scenarios['static_demand'][0].graphs.harvest_exp_prov_area
        return str(ScaledFigure(graph=graph, caption=caption))

    def harvest_exp_pro_vol_calib(self):
        caption = ("Comparison of expected against provided harvest in the calibration scenario."
                   " Values are in volumes grouped into one plot for each disturbance type.")
        graph   = self.scenarios['calibration'][0].graphs.harvest_exp_prov_vol
        return str(ScaledFigure(graph=graph, caption=caption))

    #------------------------------ Tables --------------------------------#
    def table_forest_type(self):
        return 0

    def table_disturbance_type(self):
        # New column names #
        names = {'dist_type_name':   'Disturbance ID',
                 'dist_desc_input': 'Description'}
        # Get the disturbances full name from their number #
        df = self.static_runner.input_data.disturbance_types
        df = df.rename(columns=names)
        df = df.set_index('Disturbance ID')
        # Make a string #
        table = tabulate(df, headers="keys", numalign="right", tablefmt="pipe")
        # Add a caption #
        return table + "\n\n   : Disturbance number and their corresponding description."
