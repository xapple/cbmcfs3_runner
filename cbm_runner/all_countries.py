# Built-in modules #
import inspect

# Third party modules #

# First party modules #
from autopaths.dir_path import DirectoryPath

# Internal modules #
from cbm_runner.country import Country

# Constants #
cbm_data_repos  = DirectoryPath("/repos/cbm_data/")

###############################################################################
# Retrieve list of all countries #
all_countries = [Country(d) for d in cbm_data_repos.flat_directories if 'orig' in d]

# For backwards compatibility #
all_runners = all_countries

###############################################################################
# Black magic: set a variable with the country code in the global namespace
# so that print(AT) for instance will show the Runner() instance for Austria
# And you can do `from cbm_runner.all_countries import AT`
for country in all_countries:
    inspect.currentframe().f_locals[country.country_iso2] = country