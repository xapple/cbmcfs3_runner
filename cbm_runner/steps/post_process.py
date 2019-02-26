# Built-in modules #

# Third party modules #

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
    def predicted_inventory(self):
        return 0

