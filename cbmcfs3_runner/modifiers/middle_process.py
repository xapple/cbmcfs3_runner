#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Written by Lucas Sinclair and Paul Rougieux.

JRC biomass Project.
Unit D1 Bioeconomy.
"""

# Built-in modules #

# Third party modules #
import pandas

# First party modules #
from plumbing.cache import property_cached
from autopaths.auto_paths import AutoPaths
from plumbing.databases.access_database import AccessDatabase

# Internal modules #

###############################################################################
class MiddleProcessor(object):
    """
    Will modify the access database after its creation by SIT but before its
    usage by CBM.

    The middle processor makes it possible to call SIT twice,
    first in default mode, then in append mode.
    Beware the order of these calls is reversed compared to the chronological period:
    1. SIT default mode adds the current yield table
       (used for the historical period and the simulation period),
    2. SIT append mode adds the historical yield table
       (used for the pool initialisation period)
    """

    all_paths = """
    /output/sit/project.mdb
    """

    random_seed = 1

    def __init__(self, parent):
        # Default attributes #
        self.parent = parent
        # Directories #
        self.paths = AutoPaths(self.parent.data_dir, self.all_paths)

    def __call__(self):
        self.set_random_seed()
        if self.parent.sit_calling == 'dual': self.finish_append()
        #self.extend_simulation(100)

    @property_cached
    def project_database(self):
        database = AccessDatabase(self.paths.project_mdb)
        database.convert_col_names_to_snake = True
        return database

    @property
    def current_timestep(self):
        """Get the current end timestep of the siumlation"""
        query = "SELECT RunLength FROM tblRunTableDetails"
        return self.project_database.cursor.execute(query).fetchone()[0]

    def extend_simulation(self, num_steps):
        """Will extend the simulation by num_steps time steps so that it runs extra
        years without any disturbances."""
        # Log message #
        self.parent.log.info("Adjusting the simulation length with extra %i steps" % num_steps)
        # Update the value in the database #
        updated_run_length = self.current_timestep + num_steps
        query = "UPDATE tblRunTableDetails SET tblRunTableDetails.RunLength = %i"
        query = query % updated_run_length
        # Execute the query #
        self.project_database.cursor.execute(query)
        self.project_database.cursor.commit()

    def finish_append(self):
        """
        According to Scott this is what we should do to finish the "yield appending" procedure
        so that it matches Roberto's procedure.
        See ticket on JIRA at https://webgate.ec.europa.eu/CITnet/jira/browse/BIOECONOMY-178
        """
        # Log message #
        self.parent.log.info("Executing final appending queries.")
        # Screen-shot 1 of page 4 of <roberto_proj_creation.pdf> #
        query = "DELETE FROM tblSimulation WHERE tblSimulation.SimulationID=2;"
        self.project_database.cursor.execute(query)
        # Screen-shot 2 of page 4 of <roberto_proj_creation.pdf> optional #
        #query = 'UPDATE tblSimulation SET Name="default" WHERE tblSimulation.SimulationID=1;'
        #self.project_database.cursor.execute(query)
        # Screen-shot 1 of page 5 of <roberto_proj_creation.pdf> #
        query = 'DELETE FROM tblRunTable WHERE tblRunTable.RunID=2;'
        self.project_database.cursor.execute(query)
        # Screen-shot 2 of page 5 of <roberto_proj_creation.pdf> #
        query = """UPDATE tblStandInitialization SET
                        RunGrowthScenarioID            = 2,
                        RunGrowthMultiplierScenarioID  = 2,
                        StandInitDistAssumptionID      = 2,
                        StandInitGCAssumptionID        = 2,
                        StandInitNonForestAssumptionID = 2
                    WHERE tblStandInitialization.StandInitID = 1;"""
        self.project_database.cursor.execute(query)
        # Save changes #
        self.project_database.cursor.commit()

    def set_random_seed(self):
        """CBM uses pseudo-randomness for instance when allocating disturbances
        that are supposed to be random. But we want every run to be comparable.
        This method will set the seed to a numerical value that's always the same.
        See https://webgate.ec.europa.eu/CITnet/jira/browse/BIOECONOMY-213
        They say it defaults to a time based seed, if we do not do this step."""
        # Set a new one #
        query = "INSERT INTO tblRandomSeed (CBMRunID, RandomSeed, OnOffSwitch) VALUES ({0},{1},{2})"
        query = query.format(1, self.random_seed, True)
        self.project_database.cursor.execute(query)
        # Check it worked #
        assert self.current_random_seed.RandomSeed == self.random_seed

    @property
    def current_random_seed(self):
        """Retrieve the random seed from the project's Access database."""
        # The query #
        query = """
        SELECT tblRandomSeed.CBMRunID, tblRandomSeed.RandomSeed, tblRandomSeed.OnOffSwitch
        FROM   tblRandomSeed
        WHERE  tblRandomSeed.CBMRunID In (
            SELECT DISTINCT Max(tblRandomSeed.CBMRunID) AS MaxOfRunID
            FROM tblRandomSeed;
        );
        """
        # Execute #
        self.project_database.cursor.execute(query)
        result = self.project_database.cursor.fetchone()
        # Check result is found #
        if result is None or result[0] is None: raise Exception("No random seed found.")
        # Return #
        return result
