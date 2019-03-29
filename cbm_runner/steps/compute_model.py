# Built-in modules #

# Third party modules #
from cbm3_python.simulation import projectsimulator

# First party modules #
from autopaths.dir_path   import DirectoryPath
from autopaths.auto_paths import AutoPaths
from plumbing.databases.access_database import AccessDatabase

# Internal modules #

# Constants #
toolbox_install_dir = DirectoryPath("/Program Files (x86)/Operational-Scale CBM-CFS3")
aidb_path           = toolbox_install_dir + "admin/dbs/ArchiveIndex_Beta_Install.mdb"
cbm_exes_path       = toolbox_install_dir + "admin/executables/"

###############################################################################
class ComputeModel(object):
    """
    This class will run CBM-CFS3.exe from the command line without using the GUI.
    It will take a Microsoft Access database (as created by SIT) as input.
    Then it will produce a new Microsoft Access database as output.
    If the input database is in a different location than when it was created
    by SIT, the tool will not work in the same way. Side-effects are everywhere.

    It currently expects a specific nightly build of the CBM software.
    """

    all_paths = """
    /output/cbm_formatted_db/project.mdb
    /output/cbm_tmp_dir/
    /output/after_simulation/project.mdb
    /logs/compute_model.log
    """

    def __init__(self, parent):
        # Default attributes #
        self.parent = parent
        # Directories #
        self.paths = AutoPaths(self.parent.data_dir, self.all_paths)

    @property
    def log(self): return self.parent.log

    def __call__(self):
        self.run_simulator()

    def setup_tmp_dir(self):
        """This doesn't seem to work, we don't get the same results if
        we operate on a copy of the output from SIT."""
        self.paths.formatted_mdb.copy(self.paths.tmp_mdb)

    def run_simulator(self):
        """Launch CBM and all its executables."""
        # Paths #
        database = self.paths.formatted_mdb
        # Messages #
        self.log.info("Launching the CBM-CFS3 model.")
        self.log.debug("Database path '%s'." % database)
        # Arguments #
        kwargs = {
            'aidb_path'                : str(aidb_path),
            'project_path'             : str(self.paths.formatted_mdb),
            'toolbox_installation_dir' : str(toolbox_install_dir),
            'cbm_exe_path'             : str(cbm_exes_path),
            'results_database_path'    : str(self.paths.after_simulation_mdb),
            'tempfiles_output_dir'     : str(self.paths.output_dir + "cbm_tmp_dir"),
            'afforestation_only'       : False,
        }
        # Use their module #
        self.results_path = projectsimulator.run(**kwargs)
        # Success message #
        self.log.info("The CBM-CFS3 model run is completed.")

    @property
    def generated_database(self):
        """Will be in a directory created by CBM."""
        return AccessDatabase(self.paths.after_simulation_mdb)
