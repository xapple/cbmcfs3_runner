#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
Test post processor - UNIT TEST

This script is just a stub, and need to be completed.
"""

# Third party modules #
import pandas

# Internal modules #
from cbmcfs3_runner.steps.post_process import PostProcessor

# Constants #

###############################################################################
def test_classifiers_join():
    """This example is under development, not completed"""
    mock_parent = type('MockParent', (object,), {'parent_dir': '~/test/'})
    post_proc = PostProcessor(mock_parent)
    post_proc.database = {'asdfasdf': pandas.Dataframe('1,2,3'),
                          'ffasdfsa': pandas.Dataframe('1,2,3')}
    assert post_proc.classifiers == pandas.Dataframe('4,4,4')