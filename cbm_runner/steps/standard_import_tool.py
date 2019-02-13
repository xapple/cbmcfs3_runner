# Built-in modules #

# Third party modules #
import pbs, pystache

# First party modules #
from autopaths.auto_paths import AutoPaths

# Internal modules #
from cbm_runner import repos_dir

###############################################################################
class StandardImportTool(object):
    """
    This class will run the tool found here:
    https://github.com/cat-cfs/StandardImportToolPlugin
    It will call the binary distribution exe with a JSON file as only parameter.
    This JSON file is automatically generated based on a template.
    Finally the log file is stored, and is checked for errors.
    """

    all_paths = """
    /input/inv_and_dist.xls
    /output/sit_config/sit_config.json
    /output/cbm_formatted_db/project.mdb
    /output/cbm_formatted_db/SITLog.txt
    /logs/sit_import.log
    """

    def __init__(self, parent):
        # Keep access to the parent object #
        self.parent = parent
        # Automatic paths object #
        self.paths = AutoPaths(self.parent.data_dir, self.all_paths)

    def __call__(self):
        self.create_json_config()
        self.run_sit()
        self.move_log()
        self.check_for_errors()

    def create_json_config(self):
        """The template is at the repository root in /templates/"""
        self.context  = {"mdb_output_path": self.paths.mdb.escaped,
                         "xls_input_path":  self.paths.xls.escaped}
        self.template = repos_dir + 'templates/sit_config.mustache'
        self.renderer = pystache.Renderer()
        self.json     = self.renderer.render_path(self.template, self.context)
        self.paths.json.write(self.json)

    def run_sit(self):
        """Don't forget to put the tool in your PATH variable."""
        pbs.Command("StandardImportToolPlugin.exe")('-c', self.paths.json)

    def move_log(self):
        """Because the location and name of the logfile cannot be customized."""
        self.paths.SITLog.move_to(self.paths.log)

    def check_for_errors(self):
        """This has not been checked yet."""
        if "error" in self.paths.log.contents.lower(): raise Exception("SIT did not run properly.")
        assert self.paths.log.contents.endswith("Done\n")