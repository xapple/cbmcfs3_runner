"""
A script to create the directory structure of each country and the four "orig" files.
"""

# Third party modules #

# First party modules #
from autopaths.dir_path   import DirectoryPath

# Constants #
base_path = "/forbiomod/EFDM/CBM/"

###############################################################################
countries = ['AT', 'BE', 'BG', 'CZ', 'DE', 'DK', 'EE', 'ES', 'FI', 'FR', 'GR',
             'HR', 'HU', 'IE', 'IT', 'LT', 'LU', 'LV', 'NL', 'PL', 'PT', 'RO',
             'SE', 'SI', 'SK', 'UK']

for code in countries:
  country_dir = DirectoryPath()