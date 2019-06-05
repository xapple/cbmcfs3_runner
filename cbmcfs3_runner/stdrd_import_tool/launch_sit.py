#!/usr/bin/env python3
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
import pbs3

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
    by calling "StandardImportToolPlugin.exe" so make sure its in your PATH.

    It expects release version 1.3.0.1

    It will call the binary distribution exe with a JSON file as only parameter.
    This JSON file is automatically generated.
    Finally the log file is stored, and is checked for errors.

    More information about "SeperateAdminEcoClassifiers" (sic):
    c.f. https://github.com/cat-cfs/StandardImportToolPlugin/wiki/Mapping-Configuration

          "admin_classifier": "Region",
          "eco_classifier":   "Climatic unit",

    Is determined by the table "UserDefdClasses" in the calibration.mdb
    """

    url = 'https://github.com/cat-cfs/StandardImportToolPlugin/releases/download/1.3.0.1/Release.zip'

    @classmethod
    def install(cls):
        """A method to automatically install the tool. Use it like this:
        >>> from cbmcfs3_runner.stdrd_import_tool.launch_sit import LaunchSIT
        >>> LaunchSIT.install()
        """
        # Download it #
        print('Downloading...')
        path     = '/Users/Administrator/test/'
        response = urlopen(cls.url)
        # Decompress it #
        print('Decompressing...')
        archive  = zipfile.ZipFile(io.BytesIO(response.read()))
        archive.extractall(path=path)
        # Move it #
        print('Moving...')
        source = DirectoryPath('/Users/Administrator/test/Release/')
        destin = DirectoryPath('/Program Files/StandardImportToolPlugin/')
        destin.remove()
        source.move_to(destin)
        # Check it #
        print('Checking installation...')
        print(pbs3.Command("StandardImportToolPlugin.exe")('--version'))

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
        # Parameters #
        if self.append: cmd = ('-a', '-c', self.create_json.paths.json)
        else:           cmd = (      '-c', self.create_json.paths.json)
        # Do it #
        self.log.info("Launching StandardImportToolPlugin.exe in %s." % self.short_name)
        pbs3.Command("StandardImportToolPlugin.exe")(*cmd)
        self.log.info("StandardImportToolPlugin has completed.")

    def move_log(self):
        """Because the location and name of the logfile cannot be customized."""
        self.log.info("Moving the log that SIT created")
        self.paths.SITLog.move_to(self.paths.log)

    def check_for_errors(self):
        """This method has not been checked yet."""
        # Let's check for the word error, you never know #
        if "error" in self.paths.log.contents.lower():
            raise Exception("SIT did not run properly.")
        # For some reason when appending we don't get the "Done" at the end #
        if not self.append:
            assert self.paths.log.contents.endswith("Done\n")

    @property
    def log(self):
        return self.parent.log

    @property_cached
    def project_mdb(self):
        self.paths.mdb.must_exist()
        return AccessDatabase(self.paths.mdb)

    @property
    def tail(self):
        """Shortcut: view the end of the log file."""
        return self.paths.log.tail()

###############################################################################
class DefaultSIT(LaunchSIT):
    """
    To be run first to create the project.
    """
    append = False
    short_name = "default_mode"

    all_paths = """
    /input/sit_config/default_config.json
    /input/xls/default_tables.xlsx                            
    /input/xls/default_tables.xls                               
    /output/sit/project.mdb
    /output/sit/SITLog.txt
    /logs/sit_default.log
    """

    yield_table_name = "yields.csv"

###############################################################################
class AppendSIT(LaunchSIT):
    """
    To be run in second to append the yield curve as new CBM assumptions in
    the project.
    """
    append = True
    short_name = "append_mode"

    all_paths = """
    /input/sit_config/append_config.json
    /input/xls/append_tables.xlsx                            
    /input/xls/append_tables.xls                               
    /output/sit/project.mdb
    /output/sit/SITLog_append.txt
    /logs/sit_append.log
    """

    yield_table_name = "historical_yields.csv"