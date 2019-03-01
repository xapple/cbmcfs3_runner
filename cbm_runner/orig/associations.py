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
    This class takes the file "associations.xls" and parses it producing JSON
    strings for consumption by SIT.
    """

    all_paths = """
    /orig/associations.xlsx
    """

    def __init__(self, parent):
        # Default attributes #
        self.parent = parent
        # Automatically access paths based on a string of many subpaths #
        self.paths = AutoPaths(self.parent.parent.data_dir, self.all_paths)

    @property_cached
    def df(self):
        self.paths.xlsx.must_exist()
        self.xls = pandas.ExcelFile(str(self.paths.xlsx))
        return self.xls.parse('associations')

    def query_to_json(self, mapping_name, user, default):
        """Create a JSON string by picking some rows in the excel file."""
        # Get rows #
        query   = "A == '%s'" % mapping_name
        mapping = self.df.query(query).set_index('B')['C'].to_dict()
        mapping = [{user:k, default:v} for k,v in mapping.items()]
        # Format JSON #
        string  = json.dumps(mapping, indent=2)
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
                                                 'default_eco_boundary'),
           'map_admin_bound': self.query_to_json('MapAdminBoundary',
                                                 'user_admin_boundary',
                                                 'default_admin_boundary'),
           'map_species':     self.query_to_json('MapSpecies',
                                                 'user_species',
                                                 'default_species'),
        }