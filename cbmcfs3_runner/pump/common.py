#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Written by Lucas Sinclair and Paul Rougieux.

JRC biomass Project.
Unit D1 Bioeconomy.
"""

###############################################################################
def reshape_yields_long(yields_wide):
    """
    Columns are:

    ['status', 'forest_type', 'region', 'management_type',
     'management_strategy', 'climatic_unit', 'conifers_broadleaves', 'sp',
     'age_class', 'volume']
     """
    # Index #
    index = ['status', 'forest_type', 'region', 'management_type',
             'management_strategy', 'climatic_unit', 'conifers_broadleaves',
             'sp']
    # Add classifier 8 for the specific case of Bulgaria
    if 'yield_tables' in yields_wide.columns:
        index += ['yield_tables']
    # Melt #
    df = yields_wide.melt(id_vars    = index,
                          var_name   = "age_class",
                          value_name = "volume")
    # Remove suffixes and keep just the number #
    df['age_class'] = df['age_class'].str.lstrip("vol").astype('int')
    # Return #
    return df

###############################################################################
def left_join(*args, **kwargs):
    return flexible_join(*args, **kwargs, how='left')

def right_join(*args, **kwargs):
    return flexible_join(*args, **kwargs, how='right')

def inner_join(*args, **kwargs):
    return flexible_join(*args, **kwargs, how='inner')

def outer_join(*args, **kwargs):
    return flexible_join(*args, **kwargs, how='outer')

###############################################################################
def flexible_join(first, other, on, how=None):
    """Implement a common join pattern with pandas set_index()
    on both data frames followed by a reset_index()."""
    # Check if `on` is a set #
    if isinstance(on, set): on = list(on)
    # Set indexes #
    first  = first.set_index(on)
    other  = other.set_index(on)
    # TODO check the data type (dtypes) of index variables
    #  are identical on both sides of the join
    result = first.join(other, how=how)
    result = result.reset_index()
    # Return #
    return result
