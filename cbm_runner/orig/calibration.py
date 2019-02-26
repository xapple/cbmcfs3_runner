# Built-in modules #

# Third party modules #
import pyodbc

# First party modules #
from autopaths.auto_paths import AutoPaths
from plumbing.databases.access_database import AccessDatabase
from plumbing.cache import property_cached

# Internal modules #

###############################################################################
class CalibrationParser(object):
    """
    This class takes the file "calibration.mdb" as input and generates CSVs from
    it.
    """

    all_paths = """
    /orig/calibration.mdb
    /input/csv/ageclass.csv
    /input/csv/classifiers.csv
    /input/csv/disturbance_events.csv
    /input/csv/disturbance_types.csv
    /input/csv/inventory.csv
    /input/csv/transition_rules.csv
    /input/csv/yields.csv
    /input/csv/disturbance_events_hist.csv
    /input/csv/transition_rules_hist.csv
    /input/csv/yields_hist.csv
    /input/csv/coefficients.csv
    """

    def __init__(self, parent):
        # Default attributes #
        self.parent = parent
        # Automatically access paths based on a string of many subpaths #
        self.paths = AutoPaths(self.parent.parent.data_dir, self.all_paths)

    file_to_table_name = {
        "ageclass":                     "Age Classes_CBM",
        "inventory":                    "BACK_Inventory",
        "classifiers":                  "Classifiers",
        "coefficients":                 "Coefficients",
        "disturbance_types":            "Disturbance Types_CBM",
        "disturbance_events":           "Dist_Events_Const",
        "disturbance_events_hist":      "HIST_DIST_EVENTS_CBM",
        "yields":                       "SELECTED_CURRENT_YTS",
        "yields_hist":                  "SELECTED_HISTORICAL_YTS",
        "transition_rules":             "TRANSITION_CBM",
        "transition_rules_hist":        "HIST_TRANSITION_CBM",
    }

    @property_cached
    def database(self): return AccessDatabase(self.paths.mdb)

    def __call__(self):
        """Extract several queries from the database into CSV files."""
        # Make each file #
        for filename, tablename in self.file_to_table_name.items():
            self.database[tablename].to_csv(str(self.paths[filename]))

    def check(self):
        """Check that each table exists."""
        for filename, tablename in self.file_to_table_name.items():
            if tablename not in self.database:
                print("Table '%s' is missing from '%s'." % (tablename, self.database))