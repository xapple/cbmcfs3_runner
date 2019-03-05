# Built-in modules #
import json

# Third party modules #
import pandas

# First party modules #
from autopaths.auto_paths import AutoPaths
from plumbing.cache import property_cached
from plumbing.common import pad_extra_whitespace

# Internal modules #

###############################################################################
class AssociationsParser(object):
    """
    This class takes the file "associations.xlsx" and converts it to CSV.
    Then later, it parses the CSV producing JSON strings for consumption by SIT.
    """

    all_paths = """
    /orig/associations.xlsx
    /input/csv/associations.csv
    """

    def __init__(self, parent):
        # Default attributes #
        self.parent = parent
        # Automatically access paths based on a string of many subpaths #
        self.paths = AutoPaths(self.parent.parent.data_dir, self.all_paths)

    @property
    def log(self): return self.parent.parent.log

    def __call__(self):
        """Convert the XLSX to CSV."""
        self.log.info("Converting associations.xlsx to associations.csv")
        self.paths.xlsx.must_exist()
        self.xlsx = pandas.ExcelFile(str(self.paths.xlsx))
        self.xlsx.parse('associations').to_csv(str(self.paths.csv), index=False)

    @property_cached
    def df(self):
        self.paths.csv.must_exist()
        return pandas.read_csv(str(self.paths.csv))

    def query_to_json(self, mapping_name, user, default,
                      standard=True, add_default=False, add_user=False):
        """Create a JSON string by picking the appropriate rows in the CSV file.
        If *add_default* is True, we are going to add a mapping that maps
        all the names in AIDB back to the same name. In case these are used
        in the calibration database. If they are not, this should have no impact.
        If add_user is True, we will map each username back to the same username"""
        # Get rows #
        query   = "A == '%s'" % mapping_name
        mapping = self.df.query(query).set_index('B')['C'].to_dict()
        # The mappings #
        standard_mapping = [{user:k, default:v} for k,v in mapping.items()]
        user_to_user     = [{user:k, default:k} for k,v in mapping.items()]
        deflt_to_deflt   = [{user:v, default:v} for k,v in mapping.items()]
        # Add only the ones we want #
        result = []
        if standard:    result += standard_mapping
        if add_user:    result += user_to_user
        if add_default: result += deflt_to_deflt
        # Format JSON #
        string  = json.dumps(result, indent=2)
        string  = pad_extra_whitespace(string, 6).strip(' ')
        # Return #
        return string

    @property_cached
    def all_mappings(self):
        """Return a dictionary of JSON structures for consumption by mustache
        templating engine."""
        return {
           'map_disturbance': self.query_to_json('MapDisturbanceType',
                                                 'user_dist_type',
                                                 'default_dist_type'),
           'map_eco_bound':   self.query_to_json('MapEcoBoundary',
                                                 'user_eco_boundary',
                                                 'default_eco_boundary', standard=False, add_user=True),
           'map_admin_bound': self.query_to_json('MapAdminBoundary',
                                                 'user_admin_boundary',
                                                 'default_admin_boundary'),
           'map_species':     self.query_to_json('MapSpecies',
                                                 'user_species',
                                                 'default_species'),
        }