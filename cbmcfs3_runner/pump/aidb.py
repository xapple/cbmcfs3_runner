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
from autopaths            import Path
from autopaths.auto_paths import AutoPaths
from plumbing.cache       import property_cached
from plumbing.databases.access_database import AccessDatabase

# Internal modules #
from cbmcfs3_runner.pump import multi_index_pivot

# Constants #
default_path = "/Program Files (x86)/Operational-Scale CBM-CFS3/Admin/DBs/ArchiveIndex_Beta_Install.mdb"
default_path = Path(default_path)

###############################################################################
class AIDB(object):
    """
    This class enables us to switch the famous "ArchiveIndexDatabase", between
    the Canadian standard and the European standard.
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
        database = AccessDatabase(self.paths.aidb)
        database.convert_col_names_to_snake = True
        return database

    @property_cached
    def dist_matrix_long(self):
        """Recreates the disturbance matrix in long format.
        Join lookup and the disturbance matrix table 'tblDM',
        Then join source and sink to add description of the origin and destination pools.
        To be continued based on /notebooks/disturbance_matrix.ipynb
        """
        dm_table = self.database['tblDM']
        source   = self.database['tblSourceName']
        sink     = self.database['tblSinkName']
        lookup   = self.database['tblDMValuesLookup']
        # Join lookup and dm_table to add the description for each DMID #
        dm_lookup = (lookup
                     .set_index('dmid')
                     .join(dm_table.set_index('dmid'))
                     .reset_index())
        # Rename #
        source = source.rename(columns={'row':         'dm_row',
                                        'description': 'row_pool'})
        sink   = sink.rename(  columns={'column':      'dm_column',
                                        'description': 'column_pool'})
        # Indexes #
        index_source = ['dm_row',    'dm_structure_id']
        index_sink   = ['dm_column', 'dm_structure_id']
        # Add source and sink descriptions #
        df = (dm_lookup.set_index(index_source)
                       .join(source.set_index(index_source))
                       .reset_index()
                       .set_index(index_sink)
                       .join(sink.set_index(index_sink))
                       .reset_index())
        # Make pool description columns suitable as column names #
        # Adds a number at the end of the disturbance name #
        df['row_pool']    = (df['row_pool'].str.replace(' ', '_') + '_' +
                             df['dm_row'].astype(str))
        df['column_pool'] = (df['column_pool'].str.replace(' ','_') + '_' +
                             df['dm_column'].astype(str))
        # Return #
        return df

    @property_cached
    def dist_matrix(self):
        """Disturbance Matrix reshaped in the form of a matrix
        with source pools in rows and sink pools in columns."""
        index = ['dmid', 'dm_structure_id', 'dm_row', 'name', 'row_pool']
        df = (self.dist_matrix_long
              .set_index(index)
              .query('proportion>0'))
        df = multi_index_pivot(df, columns='column_pool', values='proportion')
        # Reorder columns by the last digit number
        col_order = sorted(df.columns,
                           key=lambda x: str(x).replace("_", "0")[-2:])
        # Exclude index columns from the re-ordering of columns
        df = df.set_index(index)[col_order[:-5]].reset_index()
        return df

