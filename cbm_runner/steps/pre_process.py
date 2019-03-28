# Built-in modules #

# Third party modules #
import pandas

# First party modules #
from plumbing.cache import property_cached
from autopaths.auto_paths import AutoPaths

# Internal modules #

###############################################################################
class PreProcessor(object):
    """
    Will modify the input CSV files before handing them to SIT.
    """

    all_paths = """
    /input/csv/disturbance_events.csv
    /input/csv/disturbance_events_filtered.csv
    """

    def __init__(self, parent):
        # Default attributes #
        self.parent = parent
        # Directories #
        self.paths = AutoPaths(self.parent.data_dir, self.all_paths)

    def __call__(self):
        self.filter_dist_events(self.paths.disturbance_events, self.paths.disturbance_events_filtered)

    def filter_dist_events(self, old_path, new_path, remove_m_types=True):
        """The calibration database is configured to run over a period of
         100 years. We would like to limit the simulation to the historical
         period. Currently Year < 2015.

         Filtering M types on Sort Type 6 is necessary to avoid the famous error:

            Error:  Illegal target type for RANDOM sort in timestep 3, action number 190, in disturbance group 1, sort typ
    e 6, target type 2.
            Error:  Invalid disturbances found in .\input\disturb.lst.  Aborting.
         """
        # Load the original dataframe #
        old_df = pandas.read_csv(str(old_path))
        # Filter rows #
        period_max = self.parent.base_year - self.parent.inventory_start_year + 1
        new_df = old_df.query("Step <= %s" % period_max)
        # Special case #
        if remove_m_types: new_df = new_df.query('Sort_Type != 6 | Measurement_type == "A"')
        # Write the result #
        new_df.to_csv(str(new_path), index=False)