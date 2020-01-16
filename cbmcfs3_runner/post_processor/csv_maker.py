#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Written by Lucas Sinclair and Paul Rougieux.

JRC biomass Project.
Unit D1 Bioeconomy.
"""

# Built-in modules #

# Third party modules #

# First party modules #
from autopaths.auto_paths import AutoPaths

# Internal modules #

# Internal modules

###############################################################################
class CSVMaker(object):
    """
    Is responsible for creating CSV files from different tables that can be
    accessed from the post processor of the CBM-CFS3 output (different
    scenarios).
    """

    all_paths = """
    /output/csv/ipcc_pools.csv
    /output/csv/inventory_age.csv
    """

    def __init__(self, parent):
        # Record the post_processor #
        self.parent = parent
        # Directories #
        self.paths = AutoPaths(self.parent.parent.data_dir, self.all_paths)

    def __call__(self):
        """Export all tables."""
        self.export_ipcc_pools()

    def export_ipcc_pools(self):
        """Export used by the land use change models LUISA and FUSION."""
        df = self.parent.ipcc.pool_indicators_long
        df.to_csv(str(self.paths.ipcc_pools),  index=False)

    def export_output_inventory(self):
        """Export used by the land use change models LUISA and FUSION."""
        df = self.parent.inventory.age_indicators
        df.to_csv(str(self.paths.inventory_age),  index=False)
