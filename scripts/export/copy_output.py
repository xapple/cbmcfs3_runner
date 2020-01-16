#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
A script to copy ALL the cbmcfs3_data (input and output and all scenarios)
from the AWS Windows machine to JRCbox.

Typically you would run this file from a command line like this:

     ipython3.exe /deploy/cbmcfs3_runner/scripts/export/copy_output.py

or from repos:

     ipython3.exe /repos/cbmcfs3_runner/scripts/export/copy_output.py
"""

# Built-in modules #

# Third party modules #
import pbs3

# Excludes #
exclude = ['--exclude', '.git']


def rclone_to_jrc_box(sub_folder):
    """Copy a given sub folder from the cbmcfs3_data folder to jrc box

    For example to copy the input data to jrc box use:

        rclone_jrc_box('countries')

    To copy the historical scenario to jrc box use:

        rclone_jrc_box('historical')

    """
    # Specify source and destination #
    source = "/repos/cbmcfs3_data/" + sub_folder
    destin = "jrcbox:" + "/Forbiomod/SourceData/EFDM/cbmcfs3_data/" + sub_folder

    # Copy #
    rlcone = pbs3.Command('rclone.exe')
    rlcone('copyto', *exclude, source, destin)

# Copy the cbmcfs3_runner input data to jrc box
#rclone_to_jrc_box('countries')

# Copy the historical scenario to jrc box
rclone_to_jrc_box('scenarios/historical')
