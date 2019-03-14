# Built-in modules #
import os, zipfile, io
from six.moves.urllib.request import urlopen

# Third party modules #
import pystache
if os.name == "posix": import sh as pbs
if os.name == "nt":    import pbs

# First party modules #
from autopaths.auto_paths import AutoPaths
from plumbing.cache import property_cached
from plumbing.databases.access_database import AccessDatabase

# Internal modules #
from cbm_runner import repos_dir

###############################################################################
class StandardImportTool(object):
    """
    This class will run the tool found here:
    https://github.com/cat-cfs/StandardImportToolPlugin

    It expects release version 1.2.1

    It will call the binary distribution exe with a JSON file as only parameter.
    This JSON file is automatically generated based on a template.
    Finally the log file is stored, and is checked for errors.

    More information about "SeperateAdminEcoClassifiers" (sic):
    c.f. https://github.com/cat-cfs/StandardImportToolPlugin/wiki/Mapping-Configuration

          "admin_classifier": "classifier3",
          "eco_classifier":   "classifier6",

    Is determined by the table "UserDefdClasses" in the calibration.mdb
    """

    url = 'https://github.com/cat-cfs/StandardImportToolPlugin/releases/download/1.2.1/Release.zip'

    all_paths = """
    /input/sit_config/sit_config.json
    /output/cbm_formatted_db/project.mdb
    /output/cbm_formatted_db/SITLog.txt
    /logs/sit_import.log
    """

    @classmethod
    def install(cls):
        """A method to install the tool"""
        path = '/Users/Administrator/test/'
        response = urlopen(self.url)
        archive  = zipfile.ZipFile(io.BytesIO(response.read()))
        archive.extractall(path=path)

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
        self.create_json_config()
        self.run_sit()
        self.move_log()
        self.check_for_errors()
        self.passed = True

    def create_json_config(self):
        """The template is at the repository root in /templates/"""
        self.log.info("Creating the SIT JSON config file.")
        # Get all the context #
        extra_mappings = self.parent.orig_to_csv.associations_parser.all_mappings
        self.context.update(extra_mappings)
        # Render it #
        self.renderer = pystache.Renderer()
        self.json     = self.renderer.render_path(self.template, self.context)
        self.paths.json.write(self.json)

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
class ImportWithXLS(StandardImportTool):
    all_paths = StandardImportTool.all_paths + """
    /input/xls/inv_and_dist.xls
    """

    template = repos_dir + 'templates/sit_xls_config.mustache'

    @property_cached
    def context(self):
        return {"mdb_output_path": self.paths.mdb.escaped,
                "xls_input_path":  self.paths.inv_xls.escaped}

###############################################################################
class ImportWithTXT(StandardImportTool):
    all_paths = StandardImportTool.all_paths + """
    /input/txt/ageclass.txt
    /input/txt/classifiers.txt
    /input/txt/disturbance_events.txt
    /input/txt/disturbance_types.txt
    /input/txt/inventory.txt
    /input/txt/transition_rules.txt
    /input/txt/yields.txt
    """

    template = repos_dir + 'templates/sit_txt_config.mustache'

    @property_cached
    def context(self):
        return {'mdb_output_path':                  self.paths.mdb.escaped,
                'ageclass_input_path':              self.paths.ageclass.escaped,
                'classifiers_input_path':           self.paths.classifiers.escaped,
                'disturbance_events_input_path':    self.paths.disturbance_events.escaped,
                'disturbance_types_input_path':     self.paths.disturbance_types.escaped,
                'inventory_input_path':             self.paths.inventory.escaped,
                'transition_rules_input_path':      self.paths.transition_rules.escaped,
                'yield_input_path':                 self.paths.yields.escaped}

###############################################################################
class ImportWithCSV(StandardImportTool):
    """This is not currently possible."""
    pass