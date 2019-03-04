# Built-in modules #
import inspect

# Third party modules #

# First party modules #
from autopaths.dir_path import DirectoryPath

# Internal modules #
from cbm_runner.runner import Runner

# Constants #
cbm_data_repos  = DirectoryPath("/repos/cbm_data/")

###############################################################################
countries = ['AT', 'BE', 'BG', 'CZ', 'DE', 'DK', 'EE', 'ES', 'FI', 'FR', 'GR',
             'HR', 'HU', 'IE', 'IT', 'LT', 'LU', 'LV', 'NL', 'PL', 'PT', 'RO',
             'SE', 'SI', 'SK', 'UK']

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
# And you can do `from cbm_runner.all_countries import AT`
for runner in all_runners:
    inspect.currentframe().f_locals[runner.country_code] = runner