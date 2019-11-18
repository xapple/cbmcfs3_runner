#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Written by Lucas Sinclair and Paul Rougieux.

JRC biomass Project.
Unit D1 Bioeconomy.

In the past this file looked like this. But now, as soon as you add a new
scenario to this directory, it will get automatically loaded.

    >>> from cbmcfs3_runner.scenarios.historical         import Historical
    >>> from cbmcfs3_runner.scenarios.static_demand      import StaticDemand
    >>> from cbmcfs3_runner.scenarios.auto_allocation    import AutoAllocation
    >>> scen_classes = [Historical, StaticDemand, AutoAllocation]

scen_classes is automatically filled with black magic functions
from inspect and importlib.
"""

# Built-in modules #
import inspect, importlib, sys

# First party modules #
from autopaths import Path

# Constants #
this_file = Path((inspect.stack()[0])[1])
this_dir  = this_file.directory

###############################################################################
# Initialize #
scen_classes = []

# Main loop #
for scen_file in this_dir.flat_files:
    # Skip some files #
    if not scen_file.endswith('.py'):     continue
    if scen_file.prefix.startswith('__'): continue
    if scen_file.prefix == 'base_scen':   continue
    # Import it #
    rel_mod_name = '.' + scen_file.prefix
    scen_module  = importlib.import_module(rel_mod_name, package=__name__)
    # Get list of all classes #
    all_classes  = [c for name, c in inspect.getmembers(scen_module, inspect.isclass)]
    # Filter for only locally defined ones #
    is_local      = lambda c: c.__module__ == scen_module.__name__
    local_classes = [c for c in all_classes if is_local(c)]
    # Filter for scenario classes #
    is_scenario   = lambda c: hasattr(c, 'short_name')
    local_classes = [c for c in all_classes if is_scenario(c)]
    # Append it #
    scen_classes += scen_class
