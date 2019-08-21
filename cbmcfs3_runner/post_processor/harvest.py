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
        * TC is in terms of tons of carbon.
        * Vol_Merch are in terms of cubic meters of wood.

        Columns are: ['DistTypeID', 'DistTypeName', 'TimeStep', 'status', 'forest_type',
                      'management_type', 'management_strategy', 'conifers_bradleaves',
                      'DOMProduction', 'CO2Production', 'MerchLitterInput', 'OthLitterInput',
                      'db', 'SoftProduction', 'HardProduction', 'TC', 'Vol_Merch',
                      'Vol_SubMerch', 'Vol_Snags', 'Vol_forest_residues']
        """
        # First ungrouped #
        ungrouped = self.parent.flux_indicators
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
        flux_raw = self.parent.database['tblFluxIndicators']
        is_equal = numpy.testing.assert_allclose
        is_equal(flux_raw['SoftProduction'].sum(), df['SoftProduction'].sum())
        is_equal(flux_raw['HardProduction'].sum(), df['HardProduction'].sum())
        # Create new columns #
        df['TC']                  = df.SoftProduction + df.HardProduction
        df['Prov_Carbon']         = df.SoftProduction + df.HardProduction + df.DOMProduction
        df['Vol_Merch']           = (df.TC * 2) / df.db
        df['Vol_SubMerch']        = (df.CO2Production * 2) / df.db
        df['Vol_Snags']           = (df.DOMProduction * 2) / df.db
        df['Vol_forest_residues'] = ((df.MerchLitterInput + df.OthLitterInput) * 2) / df.db
        # Return #
        return df

    #-------------------------------------------------------------------------#
    @property_cached
    def provided_volume(self):
        """
        Based on Roberto's query `Harvest summary check` visible in the original calibration database.

        Columns are:    ['DistTypeID', 'DistTypeName', 'TimeStep', 'status', 'forest_type',
        (of the output)  'management_type', 'management_strategy', 'Vol_Merch', 'Vol_Snags',
                         'Vol_SubMerch', 'Vol_forest_residues', 'TC', 'tot_vol']

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
                    'Vol_forest_residues': 'sum',
                    'Prov_Carbon':         'sum',
                    'TC':                  'sum'})
              .reset_index())
        # Add the total volume column #
        df['tot_vol'] = df.Vol_Merch + df.Vol_SubMerch + df.Vol_Snags
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
        This corresponds to the "expected" aspect of "expected_provided" harvest
        and will contain both Area ('A') and Mass ('M'). The units for 'M' are
        tons of carbon and hectares for 'A'.

        This method Prepares the disturbance table for joining operations with
        harvest tables.

        It could be a good idea to check why some countries have DistTypeName as int64
        and others have DistTypeName as object.

        Columns are: ['status', 'forest_type', 'region', 'management_type',
                      'management_strategy', 'climatic_unit', 'conifers_bradleaves',
                      'UsingID', 'SWStart', 'SWEnd', 'HWStart', 'HWEnd', 'Last_Dist_ID',
                      'Efficency', 'Sort_Type', 'Measurement_type', 'Amount', 'Dist_Type_ID',
                      'TimeStep'],
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
        # Remove slashes #
        df = df.rename(columns=lambda n:n.replace('/','_'))
        # Dist_Type_ID is actually DistTypeName #
        df = df.rename(columns = {'Dist_Type_ID': 'DistTypeName'})
        # Return result #
        return df

    #-------------------------------------------------------------------------#
    def compute_expected_provided(self, provided, meas_type, prov_col_name):
        """
        Compares the amount of harvest requested in the disturbance tables (an input to the simulation)
        to the amount of harvest actually performed by the model (extracted from the flux indicator table).

        Based on Roberto's query `Harvest_expected_provided` visible in the original calibration database.

        In this method we transform *df*, by adding:

         - Years instead of TimeSteps
         - Rows where expected and provided are both zero removed
         - An extra column indicating the delta between expected and provided
         - An extra column indicating the disturbance description sentence.
        """
        # Columns we will keep #
        index = ['TimeStep',
                 'DistTypeName',
                 'forest_type',
                 'Measurement_type',
                 #'region',
                 #'management_type',
                 #'management_strategy',
                 #'conifers_bradleaves'
                 #'status'
                ]
        # Load #
        expected = self.disturbances
        # Filter for measurement type #
        selector = expected['Measurement_type'] == meas_type
        expected = expected.loc[selector].copy()
        # Aggregate expected #
        expected = (expected
                    .groupby(index)
                    .agg({'Amount': 'sum'})
                    .reset_index())
        # Aggregate provided #
        provided = (provided
                    .groupby(index)
                    .agg({prov_col_name: 'sum'})
                    .reset_index())
        # Index columns to join disturbances and harvest check #
        # Set the same index on both data frames #
        provided = provided.set_index(index)
        expected = expected.set_index(index)
        # Do the join #
        df = (provided.join(expected, how='outer')).reset_index()
        # Sum two columns #
        df = df.rename(columns = {'Amount':      'expected',
                                  prov_col_name: 'provided'})
        # Remove rows where both expected and provided are zero #
        selector = (df['expected'] == 0.0) & (df['provided'] == 0.0)
        df = df.loc[~selector].copy()
        # Add the delta column #
        df['delta'] = (df.expected - df.provided)
        # Add year and remove TimeStep #
        df['year'] = self.parent.parent.country.timestep_to_years(df['TimeStep'])
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
        "Measurement_type == 'M'"

        Columns are: ['status', 'TimeStep', 'DistTypeName', 'forest_type', 'management_type',
                      'management_strategy', 'expected', 'provided', 'Measurement_type',
                      'DistDescription']
        """
        # Compute #
        df = self.provided_volume
        return self.compute_expected_provided(df, 'M', 'Prov_Carbon')

    #-------------------------------------------------------------------------#
    @property_cached
    def exp_prov_by_area(self):
        """
        Same as above but for "Measurement_type == 'A'"

        Columns are: ['status', 'TimeStep', 'DistTypeName', 'forest_type', 'management_type',
                      'management_strategy', 'expected', 'provided', 'Measurement_type',
                      'DistDescription']
        """
        # Compute #
        df = self.provided_area
        return self.compute_expected_provided(df, 'A', 'DistArea')

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