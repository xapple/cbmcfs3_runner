# Special variables #
__version__ = '0.2.0'

# Built-in modules #
import os, sys

# Constants #
project_name = 'cbm_runner'
project_url  = 'https://webgate.ec.europa.eu/CITnet/stash/projects/BIOECONOMY/repos/cbm_runner'

# Get paths to module #
self       = sys.modules[__name__]
module_dir = os.path.dirname(self.__file__) + '/'

# The repository directory #
from autopaths.dir_path import DirectoryPath
repos_dir = DirectoryPath(module_dir).directory

# The module is maybe in a git repository #
from plumbing.git import GitRepo
git_repo = GitRepo(repos_dir, empty=True)

# Change the pbs truncate cap #
from pbs import ErrorReturnCode
ErrorReturnCode.truncate_cap = 2000