# Third party modules #

# First party modules #

###############################################################################
class Graphs(object):
    """
    This class will take care of creating all graphs and visualizations from both
    the input and output data.
    """

    all_paths = """
    /output/after_simulation/project.mdb
    """

    def __init__(self, parent):
        # Default attributes #
        self.parent = parent
        # Directories #
        self.paths = AutoPaths(self.parent.data_dir, self.all_paths)
