#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
A script to copy the CBM output databases from the AWS Windows machine to JRCbox.

Typically you would run this file from a command line like this:

     ipython3.exe /deploy/cbmcfs3_notes/src/copy/copy_output.py
"""

# Built-in modules #

# Third party modules #
import pbs3
from tqdm import tqdm

# Internal modules #
from cbmcfs3_runner.core.continent import continent

# Constants #
scenario = continent.scenarios['static_demand']
runners  = [r[-1] for k,r in scenario.runners.items()]

###############################################################################
print('Copying all reports')

# Source #
source = "/repos/cbmcfs3_data/reports/countries/"

# Destination #
destin = "jrcbox:" + "Forbiomod/SourceData/EFDM/reports/"

# Copy #
rlcone = pbs3.Command('rclone.exe')
rlcone('copyto', source, destin)

###############################################################################
print('Copying all output mdbs')

for r in tqdm(runners):
    # Source #
    output_mdb = r.post_processor.paths.project_mdb
    # Destination #
    destin = "jrcbox:" + "Forbiomod/SourceData/EFDM/static_demand/"
    destin += r.country.iso2_code + '/output.mdb'
    # Copy #
    rlcone = pbs3.Command('rclone.exe')
    rlcone('copyto', output_mdb, destin)
    # Optional debugging #
    if False: print('rclone', 'copyto', output_mdb, destin)
