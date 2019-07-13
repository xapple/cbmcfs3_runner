#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Written by Lucas Sinclair and Paul Rougieux.

JRC biomass Project.
Unit D1 Bioeconomy.
"""

# Built-in modules #
import re

# Third party modules #
import pandas

# First party modules #
from plumbing.cache import property_cached
from autopaths.auto_paths import AutoPaths

# Internal modules #

###############################################################################
class DistSurplus(object):
    """
    See notebook "disturbance_report.fil.ipynb" for more details about the methods below.
    """

    all_paths = """
    /output/cbm_tmp_dir/CBMRun/output/report.fil
    /output/cbm_tmp_dir/surplus.csv
    """

    def __init__(self, parent):
        # Default attributes #
        self.parent = parent
        # Directories #
        self.paths = AutoPaths(self.parent.parent.data_dir, self.all_paths)

    #-------------------------------------------------------------------------#
    def generate_df(self):
        """
        Parse the output file "report.fil" and produce a data frame
        saved to disk.

        One `pass_num` is for instance " for Pass 19"
        One `info_text` is for instance:

            Timestep:           1
            Year:               1
            Disturbance Type:   12
            Default Disturbance Type:   142
            Disturbance Group:  1
            Sort Type:          6
            Target Type:        1
            Target Area:        43145
            Eligible Area:      625316
            Efficiency:         1
            Surplus Area:       582171
            Area Prop'n:        0.0689971
            Records Eligible    287
            Records Changed:    287

        Note that the output is inconsistent, and the above missing
        colon on Records Eligible is produced by CBM.
        """
        # Contents #
        contents = self.paths.fil.contents
        # String to match #
        string = '^Disturbance Reconciliation(.+?):\n(.+?)\n\n'
        # Find all occurrences #
        matches = re.findall(string, contents, re.DOTALL|re.MULTILINE)
        # Split the pass numbers and the info chunks #
        all_pass_nums, all_infos = zip(*matches)
        # Make one line into a tuple #
        def line_to_pair(line):
            """'Timestep:  2' becomes ('Timestep', '2')"""
            return [elem.strip().strip(':') for elem in line.split('  ') if elem]
        # Make a series out of one info chunk #
        def text_to_series(text):
            cols, vals = zip(*[line_to_pair(line) for line in text.split('\n')])
            return pandas.Series(data=vals, index=cols)
        # Make a dataframe with all the series as rows #
        rows = (text_to_series(text) for text in all_infos)
        df = pandas.concat(rows, axis=1, sort=True).T
        # Save the dataframe #
        df.to_csv(str(self.paths.surplus_csv), index=False)

    #-------------------------------------------------------------------------#
    @property_cached
    def df(self):
        """
        Load the saved CSV.
        """
        if not self.paths.surplus_csv.exists: self.generate_df()
        return pandas.read_csv(str(self.paths.surplus_csv))