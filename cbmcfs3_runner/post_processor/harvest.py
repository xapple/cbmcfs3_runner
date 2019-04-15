#!/usr/bin/env python2
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
from plumbing.cache import property_cached
from autopaths.auto_paths import AutoPaths

# Internal modules #

###############################################################################
class Harvest(object):
    """
    See notebook "simulated_harvest.ipynb" for more details.
    """

    all_paths = """
    /output/harvest/
    """

    def __init__(self, parent):
        # Default attributes #
        self.parent = parent
        # Directories #
        self.paths = AutoPaths(self.parent.data_dir, self.all_paths)

    @property_cached
    def check(self):
        """
        Converts flux indicators in tons of carbon to harvested
        wood products volumes in cubic meters of wood.
        """
        # Load tables #
        flux_indicators  = self.parent.database['tblFluxIndicators']
        disturbance_type = self.parent.database['tblDisturbanceType']
        # First ungrouped #
        ungrouped = (flux_indicators
                     .set_index('DistTypeID')
                     .join(disturbance_type.set_index('DistTypeID'))
                     .reset_index()
                     .set_index('UserDefdClassSetID')
                     .join(self.parent.classifiers_coefs.reset_index().set_index('UserDefdClassSetID')))
        # Then group #
        return (ungrouped
                .groupby(['DistTypeID',
                          'TimeStep',
                          'status',
                          'forest_type',
                          'management_type',
                          'management_strategy',
                          'conifers_bradleaves',
                          # Not real grouping variables only here to keep them in the final table
                          'DOMProduction',
                          'CO2Production',
                          'MerchLitterInput',
                          'OthLitterInput',
                          'db'])
                .agg({'SoftProduction': 'sum',
                       'HardProduction':'sum'})
                .reset_index())

    @property_cached
    def summary_check(self):
        """
        Lorem ipsum.
        """
        # Load tables #
        disturbance_type = self.parent.database['tblDisturbanceType']
        # Compute #
        result = (self.check
                  .set_index('DistTypeID')
                  .join(disturbance_type.set_index('DistTypeID'))
                  .groupby(['DistTypeID',
                            'DistTypeName',
                            'TimeStep',
                            'status',
                            'forest_type',
                            'management_type',
                            'management_strategy'])
                  .agg({'Vol_Merch':           'sum',
                        'Vol_Snags':           'sum',
                        'Vol_SubMerch':        'sum',
                        'Forest_residues_Vol': 'sum',
                        'TC':                  'sum'})
                  .reset_index())
        # Add the total volume column #
        result['tot_vol'] = hs.Vol_Merch + hs.Vol_Snags + hs.Vol_SubMerch
        # Return result #
        return result

    @property_cached
    def total(self):
        """
        Lorem ipsum.
        """
        # Load tables #
        disturbance_type = self.parent.database['tblDisturbanceType']
        # Compute #
        result = (self.check
                  .set_index('DistTypeID')
                  .join(disturbance_type.set_index('DistTypeID'))
                  .groupby(['DistTypeName'])
                  .agg({'TC':                  'sum',
                        'Vol_Merch':           'sum',
                        'Vol_SubMerch':        'sum',
                        'Vol_Snags':           'sum',
                        'Forest_residues_Vol': 'sum'})
                  .reset_index())
        # Add the total volume column #
        result['tot_vol'] = th.Vol_Merch + th.Vol_SubMerch + th.Vol_Snags
        # Return result #
        return result

    @property_cached
    def expected_provided(self):
        """
        Lorem ipsum.
        """
        # Load tables #
        disturbances = self.parent.parent.input_data.disturbance_events
        user_classes = self.parent.database['tblUserDefdClasses']
        # Add an underscore to each cell #
        user_classes['id'] = '_' + user_classes.UserDefdClassID.astype(str)
        user_classes = user_classes.set_index('id')['ClassDesc']
        user_classes = user_classes.apply(lambda x: x.lower().replace(' ', '_'))
        # user_classes is a dict-like object #
        disturbances = disturbances.rename(columns = user_classes)
        disturbances = disturbances.rename(columns = {'Step':         'TimeStep',
                                                      'Dist_Type_ID': 'DistTypeName'})
        # Index columns to join disturbances and harvest check #
        index = ['status',
                 'TimeStep',
                 'DistTypeName',
                 'forest_type',
                 'management_type',
                 'management_strategy']
        result = (self.summary_check
                  .set_index(index)
                  .join(disturbances.set_index(index)))
        result = (result
                  .groupby(index)
                  .agg({'Amount':'sum',
                        'TC':    'sum'})
                  .rename(columns = {'Amount': 'expected',
                                     'TC':     'provided'})
                  .reset_index())
        # Add the difference column #
        result['delta'] = (result.provided - result.expected) / result.expected * 100
        # Return result #
        return result