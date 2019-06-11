#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Written by Lucas Sinclair and Paul Rougieux.

JRC biomass Project.
Unit D1 Bioeconomy.
"""

# Built-in modules #

# Third party modules #
import numpy

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

        Columns are: ['DistTypeID', 'DistTypeName', 'TimeStep', 'status', 'forest_type',
                      'management_type', 'management_strategy', 'conifers_bradleaves',
                      'DOMProduction', 'CO2Production', 'MerchLitterInput', 'OthLitterInput',
                      'db', 'SoftProduction', 'HardProduction', 'TC', 'Vol_Merch',
                      'Vol_SubMerch', 'Vol_Snags', 'Forest_residues_Vol']
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
        # The index we will use for grouping #
        index = ['DistTypeID',
                 'DistTypeName',
                 'TimeStep',
                 'status',
                 'forest_type',
                 'management_type',
                 'management_strategy',
                 'conifers_bradleaves']
        # Not real grouping variables only here to keep them in the final table
        # Their values should be unique for the all combination of the other grouping vars
        # But in fact they are not! But we will group again later with other vars
        secondary_index = ['DOMProduction',
                           'CO2Production',
                           'MerchLitterInput',
                           'OthLitterInput',
                           'db']
        # Check that we don't produce NaNs #
        # See ~/repos/examples/python_modules/pandas/join_and_produce_nan.py
        # Check for NaNs coming from a join tables to avoid using them in an aggregation index
        # (currently ES, HU have some in the secondary_index) #
        assert not ungrouped[index].isna().any().any()
        # Then group #
        df = (ungrouped
              .groupby(index + secondary_index)
              .agg({'SoftProduction': 'sum',
                    'HardProduction': 'sum'})
              .reset_index())
        # Check conservation of total mass #
        is_equal = numpy.testing.assert_allclose
        is_equal(flux_indicators['SoftProduction'].sum(), df['SoftProduction'].sum())
        is_equal(flux_indicators['HardProduction'].sum(), df['HardProduction'].sum())
        # Create new columns #
        df['TC']                  = df.SoftProduction + df.HardProduction
        df['Vol_Merch']           = (df.TC * 2) / df.db
        df['Vol_SubMerch']        = (df.CO2Production * 2) / df.db
        df['Vol_Snags']           = (df.DOMProduction * 2) / df.db
        df['Forest_residues_Vol'] = ((df.MerchLitterInput + df.OthLitterInput) * 2) / df.db
        # Return #
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
    def provided_volume(self):
        """
        Based on Roberto's query `Harvest summary check` visible in the original calibration database.

        Columns are:    ['DistTypeID', 'DistTypeName', 'TimeStep', 'status', 'forest_type',
        (of the output)  'management_type', 'management_strategy', 'Vol_Merch', 'Vol_Snags',
                         'Vol_SubMerch', 'Forest_residues_Vol', 'TC', 'tot_vol']

        This corresponds to the "provided" aspect of "expected_provided" harvest and contains
        only volumes ('M').
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
        # Add the Measurement_type #
        df['Measurement_type'] = 'M'
        # Return result #
        return df

    #-------------------------------------------------------------------------#
    @property_cached
    def provided_area(self):
        """
        Load area disturbed from the table 'TblDistIndicators'

        Columns are:    ['DistIndID', 'SPUID', 'DistTypeID', 'TimeStep', 'UserDefdClassSetID',
                         'LandClassID', 'kf2', 'kf3', 'kf4', 'kf5', 'kf6', 'DistArea',
                         'DistProduct']

        This corresponds to the "provided" aspect of "expected_provided" harvest and contains
        only areas ('A').
        """
        # Load #
        dist_indicators  = self.parent.database['TblDistIndicators']
        disturbance_type = self.parent.database['tblDisturbanceType']
        # First ungrouped #
        ungrouped = (dist_indicators
                     .set_index('DistTypeID')
                     .join(disturbance_type.set_index('DistTypeID'))
                     .reset_index()
                     .set_index('UserDefdClassSetID')
                     .join(self.parent.classifiers.set_index('UserDefdClassSetID'))
                     .reset_index())
        # The index we will use for grouping #
        index = ['DistTypeID',
                 'DistTypeName',
                 'TimeStep',
                 'status',
                 'forest_type',
                 'region',
                 'management_type',
                 'management_strategy',
                 'conifers_bradleaves']
        # Compute #
        df = (ungrouped
              .set_index('DistTypeID')
              .groupby(index)
              .agg({'DistArea':    'sum',
                    'DistProduct': 'sum'})
              .reset_index())
        # Add the Measurement_type #
        df['Measurement_type'] = 'A'
        # Return result #
        return df

    #-------------------------------------------------------------------------#
    @property_cached
    def disturbances(self):
        """
        Measurement_type can be 'M' for mass or 'A' for area.

        Prepare the disturbance table for join operations with harvest tables.
        It could be a good idea to check why some countries have DistTypeName as int64
        and others have DistTypeName as object.

        Columns are: ['status', 'forest_type', 'region', 'management_type',
                      'management_strategy', 'climatic_unit', 'conifers/bradleaves',
                      'UsingID', 'SWStart', 'SWEnd', 'HWStart', 'HWEnd', 'Last_Dist_ID',
                      'Efficency', 'Sort_Type', 'Measurement_type', 'Amount', 'Dist_Type_ID',
                      'TimeStep'],

        This corresponds to the "expected" aspect of "expected_provided" harvest
        and will contain both Area ('A') and Volumes ('M').
        """
        # Load disturbances table from excel file #
        df = self.parent.parent.input_data.disturbance_events
        # Rename classifier columns _1, _2, _3 to forest_type, region, etc. #
        df = df.rename(columns = self.parent.classifiers_mapping)
        # C.f the PL column problem #
        df = df.rename(columns = {'natural_forest_region': 'management_type'})
        # This column also need to be manually renamed #
        df = df.rename(columns = {'Step': 'TimeStep'})
        # For joining with other data frames, DistType has to be of dtype object not int64 #
        df['Dist_Type_ID'] = df['Dist_Type_ID'].astype(str)
        # Remove columns that are not really used #
        df = df.drop(columns=[c for c in df.columns if c.startswith("Min") or c.startswith("Max")])
        # Dist_Type_ID is actually DistTypeName #
        df = df.rename(columns = {'Dist_Type_ID': 'DistTypeName'})
        # Return result #
        return df

    #-------------------------------------------------------------------------#
    def compute_expected_provided(self, df):
        """
        Compares the amount of harvest requested in the disturbance tables (an input to the simulation)
        to the amount of harvest actually performed by the model (extracted from the flux indicator table).

        Based on Roberto's query `Harvest_expected_provided` visible in the original calibration database.

        Then we add:

         - Years instead of TimeSteps
         - Rows where expected and provided are both zero removed
         - An extra column indicating the delta between expected and provided
         - An extra column indicating the disturbance description sentence.

        Columns are: ['status', 'TimeStep', 'DistTypeName', 'forest_type', 'management_type',
                      'management_strategy', 'expected', 'provided', 'Measurement_type',
                      'DistDescription']
        """
        # Remove rows where both expected and provided are zero #
        selector = (df['expected'] == 0.0) & (df['provided'] == 0.0)
        df = df.loc[~selector].copy()
        # Add the delta column #
        df['delta'] = (df.expected - df.provided)
        # Add year and remove TimeStep #
        df['year'] = self.parent.timestep_to_years(df['TimeStep'])
        df = df.drop('TimeStep', axis=1)
        # Get the disturbances full name from their number #
        dist_type = (self.parent.parent.input_data.disturbance_types
                     .rename(columns={'DisturbanceTypeID': 'DistTypeName',
                                                   'Name': 'DistDescription'})
                     .set_index('DistTypeName'))
        # Add a column named 'DistDescription' #
        df = (df.set_index('DistTypeName')
                .join(dist_type)
                .reset_index())
        # Only if we are in the calibration scenario #
        if self.parent.parent.scenario.short_name == 'calibration':
            # Patch the harvest data frame to stop at the simulation year #
            selector = df['year'] <= self.parent.parent.country.base_year
            df = df.loc[selector].copy()
        # Return result #
        return df

    #-------------------------------------------------------------------------#
    @property_cached
    def exp_prov_by_volume(self):
        """
        Same as above but for "Measurement_type == 'M'"

        Columns are: ['status', 'TimeStep', 'DistTypeName', 'forest_type', 'management_type',
                      'management_strategy', 'expected', 'provided', 'Measurement_type',
                      'DistDescription']
        """
        # Load #
        provided = self.provided_volume
        expected = self.disturbances
        # Filter for volume #
        selector = expected['Measurement_type'] == 'M'
        expected = expected.loc[selector].copy()
        # Index columns to join disturbances and harvest check #
        index = ['status',
                 'TimeStep',
                 'DistTypeName',
                 'forest_type',
                 'management_type',
                 'management_strategy',
                 'Measurement_type']
        # Set the same index on both data frames #
        provided = provided.set_index(index)
        expected = expected.set_index(index)
        # Do the join #
        df = (provided.join(expected, how='outer')).reset_index()
        # Sum two columns #
        df = (df
              .groupby(index)
              .agg({'Amount': 'sum',
                    'TC':     'sum'})
              .rename(columns = {'Amount': 'expected',
                                 'TC':     'provided'})
              .reset_index())
        # Compute #
        return self.compute_expected_provided(df)

    #-------------------------------------------------------------------------#
    @property_cached
    def exp_prov_by_area(self):
        """
        Same as above but for "Measurement_type == 'A'"

        Columns are: ['status', 'TimeStep', 'DistTypeName', 'forest_type', 'management_type',
                      'management_strategy', 'expected', 'provided', 'Measurement_type',
                      'DistDescription']
        """
        # Load #
        provided = self.provided_area
        expected = self.disturbances
        # Filter for volume #
        selector = expected['Measurement_type'] == 'A'
        expected = expected.loc[selector].copy()
        # Index columns to join disturbances and harvest check #
        index = ['status',
                 'TimeStep',
                 'DistTypeName',
                 'forest_type',
                 'region',
                 'management_type',
                 'management_strategy',
                 'Measurement_type']
        # Set the same index on both data frames #
        provided = provided.set_index(index)
        expected = expected.set_index(index)
        # Do the join #
        df = (provided.join(expected, how='right')).reset_index()
        # Sum two columns #
        df = (df
              .groupby(index)
              .agg({'Amount':    'sum',
                    'DistArea':  'sum'})
              .rename(columns = {'Amount':   'expected',
                                 'DistArea': 'provided'})
              .reset_index())
        # Compute #
        return self.compute_expected_provided(df)

    #-------------------------------------------------------------------------#
    def check_exp_prov(self):
        """Check that the total quantities of area and volume are conserved."""
        # Load #
        area = self.exp_prov_by_area
        volu = self.exp_prov_by_volume
        # Check expected #
        processed = volu['expected'].sum() + area['expected'].sum()
        raw       = self.parent.parent.input_data.disturbance_events['Amount'].sum()
        numpy.testing.assert_allclose(processed, raw)
        # Check provided area #
        processed = area['provided'].sum()
        raw       = self.parent.database['TblDistIndicators']['DistArea'].sum()
        numpy.testing.assert_allclose(processed, raw)
        # Check provided volume #
        processed = volu['provided'].sum()
        raw       = self.parent.database['TblFluxIndicators']
        raw       = raw['SoftProduction'].sum() + raw['HardProduction'].sum()
        numpy.testing.assert_allclose(processed, raw)

    #-------------------------------------------------------------------------#
    @property_cached
    def silviculture(self):
        """Prepare the silviculture table for joining operations with harvest tables."""
        # Load file #
        df = self.parent.parent.country.silviculture.df
        # Rename classifiers from _1 to forest etc. #
        df = df.rename(columns = self.parent.classifiers_mapping)
        # Rename a column #
        df = df.rename(columns = {'Dist_Type_ID': 'DistTypeName'})
        # Change the type of DistTypeName to string so that it has the same type as
        # the `harvest_check` DistTypeName column
        df['DistTypeName'] = df['DistTypeName'].astype(str)
        # Change the type of management_strategy to string (for SI)
        df['management_strategy'] = df['management_strategy'].astype(str)
        # Return #
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
        # Take only a few columns #
        silv = self.silviculture[join_index + ['HWP']]
        silv = silv.set_index(join_index)
        # Join #
        df = (self.check
              .reset_index()
              .set_index(join_index)
              .join(silv))
        # We want the columns with NaNs to be thrown away
        # Because they represent disturbances that do not produce any harvest
        # Otherwise we would do: assert not df[join_index].isna().any().any()
        # Group #
        df = (df.groupby(['TimeStep', 'HWP'])
                .agg({'Vol_Merch':    'sum',
                      'Vol_SubMerch': 'sum',
                      'Vol_Snags':    'sum',
                      'TC':           'sum'})
                .reset_index())
        # Return #
        return df

    #-------------------------------------------------------------------------#
    @property_cached
    def irw_b(self):
        """Harvest volumes of Industrial Round Wood Broadleaves."""
        df = (self.hwp_intermediate
              .query('HWP == "IRW_B"')
              .rename(columns={'Vol_Merch':    'Vol_Merch_IRW_B',
                               'Vol_SubMerch': 'Vol_SubMerch_IRW_B',
                               'Vol_Snags':    'Vol_Snags_IRW_B',
                               'TC':           'TC_IRW_B'}))
        # Drop HWP column
        # because it doesn't make sense anymore below when we join different products together
        df = df.drop('HWP', axis = 1)
        return df

    #-------------------------------------------------------------------------#
    @property_cached
    def irw_c(self):
        """Harvest volumes of Industrial Round Wood Coniferous."""
        df = (self.hwp_intermediate
              .query('HWP == "IRW_C"')
              .rename(columns={'Vol_Merch':    'Vol_Merch_IRW_C',
                               'Vol_SubMerch': 'Vol_SubMerch_IRW_C',
                               'Vol_Snags':    'Vol_Snags_IRW_C',
                               'TC':           'TC_IRW_C'}))
        df = df.drop('HWP', axis = 1)
        return df

    #-------------------------------------------------------------------------#
    @property_cached
    def fw_b(self):
        """Harvest volumes of Fuel Wood Broadleaves."""
        df = (self.hwp_intermediate
              .query('HWP == "FW_B"')
              .rename(columns={'Vol_Merch':    'Vol_Merch_FW_B',
                               'Vol_SubMerch': 'Vol_SubMerch_FW_B',
                               'Vol_Snags':    'Vol_Snags_FW_B',
                               'TC':           'TC_FW_B'}))
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
              .rename(columns={'Vol_Merch':    'Vol_Merch_FW_C',
                               'Vol_SubMerch': 'Vol_SubMerch_FW_C',
                               'Vol_Snags':    'Vol_Snags_FW_C',
                               'TC':           'TC_FW_C'}))
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
        df['TOT_Vol_FW_C'] = numpy.where(df['Vol_Merch_FW_C'] >= 0,
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

        Join "Vol_Merch" columns from "irw_b" and "irw_c"
        to the total columns from "fw_b_total" and "fw_c_total",
        using the time step as an index.
        """
        df = (self.irw_c
              .set_index('TimeStep')[['Vol_Merch_IRW_C']]
              .join(self.irw_b.set_index('TimeStep')[['Vol_Merch_IRW_B']])
              .join(self.fw_c_total.set_index('TimeStep')[['TOT_Vol_FW_C']])
              .join(self.fw_b_total.set_index('TimeStep')[['TOT_Vol_FW_B']])
              .reset_index())
        return df