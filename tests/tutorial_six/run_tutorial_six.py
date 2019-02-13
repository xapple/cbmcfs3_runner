#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
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
runner = Runner(this_dir + 'data/')
#runner.clear_all_outputs()
#runner.standard_input_tool()
#runner.compute_model()
runner()