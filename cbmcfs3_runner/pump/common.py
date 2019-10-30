#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Written by Lucas Sinclair and Paul Rougieux.

JRC biomass Project.
Unit D1 Bioeconomy.
"""

# Third party modules #
import pandas

###############################################################################
def multi_index_pivot(df, columns=None, values=None):
    """
    Pivot a pandas data frame on multiple index variables.
    Copied from https://github.com/pandas-dev/pandas/issues/23955

    TODO: add warning when there is no index set.
     Otherwise the error message is cryptic:
     KeyError: "None of [Index([None], dtype='object')] are in the [columns]"
    """
    names        = list(df.index.names)
    df           = df.reset_index()
    list_index   = df[names].values
    tuples_index = [tuple(i) for i in list_index] # hashable
    df           = df.assign(tuples_index=tuples_index)
    df           = df.pivot(index="tuples_index", columns=columns, values=values)
    tuples_index = df.index  # reduced
    index        = pandas.MultiIndex.from_tuples(tuples_index, names=names)
    df.index     = index
    # Remove confusing index column name #
    df.columns.name = None
    df = df.reset_index()
    # Return #
    return df
