#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Written by Lucas Sinclair and Paul Rougieux.

JRC biomass Project.
Unit D1 Bioeconomy.
"""

# Built-in modules #

# Third party modules #
import pandas

# First party modules #
from autopaths.auto_paths import AutoPaths
from plumbing.cache import property_cached

###############################################################################
class FusionData(object):
    """
    This class will provide access to the FUSION inventory data of a Country
    as a pandas dataframe. 
    
    The inventory from FUSION has the same format as 
    the inventory we feed to CBM.
    The only difference is that the forest protection status 'For' 
    are divided into 3 status of Availability for Wood Supply (AWS)
    'FNAWS', 'FRAWS' and 'FAWS' where NA means not available, 
    RA means restricted available and A means available. 
    """

    all_paths = """
    /fusion/back_inventory_aws.csv
    """

    def __init__(self, parent):
        # Default attributes #
        self.parent = parent
        # Directories #
        self.paths = AutoPaths(self.parent.data_dir, self.all_paths)

    def __getitem__(self, item):
        return pandas.read_csv(str(self.paths[item]))

    @property_cached
    def inventory_aws(self):
        """
        Inventory data loaded from the fusion back_inventory_aws.csv file
        Columns are:

            ['status', 'forest_type', 'region', 'management_type',
             'management_strategy', 'climatic_unit', 'conifers_broadleaves',
             'using_id', 'age', 'area', 'delay', 'unfcccl', 'hist_dist', 'last_dist',
             'age_class'],
        """
        df = self['back_inventory_aws']
        return df.rename(columns = self.parent.classifiers.mapping)
