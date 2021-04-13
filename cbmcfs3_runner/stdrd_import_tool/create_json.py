#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Written by Lucas Sinclair and Paul Rougieux.

JRC biomass Project.
Unit D1 Bioeconomy.
"""

# Built-in modules #
import os

# Third party modules #
import simplejson as json

# First party modules #
from autopaths.auto_paths import AutoPaths

###############################################################################
class CreateJSON(object):
    """This class will generate the JSON file needed by SIT."""

    template = {
      "output_path": None,
      "import_config": {
        "ageclass_path":           None,
        "classifiers_path":        None,
        "disturbance_events_path": None,
        "disturbance_types_path":  None,
        "inventory_path":          None,
        "transition_rules_path":   None,
        "yield_path":              None},
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
        # Default attributes #
        self.parent = parent
        self.runner = parent.parent
        # Automatically access paths based on a string of many subpaths #
        self.paths = AutoPaths(self.runner.data_dir, self.parent.all_paths)

    def __call__(self):
        self.paths.json.write(json.dumps(self.content, indent=4, ignore_nan=True))

    @property
    def content(self):
        # Make a copy of the template #
        config = self.template.copy()
        # Two main paths #
        config['output_path']           = self.parent.paths.mdb
        csv_dir = self.parent.parent.data_dir + "input/csv/"      
        config['import_config']['ageclass_path'] = csv_dir + "ageclass.csv"
        config['import_config']['classifiers_path'] = csv_dir + "classifiers.csv"
        config['import_config']['disturbance_events_path'] = csv_dir + "disturbance_events.csv"
        config['import_config']['disturbance_types_path'] = csv_dir + "disturbance_types.csv"
        config['import_config']['inventory_path'] = csv_dir + "inventory.csv"
        config['import_config']['transition_rules_path'] = csv_dir + "transition_rules.csv"
        # different yiled tables name for initialization and running
        config['import_config']['yield_path'] = csv_dir + self.parent.yield_table_name
        # Retrieve the four classifiers mappings #
        mappings = self.runner.country.associations.all_mappings
        # Set the four classifiers mappings #
        maps = config['mapping_config']
        maps['spatial_units']['admin_mapping']                = mappings['map_admin_bound']
        maps['spatial_units']['eco_mapping']                  = mappings['map_eco_bound']
        maps['disturbance_types']['disturbance_type_mapping'] = mappings['map_disturbance']
        maps['species']['species_mapping']                    = mappings['map_species']
        # The extra non-forest classifiers #
        if mappings['map_nonforest']:
            maps['nonforest'] = {
                "nonforest_classifier": "Forest type",
                "nonforest_mapping": mappings['map_nonforest']}
        # Return result #
        return config
