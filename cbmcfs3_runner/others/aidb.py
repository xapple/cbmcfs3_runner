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
class AIDB(object):
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

    @property_cached    
    def dist_matrix_long(self):
        """Disturbnace matrix in long format"""
        # To be continued based on 
        # /notebooks/disturbance_matrix.ipynb
        dmtabl = self.database['tblDM']
        source = self.database['tblSourceName']
        sink   = self.database['tblsinkname']
        lookup = self.database['tblDMValuesLookup']
        source = source.rename(columns={'Row':'DMRow', 'Description':'row_pool'})
        index_source = ['DMRow', 'DMStructureID']
        sink = sink.rename(columns={'Column':'DMColumn', 'Description':'column_pool'})
        index_sink = ['DMColumn', 'DMStructureID']
        dist_matrix_long = (dm_lookup
                        .set_index(index_source)
                        .join(source.set_index(index_source))
                        .reset_index()
                        .set_index(index_sink)
                        .join(sink.set_index(index_sink))
                        .reset_index()
                        .query('Name in @disturbance_names'))
        dist_matrix_long.head()
        
        # Make pool description columns suitable as column names 
        dist_matrix_long['row_pool'] = (dist_matrix_long['row_pool'].str.replace(' ', '_') + '_' + 
                                    dist_matrix_long['DMRow'].astype(str))
        dist_matrix_long['column_pool'] = (dist_matrix_long['column_pool'].str.replace(' ','_') + '_' + 
                                       dist_matrix_long['DMColumn'].astype(str))
        dist_matrix_long['Name'] = (dist_matrix_long['Name'].str.replace(' ','_'))
