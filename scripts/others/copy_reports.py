#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
A script to copy PDF reports from the distant machine to the local workstation.

Typically you would run this file from a command line like this:

     python3 ~/repos/cbmcfs3_runner/scripts/others/copy_reports.py
"""

# Built-in modules #
import os

# Third party modules #
import pbs3

# Constants #
home = os.environ.get('HOME', '~') + '/'

###############################################################################
pbs3.rsync('-avz', 'cbm1:repos/cbmcfs3_data/reports/countries/',
                 home + 'repos/cbmcfs3_data/reports/countries/')