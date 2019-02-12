# Built-in modules #

# Third party modules #
import pbs

# Internal modules #

###############################################################################
class StandardImportTool(object):

    all_paths = """
    /input/inv_and_dist.xls
    /input/sit_config.json
    """

    def __init__(self, parent):
        # Default attributes #
        self.parent = parent
        # Directories #
        self.p = AutoPaths(self.parent.io_dir, self.all_paths)

    def __call__(self):
        pbs("StandardImportToolPlugin.exe", '-c', self.p.json)
