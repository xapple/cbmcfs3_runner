#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
A script to copy files into the directory structure for the "fake" calibration scenario
that we will not actually run, but pretend it has been run by directly copying the output
database into the output directory.

Typically you would run this file from a command line like this:

     ipython3.exe -i -- /deploy/cbmcfs3_runner/scripts/orig/setup_calib_scenario.py
"""

# Third party modules #
from tqdm import tqdm

# Internal modules #
from cbmcfs3_runner.core.continent import continent

# Constants #
scenario = continent.scenarios['calibration']
runners  = [r[0] for k,r in scenario.runners.items()]

###############################################################################
for r in tqdm(runners):
    calib_mdb  = r.country.paths.calibration_mdb
    output_mdb = r.post_processor.paths.project_mdb
    calib_mdb.copy(output_mdb)