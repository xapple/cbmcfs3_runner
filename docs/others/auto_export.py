#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script to automatically export the graffle files to PDF files.

Install this module first:

    python3 -m pip install --user omnigraffle_export

And open the relevant document in Omnigraffle's GUI before running.
"""

# Built-in modules #

# First party modules #
from autopaths import Path

# Third party modules #
from omnigraffle_export import omnigraffle

###############################################################################
instance      = omnigraffle.OmniGraffle()
document      = instance.active_document()
path          = Path(document.path)
canvas_name   = document.active_canvas_name()
export_format = 'pdf'
target_path   = path.directory.directory + 'exported_to_%s/' % export_format
target_path  += path.short_prefix + '.' + export_format

###############################################################################
if __name__ == "__main__":
    print("Export '%s' to '%s'" % (path, target_path))
    document.export(canvas_name, target_path, format=export_format)