# Built-in modules #
import shutil

# Third party modules #

# Internal modules #

###############################################################################
class AIDBSwitcher(object):
    """
    This class enables us to switch the famous "ArchiveIndexDatabase", between
    the canadian standard and the european standard.
    """

    def __init__(self, parent):
        # Default attributes #
        self.parent = parent

    def switch_to_europe(self):
        pass
        shutil.move()

    def switch_to_canada(self):
        pass
        shutil.move()
