#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
TUTORIAL SIX - INTEGRATION TEST

Typically you would run this file from a command line like this:

     ipython.exe -i -- /deploy/cbm_runner/tests/tutorial_six/run_tutorial_six.py
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
runner = Runner(this_dir + 'data/', 'tutorial_six')
#print(runner.post_processor.classifiers)


#runner.standard_import_tool()
#runner.compute_model()
runner.graphs()
runner.reports.inventory_report()