"""
A script to run all the countries.

The first step is to create the CSV files from the calibration database for every country.
The last step is generating a report with the outcome of the simulation.

Typically you would run this file from a command line like this:

     ipython.exe -i -- /deploy/cbm_runner/scripts/run_all_countries.py
"""

# Built-in modules #
import inspect

# Third party modules #
from tqdm import tqdm

# First party modules #
from autopaths.file_path import FilePath

# Internal modules #
from cbm_runner.all_countries import continent

# Constants #
this_file = FilePath((inspect.stack()[0])[1])
this_dir  = this_file.directory

###############################################################################
#for c in continent.all_countries: passing_sit += [c.country_iso2] if 'Moving' in c.tail else []
passing_sit = ['BG', 'CZ', 'DK', 'EE', 'ES', 'FI', 'FR', 'GB', 'GR', 'HR', 'LT', 'LU', 'PT', 'SI']
passing_sit = ['BG', 'DK', 'EE', 'ES', 'FI', 'GB', 'GR', 'HR', 'LT', 'LU', 'PT', 'SI']
passing_sit = [continent[c] for c in passing_sit]

###############################################################################
# Run each country and send errors to the log #
for country in tqdm(passing_sit): #tqdm(continent.all_countries, ncols=60):
    try:
        country(silent=True)
    except Exception:
        pass

###############################################################################
execfile(this_dir + 'compile_logs.py')