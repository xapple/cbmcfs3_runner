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
        self.paths = AutoPaths(self.parent.parent.data_dir, self.all_paths)

    @property_cached
    def check(self):
        """
        Converts flux indicators in tons of carbon to harvested
        wood products volumes in cubic meters of wood.

        Based on Roberto's query `Harvest analysis check` visible in the original calibration database.
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
        df = (ungrouped
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
                    'HardProduction': 'sum'})
              .reset_index())
        df['TC'] = df.SoftProduction + df.HardProduction
        df['Vol_Merch'] =  (df.TC*2)/df.db
        df['Vol_SubMerch'] = (df.CO2Production*2)/df.db
        df['Vol_Snags'] = (df.DOMProduction*2)/df.db
        df['Forest_residues_Vol'] = ((df.MerchLitterInput + df.OthLitterInput) * 2)/df.db
        return(df)


    @property_cached
    def summary_check(self):
        """
        Based on Roberto's query `Harvest summay check` visible in the original calibration database.
        """
        # Load tables #
        disturbance_type = self.parent.database['tblDisturbanceType']
        # Compute #
        df = (self.check
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
        df['tot_vol'] = df.Vol_Merch + df.Vol_Snags + df.Vol_SubMerch
        # Return result #
        return df

    @property_cached
    def total(self):
        """
        Based on Roberto's query `TOT_Harvest` visible in the original calibration database.
        """
        # Load tables #
        disturbance_type = self.parent.database['tblDisturbanceType']
        # Compute #
        df = (self.check
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
        df['tot_vol'] = df.Vol_Merch + df.Vol_SubMerch + df.Vol_Snags
        # Return result #
        return df

    @property_cached
    def expected_provided(self):
        """
        Compares the amount of harvest requested in the disturbance tables (an input to the simulation)
        to the amount of harvest actually performed by the model (extracted from the flux indicator table).

        Based on Roberto's query `Harvest_expected_provided` visible in the original calibration database.

        See notebook "simulated_harvest.ipynb" for more details.
        """
        # Load tables #
        disturbances = self.parent.parent.input_data.disturbance_events
        user_classes = self.parent.database['tblUserDefdClasses']
        # Rename classifier columns in the disturbance table
        # Add an underscore to the classifier number so it can be used for renaming #
        user_classes['id'] = '_' + user_classes.UserDefdClassID.astype(str)
        user_classes = user_classes.set_index('id')['ClassDesc']
        user_classes = user_classes.apply(lambda x: x.lower().replace(' ', '_'))
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
        df = (self.summary_check
              .set_index(index)
              .join(disturbances.set_index(index)))
        df = (df
              .groupby(index)
              .agg({'Amount':'sum',
                    'TC':    'sum'})
              .rename(columns = {'Amount': 'expected',
                                 'TC':     'provided'})
              .reset_index())
        # Add the difference column #
        df['delta'] = (df.provided - df.expected) / df.expected * 100
        # Return result #
        return df