#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Written by Lucas Sinclair, Viorel Blujdea and Paul Rougieux.

JRC Biomass Project.
Unit D1 Bioeconomy.

See the script/compare_aidb.py for the use of this class

"""

# Built-in modules #


# First party modules #
from plumbing.cache import property_cached

# Internal modules #
from libcbm_runner.core.continent import continent as libcbm_continent
from cbmcfs3_runner.pump import libcbm_mapping

# Keep only mapping between names that exist in both cbmcfs3 and libcbm (remove empty values)
df = libcbm_mapping.turnover_rates
turnover_mapping = df.loc[(df == df).sum(axis=1)==2].reset_index(drop=True)

###############################################################################
class CompareAIDB(object):
    """
    This class will enable us to compare the AIDB from the old MS Access
    format supported by CBM-CFS3 with the new SQLite format supported by
    libcbm.

    You instantiate the class with a Country object from cbmcfs3_runner.
    Then you get access to the corresponding Country object from libcbm_runner.

    Then you can inspect objects as so:

        >>> from cbmcfs3_runner.pump.aidb_comparison import CompareAIDB
        >>> from cbmcfs3_runner.core.continent import continent as cbmcfs3_continent
        >>> c = cbmcfs3_continent.countries['AT']
        >>> comp = CompareAIDB(c)
        >>> print(comp.libcbm_aidb.db.read_df('slow_mixing_rate'))
        >>> print(comp.cbmcfs3_aidb.database['tblSlowAGtoBGTransferRate'])

    """

    def __init__(self, cbmcfs3_country):
        # Main attributes #
        self.cbmcfs3_country = cbmcfs3_country
        self.iso2_code = self.cbmcfs3_country.iso2_code

    @property_cached
    def libcbm_country(self):
        """The matching libcbm country object."""
        return libcbm_continent.countries[self.cbmcfs3_country.iso2_code]

    @property_cached
    def cbmcfs3_aidb(self):
        return self.cbmcfs3_country.aidb

    @property_cached
    def libcbm_aidb(self):
        return self.libcbm_country.aidb

    def __call__(self):
        msg = "Comparing %s with %s."
        print(msg % (self.cbmcfs3_aidb, self.libcbm_aidb))

    def compare_table(self, table_name):
        df1 = self.libcbm_aidb.db.read_df(table_name)
        df2 = self.cbmcfs3_aidb.database[table_name]

    def load_turnover_parameters(self):
        """Return a data frame comparing turnover parameters between cbmcfs3 and libcbm"""
        # Load libcbm turnover
        eco_lib = self.libcbm_aidb.db.read_df('eco_boundary_tr')
        turn_lib = self.libcbm_aidb.db.read_df('turnover_parameter')
        lib_turnover  = eco_lib.merge(turn_lib, how='inner')

        # Load cbmcfs3 turnover
        cfs3_turnover = self.cbmcfs3_aidb.database['tblecoboundarydefault']

        # Combine the two
        index = ['eco_boundary_id', 'eco_boundary_name']
        # Reshape to long format
        lib_turnover_long = (lib_turnover
                             .rename(columns={'name':'eco_boundary_name'})
                             .melt(id_vars=index, var_name='libcbm', value_name='libcbm_value'))
        cfs3_turnover_long = (cfs3_turnover
                              .melt(id_vars=index, var_name='cbmcfs3', value_name='cbmcfs3_value'))
        # Join tables using to consecutive join instructions
        # 1. right join with the mapping table
        combined = cfs3_turnover_long.merge(turnover_mapping, on="cbmcfs3", how="right")
        # 2. left join with the libcbm turnover table
        combined = combined.merge(lib_turnover_long, on=index + ["libcbm"], how="left")
        combined.head(2)
        # Compute the difference
        combined['diff'] = combined["cbmcfs3_value"] - combined["libcbm_value"]
        return combined

    def check_turnover_parameters(self, threshold=1e-9):
        """Check that the absolute value of the difference between the turnover parameters is below the given threshold"""
        df = self.load_turnover_parameters()
        all_equal = all(df['diff'].abs() < threshold)
        if all_equal:
            print(f"{self.iso2_code} turnover rates are identical in libcbm and cbmcfs3")
        else:
            problem_rows = df[df['diff'].abs() > threshold]
            msg = f"Turnover parameter mismatch in '{self.iso2_code}'\n{problem_rows}.\n"
            msg += "You can load the comparison table with: \n"
            msg += f"compare = CompareAIDB(cbmcfs3_continent.countries['{self.iso2_code}'])\n"
            msg += "df = compare.load_turnover_parameters()\n"
            msg += f"problem_rows = df[df['diff'].abs() > {threshold}]"
            raise ValueError(msg)
