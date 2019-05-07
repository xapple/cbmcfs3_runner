#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
A script to run the current feature that is being developed and test it.

Typically you would run this file from a command line like this:

     ipython3.exe -i -- /deploy/cbmcfs3_runner/scripts/running/current.py
"""

# Built-in modules #

# Third party modules #
from tqdm import tqdm

# First party modules #

# Internal modules #
from cbmcfs3_runner.core.continent import continent

###############################################################################
# Run each country and send errors to the log #
#scenario = continent.scenarios['calibration']
#runners  = [r[0] for k,r in scenario.runners.items()]

#for r in tqdm(runners[1:2], ncols=60):
#    r.graphs(rerun=True)
#    r.report()

###############################################################################
# Get one country #
c = continent.countries['AT']

# Get runners #
runners = [r for runners in c.scenarios.values() for r in runners]

# Regen graphs #
for r in runners: r.graphs(rerun=True)
c.graphs(rerun=True)

# Make report #
c.report()

#for c in tqdm(continent, ncols=60):
#    runners = [r.graphs(rerun=True) for runners in c.scenarios.values() for r in runners]
#    c.report()
