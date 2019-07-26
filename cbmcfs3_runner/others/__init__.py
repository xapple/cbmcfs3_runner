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
