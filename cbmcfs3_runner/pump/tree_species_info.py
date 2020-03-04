#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Written by Lucas Sinclair and Paul Rougieux.

JRC Biomass Project.
Unit D1 Bioeconomy.

Typically you can use this class this like:

    >>> from cbmcfs3_runner.pump.tree_species_info import df as species_info
    >>> print(species_info)
"""

# Built-in modules #

# Internal modules #
from cbmcfs3_runner import module_dir

# First party modules #

# Third party modules #
import pandas

###############################################################################
def load_species_info():
    """
    This table summarizes the link between species codes used by RP and their
    mapping to actual latin names of genera and species.

    Not all codes could be identified unfortunately. Even by looking at all the
    publications.

    Most answers were found in:
    bioeconomy_notes/shared_with_us/roberto_docs/classifier_overview_nfi_cz_uk/classifiers_overview.xlsx
    """
    # Constants #
    result = module_dir + 'extra_data/species_abbreviations.csv'
    result = pandas.read_csv(str(result))
    # Fill missing values #
    for col in ['species', 'genus']:
        result[col] = result[col].fillna('missing')
    # Return #
    return result

###############################################################################
# Create a dataframe #
df = load_species_info()