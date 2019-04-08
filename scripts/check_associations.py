"""
A script to test if the associations.csv are good.

Typically you would run this file from a command line like this:

     ipython.exe -i -- /deploy/cbmcfs3_runner/scripts/check_associations.py
"""

# Built-in modules #

# Third party modules #

# First party modules #

# Internal modules #
from cbmcfs3_runner.all_countries import continent

# Constants #

###############################################################################
for country in continent: country.orig_to_csv.associations_parser.list_missing()
