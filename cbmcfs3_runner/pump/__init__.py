#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Written by Lucas Sinclair and Paul Rougieux.

JRC biomass Project.
Unit D1 Bioeconomy.
"""

# Third party modules #
import pandas

def count_unique_index(df, by=None):
    """Count the unique combinations of values
    taken by the variable (columns) in the data frame *df*.

    >>> df = ''' i   | A  | B | C
                 For | 3  | 1 | x
                 For | 3  | 2 | x
                 For | 3  | 3 | y '''
    >>> from plumbing.dataframes import string_to_df
    >>> df = string_to_df(df)
    >>> count_unique_index(df, by=['A', 'B'])

       A  C  count
    0  3  x      2
    1  3  y      1
    """
    if by is None: by = df.columns
    return df.groupby(by).size().reset_index().rename(columns={0:'count'})

def multi_index_pivot(df, columns=None, values=None):
    """Pivot a pandas data frame on multiple index variables.
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
    return df
