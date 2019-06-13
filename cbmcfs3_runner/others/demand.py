#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Written by Lucas Sinclair and Paul Rougieux.

JRC biomass Project.
Unit D1 Bioeconomy.
"""

# Built-in modules #

# First party modules #
from autopaths            import Path
from autopaths.auto_paths import AutoPaths
from plumbing.cache       import property_cached
from plumbing.databases.access_database import AccessDatabase

# Internal modules #

# Constants #
default_path = "/Program Files (x86)/Operational-Scale CBM-CFS3/Admin/DBs/ArchiveIndex_Beta_Install.mdb"
default_path = Path(default_path)

###############################################################################
class Demand(object):
    """
    This class enables us to switch the famous "ArchiveIndexDatabase", between
    the canadian standard and the European standard.
    """

    all_paths = """
    /orig/aidb_eu.mdb
    """

    def __init__(self, parent):
        # Default attributes #
        self.parent = parent
        # Automatically access paths based on a string of many subpaths #
        self.paths = AutoPaths(self.parent.data_dir, self.all_paths)

    def switch(self):
        default_path.remove()
        self.paths.aidb.copy(default_path)

    @property_cached
    def database(self):
        return AccessDatabase(self.paths.aidb)