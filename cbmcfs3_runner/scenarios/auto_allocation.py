#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This scenarios is based on static_demand, 
but the species, manaement type and management strategy are
not specified based on the silviculture table, 
they are simply let for CBM to decide.

Classifiers in the disturbance table of the static_demand sceanrio

| forest_type | species | admin | mngt type | mngt strat | eco | con_broad |
| For         | QR      | ?     | H         | E          | ?   | Broad     |
| For         | PA      | ?     | H         | E          | ?   | Con       |

Classifiers in the disturbance table of the auto_allocation scenario

| forest_type | species | admin | mngt type | mngt strat | eco | con_broad |
| For         | ?       | ?     | ?         | ?          | ?   | Broad     |
| For         | ?       | ?     | ?         | ?          | ?   | Con       |
"""

# Built-in modules #

# First party modules #
from plumbing.cache import property_cached

# Internal modules #
from cbmcfs3_runner.scenarios.base_scen import Scenario
from cbmcfs3_runner.core.runner import Runner

###############################################################################
class AutoAllocation(Scenario):
    short_name = 'auto_allocation'

    @property_cached
    def runners(self):
        """A dictionary of country codes as keys with a list of runners as values."""
        result = {c.iso2_code: [Runner(self, c, 0)] for c in self.continent}
        # Modify these runners #
        for country in self.continent:
            runner = result[country.iso2_code][-1]
            pre_pro = runner.pre_processor
            # Replace disturbances by their aggregated version #
            pre_pro.disturbance_events = pre_pro.events_auto_allocation
        return result
  
    @property_cached    
    def df_auto_allocation(self):
        # TODO move this to a relevant place
        """Aggregate disturbances on the species, management type and
        management strategy classifiers for the auto allocation scenario"""
        self.parent.df
        