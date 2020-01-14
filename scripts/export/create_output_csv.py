#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
A script to create all useful export CSVs.

Typically you would run this file from a command line like this:

     ipython3.exe -i -- /deploy/cbmcfs3_runner/scripts/export/create_output_csv.py
"""

# Built-in modules #

# Third party modules #

# First party modules #

# Internal modules #
from cbmcfs3_runner.core.continent import continent

###############################################################################
scenario = continent.scenarios['historical']
scenario