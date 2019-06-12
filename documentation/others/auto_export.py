#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script to automatically xxxxx

Install this module:

    python3 -m pip install --user omnigraffle_export
"""

# Built-in modules #
import os

# First party modules #
from autopaths import Path

# Third party modules #
import omnigraffle

###############################################################################
omnigraffle   = omnigraffle.OmniGraffle()
graffle       = omnigraffle.active_document()
path          = Path(graffle.path)
canvas_name   = graffle.active_canvas_name()
export_format = 'pdf'
target_path   = path.directory.direcoty + 'exported_to_%s/' + ''

graffle.export(canvas_name, target_path, format=export_format)

###############################################################################
if __name__ == "__main__":
    pass