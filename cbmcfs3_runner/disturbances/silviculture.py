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
    on the historical inventory and yield curve within a country.

    In essence we will harvest proportionally to what is found in a country.
    In terms of volume, if a country has 90% of firs, we will harvest 90% there.
    Of course this is within the harvestable range, we will exclude trees that are
    too young.
    """

    all_paths = """
    /orig/silv_treatments.csv
    /orig/harvest_corr_fact.csv
    """

    # Ignore some disturbances that are of type "natural"
    # when calculating the harvest proportion.
    # Used in self.stock_available_agg
    # These disturbance ids are the same for all countries.
    # See also the information contained in the 'man_nat' column
    dist_to_ignore = ['5', '7', '21', 'DISTID1', 'DISTID5', 'DISTID7',
                      'DISTID9b_H', 'DISTID9c_H']

    def __init__(self, parent):
        # Default attributes #
        self.parent = parent
        # Automatically access paths based on a string of many subpaths #
        self.paths = AutoPaths(self.parent.data_dir, self.all_paths)

    @property_cached
    def treatments(self):
        """Load the CSV that is 'silv_treatments.csv'.
        The column "Man_Nat" represents either 'Man-made disturbance'
        or a Natural disturbance.
        'Perc_merch_biom_rem' is redundant with 'Dist_ID' and simply shows
        the percent of thinning.
        """
        df = pandas.read_csv(str(self.paths.treatments))
        # dist_type_id can be given as either a numeric or a character variable
        # convert to string to prevent issues when merging and filtering
        df['dist_type_id'] = df['dist_type_id'].astype(str)
        # Rename the classifier columns to full names #
        df = df.rename(columns = self.parent.classifiers.mapping)
        # 'For' and 'CC' receive the same silviculture treatment.
        # Duplicate 'CC' rows in the silviculture treatment table and mark them as 'For'
        silv_for = df.query("status == 'CC'").copy()
        silv_for['status'] = 'For'
        df = df.append(silv_for)
        # Return #
        return df

    @property_cached
    def hwp_map(self):
        """Mapping to add HWP information to a disturbance table
        This table contains the classifiers columns,
        the disturbance ids and HWP columns."""
        return self.treatments[['status', 'forest_type',
                                'management_type', 'management_strategy',
                                'conifers_bradleaves', 'dist_type_id',
                                'hwp']]

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

        * IRW stands for Industrial Round Wood
        * FW stands for Fuel Wood
        * C stands for coniferous
        * B stands for broadleaved
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

        Columns are: ['status', 'forest_type', 'region', 'management_type',
                      'management_strategy', 'climatic_unit',
                      'conifers_bradleaves', 'age_class', 'area', 'volume',
                      'stock', 'age']
        """
        # Load data frames #
        inventory     = self.parent.orig_data.inventory
        h_yields_long = self.parent.orig_data.historical_yields_long
        # Index #
        index = ['status', 'forest_type', 'region', 'management_type',
                 'management_strategy', 'climatic_unit', 'conifers_bradleaves',
                 'age_class']
        # Join #
        df = (inventory
              .set_index(index)
              .join(h_yields_long.set_index(index))
              .reset_index())
        # Compute stock #
        df['stock'] = df['area'] * df['volume']
        # We are not interested in these columns #
        cols_to_drop = ['using_id', 'age', 'delay', 'unfcccl', 'hist_dist', 'last_dist', 'sp']
        df = df.drop(columns=cols_to_drop)
        # Compute the actual age #
        df['age'] = df['age_class'] * 10
        # Return #
        return df

    @property_cached
    def stock_available_by_age(self):
        """Calculate the stock available based on the harvest proportion
        in the silviculture_treatments table and multiplied by a correction factor.

        Note: the harvest proportion in the silviculture_treatments table should be
        the same as the proportion going to products in the disturbance matrix.
        See script "scripts/checking/check_harvest_prop.py".

        The status classifier does not have the same value between the data frames
        silviculture and stock_based_on_yield.

        Columns are: ['status', forest_type', 'management_type', 'management_strategy',
                      'conifers_bradleaves', 'status', 'region', 'climatic_unit',
                      'age_class', 'area', 'volume', 'stock', 'age',
                      'dist_type_id', 'sort_type', 'efficiency', 'min_age',
                      'max_age', 'min_since_last', 'max_since_last', 'hwp',
                      'regen_delay', 'reset_age', 'percent', 'wd', 'owc_perc',
                      'snag_perc', 'perc_merch_biom_rem', 'man_nat', 'corr_fact',
                      'stock_available']

        Min_since_last represents the minimum age since the last disturbance for
        a new disturbance to be applied.
        """
        # Join with correction factor #
        silviculture = (self.treatments
                        .set_index('forest_type')
                        .join(self.corr_fact
                              .set_index('forest_type'))
                        .reset_index())
        # Join only on these classifiers #
        index = ['status', 'forest_type', 'management_type',
                 'management_strategy', 'conifers_bradleaves']
        # Join #
        df = (self.stock_based_on_yield
              .set_index(index)
              .join(silviculture.set_index(index))
              .reset_index()
              .query('min_age < age & age < max_age')
              .query('stock > 0')
              .copy())
        # Compute the stock available #
        df['stock_available'] = (df['stock']
                                 * df['corr_fact']
                                 * df['perc_merch_biom_rem']
                                 / df['min_since_last'])
        # Return #
        return df

    @property_cached
    def stock_available_agg(self):
        """Aggregate stock_available_by_age and sum the stock available over
        all age classes. Natural disturbances are ignored.

        Columns are: ['status', 'forest_type', 'management_type', 'management_strategy',
                      'conifers_bradleaves', 'dist_type_id', 'stock_available',
                      'hwp', 'status']
        """
        # Index #
        # Note the presence of 'hwp' now in the index
        index = ['status', 'forest_type', 'management_type', 'management_strategy',
                 'conifers_bradleaves', 'dist_type_id', 'hwp']
        # These variables will be added to the groupby aggregate operation
        # Because we need them later to create disturbances
        vars_to_create_dists = ['sort_type', 'efficiency', 'min_age', 'max_age',
                                'min_since_last', 'max_since_last',
                                'regen_delay', 'reset_age', 'wd', 'man_nat']
        # Aggregate #
        df = (self.stock_available_by_age
              .query("dist_type_id not in @self.dist_to_ignore and man_nat=='Man'")
              .groupby(index + vars_to_create_dists)
              .agg({'stock_available': 'sum'})
              .reset_index())
        # Return #
        return df

    @property_cached
    def harvest_proportion(self):
        """To allocate the harvest across
        disturbance types (clear cut, thinning)
        and additional classifiers (forest type, management type,
        management strategy) we use a proportion based
        on the historical inventory and yield curve.

        The harvest proportion is calculated from the stock available
        by combining two information sources:

            * The inventory provides an area by forest type and age class
            * The growth/yield curve provides a volume by forest type and age class

        We multiply those two values to obtain a
        "stock = area * volume" for each particular classifiers
        and age class combination.

        The stock available is then calculated based
        on the percentage moved in the disturbance matrix
        (also available in the silviculture table perc_merch_biom_rem)
        and on an empirical harvest correction factor,
        for each disturbance and combination of classifiers:

            stock available = stock * percentage harvested

        by the disturbance * correction factor.

        The data frame below is the allocation of harvest
        along the classifiers used in self.stock_available_agg:

            ['status', 'forest_type', 'management_type', 'management_strategy',
             'conifers_bradleaves', 'dist_type_id' ].

        The proportion is based on the available stock by
        harvested wood products (HWP) category.

        Columns are: ['status', 'forest_type', 'management_type', 'management_strategy',
                      'conifers_bradleaves', 'dist_type_id', 'stock_available',
                      'hwp', 'status', 'stock_tot', 'prop']
        """
        # Load dataframe #
        df = self.stock_available_agg.copy()
        # Add column stock_tot #
        df['stock_tot'] = df.groupby(['hwp'])['stock_available'].transform('sum')
        # Add column prop #
        df['prop']      = df['stock_available'] / df['stock_tot']
        # Drop redundant total column #
        df.drop(columns=['stock_tot'])
        # Sort for readability #
        df = df.sort_values(by=['hwp'], ascending=False)
        # Return
        return df
