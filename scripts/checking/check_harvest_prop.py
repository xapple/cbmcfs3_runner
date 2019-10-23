#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
A script to check stuff in our pipeline.

Typically you would run this file from a command line like this:

     ipython3.exe -i -- /deploy/cbmcfs3_runner/scripts/checking/check_harvest_prop.py

There are 3 sources for the same numbers and we want to check constancy.

See https://webgate.ec.europa.eu/CITnet/jira/browse/BIOECONOMY-206
"""

# Built-in modules #
import re

# Third party modules #
import numpy

# First party modules #

# Internal modules #
from cbmcfs3_runner.core.continent import continent

###############################################################################
for c in continent:
    # Message #
    print('\n--- Country %s ---' % c.iso2_code)

    # Condition #
    if c.iso2_code == 'HU':
        print('Broken data frame')
        continue

    # Runner #
    r = continent[('static_demand', c.iso2_code, -1)]

    # First source #
    first = r.country.silviculture.treatments.set_index('dist_type_name')['perc_merch_biom_rem']
    # Check it is coherent within itself #
    disturbance_ids = first.index.unique()
    for dist_id in disturbance_ids:
        if isinstance(first[dist_id], numpy.float64): continue
        if len(set(first[dist_id])) != 1:
            msg = "Mismatch on %s: not unique within treatments"
            print(msg % dist_id)
    # Remove redundancy #
    first = first.drop_duplicates()
    # Make into str #
    first.index = first.index.astype(str)
    # Make into percentage #
    first = first.apply(lambda x: int(x*100))

    # Second source #
    #second = r.country.silviculture.harvest_prop_fact

    # Third source #
    third    = r.input_data.disturbance_types
    selector = third['dist_description'].str.contains('%')
    third    = third.loc[selector].copy()
    # Extract #
    def extract(name):
        query = "[0-9]+[ ]?%"
        found = re.findall(query, name)
        if not found: return None
        return int(found[0].replace(' ','').replace('%',''))
    third['dist_description'] = third['dist_description'].apply(extract)
    # Make into series #
    third = third.set_index('dist_type_name')['dist_description']

    # Compare IDs #
    msg = "Disturbances in input but not treatments:"
    print(msg, set(third.index) - set(first.index))

    msg = "Disturbances in treatments but not in input:"
    print(msg, set(first.index) - set(third.index))

    # Compare all sources by checking consistency #
    for dist_id, prop in first.items():
        if dist_id not in third.index: continue
        if third[dist_id] != prop:
            msg = "Mismatch: dist_type_name %s, Treatments %s, Dist Input %s"
            print(msg % (dist_id, third[dist_id], prop))
