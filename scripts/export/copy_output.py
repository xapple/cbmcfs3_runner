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

# Source #
source = "/repos/cbmcfs3_data/"

# Destination #
destin = "jrcbox:" + "/Forbiomod/SourceData/EFDM/cbmcfs3_data/"

# Excludes #
exclude = ['--exclude', '.git']

# Copy #
rlcone = pbs3.Command('rclone.exe')
rlcone('copyto', source, destin, *exclude)
