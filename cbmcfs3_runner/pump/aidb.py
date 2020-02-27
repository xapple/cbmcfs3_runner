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
from plumbing.dataframes import multi_index_pivot

# Constants #
default_path = "/Program Files (x86)/Operational-Scale CBM-CFS3/Admin/DBs/ArchiveIndex_Beta_Install.mdb"
default_path = Path(default_path)

###############################################################################
class AIDB(object):
    """
    This class enables us to switch the famous "ArchiveIndexDatabase", between
    the Canadian standard and the European standard.
    It also provides access to the data within this database.
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
    def dm_table(self):
        """Main disturbance matrix."""
        # Load #
        df = self.database['tblDM']
        # Rename #
        df = df.rename(columns={       "name": "dist_desc_dm",
                                "description": "dist_desc_long"})
        # Return #
        return df

    @property_cached
    def source(self):
        """Name of source pools."""
        # Load #
        df = self.database['tblSourceName']
        # Rename #
        df = df.rename(columns={        'row': 'dm_row',
                                'description': 'row_pool'})
        # Return #
        return df

    @property_cached
    def sink(self):
        """Name of sink pools."""
        # Load #
        df = self.database['tblSinkName']
        # Rename #
        df = df.rename(columns={     'column': 'dm_column',
                                'description': 'column_pool'})
        # Return #
        return df

    @property_cached
    def lookup(self):
        """Proportion by source and sink."""
        # Load #
        df = self.database['tblDMValuesLookup']
        # Return #
        return df

    @property_cached
    def dist_type_default(self):
        """Link between dist_type_id and dist_desc_aidb."""
        # Load #
        df = self.database['tbldisturbancetypedefault']
        # Rename #
        df = df.rename(columns = {'dist_type_name': 'dist_desc_aidb'})
        # Return #
        return df

    @property_cached
    def dm_assoc_default(self):
        """
        Link between default_dist_type_id, default_ec_id, and dmid

        Pay attention to the tricky annual_order which might generate
        errors in some cases (see also libcbm aidb import efforts)

        Shape in the EU AIDB: 110180 rows × 6 columns
        """
        # Load #
        df = self.database['tbldmassociationdefault']
        # Rename #
        # TODO, check if dist_type_id is exactly the correct name
        df = df.rename(columns = {'default_disturbance_type_id': 'dist_type_id',
                                                         'name': 'assoc_name',
                                                  'description': 'assoc_desc'})
        # Return #
        return df

    @property_cached
    def dm_assoc_default_short(self):
        """Same as above but with any "Annual order" > 1 dropped."""
        # Load #
        df = self.dm_assoc_default
        # Collapse #
        df = df.query("annual_order < 2").copy()
        # Check that the combination of dist_type_id and dmid
        # is unique on dist_type_id
        a = len(set(df['dist_type_id']))
        b = len(df[['dmid', 'dist_type_id']].drop_duplicates())
        assert a == b
        # Keep only a couple columns #
        df = df[['dmid', 'dist_type_id']].drop_duplicates()
        # Return #
        return df

    @property_cached
    def dm_assoc_spu_default(self):
        """
        Link between default_dist_type_id, spuid and dmid.
        Warning, it contains only wildfire distances in the EU AIDB.

        Shape in the EU aidb: 920 rows × 6 columns
        """
        # Load #
        df = self.database['tbldmassociationspudefault']
        # Rename
        # TODO check if dist_type_id is exactly the correct name
        df = df.rename(columns = {'default_disturbance_type_id': 'dist_type_id',
                                                         'name': 'spu_name',
                                                  'description': 'spu_desc'})
        # Return #
        return df

    @property_cached
    def dist_matrix_long(self):
        """
        Recreates the disturbance matrix in long format.
        Join lookup and the disturbance matrix table 'tblDM',
        Then join source and sink to add description of the origin and destination pools.
        To be continued based on /notebooks/disturbance_matrix.ipynb

        There is a many-to-one relationship between dist_type_name and dmid
        (disturbance matrix id),
        i.e for each dist_type_name there is one and only one dmid.
        The opposite is not true, as there are more dist_type_name than dmid.

        Columns are:

            ['dist_desc_input', 'dist_desc_aidb', 'dist_type_id', 'dmid',
             'dm_column', 'dm_structure_id', 'dm_row', 'proportion', 'dist_desc_dm',
             'dist_desc_long', 'row_pool', 'column_pool', 'on_off_switch',
             'description', 'is_stand_replacing', 'is_multi_year',
             'multi_year_count', 'dist_type_name'],
        """
        # Load tables from the aidb #
        dm_table     = self.dm_table
        source       = self.source
        sink         = self.sink
        lookup       = self.lookup
        assoc_short  = self.dm_assoc_default_short
        dist_default = self.dist_type_default
        # Load tables from orig_data #
        map_disturbance = self.parent.associations.map_disturbance
        dist_types      = self.parent.orig_data.disturbance_types
        # Join lookup and dm_table to add the description for each `dmid` #
        dm_lookup = (lookup
                     .set_index('dmid')
                     .join(dm_table.set_index('dmid'))
                     .reset_index())
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
        # Add 'dist_type_name' corresponding to orig/disturbance_types.csv
        df = df.left_join(assoc_short,     'dmid')
        df = df.left_join(dist_default,    'dist_type_id')
        df = df.left_join(map_disturbance, 'dist_desc_aidb')
        df = df.left_join(dist_types,      'dist_desc_input')
        # Return #
        return df

    @property_cached
    def dist_matrix(self):
        """
        The disturbance matrix is reshaped in the form of a matrix
        with source pools in rows and sink pools in columns.
        """
        # Load #
        df = self.dist_matrix_long.copy()
        # Make pool description columns suitable as column names #
        # Adds a number at the end of the disturbance name #
        df['row_pool']    = (df['row_pool'].str.replace(' ', '_') + '_' +
                             df['dm_row'].astype(str))
        df['column_pool'] = (df['column_pool'].str.replace(' ','_') + '_' +
                             df['dm_column'].astype(str))
        # Filter proportions #
        # TODO correct missing name from the index (see HU for example)
        index = ['dmid', 'dm_structure_id', 'dm_row', 'name', 'row_pool']
        df = (df
              .set_index(index)
              .query('proportion>0'))
        # Pivot #
        df = multi_index_pivot(df, columns='column_pool', values='proportion')
        # Reorder columns by the last digit number
        col_order = sorted(df.columns,
                           key=lambda x: str(x).replace("_", "0")[-2:])
        # Exclude index columns from the re-ordering of columns
        df = df.set_index(index)[col_order[:-5]].reset_index()
        # Return #
        return df

    @property_cached
    def merch_biom_rem(self):
        """
        Retrieve the percentage of merchantable biomass removed
        from every different disturbance type used in the silviculture
        treatments.

        The column "perc_merch_biom_rem" comes from silviculture.csv
        The column "proportion" comes from aidb.mdb and multiple joins.
        """
        # Load #
        df         = self.dist_matrix_long
        dist_types = self.parent.orig_data.disturbance_types
        treats     = self.parent.silviculture.treatments
        # Filter dist_mat to take only disturbances that are actually used #
        selector = df['dist_type_name'].isin(dist_types['dist_type_name'])
        df = df[selector].copy()
        # Take only products #
        df = df.query("column_pool == 'products'")
        df = df.query("row_pool == 'Softwood merchantable' or row_pool == 'Hardwood merch'")
        # Join #
        df = treats.left_join(df, 'dist_type_name')
        # Take columns of interest #
        cols = ['dist_type_name', 'perc_merch_biom_rem', 'dist_desc_aidb', 'row_pool', 'proportion']
        df = df[cols]
        # Compute difference #
        df['diff']= df['perc_merch_biom_rem'] - df['proportion']
        # NaNs appear because of natural disturbances #
        df = df.fillna(0)
        # Check #
        assert all(df['diff'].abs() < 1e-3)
        # Return #
        return df

    @property_cached
    def dmid_map(self):
        """Map the dist_type_name to its dmid for the current country.
           Only returns the unique available combinations
           of dmid and dist_type_name.
           Note two dist_type_name can map to the same dmid.

           Columns:
               ['dist_type_name', 'dmid', 'dist_desc_aidb']
        """
        # Load #
        dist_mat   = self.dist_matrix_long
        # Keep only two columns #
        columns_of_interest = ['dist_type_name', 'dmid', 'dist_desc_aidb']
        df = dist_mat[columns_of_interest].drop_duplicates()
        # Check #
        #assert not any(df['dmid'] == numpy.nan)
        # Return #
        return df