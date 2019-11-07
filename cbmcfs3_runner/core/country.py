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
from autopaths.dir_path   import DirectoryPath
from autopaths.auto_paths import AutoPaths
from plumbing.cache       import property_cached

# Internal modules #
from cbmcfs3_runner        import module_dir
from cbmcfs3_runner.graphs import country_graphs, load_graphs_from_module
from cbmcfs3_runner.pump.orig_data                 import OrigData
from cbmcfs3_runner.pump.fusion_data               import FusionData
from cbmcfs3_runner.pump.aidb                      import AIDB
from cbmcfs3_runner.pump.classifiers               import Classifiers
from cbmcfs3_runner.reports.country                import CountryReport
from cbmcfs3_runner.stdrd_import_tool.associations import Associations
from cbmcfs3_runner.disturbances.demand            import Demand
from cbmcfs3_runner.disturbances.silviculture      import Silviculture
from cbmcfs3_runner.pump.faostat                   import faostat

# Constants #
country_code_path = module_dir + 'extra_data/country_codes.csv'
ref_years_path    = module_dir + 'extra_data/reference_years.csv'

# Load extra data #
all_codes   = pandas.read_csv(str(country_code_path))
ref_years   = pandas.read_csv(str(ref_years_path))

###############################################################################
class Country(object):
    """
    This object gives access to the data pertaining to one country
    amongst the 26 EU member states we are examining.

    The data storred in orig_data consists of original csv file. The
    data storred in export_data also constists of csv files, exported
    from a calibration database (an MS access database used by CBMCFS3)
    """

    all_paths = """
    /orig/
    /orig/silviculture.sas
    /orig/aidb_eu.mdb
    /orig/calibration.mdb
    /orig/associations.csv
    /orig/coefficients.csv
    /export/
    /graphs/
    /report/report.pdf
    """

    def __repr__(self):
        return '%s object code "%s"' % (self.__class__, self.iso2_code)

    def __init__(self, continent, data_dir=None):
        """Store the data directory paths where everything will start from."""
        # Parent #
        self.continent = continent
        # Main directory #
        self.data_dir = DirectoryPath(data_dir)
        # Automatically access paths based on a string of many subpaths #
        self.paths = AutoPaths(self.data_dir, self.all_paths)
        # Set country codes #
        self.set_codes()
        # Store the reference years #
        self.set_years()

    def __call__(self):
        self.graphs(rerun=True)
        self.report()
        #c.report.copy_to_outbox()

    def set_codes(self):
        """
        Update all the country codes for this country.
        Typically the result will look something like this:

         'iso2_code':      'BE',
         'country_num':    255,
         'country_name':   'Belgium',
         'country_m49':    56,
         'country_iso3':   'BEL',
         'nuts_zero_2006': 'BE',
         'nuts_zero_2016': 'BE',
        """
        # The reference ISO2 code #
        self.iso2_code = self.data_dir.name
        # Load name mappings #
        row = all_codes.loc[all_codes['iso2_code'] == self.iso2_code].iloc[0]
        # Store all the country references codes #
        self.country_num  = row['country_code']
        self.country_name = row['country']
        self.country_m49  = row['m49_code']
        self.country_iso3 = row['iso3_code']
        # More crazy codes #
        self.nuts_zero_2006 = row['nuts_zero_2006']
        self.nuts_zero_2016 = row['nuts_zero_2010']

    def set_years(self):
        """Update all the reference years for this country."""
        # This is the same for all countries #
        self.base_year = 2015
        # This is different for each country.
        # inventory_start_year is the oldest year in the inventory data
        # reported by the national forest inventory
        row = ref_years.loc[ref_years['country'] == self.iso2_code].iloc[0]
        self.inventory_start_year = row['ref_year']

    def timestep_to_year(self, timestep):
        """
        TimeStep 0 is the output of the makelist (so called "spin-up") procedure.
        It represents the initial state.

        Will convert a Series containing simulation time-steps such as:
           [1, 2, 3, 4, 5]
        to actual corresponding simulation years such as:
           [1990, 1991, 1992, 1993, 1994]

        #TODO check that there is not an off by one error here.
        """
        return timestep + self.inventory_start_year - 1

    def year_to_timestep(self, year):
        """
        The reverse operation of `timestep_to_year`.
        Will convert a Series containing years such as:
           [1990, 1991, 1992, 1993, 1994]
        to simulation time-steps such as:
           [1, 2, 3, 4, 5]

        Checking the consistency between the 2 functions:

            >>> runner = continent[('static_demand', 'ZZ', 0)]
            >>> year = runner.country.timestep_to_year([1,2])
            >>> runner.country.year_to_timestep(year)
            array([1, 2])
        """
        return year - self.inventory_start_year + 1

    @property_cached
    def associations(self):
        """
        Associations of admin/eco/species/disturbances names between
        the input and the reference.
        """
        return Associations(self)

    @property_cached
    def aidb(self):
        """Archive Index Database."""
        return AIDB(self)

    @property_cached
    def silviculture(self):
        """Load the allocation rules for harvests."""
        return Silviculture(self)

    @property_cached
    def orig_data(self):
        """Access the original CSV files as exported from the DB."""
        return OrigData(self)

    @property_cached
    def fusion_data(self):
        """Access the CSV files from FUSION."""
        return FusionData(self)

    @property_cached
    def classifiers(self):
        """Load the classifiers and their names."""
        return Classifiers(self)

    @property_cached
    def demand(self):
        """Parses the GFTM demands."""
        return Demand(self)

    @property_cached
    def coefficients(self):
        """
        Load the conversion coefficients from tons of carbon
        to cubic meters of wood.
        The 'density' columns is the volumetric mass density in tons/m3
        for a given species.

        Columns are: ['id', 'forest_type', 'density', 'harvest_gr']
        """
        return pandas.read_csv(str(self.paths.coefficients))

    @property_cached
    def faostat(self):
        """Load the faostat forestry dataset of this country."""
        df = faostat.forestry.query('country == "%s"' % self.iso2_code)
        return df.drop(columns='country')

    @property_cached
    def scenarios(self):
        """
        A dictionary linking scenario names to a list of runners
        that concern only this country.
        """
        from cbmcfs3_runner.core.continent import continent
        return {n: s.runners[self.iso2_code] for n,s in continent.scenarios.items()}

    @property_cached
    def graphs(self):
        return load_graphs_from_module(self, country_graphs)

    @property_cached
    def report(self):
        return CountryReport(self)