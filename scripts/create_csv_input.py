"""
A script to create the CSV files from the calibration database for every country.

Typically you would run this file from a command line like this:

     ipython.exe -i -- /deploy/cbm_runner/scripts/create_csv_input.py
"""

# Built-in modules #
import inspect

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

###############################################################################
# Create one runner object for each country
all_runners = []
for code in countries:
    cbm_data_dir = cbm_data_repos + code + '/'
    runner = Runner(cbm_data_dir, code)
    all_runners.append(runner)

###############################################################################
# Black magic: set a variable with the country code in the global namespace
# so that print(AT) for instance will show the Runner() instance for Austria
for runner in all_runners:
    inspect.currentframe().f_locals[runner.country_code] = runner

###############################################################################
# Run each country and send errors to the log  #
for runner in all_runners:
    try:
        runner()
    except Exception:
        message = "Country '%s' encountered an exception. See log file."
        runner.log.error(message % runner.country_code)
        runner.log.exception("Exception", exc_info=1)
        raise
    1/0

###############################################################################
# Main loop #
for runner in all_runners:
    # Create CSVs #
    #runner.orig_to_csv.calibration_parser()
    #runner.orig_to_csv.associations_parser()
    # Create XLS #
    #runner.csv_to_xls()
    # Mappings #
    #print runner.orig_to_csv.associations_parser.all_mappings
    # AIDB #
    #runner.switcher()
    # SIT #
    #runner.standard_import_tool()
    #runner.standard_import_tool.create_json_config()
    #runner.standard_import_tool.run_sit()
    #runner.standard_import_tool.move_log()
    # SAS
    #x = runner.orig_to_csv.silviculture_parser
    #1/0
    pass