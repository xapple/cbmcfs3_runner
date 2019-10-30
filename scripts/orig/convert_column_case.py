#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
A script to convert the column names from CamelCase to snake_case.

Typically you would run this file from a command line like this:

     ipython3.exe -i -- /deploy/cbmcfs3_runner/scripts/orig/convert_column_case.py
"""

# Built-in modules #
import os

# Third party modules #
import pandas
from tqdm import tqdm

# First party modules #
import autopaths
from autopaths            import Path
from autopaths.auto_paths import AutoPaths
from plumbing.common      import camel_to_snake
from plumbing.cache       import property_cached

# Internal modules #
from cbmcfs3_runner.core.continent import continent

# Constants #
home = os.environ.get('HOME', '~') + '/'

###############################################################################
class CaseConverter(object):
    """
    This class takes many of the CSV files in "export/" and "orig/" and
    converts their title case in their column names.
    """

    all_paths = """
    /orig/coefficients.csv
    /orig/silv_treatments.csv
    /export/ageclass.csv
    /export/inventory.csv
    /export/classifiers.csv
    /export/disturbance_events.csv
    /export/disturbance_types.csv
    /export/transition_rules.csv
    /export/yields.csv
    /export/historical_yields.csv
    /fusion/back_inventory_aws.csv
    """

    def __init__(self, country):
        # Default attributes #
        self.country = country
        # Automatically access paths based on a string of many subpaths #
        self.paths = AutoPaths(self.country.data_dir, self.all_paths)

    def __call__(self):
        for p in self.paths:
            # Some countries don't have that fusion file #
            if not p: continue
            # Read into memory #
            df = pandas.read_csv(str(p))
            # Change #
            df = df.rename(columns = camel_to_snake)
            # Write back to disk #
            df.to_csv(str(p), index=False, float_format='%g')

    def fix_spelling(self):
        """Some words were written wrongly but not in all countries."""
        # Read #
        df = pandas.read_csv(str(self.paths.disturbance_events))
        # Change #
        df = df.rename(columns = {'efficency': 'efficiency',
                                  'sor_type':  'sort_type'})
        # Write #
        df.to_csv(str(self.paths.disturbance_events), index=False, float_format='%g')

###############################################################################
class CaseRenamer(object):
    """
    This class takes our python source files and renames the column variables
    to match the new case. It can also operate on the jupyter notebooks.
    """

    def __init__(self, base_dir, extension):
        # Default attributes #
        self.base_dir = Path(base_dir)
        self.extension = extension

    col_names = {
        'ageclass':     'AgeClassID,Size',
        'classifiers':  'ClassifierNumber,ClassifierValueID',
        'disturbances': 'UsingID,SWStart,SWEnd,HWStart,HWEnd,Min_since_last_Dist,'
                        'Max_since_last_Dist,Last_Dist_ID,Min_tot_biom_C,Max_tot_biom_C,'
                        'Min_merch_soft_biom_C,Max_merch_soft_biom_C,Min_merch_hard_biom_C,'
                        'Max_merch_hard_biom_C,Min_tot_stem_snag_C,Max_tot_stem_snag_C,'
                        'Min_tot_soft_stem_snag_C,Max_tot_soft_stem_snag_C,Min_tot_hard_stem_snag_C,'
                        'Max_tot_hard_stem_snag_C,Min_tot_merch_stem_snag_C,Max_tot_merch_stem_snag_C,'
                        'Min_tot_merch_soft_stem_snag_C,Max_tot_merch_soft_stem_snag_C,'
                        'Min_tot_merch_hard_stem_snag_C,Max_tot_merch_hard_stem_snag_C,Efficency,'
                        'Sort_Type,Measurement_type,Amount,Dist_Type_ID,Step',
        'yields':       'Sp',
        'inventory':    'UsingID,Age,Area,Delay,UNFCCCL,HistDist,LastDist',
        'transitions':  'UsingID,SWStart,SWEnd,HWStart,HWEnd,Dist_Type_ID,RegenDelay,ResetAge,Percent',
        'treatments':   'Dist_Type_ID,Sort_Type,Efficiency,Min_age,Max_age,Min_since_last,'
                        'Max_since_last,HWP,RegenDelay,ResetAge,Percent,WD,OWC_Perc,Snag_Perc,'
                        'Perc_Merch_Biom_rem,Man_Nat',
        'database':     'TimeStep, UserDefdClassID, UserDefdClassSetID, UserDefdSubclassID,'
                        'UserDefdSubClassName, AveAge, Biomass, DistArea,'
                        'BEF_Tot, BG_Biomass, Tot_Merch, Tot_ABG, BG_Biomass,'
                        'Vol_Merch, Vol_SubMerch, Vol_Snags, TC, TC_FW_C,'
                        'Vol_Merch_FW_B, Vol_SubMerch_FW_B, Vol_Snags_FW_B,'
                        'Vol_SubMerch_IRW_B, Vol_Snags_IRW_B,'
                        'TOT_Vol_FW_B, DMStructureID, DMColumn, DMRow, DMID',
        'products':     'SW_Merch, SW_Foliage, SW_Other, HW_Merch, HW_Foliage, HW_Other, SW_Coarse,'
                        'SW_Fine, HW_Coarse, HW_Fine, Merch_C_ha,'
                        'Snag_Perc, OWC_Perc, FW_amount, IRW_amount,'
                        'SoftProduction, HardProduction, DOMProduction,'
                        'CO2Production, MerchLitterInput, OthLitterInput,'
                        'Prov_Carbon, Vol_forest_residues,',
        'extras':       'IRW_C, FW_C, IRW_B, FW_B'
     }

    @property_cached
    def cols_before(self):
        cols_before = ','.join(self.col_names.values()).split(',')
        return list(set(name.strip() for name in cols_before))

    @property_cached
    def cols_after(self):
        return [camel_to_snake(col) for col in self.cols_before]

    @property_cached
    def code_files(self):
        return [f for f in self.base_dir.files if f.extension == self.extension]

    def __call__(self):
        for file in tqdm(self.code_files):
            for old_name, new_name in zip(self.cols_before, self.cols_after):
                # Only if it is found enclosed in quotes #
                file.replace_word("'%s'" % old_name, "'%s'" % new_name)
                # Only if it is with the word 'query' on the same line #
                self.replace_word_if_other_word(file, old_name, 'query', new_name)

    def replace_word_if_other_word(self, path, word1, word2, replacement_word):
        """
        Search the file for a given word, and if found,
        check the line in which it appears for another second word,
        if both the first and second word are found on the same line,
        then replace every occurrence of the first word with
        the replacement word.
        """
        # The original file #
        orig_file = Path(path)
        # Create a new file #
        result_file = autopaths.tmp_path.new_temp_file()
        # Generate the lines #
        def new_lines():
            for line in orig_file:
                if word2 in line: yield line.replace(word1, replacement_word)
                else: yield line
        # Open input/output files, note: output file's permissions lost #
        result_file.writelines(new_lines())
        # Switch the files around #
        orig_file.remove()
        result_file.move_to(orig_file)

###############################################################################
if __name__ == '__main__':
    # First part #
    converters = [CaseConverter(c) for c in continent]
    for converter in tqdm(converters): converter()
    for converter in tqdm(converters): converter.fix_spelling()
    # Second part #
    code_dir = home + "repos/cbmcfs3_runner/cbmcfs3_runner/"
    renamer  = CaseRenamer(code_dir, '.py')
    renamer()
    # Third part #
    code_dir = home + "repos/bioeconomy_notes/notebooks/"
    renamer  = CaseRenamer(code_dir, '.md')
    renamer()

