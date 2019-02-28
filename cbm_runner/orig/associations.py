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
    This class takes the file "associations.xls" and parses it.
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

    def query_to_json(self, query):
        mapping = self.df.query(query).set_index('B')['C'].to_dict()
        mapping = [{'user_admin_boundary':k, 'default_admin_boundary':v} for k,v in mapping.items()]
        string = json.dumps(mapping, indent=2)
        return pad_extra_whitespace(string, 6)

    @property_cached
    def all_mappings(self):
        """Return a dictionary of JSON structures"""
        return {
           'map_disturbance':  self.query_to_json("A == 'MapDisturbanceType'"),
           'map_eco_bound':    self.query_to_json("A == 'MapEcoBoundary'"),
           'map_admin_bound':  self.query_to_json("A == 'MapAdminBoundary'"),
           'map_species':      self.query_to_json("A == 'MapSpecies'"),
        }