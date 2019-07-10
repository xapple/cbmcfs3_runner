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
from plumbing.dataframes import string_to_df

# Internal modules #

###############################################################################
class Silviculture(object):
    """
    This class gives access to information contained in the file
    "silviculture.sas".

    The silviculture treatments table is used to transform economic demand
    into disturbances. A list of disturbances specifies in which set of stands
    to harvest at which time step.

    The economic model provides future demand volumes distinguished only
    by the coniferous/broadleaves classifier.

    To allocate the harvest across disturbance
    types (clear cut, thinning) and additional classifiers (forest type,
    management type, management strategy) we use a proportion method based
    on the historical inventory and yield curve.
    """

    all_paths = """
    /orig/silv_treatments.csv
    /orig/harvest_corr_fact.csv
    """

    # Ignore some disturbances that are of type "natural"
    # when calculating the harvest proportion.
    # This is the same for all countries.
    dist_to_ignore = ['5', '7', '21', 'DISTID1', 'DISTID5', 'DISTID7',
                      'DISTID9b_H', 'DISTID9c_H']

    def __init__(self, parent):
        # Default attributes #
        self.parent = parent
        # Automatically access paths based on a string of many subpaths #
        self.paths = AutoPaths(self.parent.data_dir, self.all_paths)

    @property_cached
    def treatments(self):
        """Load the CSV that is 'silv_treatments.csv'."""
        df = pandas.read_csv(str(self.paths.treatments))
        # Dist_Type_ID can be given as either a numeric or a character variable
        # convert to string to prevent issues when merging and filtering
        df['Dist_Type_ID'] = df['Dist_Type_ID'].astype(str)
        # Rename the classifier columns to full names #
        df = df.rename(columns = self.parent.classifiers.mapping)
        # Return #
        return df

    @property_cached
    def corr_fact(self):
        """Load the CSV that is 'harvest_corr_fact.csv'."""
        return pandas.read_csv(str(self.paths.corr_fact))

    @property_cached
    def pool_allocation(self):
        """
        Allocation of harvested pools to different
        co-products, based on the main harvested wood product.

        The merchantable volume 'Tot_V_Merch' always goes
        to the product that is harvested.
        The sub merchantable and snag volume 'Tot_V_SubMerch' and 'Tot_V_Snags'
        go to the corresponding fuel wood pool, either coniferous or broadleaved.
        """
        s = """     pool  |   HWP  |  co_product
             Tot_V_Merch  |  FW_C  |  FW_C
          Tot_V_SubMerch  |  FW_C  |  FW_C
             Tot_V_Snags  |  FW_C  |  FW_C
             Tot_V_Merch  | IRW_C  | IRW_C
          Tot_V_SubMerch  | IRW_C  |  FW_C
             Tot_V_Snags  | IRW_C  |  FW_C
             Tot_V_Merch  |  FW_B  |  FW_B
          Tot_V_SubMerch  |  FW_B  |  FW_B
             Tot_V_Snags  |  FW_B  |  FW_B
             Tot_V_Merch  | IRW_B  | IRW_B
          Tot_V_SubMerch  | IRW_B  |  FW_B
             Tot_V_Snags  | IRW_B  |  FW_B
        """
        # Convert string to data frame #
        return string_to_df(s)

    @property_cached
    def stock_based_on_yield(self):
        """
        Calculate the theoretical stock based on the inventory area
        by age class multiplied by the corresponding volume-per-hectare for
        each age class producing "stock" in terms of m^3.
        """
        inventory = self.parent.orig_data.inventory
        h_yields_long = self.parent.orig_data.historical_yields_long
        index = ['status', 'forest_type', 'region', 'management_type',
                 'management_strategy', 'climatic_unit', 'conifers_bradleaves',
                 'age_class']
        # Join #
        df = (inventory
              .set_index(index)
              .join(h_yields_long.set_index(index))
              .reset_index())
        # Compute stock #
        df['stock'] = df['Area'] * df['volume']
        # We are not interested in these columns #
        cols_to_drop = ['UsingID', 'Age', 'Delay', 'UNFCCCL', 'HistDist', 'LastDist', 'Sp']
        df = df.drop(columns=cols_to_drop)
        # Compute the actual age #
        df['age'] = df['age_class'] * 10
        # Return #
        return df

    @property_cached
    def stock_available_by_age(self):
        """
        Calculate the stock available based on the harvest proportion
        in the silviculture_treatments table and multiply by a correction factor.

        Note: the harvest proportion in the silviculture_treatments table should be
        the same as the proportion going to products in the disturbance matrix.
        See script "scripts/checking/check_harvest_prop.py".

        The status classifier does not have the same value between the data frames
        silviculture and stock_based_on_yield.
        """
        # Join with correction factor #
        silviculture = (self.treatments
                        .set_index('forest_type')
                        .join(self.corr_fact.set_index('forest_type'))
                        .reset_index())
        # Check that status is unique #
        if len(silviculture['status'].unique()) > 1:
            msg  = "Silviculture status is not unique. %s"
            msg += "Please check the merge with stock_based_on_yield"
            raise Exception(msg % silviculture['status'].unique())
        # As it's unique we can drop it, because there is also "status" in stock_based_on_yield #
        silviculture = silviculture.drop(columns=['status'])
        # Join only on these classifiers #
        index = ['forest_type', 'management_type', 'management_strategy', 'conifers_bradleaves']
        # Join #
        df = (self.stock_based_on_yield
              .set_index(index)
              .join(silviculture.set_index(index))
              .reset_index()
              .query('Min_age < age & age < Max_age')
              .query('stock > 0')
              .copy())
        # Compute the stock available #
        df['stock_available'] = (df['stock']
                                 * df['corr_fact']
                                 * df['Perc_Merch_Biom_rem']
                                 / df['Min_since_last'])
        # Return #
        return df

    @property_cached
    def stock_available_agg(self):
        """
        Aggregate stock_available_by_age and sum the stock available over
        all age classes. Some natural disturbances are ignored.
        """
        index = ['forest_type', 'management_type', 'management_strategy',
                 'conifers_bradleaves', 'Dist_Type_ID']
        # Aggregate #
        df = (self.stock_available_by_age
              .query("Dist_Type_ID not in @self.dist_to_ignore")
              .groupby(index)
              .agg({'stock_available': 'sum'})
              .reset_index())
        # Add the harvested wood products column #
        silviculture = self.treatments[index + ['HWP']]
        # Join #
        df = (df
              .set_index(index)
              .join(silviculture.set_index(index))
              .reset_index())
        # Setting status to 'For' might not be necessary.
        # Just here as a reminder that status is homogeneous at the moment.
        # Harvest proportion calculation has to be changed once we deal with
        # forests available for thinning only status='th'
        # vs forests available for both thinning and clear cut status='CC'.
        df['status'] = 'For'
        # Return #
        return df

    @property_cached
    def harvest_proportion(self):
        """
        Allocation of harvest along different classifiers.
        """
        # Join silv_stock on the HWP field.
        # This expands the data frame for each possible combinations of HWP.
        demand_hist = self.parent.demand.historical
        hwp_const_irw_fw = (demand_hist
                            .set_index('HWP')
                            .join(self.stock_available_agg.set_index('HWP'))
                            .reset_index())
        # Aggregate #
        index = ['step', 'HWP']
        stock_t_step_const = (hwp_const_irw_fw
                              .groupby(index)
                              .agg({'stock_available': 'sum'})
                              .reset_index())
        # Rename #
        stock_t_step_const = stock_t_step_const.rename(columns={'stock_available' : 'stock_tot'})
        # Join back the total data frame to the original data frame
        # to calculate the proportion of volume available amongst the total available volume
        # for each management_type, management_strategy, forest_type, disturbance_type_id
        # There probably is another way
        # to calculate the proportion by using "apply" over a group-by window.
        # Join #
        df = (hwp_const_irw_fw
              .set_index(index)
              .join(stock_t_step_const.set_index(index))
              .reset_index())
        # Compute proportion #
        df['prop'] = df['stock_available'] / df['stock_tot']
        # Return #
        return df
