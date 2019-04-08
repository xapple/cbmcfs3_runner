# Special variables #
__version__ = '0.2.1'

# Built-in modules #
import os, sys

# First party modules #
from autopaths.dir_path import DirectoryPath
from plumbing.git import GitRepo

# Constants #
project_name = 'cbmcfs3_runner'
project_url  = 'https://webgate.ec.europa.eu/CITnet/stash/projects/BIOECONOMY/repos/cbmcfs3_runner'

# Get paths to module #
self       = sys.modules[__name__]
module_dir = DirectoryPath(os.path.dirname(self.__file__))

# The repository directory #
repos_dir = module_dir.directory

# The module is maybe in a git repository #
git_repo = GitRepo(repos_dir, empty=True)

# Change the pbs truncate cap for longer stderr #
if os.name == "posix": from sh  import ErrorReturnCode
if os.name == "nt":    from pbs import ErrorReturnCode
ErrorReturnCode.truncate_cap = 2000