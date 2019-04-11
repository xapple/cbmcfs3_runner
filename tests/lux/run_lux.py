#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
TUTORIAL LUX - INTEGRATION TEST

Typically you would run this file from a command line like this:

     ipython.exe -i -- /deploy/cbmcfs3_runner/tests/lux/run_lux.py
"""

# Built-in modules #

# Internal modules #
from cbmcfs3_runner.core.continent import continent

# Third party modules #

# Constants #

###############################################################################
# Object #
runner = continent.scenarios['static_demand'].runners['LU'][0]

# Skip some steps #
runner()
#runner.input_data.copy_from_country()
