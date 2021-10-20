#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Written by Lucas Sinclair and Paul Rougieux.

JRC biomass Project.
Unit D1 Bioeconomy.

Provides access to a mapping table between cbmcfs3 pool names and libcbm pool names.

You can use this object like this:

    >>> from cbmcfs3_runner.pump.libcbm_mapping import libcbm_mapping
    >>> print(libcbm_mapping)
"""

# Third party modules #
import pandas

# Internal modules #
from cbmcfs3_runner import module_dir

# Load a dataframe #
libcbm_mapping_path = module_dir + 'extra_data/libcbm_pools.csv'
libcbm_mapping = pandas.read_csv(libcbm_mapping_path)

