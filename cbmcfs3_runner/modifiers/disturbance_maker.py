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
    def new_events(self):
        """Lorem ipsum.
        We have to proceed by steps, by first harvesting round-wood.
        Each cubic meter of round-wood harvest will produce some fuel-wood,
        which we later won't have to harvest.
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

            prod   prop  _1  _2  _3    _7 Snag_Perc OWC_Perc
            IRW    0.9  AA  MT  AR  Broad      0.02     0.14
            IRW    0.1  BB  MT  AR  Broad      0.03     0.12
            IRW    0.5  ZZ  MT  AR    Con      0.02     0.14
            IRW    0.5  YY  MT  AR    Con      0.03     0.12

        We keep the two percentage columns because we want to be able to
        switch one or the other on or off.

        Result of the join:

            prod   prop  _1  _2  _3    _7 Snag_Perc OWC_Perc     volume  year
            IRW    0.9  AA  MT  AR  Broad      0.02     0.14   121400.0  1999
            IRW    0.1  BB  MT  AR  Broad      0.03     0.12   121400.0  1999
            IRW    0.5  ZZ  MT  AR    Con      0.02     0.14   120300.0  1999
            IRW    0.5  YY  MT  AR    Con      0.03     0.12   120300.0  1999

        Then we add the column: IRW_amount = prop * volume
        As well as the:          FW_amount = IRW_amount * (Snag_perc + OWC_Perc)

            prod   prop  _1  _2  _3    _7 Snag_Perc OWC_Perc IRW_amount  FW_amount  year
            IRW    0.9  AA  MT  AR  Broad      0.02     0.14     110000       5000  1999
            IRW    0.1  BB  MT  AR  Broad      0.03     0.12       1000         90  1999
            IRW    0.5  ZZ  MT  AR    Con      0.02     0.14      60000       4000  1999
            IRW    0.5  YY  MT  AR    Con      0.03     0.12       6000        600  1999

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

            prod  prop  _1  _2  _3    _7 Snag_Perc OWC_Perc
            FW    0.8  AA  MT  AR  Broad      0.01     0.14
            FW    0.2  BB  MT  AR  Broad      0.03     0.12
            FW    0.6  ZZ  MT  AR    Con      0.02     0.14
            FW    0.4  YY  MT  AR    Con      0.03     0.12

        Result of the join:

            prod   prop  _1  _2  _3    _7 Snag_Perc OWC_Perc     volume  year
            FW    0.8  AA  MT  AR  Broad      0.01     0.14     11423.0  1999
            FW    0.2  BB  MT  AR  Broad      0.03     0.12     11423.0  1999
            FW    0.6  ZZ  MT  AR    Con      0.02     0.14         0.0  1999
            FW    0.4  YY  MT  AR    Con      0.03     0.12         0.0  1999

        Then we add the column:  FW_amount = prop * volume * (1 + Snag_perc + OWC_Perc)
        Then we add the column:  FW_amount = prop * volume * (1 + Snag_perc + OWC_Perc)

            prod  prop  _1  _2  _3    _7 Snag_Perc OWC_Perc FW_amount  year
            FW    0.8  AA  MT  AR  Broad      0.01     0.14      5000  1999
            FW    0.2  BB  MT  AR  Broad      0.03     0.12        90  1999
            FW    0.6  ZZ  MT  AR    Con      0.02     0.14      4000  1999
            FW    0.4  YY  MT  AR    Con      0.03     0.12       600  1999

        Result:

            prod  prop  _1  _2  _3    _7 Snag_Perc OWC_Perc IRW_amount  FW_amount  year
            FW    0.9  AA  MT  AR  Broad      0.02     0.14     110000       5000  1999
            FW    0.1  BB  MT  AR  Broad      0.03     0.12       1000         90  1999
            FW    0.5  ZZ  MT  AR    Con      0.02     0.14      60000       4000  1999
            FW    0.5  YY  MT  AR    Con      0.03     0.12       6000        600  1999


        """
        # Load data #
        demands = self.country.demand.df
        # Lorem #
        #allocation =
        # Do it #
        demands.join(allocation)
        # Return #
        return df

    def add_events(self):
        """Append the new disturbances to the disturbance file."""
        # Load data #
        df = self.new_events
        # Write the result #
        df.to_csv(str(self.paths.csv), mode='a', index=False)

