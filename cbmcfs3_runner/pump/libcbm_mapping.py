#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Written by Lucas Sinclair and Paul Rougieux.

JRC biomass Project.
Unit D1 Bioeconomy.

Provides access to a mapping table between cbmcfs3 pool names and libcbm pool names.

You can use this object like this:

    >>> from cbmcfs3_runner.pump import libcbm_mapping
    >>> print("Pools\n", libcbm_mapping.pools)
    >>> print("Turnover rates\n", libcbm_mapping.turnover_rates)
    >>> print("Decay rates\n", libcbm_mapping.decay_rates)

"""

# Third party modules #
import pandas

# Internal modules #
from cbmcfs3_runner import module_dir

# Load a correspondance table between cbmcfs3 and libcbm pool names
pools = pandas.read_csv(module_dir + 'extra_data/libcbm_pools.csv')
# Keep a legacy name for compatibility purposes
libcbm_mapping = pools

# Load a correspondance table between cbmcfs3 and libcbm turnover rates
turnover_rates = pandas.read_csv(module_dir + 'extra_data/libcbm_turnover_rates.csv')

decay_rates = pandas.read_csv(module_dir + 'extra_data/libcbm_decay_rates.csv')

cbmcfs3_pools = pandas.read_csv(module_dir + 'extra_data/cbmcfs3_dom_pools.csv')
