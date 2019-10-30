#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
A script to modify all the Microsoft Access Databases known as "AIDB" that were originally downloaded from JRCbox.

We need to modify them because they contain inconsistencies.

Typically you would run this file from a command line like this:

     ipython3.exe -i -- /deploy/cbmcfs3_runner/scripts/orig/fix_all_aidbs.py
"""

# Built-in modules #

# Third party modules #
from tqdm import tqdm

# First party modules #
from plumbing.cache import property_cached
from autopaths.auto_paths import AutoPaths
from plumbing.databases.access_database import AccessDatabase

# Internal modules #
from cbmcfs3_runner.core.continent import continent

# Constants #

###############################################################################
class FixerOfAIDB(object):
    """
    This class takes the file "aidb_eu.mdb" and modifies it.
    """

    all_paths = """
    /orig/aidb_eu.mdb
    """

    def __init__(self, country):
        # Default attributes #
        self.country = country
        # Automatically access paths based on a string of many subpaths #
        self.paths = AutoPaths(self.country.data_dir, self.all_paths)

    @property_cached
    def database(self):
        database = AccessDatabase(self.country.paths.aidb_eu_mdb)
        return database

    def __call__(self):
        self.remove_171()

    def remove_171(self):
        """
        In the EU AIDB, in the table "tblBioTotalStemwoodGenusDefault", many entries
        exist. About 6'000 of them. Amongst those, 37 have the "default_genus_id"
        set to 171. But, in the table "tblGenusTypeDefault", there is no genus 171 defined.

        At the same time, we see that in 'tblSpeciesTypeDefault' there is a species
        with id 171, with a genus 14, so probably it's a mix up?

        As a fix we delete all offending entries from tblBioTotalStemwoodGenusDefault.
        Note: these concern only Sweden.
        """
        # Optionally we could update them #
        query = """UPDATE tblBioTotalStemwoodGenusDefault
                   SET    default_genus_id = 14,
                   WHERE  tblBioTotalStemwoodGenusDefault.DefaultGenusID = 171;"""
        # But actually, let's just delete them #
        query = """DELETE FROM tblBioTotalStemwoodGenusDefault
                   WHERE tblBioTotalStemwoodGenusDefault.DefaultGenusID=171;"""
        # Execute #
        self.database.cursor.execute(query)
        # Save changes #
        self.database.cursor.commit()

###############################################################################
if __name__ == '__main__':
    fixers = [FixerOfAIDB(c) for c in continent]
    for fixer in tqdm(fixers): fixer()