# Built-in modules #
from collections import OrderedDict

# First party modules #

# Third party modules #
from tqdm import tqdm
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

###############################################################################
def concat_as_dict(scenario, step=-1, func=None, verbose=False):
    """A dictionary of data frames, with country iso2 code as keys."""
    # Default option, function that takes a runner, returns a data frame #
    if func is None: func = lambda r: r.input_data.disturbance_events
    # Retrieve data #
    result = [(iso2, func(runners[step]).copy()) for iso2,runners in tqdm(scenario.runners.items())]
    # Return result #
    return OrderedDict(result)

#-----------------------------------------------------------------------------#
def concat_as_df(scenario, *args, **kwargs):
    """A data frame with many countries together."""
    # Get data #
    dict_of_df = concat_as_dict(scenario, *args, **kwargs)
    # When classifiers are present
    # add column '_8' for all countries except BG
    if '_7' in dict_of_df['AT'].columns:
        for iso2, df in dict_of_df.items():
            if iso2 == "BG": continue
            loc = list(dict_of_df['BG'].columns).index('_8')
            df.insert(loc, '_8', '')
    # The option sort=True adds a column of NaN if the column is missing
    # for a particular country
    df = pandas.concat(dict_of_df, sort=True)
    df = df.reset_index(level=0)
    df = df.rename(columns={'level_0': 'country_iso2'})
    # Reset the index that now has lots of duplicates
    df = df.reset_index()
    # Remove the index column if it has the default name
    if 'index' in df.columns:
        df = df.drop(columns=['index'])
    # Return #
    return df

#-----------------------------------------------------------------------------#
def compare_col_names(scenario, *args, **kwargs):
    """
    Compare column names in a dictionary of data frames
    to a reference data frame present under the `key_ref`.
    """
    # Reference key #
    key_ref = kwargs.get('key_ref')
    if key_ref is None: key_ref = "AT"
    # Message #
    print("Specific to this country, present in reference country: ", key_ref)
    # Get data #
    dict_of_df = concat_as_dict(scenario, *args, **kwargs)
    # Iterate #
    ref_columns = set(dict_of_df[key_ref].columns)
    comparison  = {iso2: set(df.columns) ^ ref_columns for iso2, df in dict_of_df.items()}
    # Return #
    return comparison

###############################################################################
def csv_download_link(df, csv_file_name, delete_prompt=True):
    """Display a download link to load a data frame as csv from within a Jupyter notebook"""
    df.to_csv(csv_file_name, index=False)
    from IPython.display import FileLink
    display(FileLink(csv_file_name))
    if delete_prompt:
        a = input('Press enter to delete the file after you have downloaded it.')
        import os
        os.remove(csv_file_name)

