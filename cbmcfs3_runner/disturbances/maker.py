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
from autopaths.auto_paths import AutoPaths

# Internal modules #

###############################################################################
class DisturbanceMaker(object):
    """
    Will create new disturbances for the simulation period
    and modify the file input file "disturbance_events.csv".
    """

    all_paths = """
    /input/csv/disturbance_events.csv
    """

    def __init__(self, parent):
        # Default attributes #
        self.parent  = parent
        self.country = parent.country
        # Directories #
        self.paths = AutoPaths(self.parent.data_dir, self.all_paths)

    def __call__(self):
        self.add_events()

    @property
    def convert_demand_to_harvest(self):
        """
        We have to proceed by steps, by first harvesting round-wood.
        Each cubic meter of round-wood harvested will produce some fuel-wood,
        which later we won't have to harvest.
        Confiers and Broadleaves are independent in their processing.

        The demands matrix is like this:

           year     _7   prod    volume
           1999  Broad    IRW  121400.0
           1999    Con    IRW  120300.0
           1999  Broad     FW   16900.0
           1999    Con     FW    1100.0

        We take only the round-wood lines:

           year     _7   prod    volume
           1999  Broad    IRW  121400.0
           1999    Con    IRW  120300.0

        We will join with an allocation matrix
        that would look as follows:

            prod   prop  dist _1  _2  _3     _7 Snag_Perc OWC_Perc  Min_Age Max_Age
            IRW    0.9      7 AA  MT  AR  Broad      0.02     0.14       20      80
            IRW    0.1     12 BB  MT  AR  Broad      0.03     0.12       20      80
            IRW    0.5     29 ZZ  MT  AR    Con      0.02     0.14       20      80
            IRW    0.5      3 YY  MT  AR    Con      0.03     0.12       20      80

        We keep the two percentage columns because we want to be able to
        switch one or the other on or off.

        Result of the join:

            prod   prop  dist   _1  _2  _3    _7 Snag_Perc OWC_Perc     volume  year
            IRW    0.9      7  AA  MT  AR  Broad      0.02     0.14   121400.0  1999
            IRW    0.1     12  BB  MT  AR  Broad      0.03     0.12   121400.0  1999
            IRW    0.5     29  ZZ  MT  AR    Con      0.02     0.14   120300.0  1999
            IRW    0.5      3  YY  MT  AR    Con      0.03     0.12   120300.0  1999

        Then we add the column: IRW_amount = prop * volume
        As well as the:          FW_amount = IRW_amount * (Snag_perc + OWC_Perc)

            prod   prop  dist  _1  _2  _3    _7 Snag_Perc OWC_Perc IRW_amount  FW_amount  year
            IRW    0.9      7 AA  MT  AR  Broad      0.02     0.14     110000       5000  1999
            IRW    0.1     12 BB  MT  AR  Broad      0.03     0.12       1000         90  1999
            IRW    0.5     29 ZZ  MT  AR    Con      0.02     0.14      60000       4000  1999
            IRW    0.5      3 YY  MT  AR    Con      0.03     0.12       6000        600  1999

        Here we can check that sum(IRW_amount) == sum(volume)
        By doing df.groupby('year', '_7').agg({'FW_amount': 'sum'}) we get:

                _7 FW_amount  year
             Broad      5090  1999
               Con      4600  1999

        Now we take the original demand matrix for FW and join with the matrix above.
        Finally we subtract what is already produced:

        We set: volume = volume - FW_amount

           year     _7   prod    volume   FW_amount  year
           1999  Broad     FW   11423.0        5090  1999
           1999    Con     FW   -3045.0        4600  1999

        Check that volume has to always be positive. Otherwise set it to zero.
        Now we will join again with an allocation matrix but that has "FW" instead "IRW":

            prod  prop  dist  _1  _2  _3    _7 Snag_Perc OWC_Perc
            FW    0.8      7  AA  MT  AR Broad      0.01     0.14
            FW    0.2     12  BB  MT  AR Broad      0.03     0.12
            FW    0.6     29  ZZ  MT  AR   Con      0.02     0.14
            FW    0.4      3  YY  MT  AR   Con      0.03     0.12

        Result of the join:

            prod  prop  dist  _1  _2  _3    _7 Snag_Perc OWC_Perc   volume  year
            FW    0.8      7  AA  MT  AR Broad      0.01     0.14  11423.0  1999
            FW    0.2     12  BB  MT  AR Broad      0.03     0.12  11423.0  1999
            FW    0.6     29  ZZ  MT  AR   Con      0.02     0.14      0.0  1999
            FW    0.4      3  YY  MT  AR   Con      0.03     0.12      0.0  1999

        Then we add the column:  FW_amount = prop * volume / (1 + Snag_Perc + OWC_Perc)
        We do this since the fuel wood harvest also generates extra fuel wood.

            prod  prop dist  _1  _2  _3    _7 Snag_Perc OWC_Perc FW_amount  year
            FW    0.8     7 AA  MT  AR  Broad      0.01     0.14      5000  1999
            FW    0.2    12 BB  MT  AR  Broad      0.03     0.12        90  1999
            FW    0.6    29 ZZ  MT  AR    Con      0.02     0.14      4000  1999
            FW    0.4     3 YY  MT  AR    Con      0.03     0.12       600  1999

        We can check that FW_amount is equal to the sum of demand / (1 + Snag_Perc + OWC_Perc)
        Finally we combine the dataframe (4) and (7) with both columns becoming amount.

            prod dist  _1  _2  _3    _7 Snag_Perc OWC_Perc    amount  year
            FW      7 AA  MT  AR  Broad      0.01     0.14      5000  1999
            FW     12 BB  MT  AR  Broad      0.03     0.12        90  1999
            FW     29 ZZ  MT  AR    Con      0.02     0.14      4000  1999
            FW      3 YY  MT  AR    Con      0.03     0.12       600  1999
            IRW     7 AA  MT  AR  Broad      0.02     0.14    110000  1999
            IRW    12 BB  MT  AR  Broad      0.03     0.12      1000  1999
            IRW    29 ZZ  MT  AR    Con      0.02     0.14     60000  1999
            IRW     3 YY  MT  AR    Con      0.03     0.12      6000  1999

        We have dropped 'prop'
        To create disturbances we are still missing "SWStart", "SWEnd", "HWStart", "HWEnd".
        In this case SW == Conifer and HW == Broad. Both values are always the same.

        """
        # Allocation
        # Join the GFTM demand and the allocation table
        # This will generate a much longer table,
        # containing different combinations of classifiers and disturbance ids
        # for each HWP and year.
        df = (self.country.demand.future
             .set_index('HWP')
             .join(self.country.silviculture.harvest_proportion.set_index('HWP')))
        # Calculate the disturbance amount based on the proportion
        df['Amount'] = df['value_ob'] * df['prop']

        # Add and re-order columns
        # # These classifiers are ignored when interacting with the economic model only
        df['climatic_unit']  = '?'
        df['region']  =  '?'

        # Min age max age are distinquished by hardwood and soft wood
        df['SWStart'] = df['Min_age']
        df['SWEnd'] = df['Max_age']
        df['HWStart'] = df['Min_age']
        df['HWEnd'] = df['Max_age']

        # Rename
        df  =  df.rename(columns = {'Min_since_last':'Min_since_last_Dist',
                                              'Max_since_last':'Max_since_last_Dist'})
        # Constant values expected by cbm_cfs3
        # See silviculture.sas
        df['UsingID'] = False
        df['Last_Dist_ID'] = -1
        df['Min_tot_biom_C'] = -1
        df['Max_tot_biom_C'] = -1
        df['Min_merch_soft_biom_C'] = -1
        df['Max_merch_soft_biom_C'] = -1
        df['Min_merch_hard_biom_C'] = -1
        df['Max_merch_hard_biom_C'] = -1
        df['Min_tot_stem_snag_C'] = -1
        df['Max_tot_stem_snag_C'] = -1
        df['Min_tot_soft_stem_snag_C'] = -1
        df['Max_tot_soft_stem_snag_C'] = -1
        df['Min_tot_hard_stem_snag_C'] = -1
        df['Max_tot_hard_stem_snag_C'] = -1
        df['Min_tot_merch_stem_snag_C'] = -1
        df['Max_tot_merch_stem_snag_C'] = -1
        df['Min_tot_merch_soft_stem_snag_C'] = -1
        df['Max_tot_merch_soft_stem_snag_C'] = -1
        df['Min_tot_merch_hard_stem_snag_C'] = -1
        df['Max_tot_merch_hard_stem_snag_C'] = -1
        df['Measurement_type'] = 'M'
        # Rearrange columns according to the raw disturbance_events.csv file
        # Note: self.country.orig_data.disturbance_events was modified
        # after we loaded it, we added additional variables.
        # To get the un-modified column order, we reload the original
        # "disturbance_events.csv" without extra columns
        dist_calib_raw = self.country.orig_data['disturbance_events']
        dist_calib_raw = dist_calib_raw.rename(columns = self.country.classifiers.mapping)
        dist_calib_columns = list(dist_calib_raw.columns)
        # Return #
        return df[dist_calib_columns]

    def add_events(self):
        """Append the new disturbances to the disturbance file."""
        # Load data #
        df = self.new_events
        # Write the result #
        df.to_csv(str(self.paths.csv), mode='a', index=False)

