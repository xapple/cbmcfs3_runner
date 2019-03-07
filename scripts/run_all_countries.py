"""
A script to run all the countries.

The first step is to create the CSV files from the calibration database for every country.
The last step is generating a report with the outcome of the simulation.

Typically you would run this file from a command line like this:

     ipython.exe -i -- /deploy/cbm_runner/scripts/run_all_countries.py
"""

# Built-in modules #

# Third party modules #
from tqdm import tqdm

# First party modules #

# Internal modules #
from cbm_runner.all_countries import *

###############################################################################
# Run each country and send errors to the log  #
for country in tqdm(all_countries, ncols=60):
    try:
        country(silent=True)
    except Exception:
        pass

###############################################################################
# For debugging #
#for runner in all_runners:
    #print runner.input_data.classifiers
    #print runner.aidb_switcher.admin_boundary
    #print runner.aidb_switcher.eco_boundary
    #1/0
    # Create CSVs #
    #runner.orig_to_csv.calibration_parser()
    #runner.orig_to_csv.associations_parser()
    # Create XLS #
    #runner.csv_to_xls()
    # Mappings #
    #print runner.orig_to_csv.associations_parser.all_mappings
    # AIDB #
    #runner.aidb_switcher()
    # SIT #
    #runner.standard_import_tool()
    #runner.standard_import_tool.create_json_config()
    #runner.standard_import_tool.run_sit()
    #runner.standard_import_tool.move_log()
    # SAS
    #x = runner.orig_to_csv.silviculture_parser
    #1/0
