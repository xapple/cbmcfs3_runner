# Built-in modules #
import json
from collections import OrderedDict

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
    This class takes the file "calibration.mdb" as well as the "aidb.mdb" and
    creates a CSV containing mappings between names.
    Then later, it parses the CSV created to produce JSON strings
    for consumption by SIT.
    """

    all_paths = """
    /input/csv/associations.csv
    """

    def __init__(self, parent):
        # Default attributes #
        self.parent = parent
        # Automatically access paths based on a string of many subpaths #
        self.paths = AutoPaths(self.parent.parent.data_dir, self.all_paths)
        # Used in multiple places #
        self.keys = ['MapAdminBoundary', 'MapEcoBoundary', 'MapSpecies', 'MapDisturbanceType']

    @property
    def log(self): return self.parent.parent.log

    @property
    def aidb(self): return self.parent.parent.aidb_switcher.database

    @property
    def calib(self): return self.parent.calibration_parser.database

    def select_rows(self, classifier_name):
        query  = "ClassifierValueID == '_CLASSIFIER' and Name == '%s'" % classifier_name
        number = self.calib['Classifiers'].query(query)['ClassifierNumber'].iloc[0]
        query  = "ClassifierValueID != '_CLASSIFIER' and ClassifierNumber == %i" % number
        rows   = self.calib['Classifiers'].query(query)
        return rows

    def regenerate_csv(self):
        """Run this once before manually fixing the CSVs.
        The keys are the names in the calibration.mdb
        The values are the names in the aidb.mdb"""
        # Admin boundaries #
        self.admin   = [(k,k) for k in self.select_rows('Region')['Name']]
        # Eco boundaries #
        self.eco     = [(k,k) for k in self.select_rows('Climatic unit')['Name']]
        # Species #
        self.species = [(k,k) for k in self.select_rows('Forest type')['Name']]
        # Disturbances #
        left  = self.aidb['tblDisturbanceTypeDefault'].set_index('DistTypeID')
        right = self.calib['tblDisturbanceType'].set_index('DefaultDistTypeID')
        self.dist = left.join(right, how='inner', lsuffix='_archive', rsuffix='_calib')
        self.dist = zip(self.dist['Description_calib'], self.dist['DistTypeName_archive'])
        # Combine the four dataframes #
        self.combined = [pandas.DataFrame(self.admin),
                         pandas.DataFrame(self.eco),
                         pandas.DataFrame(self.species),
                         pandas.DataFrame(self.dist)]
        self.combined = pandas.concat(self.combined, keys=self.keys).reset_index(0)
        # Write the CSV #
        self.combined.to_csv(str(self.paths.csv), header = ['A', 'B', 'C'], index=False)

    def print_messages(self, default, names, key):
        template = "%s - %s - '%s' missing from archive index database."
        for name in names:
            if name not in default:
                print template % (key, self.parent.parent.country_iso2, name)

    def list_missing(self):
        # Admin boundaries #
        default = set(self.aidb['tblAdminBoundaryDefault']['AdminBoundaryName'])
        names   = self.key_to_rows(self.keys[0]).values()
        self.print_messages(default, names, self.keys[0])
        # Eco boundaries #
        default = set(self.aidb['tblEcoBoundaryDefault']['EcoBoundaryName'])
        names   = self.key_to_rows(self.keys[1]).values()
        self.print_messages(default, names, self.keys[1])
        # Species #
        default = set(self.aidb['tblSpeciesTypeDefault']['SpeciesTypeName'])
        names   = self.key_to_rows(self.keys[2]).values()
        self.print_messages(default, names, self.keys[2])
        # Disturbances #
        default = set(self.aidb['tblDisturbanceTypeDefault']['DistTypeName'])
        names   = self.key_to_rows(self.keys[3]).values()
        self.print_messages(default, names, self.keys[3])

    @property_cached
    def df(self):
        """Load the CSV that was produced by self.regenerate_csv"""
        self.paths.csv.must_exist()
        return pandas.read_csv(str(self.paths.csv))

    def key_to_rows(self, mapping_name):
        query   = "A == '%s'" % mapping_name
        mapping = self.df.query(query).set_index('B')['C'].to_dict()
        return mapping

    def rows_to_json(self, mapping_name, user, default):
        """Create a JSON string by picking the appropriate rows in the CSV file."""
        # Get rows #
        mapping = self.key_to_rows(mapping_name)
        # Add rows #
        result = [{user:k, default:v} for k,v in mapping.items()]
        # Format JSON #
        string  = json.dumps(result, indent=2)
        string  = pad_extra_whitespace(string, 6).strip(' ')
        # Return #
        return string

    @property_cached
    def all_mappings(self):
        """Return a dictionary of JSON structures for consumption by the mustache
        templating engine."""
        return {
           'map_admin_bound': self.rows_to_json(self.keys[0],
                                                'user_admin_boundary',
                                                'default_admin_boundary'),
           'map_eco_bound':   self.rows_to_json(self.keys[1],
                                                'user_eco_boundary',
                                                'default_eco_boundary'),
           'map_species':     self.rows_to_json(self.keys[2],
                                                'user_species',
                                                'default_species'),
           'map_disturbance': self.rows_to_json(self.keys[3],
                                                'user_dist_type',
                                                'default_dist_type'),
        }

