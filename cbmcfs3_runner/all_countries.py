# Built-in modules #
import inspect

# Third party modules #

# First party modules #
from autopaths.dir_path import DirectoryPath

# Internal modules #
from cbmcfs3_runner.continent import Continent

# Constants #
cbm_data_repos = DirectoryPath("/repos/cbm_data/")

###############################################################################
# Create list of all countries #
continent = Continent(cbm_data_repos)

###############################################################################
# Black magic: set a variable with the country code in the global namespace
# so that print(AT) for instance will show the Runner() instance for Austria
# And you can do `from cbmcfs3_runner.all_countries import AT`
for country in continent.all_countries:
    inspect.currentframe().f_locals[country.country_iso2] = country