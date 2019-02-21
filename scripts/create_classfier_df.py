"""
A test script (throw it away later) to create a specific dataframe.
"""

# Third party modules #

# Internal modules #
from cbm_runner.runner import Runner
import cbm_runner

###############################################################################
runner = Runner(cbm_runner.repos_dir + "tests/tutorial_six/data/")
sim_result = runner.post_processor.sim_result

user_classes           = sim_result["tblUserDefdClasses"]
user_sub_classes       = sim_result["tblUserDefdSubclasses"]
user_class_sets        = sim_result["tblUserDefdClassSets"]
user_class_sets_values = sim_result["tblUserDefdClassSetValues"]

index = ['UserDefdClassID', 'UserDefdSubclassID']
classifiers = user_sub_classes.set_index(index)
classifiers = classifiers.join(user_class_sets_values.set_index(index))

index = ['UserDefdClassID', 'UserDefdClassSetID']
classifiers = classifiers.reset_index().set_index(index)
classifiers = classifiers[['UserDefdSubClassName']].unstack('UserDefdClassID')

# remplacer 1, 2, 3
# par Species Site quality Forest type
# ou plutôt species, site_quality, forest_type disponible dans la table
# tblUserDefdClasses

# This object will link: 1->species 2->forest_type etc.
mapping = user_classes.set_index('UserDefdClassID')['ClassDesc']
mapping = mapping.apply(lambda x: x.lower().replace(' ', '_'))

# This method will rename the columns using the mapping
classifiers = classifiers.rename(mapping, axis=1)
