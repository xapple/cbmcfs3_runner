# Special variables #
__version__ = '0.1.0'

# Built-in modules #
import os, sys

# Get paths to module #
self       = sys.modules[__name__]
module_dir = os.path.dirname(self.__file__) + '/'

# The repository directory #
from autopaths.dir_path import DirectoryPath
repos_dir = DirectoryPath(module_dir).directory
