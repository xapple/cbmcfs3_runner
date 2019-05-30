#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
A list of all scenarios classes.
"""

# Built-in modules #

# First party modules #

# Internal modules #
from cbmcfs3_runner.scenarios.static_demand import StaticDemand
from cbmcfs3_runner.scenarios.calibration   import Calibration
from cbmcfs3_runner.scenarios.fake_yields   import FakeYields

###############################################################################
scen_classes = [StaticDemand, Calibration, FakeYields, GrowthOnly]