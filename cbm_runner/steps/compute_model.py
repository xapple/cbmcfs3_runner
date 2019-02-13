# Built-in modules #
import os

# Third party modules #
from simulation.simulator import Simulator
from cbm3data.aidb        import AIDB
from cbm3data.accessdb    import AccessDB

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

    all_paths = """
    /output/cbm_formatted_db/project.mdb
    /output/cbm_tmp_dir/project.mdb
    /output/cbm_tmp_dir/project.cbmproj  
    /logs/compute_model.log
    """

    def __init__(self, parent):
        # Default attributes #
        self.parent = parent
        # Directories #
        self.paths = AutoPaths(self.parent.data_dir, self.all_paths)

    def __call__(self):
        self.setup_tmp_dir()
        self.run_simulator()

    def setup_tmp_dir(self):
        self.paths.formatted_mdb.copy(self.paths.tmp_mdb)

    def run_simulator(self):
        # Open contexts managers #
        with AIDB(aidb_path, False)                   as aidb, \
             AccessDB(str(self.paths.formatted_mdb), False) as proj:
        # Run all methods #
            self.sim_id = aidb.AddProjectToAIDB(proj)
            s = Simulator(executablePath   = cbm_exes_path,
                          simID            = self.sim_id,
                          projectPath      = str(self.paths.formatted_mdb.directory),
                          CBMRunDir        = cbm_work_dir,
                          toolboxPath      = toolbox_install_dir)
            # This list of operations is taken from "simulator.py" #
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