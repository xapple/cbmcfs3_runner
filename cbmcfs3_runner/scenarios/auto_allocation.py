#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This scenario is based on static_demand. Except that here the species,
management type and management strategy are not specified based on
the silviculture table, they are simply let for CBM to decide with
question marks.

Classifiers in the disturbance table of the original static_demand scenario:

    | forest_type | species | admin | mngt type | mngt strat | eco | con_broad |
    | For         | QR      | ?     | H         | E          | ?   | Broad     |
    | For         | PA      | ?     | H         | E          | ?   | Con       |

Classifiers in the disturbance table of the new auto_allocation scenario:

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