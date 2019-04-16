#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Written by Lucas Sinclair and Paul Rougieux.

JRC biomass Project.
Unit D1 Bioeconomy.
"""

# Third party modules #

# First party modules #
from plumbing.cache import property_cached
from autopaths.auto_paths import AutoPaths

# Internal modules #
from cbmcfs3_runner.graphs.inventory import InputInventory, PredictedInventory, InventoryScatter

###############################################################################
class Graphs(object):
    """
    This class will take care of creating all graphs and visualizations from both
    the input and output data.
    """

    all_paths = """
    /output/graphs/inventory/input_inventory.pdf
    /output/graphs/inventory/predicted_inventory.pdf
    /output/graphs/inventory/inventory_scatter.pdf
    """

    def __init__(self, parent):
        # Default attributes #
        self.parent = parent
        # Directories #
        self.paths = AutoPaths(self.parent.data_dir, self.all_paths)

    def __call__(self):
        self.input_inventory.plot_and_save()
        self.predicted_inventory.plot_and_save()
        self.inventory_scatter.plot_and_save()

    @property_cached
    def input_inventory(self):
        return InputInventory(self, self.paths.input_pdf)

    @property_cached
    def predicted_inventory(self):
        return PredictedInventory(self, self.paths.predicted_pdf)

    @property_cached
    def inventory_scatter(self):
        return InventoryScatter(self, self.paths.scatter_pdf)
