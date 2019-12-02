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
    Pivot a pandas data frame from long to wide format on multiple index variables.
    Copied from https://github.com/pandas-dev/pandas/issues/23955

    Note: you can perform the opposite operation, i.e.
    unpivot a DataFrame from wide format to long format with df.melt().
    In contrast to `pivot`, `melt` does acccept a multiple index specified
    as the `id_vars` argument.

    TODO: add warning when there is no index set.
    Otherwise the error message is cryptic:
    KeyError: "None of [Index([None], dtype='object')] are in the [columns]"

    TODO: add example use for this function
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
