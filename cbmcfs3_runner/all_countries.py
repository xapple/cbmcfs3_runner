# Built-in modules #
import inspect

# Third party modules #

# First party modules #

# Internal modules #
from cbmcfs3_runner.continent import continent

###############################################################################
# Black magic: set a variable with the country code in the global namespace
# so that print(AT) for instance will show the Country() instance for Austria
# And you can do `from cbmcfs3_runner.all_countries import AT`
for country in continent.all_countries:
    inspect.currentframe().f_locals[country.country_iso2] = country