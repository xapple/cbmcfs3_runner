#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Written by Lucas Sinclair and Paul Rougieux.

JRC biomass Project.
Unit D1 Bioeconomy.
"""

# Built-in modules #
import logging

# Third party modules #

# First party modules #
from autopaths            import Path
from autopaths.auto_paths import AutoPaths
from plumbing.cache       import property_cached
from plumbing.databases.access_database import AccessDatabase

# Internal modules #

# Constants #
toolbox_install_dir = Path("/Program Files (x86)/Operational-Scale CBM-CFS3/")
aidb_path           = toolbox_install_dir + "admin/dbs/ArchiveIndex_Beta_Install.mdb"
cbm_exes_path       = toolbox_install_dir + "admin/executables/"

###############################################################################
class LaunchCBM(object):
    """
    This class will run CBM-CFS3.exe from the command line without using the GUI.
    It will take a Microsoft Access database (as created by SIT) as input.
    Then it will produce a new Microsoft Access database as output.
    If the input database is in a different location than when it was created
    by SIT, the tool will not work in the same way. Side-effects are everywhere.

    It currently expects the release of CBM-CFS3 version 1.2.7004.294
    And the module cbm3_python at commit 217381adc1a169e4d143fa3e6ffb92a84bf3495f
    """

    all_paths = """
    /output/sit/project.mdb
    /output/
    /output/cbm_tmp_dir/
    /output/cbm/project.mdb
    /logs/cbm_run.log
    """

    def __init__(self, parent):
        # Default attributes #
        self.parent = parent
        # Directories #
        self.paths = AutoPaths(self.parent.data_dir, self.all_paths)

    @property
    def log(self): return self.parent.log

    def __call__(self):
        self.run_simulator()

    def run_simulator(self):
        """Launch CBM and all its executables."""
        # Messages #
        self.log.info("Launching the CBM-CFS3 model.")
        self.log.debug("Database path '%s'." % self.paths.sit_mdb)
        # Arguments #
        kwargs = {
            'aidb_path'                : str(aidb_path),
            'project_path'             : str(self.paths.sit_mdb),
            'toolbox_installation_dir' : str(toolbox_install_dir),
            'cbm_exe_path'             : str(cbm_exes_path),
            'results_database_path'    : str(self.paths.cbm_mdb),
            'tempfiles_output_dir'     : str(self.paths.output_dir + "cbm_tmp_dir"),
            'skip_makelist'            : False,
            'stdout_path'              : str(self.paths.log),
        }
        # Import #
        from cbm3_python.simulation import projectsimulator
        # Use their module #
        self.results_path = projectsimulator.run(**kwargs)
        # Remove the stream handler that they add to the root logger :/ #
        logging.root.handlers.pop(0)
        # Success message #
        self.log.info("The CBM-CFS3 model run is completed.")

    @property_cached
    def generated_database(self):
        """Will be in a directory created by CBM."""
        return AccessDatabase(self.paths.cbm_mdb)

    @property
    def tail(self):
        """Shortcut: view the end of the log file."""
        return self.paths.log.tail()
