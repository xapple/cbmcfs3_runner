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
    This CSV is then manually edited to fix inconsistencies.
    Later, it parses the CSV created to produce the JSON
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
        self.extra_keys = ['MapNonForestType']

    @property
    def log(self): return self.parent.parent.log

    @property
    def aidb(self):
        """Shortcut to the AIDB"""
        return self.parent.parent.aidb_switcher.database

    @property
    def calib(self):
        """Shortcut to the Calibration DB"""
        return self.parent.calibration_parser.database

    def select_rows(self, classifier_name):
        """
        Here is an example call:

        >>> self.select_rows('Climatic unit')
            ClassifierNumber ClassifierValueID   Name
        19                 6                25  CLU25
        20                 6                34  CLU34
        21                 6                35  CLU35
        22                 6                44  CLU44
        23                 6                45  CLU45
        """
        query  = "ClassifierValueID == '_CLASSIFIER' and Name == '%s'" % classifier_name
        number = self.calib['Classifiers'].query(query)['ClassifierNumber'].iloc[0]
        query  = "ClassifierValueID != '_CLASSIFIER' and ClassifierNumber == %i" % number
        rows   = self.calib['Classifiers'].query(query)
        return rows

    def regenerate_csv(self):
        """Run this once before manually fixing the CSVs.
        The keys are the names in the calibration.mdb
        The values are the names in the aidb.mdb"""
        # Remove this warning if you must #
        raise Exception("Are you sure you want to regenerate the associations CSV?" + \
                        "They have been edited manually.")
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
        # Filter empty disturbances #
        self.dist = [(calib, archive) for calib, archive in self.dist if calib]
        # Combine the four dataframes #
        self.combined = [pandas.DataFrame(self.admin),
                         pandas.DataFrame(self.eco),
                         pandas.DataFrame(self.species),
                         pandas.DataFrame(self.dist)]
        self.combined = pandas.concat(self.combined, keys=self.keys).reset_index(0)
        # Write the CSV #
        self.combined.to_csv(str(self.paths.csv), header = ['A', 'B', 'C'], index=False)

    @property_cached
    def df(self):
        """Load the CSV that was produced by self.regenerate_csv()"""
        self.paths.csv.must_exist()
        return pandas.read_csv(str(self.paths.csv))

    def list_missing(self):
        """
        A method to predict what errors the StandardImport tool will throw
        by checking the contents of the AIDB.
        """
        # Print function #
        def print_messages(default, names, key):
            template = "%s - %s - '%s' missing from archive index database."
            for name in names:
                if name not in default:
                    print(template % (key, self.parent.parent.country_iso2, name))
        # Admin boundaries #
        default = set(self.aidb['tblAdminBoundaryDefault']['AdminBoundaryName'])
        names   = self.key_to_rows(self.keys[0]).values()
        print_messages(default, names, self.keys[0])
        # Eco boundaries #
        default = set(self.aidb['tblEcoBoundaryDefault']['EcoBoundaryName'])
        names   = self.key_to_rows(self.keys[1]).values()
        print_messages(default, names, self.keys[1])
        # Species #
        default = set(self.aidb['tblSpeciesTypeDefault']['SpeciesTypeName'])
        names   = self.key_to_rows(self.keys[2]).values()
        print_messages(default, names, self.keys[2])
        # Disturbances #
        default = set(self.aidb['tblDisturbanceTypeDefault']['DistTypeName'])
        names   = self.key_to_rows(self.keys[3]).values()
        print_messages(default, names, self.keys[3])

    def key_to_rows(self, mapping_name):
        """
        Here is an example call:

        >>> self.key_to_rows('MapDisturbanceType')
        {'10% commercial thinning': '10% Commercial thinning',
         'Deforestation': 'Deforestation',
         'Fire': 'Wild Fire',
         'Generic 15%': 'generic 15% mortality',
         'Generic 20%': 'generic 20% mortality',
         'Generic 30%': 'generic 30% mortality',
         'Spruce Beetle 2% mortality (Ice sleet)': 'Spruce Beetle 2% mortality'}
        """
        query   = "A == '%s'" % mapping_name
        mapping = self.df.query(query).set_index('B')['C'].to_dict()
        return mapping

    def rows_to_list(self, mapping_name, user, default):
        """Create a list string by picking the appropriate rows in the CSV file."""
        return [{user:k, default:v} for k,v in self.key_to_rows(mapping_name).items()]

    @property_cached
    def all_mappings(self):
        """Return a dictionary for creation of the JSON file."""
        return {
           'map_admin_bound': self.rows_to_list(self.keys[0],
                                                'user_admin_boundary',
                                                'default_admin_boundary'),
           'map_eco_bound':   self.rows_to_list(self.keys[1],
                                                'user_eco_boundary',
                                                'default_eco_boundary'),
           'map_species':     self.rows_to_list(self.keys[2],
                                                'user_species',
                                                'default_species'),
           'map_disturbance': self.rows_to_list(self.keys[3],
                                                'user_dist_type',
                                                'default_dist_type'),
        }

