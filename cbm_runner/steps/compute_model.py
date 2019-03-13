# Built-in modules #

# Third party modules #
from simulation.simulator import Simulator
from cbm3data.aidb        import AIDB
from cbm3data.accessdb    import AccessDB as LegacyDB

# First party modules #
from autopaths.dir_path   import DirectoryPath
from autopaths.auto_paths import AutoPaths

# Internal modules #

# Constants #
toolbox_install_dir = DirectoryPath("/Program Files (x86)/Operational-Scale CBM-CFS3")
aidb_path           = toolbox_install_dir + "admin/dbs/ArchiveIndex_Beta_Install.mdb"
cbm_exes_path       = toolbox_install_dir + "admin/executables/"
cbm_work_dir        = toolbox_install_dir + "temp/"

###############################################################################
class ComputeModel(object):
    """
    This class will run CBM-CFS3.exe from the command line without using the GUI.
    It will take a Microsoft Access database (as created by SIT) as input.
    Then it will produce a new Microsoft Access database as output.
    If the input database is in a different location than when it was created
    by SIT, the tool will not work in the same way. Side-effects are everywhere.
    """

    all_paths = """
    /output/cbm_formatted_db/project.mdb
    /output/cbm_tmp_dir/project.mdb
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
        #self.setup_tmp_dir()
        self.run_simulator()
        self.copy_output()

    def setup_tmp_dir(self):
        """This doesn't seem to work, we don't get the same results if
        we operate on a copy of the output from SIT."""
        self.paths.formatted_mdb.copy(self.paths.tmp_mdb)

    def run_simulator(self):
        """
        Part of this code was taken from:
        https://github.com/cat-cfs/cbm3_python/blob/master/simulate.py#L36
        """
        # Paths #
        database = self.paths.tmp_mdb # Fails for unknown reason, don't use
        database = self.paths.formatted_mdb
        # Messages #
        self.log.info("Launching the CBM-CFS3 model.")
        self.log.debug("Database path '%s'." % database)
        self.log.debug("Working directory path '%s'." % cbm_work_dir)
        # Open contexts managers #
        with AIDB(aidb_path, False) as aidb, \
             LegacyDB(str(database), False) as proj:
        # Run all methods #
            self.log.info("Adding the project to the AIDB.")
            self.sim_id = aidb.AddProjectToAIDB(proj)
            self.log.debug("Received simulation ID %i." % self.sim_id)
            s = Simulator(executablePath   = str(cbm_exes_path),
                          simID            = self.sim_id,
                          projectPath      = str(database.directory),
                          CBMRunDir        = str(cbm_work_dir),
                          toolboxPath      = str(toolbox_install_dir))
            s.CleanupRunDirectory()
            s.CreateMakelistFiles()
            s.copyMakelist()
            s.runMakelist()
            s.loadMakelistSVLS()
            s.DumpMakelistSVLs()
            s.copyMakelistOutput()
            s.CreateCBMFiles()
            s.CopyCBMExecutable()
            s.RunCBM()
            s.CopyTempFiles()
            s.LoadCBMResults()
        self.log.info("The CBM-CFS3 model run is completed.")

    @property
    def generated_database(self):
        """Will be in a directory created by CBM."""
        path = self.paths.formatted_dir + str(self.sim_id) + '/' + str(self.sim_id) + '.mdb'
        path.must_exist()
        return path

    def copy_output(self):
        """Place the generated database in a separate directory."""
        self.generated_database.copy(self.paths.after_mdb)
