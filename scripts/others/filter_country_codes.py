#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
A script to generate the country names files.
"""

# Built in modules #
import inspect

# First party modules #
from autopaths import Path

# This directory #
this_file = Path((inspect.stack()[0])[1])
this_dir  = this_file.directory

# Constants #
source = Path("/deploy/cbm_runner/data/faostat_countries.csv")
destin = this_dir + 'country_codes.csv'

# CBM module #
from cbm_runner.all_countries import continent
all_country_codes = set(c.nuts_zero_2006 for c in continent)

# Condition #
def condition(line):
    return line.strip()[-2:] in all_country_codes

# Filter #
destin.writelines(line for line in source if condition(line))