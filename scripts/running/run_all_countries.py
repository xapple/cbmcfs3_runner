#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
A script to run all the countries.

The first step is to create the CSV files from the calibration database for every country.
The last step is generating a report with the outcome of the simulation.

Typically you would run this file from a command line like this:

     ipython.exe -i -- /deploy/cbmcfs3_runner/scripts/run_all_countries.py
"""

# Built-in modules #
import inspect

# Third party modules #
from tqdm import tqdm

# First party modules #
from autopaths import Path

# Internal modules #
from cbmcfs3_runner.continent import continent

###############################################################################
# Run each country and send errors to the log #
for country in tqdm(continent.all_countries[:11], ncols=60):
    try:
        country(silent=True)
    except Exception:
        pass

###############################################################################
# Update the log summary
this_file = Path((inspect.stack()[0])[1])
this_dir  = this_file.directory
execfile(this_dir + 'compile_logs.py')