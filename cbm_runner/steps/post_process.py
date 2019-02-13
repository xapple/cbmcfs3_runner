# Built-in modules #

# Third party modules #

# First party modules #
from plumbing.cache import property_cached

# Internal modules #

###############################################################################
class PostProcessor(object):
    """
    Lorem.
    """

    all_paths = """
    /output/after_simulation/project.mdb
    """

    def __init__(self, parent):
        # Default attributes #
        self.parent = parent
        # Directories #
        self.paths = AutoPaths(self.parent.data_dir, self.all_paths)

    @property_cached
    def predicted_inventory(self):
        return 0