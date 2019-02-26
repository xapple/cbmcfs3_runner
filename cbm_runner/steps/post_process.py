# Built-in modules #
import StringIO

# Third party modules #
import pandas

# First party modules #
from plumbing.databases.access_database import AccessDatabase
from plumbing.cache import property_cached
from autopaths.auto_paths import AutoPaths

# Internal modules #

###############################################################################
class PostProcessor(object):
    """
    Provides access to the Access database.
    Computes aggregates and joins to facilitate analysis. 
    """

    all_paths = """
    /output/after_simulation/project.mdb
    """

    def __init__(self, parent):
        # Default attributes #
        self.parent = parent
        # Directories #
        self.paths = AutoPaths(self.parent.data_dir, self.all_paths)

    @property_cached
    def sim_result(self):
        path = self.parent.compute_model.paths.after_mdb
        path.must_exist()
        return AccessDatabase(path)

    @property_cached
    def classifiers(self):
        """Creates a mapping between 'UserDefdClassSetID'
        and species, site_quality and forest_type, etc."""
        # The three tables we will need #
        user_classes           = self.sim_result["tblUserDefdClasses"]
        user_sub_classes       = self.sim_result["tblUserDefdSubclasses"]
        user_class_sets_values = self.sim_result["tblUserDefdClassSetValues"]
        # Lorem ipsum #
        index = ['UserDefdClassID', 'UserDefdSubclassID']
        classifiers = user_sub_classes.set_index(index)
        classifiers = classifiers.join(user_class_sets_values.set_index(index))
        # Lorem ipsum #
        index = ['UserDefdClassID', 'UserDefdClassSetID']
        classifiers = classifiers.reset_index().set_index(index)
        classifiers = classifiers[['UserDefdSubClassName']].unstack('UserDefdClassID')
        # This object will link: 1->species, 2->forest_type, etc.
        mapping = user_classes.set_index('UserDefdClassID')['ClassDesc']
        mapping = mapping.apply(lambda x: x.lower().replace(' ', '_'))
        # This method will rename the columns using the mapping
        classifiers = classifiers.rename(mapping, axis=1)
        # Remove multilevel column index, replace by level(1) (second level)
        classifiers.columns = classifiers.columns.get_level_values(1)
        # Remove the confusing name #
        del classifiers.columns.name
        return classifiers
   
    @property_cached
    def coefficients(self):
        csv = """ID,species,C,DB,Harvest_Gr
               76,AA,0.5,0.4,Con
               77,HP,0.5,0.4,Con
               79,PS,0.5,0.42,Con
               80,FS,0.5,0.58,Broad
               81,QR,0.5,0.58,Broad
               83,LD,0.5,0.46,Con
               86,OB,0.5,0.5,Broad
               87,OC,0.5,0.4,Con"""
        csv = StringIO.StringIO(csv)
        return pandas.read_csv(csv)

    @property_cached
    def bef_ft(self):
        pool = self.sim_result["tblPoolIndicators"].set_index('UserDefdClassSetID')
        bef_ft = pool.join(self.classifiers, on="UserDefdClassSetID")
        cols_sum = {'SW_Merch'  :'sum',
                    'SW_Foliage':'sum',
                    'SW_Other'  :'sum',
                    'HW_Merch'  :'sum',
                    'HW_Foliage':'sum',
                    'HW_Other'  :'sum',
                    'SW_Coarse' :'sum',
                    'SW_Fine'   :'sum',
                    'HW_Coarse' :'sum',
                    'HW_Fine'   :'sum'}
        bef_ft = bef_ft.groupby("forest_type").agg(cols_sum)
        bef_ft['Tot_Merch']  = bef_ft.SW_Merch + bef_ft.HW_Merch
        bef_ft['Tot_ABG']    = bef_ft.SW_Merch + bef_ft.HW_Merch + \
                               bef_ft.SW_Foliage + bef_ft.HW_Foliage + \
                               bef_ft.HW_Other + bef_ft.SW_Other
        bef_ft['BG_Biomass'] = bef_ft.SW_Coarse + bef_ft.SW_Fine + \
                               bef_ft.HW_Coarse + bef_ft.HW_Fine
        bef_ft['BEF_Tot']    = (bef_ft.Tot_ABG + bef_ft.BG_Biomass) / bef_ft.Tot_ABG
        return bef_ft 

    @property_cached
    def predicted_inventory(self):
        age_indicators = self.sim_result["tblAgeIndicators"]
        inv = age_indicators.set_index('UserDefdClassSetID').join(self.classifiers, on='UserDefdClassSetID')
        inv = inv.reset_index().set_index('forest_type').join(self.bef_ft, on='forest_type')
        inv = inv.reset_index().set_index('species').join(self.coefficients.set_index('species'), on='species')
        inv = inv.reset_index()
        inv = inv[['species', 'forest_type',
                   'AveAge', 'TimeStep', 'Area', 
                   'Biomass', 'BEF_Tot',
                   'DB']]
        inv['Merch_C_ha'] = inv.Biomass / inv.BEF_Tot
        inv['Merch_Vol_ha'] = inv.Merch_C_ha / inv.DB
        return inv 
