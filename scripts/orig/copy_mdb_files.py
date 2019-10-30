#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
A script to create the directory structure of each country and three of the "orig" files.

Typically you would run this file from a command line like this:

     ipython3.exe -i -- /deploy/cbmcfs3_runner/scripts/orig/copy_orig_files.py
"""

# Third party modules #

# First party modules #
from autopaths import Path

# Constants #
base_path       = Path("/forbiomod/EFDM/CBM/")
cbm_data_repos  = Path("/repos/cbmcfs3_data/")

###############################################################################
countries = ['AT', 'BE', 'BG', 'CZ', 'DE', 'DK', 'EE', 'ES', 'FI', 'FR', 'GR',
             'HR', 'HU', 'IE', 'IT', 'LT', 'LU', 'LV', 'NL', 'PL', 'PT', 'RO',
             'SE', 'SI', 'SK', 'UK']

all_paths = """
/orig/silviculture.sas
/orig/calibration.mdb
/orig/aidb_eu.mdb
"""

for code in countries:
    # Get 4 directories #
    cbm_data_dir   = cbm_data_repos + code   + '/'
    orig_data_dir  = cbm_data_dir   + 'orig' + '/'
    forbiomod_dir  = base_path      + code   + '/'
    from_calib_dir = forbiomod_dir  + 'from_CBM_calibration/'
    # Get 3 files #
    aidb             = from_calib_dir + '/Archive*.mdb'
    calibration_mdb  = from_calib_dir + '/%s*.mdb' % code
    silviculture_sas = from_calib_dir + '/*.sas'
    # Create destination #
    orig_data_dir.create_if_not_exists()
    # Copy #
    aidb.copy(            orig_data_dir + 'aidb_eu.mdb')
    calibration_mdb.copy( orig_data_dir + 'calibration.mdb')
    silviculture_sas.copy(orig_data_dir + 'silviculture.sas')
