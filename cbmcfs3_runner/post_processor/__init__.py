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
from plumbing.databases.access_database import AccessDatabase
from plumbing.cache       import property_cached
from autopaths.auto_paths import AutoPaths

# Internal modules #
from cbmcfs3_runner.post_processor.harvest      import Harvest
from cbmcfs3_runner.post_processor.inventory    import Inventory
from cbmcfs3_runner.post_processor.products     import Products

###############################################################################
class PostProcessor(object):
    """
    Provides access to the Access database.
    Computes aggregates and joins to facilitate analysis.
    """

    all_paths = """
    /output/cbm/project.mdb
    """

    def __init__(self, parent):
        # Default attributes #
        self.parent = parent
        # Directories #
        self.paths = AutoPaths(self.parent.data_dir, self.all_paths)

    def __call__(self):
        self.harvest.check_exp_prov()

    def sanitize_names(self, name):
        """Remove spaces and slashes from column names."""
        return name.lower().replace(' ', '_').replace('/','_')

    @property
    def database(self):
        """The CBM database, after the model is run."""
        database = AccessDatabase(self.paths.mdb)
        database.convert_col_names_to_snake = True
        return database

    @property_cached
    def classifiers(self):
        """
        Creates a mapping between 'user_defd_class_set_id'
        and the classifiers values present in the CBM output data:

         * species, site_quality and forest_type in tutorial six
         * status, forest_type, region, management_type, management_strategy, climatic_unit, conifers_broadleaves
         in the European dataset

         Columns are: ['user_defd_class_id', 'status', 'forest_type', 'region', 'management_type',
                       'management_strategy', 'climatic_unit', 'conifers_broadleaves']
        """
        # Load the three tables we will need #
        user_classes           = self.database["tblUserDefdClasses"]
        user_sub_classes       = self.database["tblUserDefdSubclasses"]
        user_class_sets_values = self.database["tblUserDefdClassSetValues"]
        # Join #
        index = ['user_defd_class_id', 'user_defd_subclass_id']
        classifiers = user_sub_classes.set_index(index)
        classifiers = classifiers.join(user_class_sets_values.set_index(index))
        # Unstack #
        index = ['user_defd_class_id', 'user_defd_class_set_id']
        classifiers = classifiers.reset_index().dropna().set_index(index)
        classifiers = classifiers[['user_defd_sub_class_name']].unstack('user_defd_class_id')
        # Rename #
        # This object will link: 1->species, 2->forest_type, etc.
        # TODO replace this with country.classifiers.mapping
        mapping = user_classes.set_index('user_defd_class_id')['class_desc']
        mapping = mapping.apply(self.sanitize_names)
        classifiers = classifiers.rename(mapping, axis=1)
        # Remove multilevel column index, replace by level(1) (second level)
        classifiers.columns = classifiers.columns.get_level_values(1)
        # Remove the confusing name #
        del classifiers.columns.name
        # In the calibration scenario we can't change names and there is a conflict #
        # This should not impact other scenarios hopefully #
        # C.f the "Broad/Conifers" to "Conifers/Bradleaves" problem in several countries #
        classifiers = classifiers.rename(columns={'broad_conifers': 'conifers_broadleaves'})
        # C.f the PL column problem #
        classifiers = classifiers.rename(columns={'natural_forest_region': 'management_type'})
        # Convert to categorical variables
        classifiers = classifiers.astype('category')
        # Reset the index
        classifiers = classifiers.reset_index()
        # Return result #
        return classifiers

    @property
    def coefficients(self):
        """Shortcut to the countries' conversion coefficients."""
        return self.parent.country.coefficients

    @property_cached
    def classifiers_coefs(self):
        """
        A join between the coefficients and the classifiers table.
        Later they can be joined on the flux indicators table using
        `user_defd_class_set_id` as an index.

        Columns are: ['index', 'forest_type', 'user_defd_class_set_id', 'status', 'region',
                      'management_type', 'management_strategy', 'climatic_unit',
                      'conifers_broadleaves', 'id', 'density', 'harvest_gr']
        """
        return self.classifiers.left_join(self.coefficients, 'forest_type')

    @property_cached
    def classifiers_mapping(self):
        return self.parent.country.classifiers.mapping

    @property_cached
    def classifiers_names(self):
        return self.parent.country.classifiers.names

    @property_cached
    def disturbance_type(self):
        columns_of_interest = ['dist_type_id', 'dist_type_name', 'description']
        df = self.database['tbldisturbancetype']
        return df[columns_of_interest]

    @property_cached
    def disturbances(self):
        """
        Load the disturbance table (input_data.disturbance_events)
        that was sent as an input to CBM for the particular simulation
        we are now analysing in the post processing step.

        This corresponds to the "expected" aspect of "expected_provided" harvest
        and will contain both Area ('A') and Mass ('M'). The units for 'M' are
        tons of carbon and hectares for 'A'.

        This method Prepares the disturbance table for joining operations with
        harvest tables.

        It could be a good idea to check why some countries have dist_type_name as int64
        and others have dist_type_name as object.

        Columns are: ['status', 'forest_type', 'region', 'management_type',
                      'management_strategy', 'climatic_unit', 'conifers_broadleaves',
                      'using_id', 'sw_start', 'sw_end', 'hw_start', 'hw_end', 'last_dist_id',
                      'efficiency', 'sort_type', 'measurement_type', 'amount', 'dist_type_name',
                      'time_step'],
        """
        # Load #
        df = self.parent.input_data.disturbance_events
        # Rename classifier columns _1, _2, _3 to forest_type, region, etc. #
        df = df.rename(columns = self.classifiers_mapping)
        # C.f the PL column problem #
        df = df.rename(columns = {'natural_forest_region': 'management_type'})
        # This column also need to be manually renamed #
        df = df.rename(columns = {'step': 'time_step'})
        # For joining with other data frames, DistType has to be of dtype object not int64 #
        df['dist_type_name'] = df['dist_type_name'].astype(str)
        # Remove columns that are not really used #
        df = df.drop(columns=[c for c in df.columns if c.startswith("Min") or c.startswith("Max")])
        # Remove slashes #
        df = df.rename(columns=lambda n:n.replace('/','_'))
        # dist_type_name is actually dist_type_name #
        df = df.rename(columns = {'dist_type_name': 'dist_type_name'})
        # Return result #
        return df

    @property_cached
    def flux_indicators(self):
        """
        Load the flux indicators table add dist_type_name, classifiers and
        coefficients.
        """
        # Load tables #
        flux_indicators  = self.database['tblFluxIndicators']
        disturbance_type = self.database['tblDisturbanceType']
        coefficients     = self.classifiers_coefs
        # Ungrouped #
        df = flux_indicators.left_join(disturbance_type, 'dist_type_id')
        df = df.left_join(coefficients, 'user_defd_class_set_id')
        # Return #
        return df

    # Do not cache since it can be re-computed trivially from the above
    @property
    def flux_indicators_long(self):
        """Flux table unpivoted to a long format. """
        df = self.flux_indicators
        # TODO: add missing variables to the index,
        # in a similar way to the pool_indicators_long table below.
        index = self.classifiers_names
        df = df.melt(id_vars = index,
                     var_name = 'pool',
                     value_name = 'tc')
        return df

    @property_cached
    def pool_indicators(self):
        """Load the pool indicators table, add classifiers."""
        # Load tables #
        pool  = self.database["tblPoolIndicators"]
        clifr = self.classifiers
        # Set indexes #
        index = 'user_defd_class_set_id'
        pool  = pool.set_index(index)
        clifr = clifr.set_index(index)
        # Join #
        return pool.join(clifr)

    # Do not cache since it can be re-computed trivially from the above
    @property
    def pool_indicators_long(self):
        """Pool indicators table in long format.
        The melt (aka. unpivot) operation leaves classifiers as
        index variables and keeps only 2 extra columns containing the
        pool name (pool) and the total carbon weight (tc).
        """
        df = self.pool_indicators
        additional_ids = ['time_step', 'spuid', 'land_class_id', 'pool_ind_id']
        # Convert additional indexes to categorical variables
        df[additional_ids] = df[additional_ids].astype('category')
        # Pivot to a long format
        index = self.classifiers_names + additional_ids
        df = df.melt(id_vars = index,
                     var_name='pool',
                     value_name='tc')
        return df

    #-------------------------------------------------------------------------#
    @property_cached
    def inventory(self):
        return Inventory(self)

    @property_cached
    def harvest(self):
        return Harvest(self)

    @property_cached
    def products(self):
        return Products(self)
