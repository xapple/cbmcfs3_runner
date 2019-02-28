"""
A script to create the CSV files from the calibration database for every country.

Typically you would run this file from a command line like this:

     ipython.exe -i -- /deploy/cbm_runner/scripts/create_csv_input.py
"""

# Third party modules #
from tqdm import tqdm

# First party modules #
from autopaths.dir_path   import DirectoryPath

# Internal modules #
from cbm_runner.runner import Runner

# Constants #
cbm_data_repos  = DirectoryPath("/repos/cbm_data/")

###############################################################################
countries = ['AT', 'BE', 'BG', 'CZ', 'DE',       'EE', 'ES', 'FI', 'FR', 'GR',
             'HR', 'HU', 'IE', 'IT',       'LU', 'LV', 'NL', 'PL', 'PT', 'RO',
             'SE', 'SI',       'UK']

countries_skipped = ['LT', 'SK', 'DK']

# Main loop #
for code in tqdm(countries):
    # Directories #
    cbm_data_dir   = cbm_data_repos + code   + '/'
    # Runner #
    runner = Runner(cbm_data_dir)
    # Create CSVs #
    #runner.orig_to_csv.calibration_parser()
    # Create XLS #
    #runner.csv_to_xls()
    # Mappings #
    #print runner.orig_to_csv.associations_parser.all_mappings
    # SIT #
    #runner.standard_import_tool()
    x = runner.orig_to_csv.silviculture_parser
    1/0