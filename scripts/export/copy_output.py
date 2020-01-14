#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
A script to copy ALL the cbmcfs3_data (input and output and all scenarios)
from the AWS Windows machine to JRCbox.

Typically you would run this file from a command line like this:

     ipython3.exe /deploy/cbmcfs3_runner/scripts/others/copy_output.py
"""

# Built-in modules #

# Third party modules #
import pbs3

# Excludes #
exclude = ['--exclude', '.git']


###############################################################################
# Copy input data
# Specify source and destination #
source = "/repos/cbmcfs3_data/countries"
destin = "jrcbox:" + "/Forbiomod/SourceData/EFDM/cbmcfs3_data/countries"

# Copy #
rlcone = pbs3.Command('rclone.exe')
rlcone('copyto', *exclude, source, destin)

###############################################################################
# Copy the historical scenario
# Specify source and destination #
source = "/repos/cbmcfs3_data/scenarios/historical"
destin = "jrcbox:" + "/Forbiomod/SourceData/EFDM/cbmcfs3_data/scenarios/historical"

# Copy #
rlcone = pbs3.Command('rclone.exe')
rlcone('copyto', *exclude, source, destin)
