#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
A script to modify the disturbance_types.csv files automatically.

See https://webgate.ec.europa.eu/CITnet/jira/browse/BIOECONOMY-228

Typically you would run this file from a command line like this:

     ipython3.exe -i -- /deploy/cbmcfs3_runner/scripts/orig/add_100_to_dist_id.py
"""

# Third party modules #
from tqdm import tqdm
import pandas

# Internal modules #
from cbmcfs3_runner.core.continent import continent

# First party modules #
from autopaths.auto_paths import AutoPaths

###############################################################################
class Add100ToDistID(object):
    """
    This class takes the file "disturbance_types.csv" and
    modifies it, by duplicating some entries with a new ID.
    Why do we have to do this? Because of arcane CBM-CFS3
    requirements.
    """

    all_paths = """
    /export/disturbance_types.csv
    """

    def __init__(self, country):
        # Default attributes #
        self.country = country
        # Automatically access paths based on a string of many subpaths #
        self.paths = AutoPaths(self.country.data_dir, self.all_paths)

    def __call__(self):
        # Our fake country ZZ doesn't work #
        if self.country.iso2_code == 'ZZ': return
        # Convenience shortcut #
        col_name = 'disturbance_type_id'
        # Get disturbances to duplicate #
        silv        = self.country.silviculture.treatments
        dist_to_dup = silv.query("man_nat == 'Man'")['dist_type_id'].unique()
        # Parse #
        self.df = pandas.read_csv(str(self.paths.types))
        self.df[col_name] = self.df[col_name].astype(str)
        self.df = self.df.set_index(col_name)
        # Make a data frame #
        self.dists = [self.df.loc[dist][0] for dist in dist_to_dup]
        self.dup   = pandas.DataFrame(zip(dist_to_dup, self.dists), columns=[col_name, 'name'])
        # Add 100 #
        self.dup[col_name] = self.dup[col_name].apply(lambda x: '1' + x)
        # Write back to disk #
        self.df = self.df.reset_index()
        self.df = pandas.concat([self.df, self.dup])
        self.df.to_csv(str(self.paths.types), index=False)

###############################################################################
if __name__ == '__main__':
    modifiers = [Add100ToDistID(c) for c in continent]
    for modifier in tqdm(modifiers): modifier()
