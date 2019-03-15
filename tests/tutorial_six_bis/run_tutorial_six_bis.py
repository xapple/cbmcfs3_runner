#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
TUTORIAL SIX BIS - INTEGRATION TEST

Typically you would run this file from a command line like this:

     ipython.exe -i -- /deploy/cbm_runner/tests/tutorial_six_bis/run_tutorial_six_bis.py
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
# Object #
runner = Runner(this_dir + 'data/', 'tutorial_six_bis')

# Mock params #
runner.country_iso2 = "T6"
runner.inventory_start_year= 2050
runner.base_year = 2140

# Run but skip some steps #
runner.log.info("Running Tutorial 6 bis.")
runner.clear_all_outputs()
runner.pre_processor()
runner.csv_to_xls()
runner.aidb_switcher()
runner.standard_import_tool.run_sit()
runner.standard_import_tool.move_log()
runner.standard_import_tool.check_for_errors()
runner.compute_model()
