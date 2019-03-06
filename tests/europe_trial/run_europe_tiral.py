#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
EUROPE TRIAL - INTEGRATION TEST

Typically you would run this file from a command line like this:

     ipython.exe -i -- /deploy/cbm_runner/tests/europe_trial/run_europe_trial.py
"""

# Built-in modules #
import inspect

# Internal modules #
from cbm_runner.runner import Runner

# Third party modules #
from autopaths.file_path import FilePath

# Constants #
this_file = FilePath((inspect.stack()[0])[1])
this_dir  = this_file.directory

###############################################################################
runner = Runner(this_dir + 'data/', 'europe_trial')
runner.csv_to_xls()
runner.aidb_switcher()
runner.standard_import_tool()