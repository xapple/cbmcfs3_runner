# Built-in modules #
import os

# First party modules #
from autopaths.file_path  import FilePath
from autopaths.auto_paths import AutoPaths
from plumbing.databases.access_database import AccessDatabase
from plumbing.cache import property_cached

# Internal modules #

# Constants #

###############################################################################
class AIDB(object):
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

    def switch(self):
        self.default_path.remove()
        self.paths.aidb.copy(self.default_path)

    @property_cached
    def database(self): return AccessDatabase(self.paths.aidb)

    @property_cached
    def admin_boundary(self): return self.database['tblAdminBoundaryDefault']

    @property_cached
    def eco_boundary(self): return self.database['tblEcoBoundaryDefault']

    @property_cached
    def species_type(self): return self.database['tblSpeciesTypeDefault']
