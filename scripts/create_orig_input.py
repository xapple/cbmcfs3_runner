"""
A script to create the directory structure of each country and the four "orig" files.

Typically you would run this file from a command line like this:

     ipython.exe -i -- /deploy/cbm_runner/scripts/create_orig_input.py
"""

# Third party modules #

# First party modules #
from autopaths.dir_path   import DirectoryPath

# Constants #
base_path       = DirectoryPath("/forbiomod/EFDM/CBM/")
cbm_data_repos  = DirectoryPath("/repos/cbm_data/")

###############################################################################
countries = ['AT', 'BE', 'BG', 'CZ', 'DE', 'DK', 'EE', 'ES', 'FI', 'FR', 'GR',
             'HR', 'HU', 'IE', 'IT', 'LT', 'LU', 'LV', 'NL', 'PL', 'PT', 'RO',
             'SE', 'SI', 'SK', 'UK']

all_paths = """
    /orig/silviculture.sas
    /orig/calibration.mdb
    /orig/aidb_eu.mdb
    /orig/associations.xlsx
    """

# Main loop - get four files #
for code in countries:
    # Directories #
    cbm_data_dir   = cbm_data_repos + code   + '/'
    orig_data_dir  = cbm_data_dir   + 'orig' + '/'
    forbiomod_dir  = base_path      + code   + '/'
    from_calib_dir = forbiomod_dir  + 'from_CBM_calibration/'
    # x #
    aidb             = from_calib_dir + '/Archive*.mdb'
    calibration_mdb  = from_calib_dir + '/%s*.mdb' % code
    silviculture_sas = from_calib_dir + '/*.sas'
    association_xls  = from_calib_dir + '/ass*.xlsx'
    # Create #
    orig_data_dir.create_if_not_exists()
    # Copy #
    aidb.copy(             orig_data_dir + 'aidb_eu.mdb')
    calibration_mdb.copy(  orig_data_dir + 'calibration.mdb')
    silviculture_sas.copy( orig_data_dir + 'silviculture.sas')
    association_xls.copy(  orig_data_dir + 'associations.xlsx')