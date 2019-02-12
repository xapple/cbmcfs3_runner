# Built-in modules #
import shutil

# Third party modules #

# Internal modules #

###############################################################################
class AIDBSwitcher(object):

    all_paths = """
    """

    def __init__(self, parent):
        # Default attributes #
        self.parent = parent
        # Directories #
        self.p = AutoPaths(self.parent.data_dir, self.all_paths)

    def switch_to_europe(self):
        shutil.move()

    def switch_to_canada(self):
        shutil.move()
