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
from plumbing.cache import property_cached

# Internal modules #
from cbmcfs3_runner import module_dir


# Constants #
country_code_path = module_dir + 'extra_data/country_codes.csv'
ref_years_path = module_dir + 'extra_data/reference_years.csv'

# Load extra data #
country_codes = pandas.read_csv(str(country_code_path))
reference_years = pandas.read_csv(str(ref_years_path))

###############################################################################
class Reference(object):
    """
    This class will provide access to country names, iso2 codes 
    and reference years for all countries in one data frame.
    """

    def __init__(self, parent):
        # Default attributes #
        self.parent = parent

    @property_cached
    def country_ref_years(self):
        country_codes = country_codes[['country', 'iso2_code']]
        country_codes = country_codes.rename(columns = {'iso2_code' : 'country_iso2'})
        reference_years = reference_years[['country', 'ref_year']]
        reference_years = reference_years.rename(columns = {'country' : 'country_iso2',
                                                            'ref_year' : 'year'})
        df = (country_codes
              .set_index('country_iso2')
              .join(reference_years.set_index('country_iso2'))
              .reset_index())
        return df
