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

###############################################################################
class ModelExecution(object):

    all_paths = """
    /output/cbm_formatted_db/project.mdb
    """

    def __init__(self, parent):
        # Default attributes #
        self.parent = parent
        # Directories #
        self.paths = AutoPaths(self.parent.io_dir, self.all_paths)
        # Paths to Access databases #
        self.aidb_path = toolbox_install_dir + "admin/dbs/ArchiveIndex_Beta_Install.mdb"
        # Others #
        self.cbm_exe_path = os.path.join(toolbox_install_dir, "admin", "executables")

    def __call__(self):
        with AIDB(self.aidb_path, False) as aidb, AccessDB(str(self.paths.mdb), False) as proj:
            sim_id  = aidb.AddProjectToAIDB(proj)
            cbm_wd = os.path.join(toolbox_install_dir, "temp")
            s = Simulator(executablePath   = self.cbm_exe_path,
                          simID            = sim_id,
                          projectPath      = str(self.paths.mdb.directory),
                          CBMRunDir        = cbm_wd,
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