def count_unique_index(df, by):
    """Count the unique combinations of values 
       taken by the variable (columns) in the data frame df.
    """
    return df.groupby(by).size().reset_index().rename(columns={0:'count'})
