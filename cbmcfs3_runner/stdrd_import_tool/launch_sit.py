#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
Written by Lucas Sinclair and Paul Rougieux.

JRC biomass Project.
Unit D1 Bioeconomy.
"""

# Built-in modules #
import os, zipfile, io
from six.moves.urllib.request import urlopen

# Third party modules #
if os.name == "posix": import sh as pbs
if os.name == "nt":    import pbs

# First party modules #
from autopaths.auto_paths import AutoPaths
from autopaths.dir_path import DirectoryPath
from plumbing.cache import property_cached
from plumbing.databases.access_database import AccessDatabase

# Internal modules #
from cbmcfs3_runner.stdrd_import_tool.create_json import CreateJSON
from cbmcfs3_runner.stdrd_import_tool.create_xls  import CreateXLS

###############################################################################
class LaunchSIT(object):
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
    /output/sit/project.mdb
    /output/sit/SITLog.txt
    /logs/sit_import.log
    """

    @classmethod
    def install(cls):
        """A method to automatically install the tool."""
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

    def __call__(self):
        self.create_xls()
        self.create_json()
        self.run_sit()
        self.move_log()
        self.check_for_errors()

    @property_cached
    def create_xls(self):
        return CreateXLS(self)

    @property_cached
    def create_json(self):
        return CreateJSON(self)

    def run_sit(self):
        """Don't forget to put the exe in your PATH variable."""
        self.log.info("Launching StandardImportToolPlugin.exe.")
        pbs.Command("StandardImportToolPlugin.exe")('-c', self.create_json.paths.json)
        self.log.info("StandardImportToolPlugin has completed.")

    def move_log(self):
        """Because the location and name of the logfile cannot be customized."""
        self.log.info("Moving the log that SIT created")
        self.paths.SITLog.move_to(self.paths.log)

    def check_for_errors(self):
        """This method has not been checked yet."""
        if "error" in self.paths.log.contents.lower():
            raise Exception("SIT did not run properly.")
        assert self.paths.log.contents.endswith("Done\n")

    @property
    def log(self):
        return self.parent.log

    @property_cached
    def project_mdb(self):
        self.paths.mdb.must_exist()
        return AccessDatabase(self.paths.mdb)
