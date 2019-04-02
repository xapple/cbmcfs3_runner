# Built-in modules #
import os, zipfile, io
from six.moves.urllib.request import urlopen

# Third party modules #
import simplejson as json
if os.name == "posix": import sh as pbs
if os.name == "nt":    import pbs

# First party modules #
from autopaths.auto_paths import AutoPaths
from autopaths.dir_path import DirectoryPath
from plumbing.cache import property_cached
from plumbing.databases.access_database import AccessDatabase

###############################################################################
class StandardImportTool(object):
    """
    This class will run the tool found here:
    https://github.com/cat-cfs/StandardImportToolPlugin

    It expects release version 1.2.1

    It will call the binary distribution exe with a JSON file as only parameter.
    This JSON file is automatically generated.
    Finally the log file is stored, and is checked for errors.

    More information about "SeperateAdminEcoClassifiers" (sic):
    c.f. https://github.com/cat-cfs/StandardImportToolPlugin/wiki/Mapping-Configuration

          "admin_classifier": "Region",
          "eco_classifier":   "Climatic unit",

    Is determined by the table "UserDefdClasses" in the calibration.mdb
    """

    url = 'https://github.com/cat-cfs/StandardImportToolPlugin/releases/download/1.2.1/Release.zip'

    all_paths = """
    /input/sit_config/sit_config.json
    /input/xls/inv_and_dist.xls
    /output/cbm_formatted_db/project.mdb
    /output/cbm_formatted_db/SITLog.txt
    /logs/sit_import.log
    """

    @classmethod
    def install(cls):
        """A method to install the tool"""
        # Download it #
        path = '/Users/Administrator/test/'
        response = urlopen(cls.url)
        archive  = zipfile.ZipFile(io.BytesIO(response.read()))
        archive.extractall(path=path)
        # Move it #
        source = DirectoryPath('/Users/Administrator/test/Release/')
        destin = DirectoryPath('/Program Files/StandardImportToolPlugin/')
        destin.remove()
        source.move_to(destin)

    def __init__(self, parent):
        # Keep access to the parent object #
        self.parent = parent
        # Automatic paths object #
        self.paths = AutoPaths(self.parent.data_dir, self.all_paths)
        # Has this step completed successfully ? #
        self.passed = False

    @property
    def log(self): return self.parent.log

    def __call__(self):
        self.json_sit_config.create()
        self.run_sit()
        self.move_log()
        self.check_for_errors()
        self.passed = True

    @property_cached
    def json_sit_config(self):
        return JsonSitConfig(self)

    def run_sit(self):
        """Don't forget to put the exe in your PATH variable."""
        self.log.info("Launching StandardImportToolPlugin.exe.")
        pbs.Command("StandardImportToolPlugin.exe")('-c', self.paths.json)
        self.log.info("StandardImportToolPlugin has completed.")

    def move_log(self):
        """Because the location and name of the logfile cannot be customized."""
        self.log.info("Moving the log that SIT created")
        self.paths.SITLog.move_to(self.paths.log)

    def check_for_errors(self):
        """This method has not been checked yet."""
        if "error" in self.paths.log.contents.lower(): raise Exception("SIT did not run properly.")
        assert self.paths.log.contents.endswith("Done\n")

    @property_cached
    def project_mdb(self):
        self.paths.mdb.must_exist()
        return AccessDatabase(self.paths.mdb)

###############################################################################
class JsonSitConfig(object):
    """This class will generate the JSON file needed by SIT."""

    template = {
      "output_path": None,
      "import_config": {
        "path":                          None,
        "ageclass_table_name":           "AgeClasses$",
        "classifiers_table_name":        "Classifiers$",
        "disturbance_events_table_name": "DistEvents$",
        "disturbance_types_table_name":  "DistType$",
        "inventory_table_name":          "Inventory$",
        "transition_rules_table_name":   "Transitions$",
        "yield_table_name":              "Growth$"
      },
      "mapping_config": {
        "spatial_units": {
          "mapping_mode":     "SeperateAdminEcoClassifiers",
              # Don't fix the 'Separate' spelling mistake
          "admin_classifier": "Region",
          "eco_classifier":   "Climatic unit",
          "admin_mapping":    None,
          "eco_mapping":      None,
        }
        ,
        "disturbance_types": {
          "disturbance_type_mapping": None,
        },
        "species": {
          "species_classifier": "Forest type",
          "species_mapping":    None,
        },
        "nonforest": None
      }
    }

    def __init__(self, parent):
        # Keep access to the parent object #
        self.parent = parent

    def create(self):
        # Make a copy of the template #
        config = self.template.copy()
        # Two main paths #
        config['output_path']           = self.parent.paths.mdb
        config['import_config']['path'] = self.parent.paths.inv_xls
        # Retrieve the four classifiers mappings #
        mappings = self.parent.parent.orig_to_csv.associations_parser.all_mappings
        # Set the four classifiers mappings #
        maps = config['mapping_config']
        maps['spatial_units']['admin_mapping']                = mappings['map_admin_bound']
        maps['spatial_units']['eco_mapping']                  = mappings['map_eco_bound']
        maps['disturbance_types']['disturbance_type_mapping'] = mappings['map_disturbance']
        maps['species']['species_mapping']                    = mappings['map_species']
        # The extra non-forest classifiers #
        if mappings['map_nonforest']:
            maps['nonforest'] = {
                "nonforest_classifier": "Status",
                "nonforest_mapping": mappings['map_nonforest']}
        # Create the file #
        self.parent.paths.json.write(json.dumps(config, indent=4, ignore_nan=True))


