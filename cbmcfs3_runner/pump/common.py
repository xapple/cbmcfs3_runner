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
    Reshape a wide data frame into a long one.

    Columns are:

    ['status', 'forest_type', 'region', 'management_type',
     'management_strategy', 'climatic_unit', 'conifers_broadleaves', 'sp',
     'age_class', 'volume']
     """
    # Index #
    index = ['status', 'forest_type', 'region', 'management_type',
             'management_strategy', 'climatic_unit', 'conifers_broadleaves',
             'sp']
    # Add classifier 8 for the specific case of Bulgaria #
    if 'yield_tables' in yields_wide.columns: index += ['yield_tables']
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
    """This method is patched onto pandas.DataFrame for convenience."""
    return flexible_join(*args, **kwargs, how='left')

def right_join(*args, **kwargs):
    """This method is patched onto pandas.DataFrame for convenience."""
    return flexible_join(*args, **kwargs, how='right')

def inner_join(*args, **kwargs):
    """This method is patched onto pandas.DataFrame for convenience."""
    return flexible_join(*args, **kwargs, how='inner')

def outer_join(*args, **kwargs):
    """This method is patched onto pandas.DataFrame for convenience."""
    return flexible_join(*args, **kwargs, how='outer')

###############################################################################
def flexible_join(first, other, on, how=None):
    """Implement a common join pattern with pandas set_index()
    on both data frames followed by a reset_index() at the end."""
    # Check if `on` is a set #
    if isinstance(on, set): on = list(on)
    # Set indexes #
    first  = first.set_index(on)
    other  = other.set_index(on)
    # TODO check the data types (dtypes) of all the index columns
    #  are matching on both sides of the join.
    result = first.join(other, how=how)
    result = result.reset_index()
    # Return #
    return result

###############################################################################
def format_vertical_headers(df):
    """
    Display a pandas data frame with vertical column headers.
    This is useful when column names are especially long
    (for example the columns of disturbance matrices contain
    very long carbon pool names).

    Inspired by https://stackoverflow.com/a/53318677/2641825

    Example use:
        >>> import pandas
        >>> data = [{'Way too long of a column to be reasonable': 4, 'Four?': 40},
        >>>         {'Way too long of a column to be reasonable': 5, 'Four?': 50}]
        >>> format_vertical_headers(pandas.DataFrame(data))
    """
    # Define styles #
    styles = [{'selector': 'th',
               'props':    [('width', '40px')]},
              {'selector': 'th.col_heading',
               'props':   [('writing-mode',   'vertical-rl'),
                           ('transform',      'rotateZ(180deg)'),
                           ('height',         '190px'),
                           ('vertical-align', 'top')]}]
    # Set styles #
    df = df.fillna('').style.set_table_styles(styles)
    # Return #
    return
