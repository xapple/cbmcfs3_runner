#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Written by Lucas Sinclair and Paul Rougieux.

JRC biomass Project.
Unit D1 Bioeconomy.
"""

# Built-in modules #

# Third party modules #

def format_vertical_headers(df):
    """Display a dataframe with vertical column headers

       Usefull when column names are long,
       for example the columns of disturance matrices contain
       very long carbon pool names.
        Example use:
        # Inspired by https://stackoverflow.com/a/53318677/2641825
        import pandas
        data = [{'Way too long of a column to be reasonable':4,'Four?':40},
                {'Way too long of a column to be reasonable':5,'Four?':50}]
        format_vertical_headers(pandas.DataFrame(data))
    """
    styles = [dict(selector="th", props=[('width', '40px')]),
              dict(selector="th.col_heading",
                   props=[("writing-mode", "vertical-rl"),
                          ('transform', 'rotateZ(180deg)'),
                          ('height', '190px'),
                          ('vertical-align', 'top')])]
    return (df.fillna('').style.set_table_styles(styles))
