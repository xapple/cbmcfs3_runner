# Built-in modules #

# Third party modules #
import pbs

# Internal modules #

###############################################################################
class AIDBSwitcher(object):

    all_paths = """
    """

    def __init__(self, parent):
        # Default attributes #
        self.parent      = parent
        # Directories #
        self.p = AutoPaths(self.parent.io_dir, self.all_paths)
        # Because os.paths.join acts strangely #
        self.raw_dir = str(self.p.layers_dir)

    def switch_to_europe(self):
        shutil.move()

    def switch_to_canada(self):
        shutil.move()
