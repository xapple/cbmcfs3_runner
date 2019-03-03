# Built-in modules #
import os

# First party modules #
from autopaths.file_path  import FilePath
from autopaths.auto_paths import AutoPaths

# Internal modules #

# Constants #

###############################################################################
class AIDBSwitcher(object):
    """
    This class enables us to switch the famous "ArchiveIndexDatabase", between
    the canadian standard and the european standard.
    """

    default_path = "/Program Files (x86)/Operational-Scale CBM-CFS3/Admin/DBs/ArchiveIndex_Beta_Install.mdb"
    default_path = FilePath(default_path)

    all_paths = """
    /orig/aidb_eu.mdb
    """

    def __init__(self, parent):
        # Default attributes #
        self.parent = parent
        # Automatically access paths based on a string of many subpaths #
        self.paths = AutoPaths(self.parent.data_dir, self.all_paths)

    def __call__(self):
        # Check if the original AIDB is still in place #
        if self.default_path.exists and not self.default_path.is_symlink:
            back_up_path = self.default_path.new_name_insert('canada')
            self.default_path.move_to(back_up_path)
        # Make a symbolic link #
        self.default_path.remove()
        self.default_path.link_from(self.paths.aidb)