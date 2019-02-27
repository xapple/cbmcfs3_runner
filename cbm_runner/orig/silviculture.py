# Built-in modules #

# Third party modules #

# First party modules #
from autopaths.auto_paths import AutoPaths

# Internal modules #

###############################################################################
class SilvicultureParser(object):
    """
    This class takes the file "silviculture.sas" as input and generates CSVs
    from it.

                tableStart <- grep("   input",sas)
            tableEnd   <- grep ("*VARIABLE DESCRIPTION:", sas)-4

            Match made using regular expression as explained in
            1

            import re

            2

            f = open(sas_files[1],'r')

            3

            sas1 = f.read()

            4

            silv = re.findall(r'   input(.*?)VARIABLE DESCRIPTION:', sas1, re.DOTALL)

            5

            #print("\n".join(silv))

            6

            type(silv[0])

            7

            silv[0].splitlines()
            P
            P
            15:41
            silv = re.findall(r'   input(.*?)VARIABLE DESCRIPTION:', sas1, re.DOTALL)
    """

    all_paths = """
    /orig/silviculture.sas
    """

    def __init__(self, parent):
        # Default attributes #
        self.parent = parent
        # Automatically access paths based on a string of many subpaths #
        self.paths = AutoPaths(self.parent.data_dir, self.all_paths)

    def __call__(self):
        pass
