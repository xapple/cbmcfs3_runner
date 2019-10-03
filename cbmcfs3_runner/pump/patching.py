#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Written by Lucas Sinclair and Paul Rougieux.

JRC biomass Project.
Unit D1 Bioeconomy.
"""

# Built-in modules #

# First party modules #

# Third party modules #
import pandas

# Internal modules #
from cbmcfs3_runner.pump.common import left_join

###############################################################################
# Add a nice method to DataFrame objects #
pandas.DataFrame.left_join = left_join

