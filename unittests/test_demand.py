#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test post processor - UNIT TEST

This script is just a stub, and need to be completed.
"""

# Third party modules #
import pandas
from six import StringIO

# Internal modules #
from cbmcfs3_runner.disturbances.demand import Demand

# Constants #

###############################################################################
def test_demand_parsing():
    """This example is under development, not completed."""

    # Fake object #
    obj = Demand()
    obj.gftm_header = 0

    # Input #
    input_row = """a | X | X  | Y | Y  | Z  | Z
                   b | C | N  | C | N  | C  | N"""
    input_row = StringIO(input_row.replace(' ',''))
    input_row = pandas.read_csv(input_row, sep="|", header=None)

    # Output
    wanted_out = """a |  b |  c | value
                    X |  C |  i |     3
                    X |  N |  i |    10
                    Y |  C |  i |     4
                    Y |  N |  j |    98
                    Z |  C |  j |    81
                    Z |  N |  j |     0"""
    wanted_out = StringIO(df.replace(' ',''))
    wanted_out = pandas.read_csv(df, sep="|", header=None)

    # Processing
    computed_out = obj.df

    # Compare
    assert computed_out == wanted_out