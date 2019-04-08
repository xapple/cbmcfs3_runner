# Built-in modules #

# Third party modules #
import pandas

# First party modules #
from plumbing.cache import property_cached
from autopaths.auto_paths import AutoPaths
from plumbing.databases.access_database import AccessDatabase

# Internal modules #

###############################################################################
class MiddleProcessor(object):
    """
    Will modify the access database after its creation by SIT but before its
    usage by CBM.
    """

    all_paths = """
    /output/cbm_formatted_db/project.mdb
    """

    def __init__(self, parent):
        # Default attributes #
        self.parent = parent
        # Directories #
        self.paths = AutoPaths(self.parent.data_dir, self.all_paths)

    @property_cached
    def project_database(self):
        return AccessDatabase(self.paths.project_mdb)

    def extend_simulation(self, N_steps):
        """Will extend the simulation by N timesteps so that it runs extra
        years without disturbances."""
        query = "UPDATE tblRunTableDetails SET tblRunTableDetails.RunLength = %s" % N_steps
        self.project_database.cursor.exexcute(query)
