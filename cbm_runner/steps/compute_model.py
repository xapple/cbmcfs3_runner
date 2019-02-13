# Built-in modules #

# Third party modules #
from simulation.simulator import Simulator
from cbm3data.aidb        import AIDB
from cbm3data.accessdb    import AccessDB

# First party modules #
from autopaths.dir_path   import DirectoryPath
from autopaths.file_path  import FilePath
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
    It will take an Microsoft Access database (as created by SIT) as input.
    Then it will produce a new Microsoft Access database as output.
    If the input database is in a different location than when it was created
    by SIT, the tool will not work in the same way. Side-effects are everywhere.
    """

    all_paths = """
    /output/cbm_formatted_db/project.mdb
    /output/cbm_tmp_dir/project.mdb
    /output/cbm_tmp_dir/project.cbmproj  
    /output/after_simulation/project.mdb
    /logs/compute_model.log
    """

    def __init__(self, parent):
        # Default attributes #
        self.parent = parent
        # Directories #
        self.paths = AutoPaths(self.parent.data_dir, self.all_paths)

    def __call__(self):
        self.setup_tmp_dir()
        #self.run_simulator(self.paths.tmp_mdb) # Fails for unknown reason
        self.run_simulator(self.paths.formatted_mdb)
        self.copy_output()

    def setup_tmp_dir(self):
        self.paths.formatted_mdb.copy(self.paths.tmp_mdb)

    def run_simulator(self, database):
        """
        This code was taken from:
        https://github.com/cat-cfs/cbm3_python/blob/master/simulate.py#L36
        """
        # Open contexts managers #
        with AIDB(aidb_path, False) as aidb, \
             AccessDB(str(database), False) as proj:
        # Run all methods #
            self.sim_id = aidb.AddProjectToAIDB(proj)
            s = Simulator(executablePath   = cbm_exes_path,
                          simID            = self.sim_id,
                          projectPath      = str(database.directory),
                          CBMRunDir        = cbm_work_dir,
                          toolboxPath      = toolbox_install_dir)
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

    @property
    def generated_database(self):
        """Will be in a direcotry created by CBM."""
        return self.paths.cbm_tmp_dir + str(self.sim_id) + '/' + str(self.sim_id) + '.mdb'

    def copy_output(self):
        """Place the generated database in a separate directory."""
        self.generated_database.copy(self.paths.after_mdb)
