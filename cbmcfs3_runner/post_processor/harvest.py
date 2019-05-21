#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Written by Lucas Sinclair and Paul Rougieux.

JRC biomass Project.
Unit D1 Bioeconomy.
"""

# Built-in modules #

# Third party modules #
import numpy as np

# First party modules #
from plumbing.cache import property_cached
from autopaths.auto_paths import AutoPaths

# Internal modules #

###############################################################################
class Harvest(object):
    """
    See notebook "simulated_harvest.ipynb" for more details about the methods below.
    """

    all_paths = """
    /output/harvest/
    """

    def __init__(self, parent):
        # Default attributes #
        self.parent = parent
        # Directories #
        self.paths = AutoPaths(self.parent.parent.data_dir, self.all_paths)

    #-------------------------------------------------------------------------#
    @property_cached
    def check(self):
        """
        Converts flux indicators in tons of carbon to harvested
        wood products volumes in cubic meters of wood.

        Based on Roberto's query `Harvest analysis check` visible in the original calibration database.

        What are the units?
        """
        # Load tables #
        flux_indicators  = self.parent.database['tblFluxIndicators']
        disturbance_type = self.parent.database['tblDisturbanceType']
        coefficients     = self.parent.classifiers_coefs.reset_index()
        # First ungrouped #
        ungrouped = (flux_indicators
                     .set_index('DistTypeID')
                     .join(disturbance_type.set_index('DistTypeID'))
                     .reset_index()
                     .set_index('UserDefdClassSetID')
                     .join(coefficients.set_index('UserDefdClassSetID')))
        # Then group #
        df = (ungrouped
              .groupby(['DistTypeID',
                        'DistTypeName',
                        'TimeStep',
                        'status',
                        'forest_type',
                        'management_type',
                        'management_strategy',
                        'conifers_bradleaves',
                        # Not real grouping variables only here to keep them in the final table
                        # Their values should be unique for the all combination of the other grouping vars
                        # But in fact they are not! But we will group again later with other vars
                        'DOMProduction',
                        'CO2Production',
                        'MerchLitterInput',
                        'OthLitterInput',
                        'db'])
              .agg({'SoftProduction': 'sum',
                    'HardProduction': 'sum'})
              .reset_index())
        # Create new columns #
        df['TC']                  = df.SoftProduction + df.HardProduction
        df['Vol_Merch']           = (df.TC * 2) / df.db
        df['Vol_SubMerch']        = (df.CO2Production * 2) / df.db
        df['Vol_Snags']           = (df.DOMProduction * 2) / df.db
        df['Forest_residues_Vol'] = ((df.MerchLitterInput + df.OthLitterInput) * 2) / df.db
        # Return #
        return df

    #-------------------------------------------------------------------------#
    @property_cached
    def summary_check(self):
        """
        Based on Roberto's query `Harvest summary check` visible in the original calibration database.

        Columns are:    ['DistTypeID', 'DistTypeName', 'TimeStep', 'status', 'forest_type',
        (of the output)  'management_type', 'management_strategy', 'Vol_Merch', 'Vol_Snags',
                         'Vol_SubMerch', 'Forest_residues_Vol', 'TC', 'tot_vol']

        This corresponds to the "provided" aspect of "expected_provided" harvest.
        """
        # Compute #
        df = (self.check
              .set_index('DistTypeID')
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

    #-------------------------------------------------------------------------#
    @property_cached
    def total(self):
        """
        Based on Roberto's query `TOT_Harvest` visible in the original calibration database.

        Columns are: ['DistTypeName', 'TC', 'Vol_Merch', 'Vol_SubMerch', 'Vol_Snags',
                      'Forest_residues_Vol', 'tot_vol']
        """
        # Compute #
        df = (self.check
              .set_index('DistTypeID')
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

    #-------------------------------------------------------------------------#
    @property_cached
    def classifiers_mapping(self):
        """
        Map classifiers columns to a better descriptive name
        This mapping table will enable us to rename
        classifier columns _1, _2, _3 to forest_type, region, etc.
        """
        # Load user_classes table from DB #
        user_classes = self.parent.database['tblUserDefdClasses']
        # Add an underscore to the classifier number so it can be used for renaming #
        user_classes['id'] = '_' + user_classes.UserDefdClassID.astype(str)
        # This makes user_classes a pandas.Series linking "_1" to "forest_type" #
        user_classes = user_classes.set_index('id')['ClassDesc']
        user_classes = user_classes.apply(lambda x: x.lower().replace(' ', '_'))
        return user_classes

    #-------------------------------------------------------------------------#
    @property_cached
    def disturbances(self):
        """
        Prepare the disturbance table for join operation with harvest tables.
        It could be a good idea to check why some countries have DistTypeName as int64
        and others have DistTypeName as object.

        Columns are: ['status', 'forest_type', 'region', 'management_type',
                      'management_strategy', 'climatic_unit', 'conifers/bradleaves',
                      'UsingID', 'SWStart', 'SWEnd', 'HWStart', 'HWEnd', 'Last_Dist_ID',
                      'Efficency', 'Sort_Type', 'Measurement_type', 'Amount', 'DistTypeName',
                      'TimeStep'],

        This corresponds to the "expected" aspect of "expected_provided" harvest.
        """
        # Load disturbances table from excel file #
        df = self.parent.parent.input_data.disturbance_events
        # Rename classifier columns _1, _2, _3 to forest_type, region, etc. #
        df = df.rename(columns = self.classifiers_mapping)
        # C.f the PL column problem #
        df = df.rename(columns = {'natural_forest_region': 'management_type'})
        # These columns also need to be manually renamed #
        df = df.rename(columns = {'Step':         'TimeStep',
                                  'Dist_Type_ID': 'DistTypeName'})
        # For joining with other data frames, DistTypeName has to be of dtype object not int64 #
        df['DistTypeName'] = df['DistTypeName'].astype(str)
        # Remove columns that are not really used #
        df = df.drop(columns=[c for c in df.columns if c.startswith("Min") or c.startswith("Max")])
        # Return result #
        return df

    #-------------------------------------------------------------------------#
    @property_cached
    def expected_provided(self):
        """
        Compares the amount of harvest requested in the disturbance tables (an input to the simulation)
        to the amount of harvest actually performed by the model (extracted from the flux indicator table).

        Based on Roberto's query `Harvest_expected_provided` visible in the original calibration database.

        Columns are: ['status', 'TimeStep', 'DistTypeName', 'forest_type', 'management_type',
                      'management_strategy', 'expected', 'provided']
        """
        # Index columns to join disturbances and harvest check #
        index = ['status',
                 'TimeStep',
                 'DistTypeName',
                 'forest_type',
                 'management_type',
                 'management_strategy']
        # Set the same index on both data frames #
        df    = self.summary_check.set_index(index)
        dists = self.disturbances.set_index(index)
        # Do the join #
        df = (df.join(dists, how='outer'))
        # Sum two columns #
        df = (df
              .groupby(index)
              .agg({'Amount': 'sum',
                    'TC':     'sum'})
              .rename(columns = {'Amount': 'expected',
                                 'TC':     'provided'})
              .reset_index())
        # Return result #
        return df

    #-------------------------------------------------------------------------#
    @property_cached
    def exp_prov_by_year(self):
        """
        Same thing as above but with:
         - Years instead of TimeSteps
         - Rows where expected and provided are both zero removed
         - An extra column indicating the delta between expected and provided

        Columns are: ['year', 'DistTypeName', 'forest_type', 'expected', 'provided', 'delta'
                      'status', 'management_type', 'management_strategy'],
        """
        # Take a reference #
        df = self.expected_provided
        # Remove rows where both expected and provided are zero #
        selector = (df['expected'] == 0.0) & (df['provided'] == 0.0)
        df = df.loc[~selector].copy()
        # Add the delta column #
        df['delta'] = (df.expected - df.provided)
        # Add year and remove TimeStep #
        df['year'] = self.parent.timestep_to_years(df['TimeStep'])
        df = df.drop('TimeStep', axis=1)
        # Rename the disturbances from their number to their real name #
        mapping = self.parent.parent.input_data.disturbance_types
        mapping = mapping.set_index('DisturbanceTypeID')['Name']
        df = df.replace({'DistTypeName': mapping})
        # Only if we are in the calibration scenario #
        if self.parent.parent.scenario.short_name == 'calibration':
            # Patch the harvest data frame to stop at the simulation year #
            selector = df['year'] <= self.parent.parent.country.base_year
            df = df.loc[selector].copy()
        # Return result #
        return df

    #-------------------------------------------------------------------------#
    @property_cached
    def silviculture(self):
        """Prepare the silviculture table for joining operations with harvest tables."""
        df = self.parent.parent.country.silviculture.df
        df = df.rename(columns = self.classifiers_mapping)
        df = df.rename(columns = {'Dist_Type_ID':'DistTypeName'})
        # Change the type of DistTypeName to string so that it has the same type as
        # the harvest_check DistTypeName column
        df['DistTypeName'] = df['DistTypeName'].astype(str)
        return df

    #-------------------------------------------------------------------------#
    @property_cached
    def hwp_intermediate(self):
        """
        Intermediate table based on `self.check`.
        Joins disturbance id from the silviculture table
        to allocate specific disturbances to specific wood products.
        """
        join_index = ['DistTypeName',
                      'forest_type',
                      'management_type',
                      'management_strategy']
        silviculture_mod = self.silviculture[join_index + ['HWP']]
        df = (self.check
              .reset_index()
              .set_index(join_index)
              .join(silviculture_mod.set_index(join_index))
              .groupby(['TimeStep', 'HWP'])
              .agg({'Vol_Merch':'sum',
                    'Vol_SubMerch':'sum',
                    'Vol_Snags':'sum',
                    'TC':'sum'})
              .reset_index())
        return df

    #-------------------------------------------------------------------------#
    @property_cached
    def irw_b(self):
        """Harvest volumes of Industrial Round Wood Broadleaves."""
        df = (self.hwp_intermediate
              .query('HWP == "IRW_B"')
              .rename(columns={'Vol_Merch':'Vol_Merch_IRW_B',
                               'Vol_SubMerch':'Vol_SubMerch_IRW_B',
                               'Vol_Snags':'Vol_Snags_IRW_B',
                               'TC':'TC_IRW_B'}))
        # Drop hwp column
        # because it doesn't make sense anymore below when we join different products together
        df = df.drop('HWP', axis = 1)
        return df

    #-------------------------------------------------------------------------#
    @property_cached
    def irw_c(self):
        """Harvest volumes of Industrial Round Wood Coniferous."""
        df = (self.hwp_intermediate
              .query('HWP == "IRW_C"')
              .rename(columns={'Vol_Merch':'Vol_Merch_IRW_C',
                               'Vol_SubMerch':'Vol_SubMerch_IRW_C',
                               'Vol_Snags':'Vol_Snags_IRW_C',
                               'TC':'TC_IRW_C'}))
        df = df.drop('HWP', axis = 1)
        return df

    #-------------------------------------------------------------------------#
    @property_cached
    def fw_b(self):
        """Harvest volumes of Fuel Wood Broadleaves."""
        df = (self.hwp_intermediate
              .query('HWP == "FW_B"')
              .rename(columns={'Vol_Merch':'Vol_Merch_FW_B',
                               'Vol_SubMerch':'Vol_SubMerch_FW_B',
                               'Vol_Snags':'Vol_Snags_FW_B',
                               'TC':'TC_FW_B'}))
        return df

    #-------------------------------------------------------------------------#
    @property_cached
    def fw_b_total(self):
        """
        Harvest volumes of Fuel Wood Broadleaves
        Join Industrial Round Wood co-products: 'Vol_SubMerch_IRW_B' and 'Vol_Snags_IRW_B'
        into the fuel wood total.
        """
        df = (self.fw_b
              .set_index('TimeStep')
              .join(self.irw_b.set_index(['TimeStep']))
              .reset_index())
        df['TOT_Vol_FW_B'] = sum([df.Vol_Merch_FW_B,
                                  df.Vol_SubMerch_FW_B,
                                  df.Vol_Snags_FW_B,
                                  df.Vol_SubMerch_IRW_B,
                                  df.Vol_Snags_IRW_B])
        df = df[['TimeStep',
                 'Vol_Merch_FW_B', 'Vol_SubMerch_FW_B', 'Vol_Snags_FW_B',
                 'Vol_SubMerch_IRW_B', 'Vol_Snags_IRW_B',
                 'TOT_Vol_FW_B']]
        return df

    #-------------------------------------------------------------------------#
    @property_cached
    def fw_c(self):
        """Harvest volumes of Fuel Wood Coniferous."""
        df = (self.hwp_intermediate
              .query('HWP == "FW_C"')
              .rename(columns={'Vol_Merch':'Vol_Merch_FW_C',
                               'Vol_SubMerch':'Vol_SubMerch_FW_C',
                               'Vol_Snags':'Vol_Snags_FW_C',
                               'TC':'TC_FW_C'}))
        return df

    #-------------------------------------------------------------------------#
    @property_cached
    def fw_c_total(self):
        """
        Harvest volumes of Fuel Wood Coniferous
        Join Industrial Round Wood co-products.
        """
        df = (self.fw_c
                  .set_index('TimeStep')
                  .join(self.irw_c.set_index(['TimeStep']))
                  .reset_index())
        df['TOT_Vol_FW_C'] = np.where(df['Vol_Merch_FW_C']>=0,
                                      sum([df.Vol_Merch_FW_C,
                                           df.Vol_SubMerch_FW_C,
                                           df.Vol_Snags_FW_C,
                                           df.Vol_SubMerch_IRW_C,
                                           df.Vol_Snags_IRW_C]),
                                      sum([df.Vol_SubMerch_IRW_C,
                                           df.Vol_Snags_IRW_C]))
        df = df[['TimeStep',
                 'Vol_Merch_FW_C','Vol_SubMerch_FW_C','Vol_Snags_FW_C',
                 'Vol_SubMerch_IRW_C','Vol_Snags_IRW_C',
                 'TOT_Vol_FW_C']]
        return df

    #-------------------------------------------------------------------------#
    @property_cached
    def hwp(self):
        """
        Volumes of Harvested Wood Products (HWP)
        Matching the product description available in the economic model
        and in the FAOSTAT historical data.

        Join "Vol_Merch" columns from irw_b and irw_c
        to the total columns from fw_b_total and fw_c_total,
        using time step as an index.
        """
        df = (self.irw_c
              .set_index('TimeStep')[['Vol_Merch_IRW_C']]
              .join(self.irw_b.set_index('TimeStep')[['Vol_Merch_IRW_B']])
              .join(self.fw_c_total.set_index('TimeStep')[['TOT_Vol_FW_C']])
              .join(self.fw_b_total.set_index('TimeStep')[['TOT_Vol_FW_B']])
              .reset_index())
        return df