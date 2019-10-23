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
## Run each country and send errors to the log #
#scenario = continent.scenarios['static_demand']
#runners  = [r[-1] for k,r in scenario.runners.items()]

## Filter #
#runners  = [r for r in runners if r.country.iso2_code in ('GB', 'GR', 'HR', 'LT', 'LV')]

## Do it #
#for r in tqdm(runners): r()

###############################################################################
## Get one country #
#c = continent.countries['GR']
#
## Get runners #
#runners = [r for runners in c.scenarios.values() for r in runners]
#
## Regen graphs #
#for r in runners: r.graphs(rerun=True)
#c.graphs(rerun=True)
#
## Make report #
#c.report()

################################################################################
#for c in tqdm(continent.countries.values()):
#    #if c.iso2_code not in ('LU',): continue
#    runners = [r for runners in c.scenarios.values() for r in runners]
#    for r in runners:
#        r.graphs.inventory_at_start(rerun=True)
#        r.graphs.inventory_at_end(rerun=True)
#    c.graphs.inventory_discrepancy(rerun=True)
#    c.report()
#    c.report.copy_to_outbox()

################################################################################
#for c in tqdm(continent.countries.values()):
#    if c.iso2_code not in ('AT',): continue
#    runners = []
#    runners += c.scenarios['static_demand']
#    runners += c.scenarios['calibration']
#    for r in runners:
#        r.graphs.harvest_exp_prov_vol(rerun=True)
#        r.graphs.harvest_exp_prov_area(rerun=True)
#    c.report()
#    c.report.copy_to_outbox()

################################################################################
#for c in tqdm(continent.countries.values()):
#    if c.iso2_code not in ('LU',): continue
#    c.graphs.merch_stock_at_start(rerun=True)
#    c.graphs.merch_stock_at_end(rerun=True)
#    c.report()
#    c.report.copy_to_outbox()

################################################################################
#for c in tqdm(continent.countries.values())[:]:
#    if c.iso2_code not in ('AT',): continue
#    scenarios = ['static_demand']
#    runners = [c.scenarios[s][-1] for s in scenarios]
#    for r in tqdm(runners): r.run(verbose=True)

################################################################################
#for c in tqdm(continent.countries.values()):
#    if c.iso2_code not in ('FR',): continue
#    statc = c.scenarios['static_demand'][-1]
#    calib = c.scenarios['calibration'][-1]
#    statc.graphs.harvest_exp_prov_vol(rerun=True)
#    calib.graphs.harvest_exp_prov_vol(rerun=True)
#    statc.graphs.harvest_exp_prov_area(rerun=True)
#    c.report()
#    c.report.copy_to_outbox()

################################################################################
#scenario = continent.scenarios['static_demand']
#runners  = [rs[-1] for k,rs in scenario.runners.items() if k == 'HU']
#runner   = runners[0]
#print(runner.run(verbose=True))

################################################################################
#for c in tqdm(continent.countries.values()):
#    runner = continent.get_runner('static_demand', c.iso2_code, -1)
#    runner.graphs.harvest_exp_prov_area(rerun=True)
#    runner.graphs.harvest_exp_prov_vol(rerun=True)

################################################################################
country = 'BE'
r = continent[('static_demand', country, -1)]
dist_mat = r.country.aidb.dist_matrix_long

