"""
A test script to test projects with a single ageclass in the inventory.

Typically you would run this file from a command line like this:

     ipython.exe -i -- /deploy/cbm_runner/scripts/single_ageclass_test.py

"""

# Third party modules #
from matplotlib import pyplot
import pandas, seaborn

# First party modules #
from autopaths.dir_path   import DirectoryPath

# Internal modules #
from cbm_runner.runner import Runner

# Constants #
orig_project_path = DirectoryPath("/deploy/cbm_runner/tests/tutorial_six_bis/data/")
temp_directory    = DirectoryPath("~/test/")

###############################################################################
runner_orig = Runner(orig_project_path)
inv_orig    = pandas.read_csv(runner_orig.csv_to_xls.paths.inventory)

# Group by age #
age_grouped = inv_orig.groupby('Age')

# Do we want to rerun the simulation #
rerun = False

# Main loop #
for i, small_inv in age_grouped:
    # Make a new directory #
    age          = small_inv.iloc[0]['Age']
    project_name = 'age_%s' % age
    project_dir  = temp_directory + project_name + '/'
    if rerun: project_dir.remove()
    if rerun: project_dir.create()
    # Create the runner #
    runner = Runner(project_dir)
    # Copy the input data #
    if rerun: runner_orig.paths.input_dir.copy(str(project_dir + 'input/'))
    # Overwrite the inventory #
    new_inv = runner.csv_to_xls.paths.inventory
    if rerun: small_inv.to_csv(str(new_inv), index=False)
    # Run the project #
    if rerun: runner.clear_all_outputs()
    if rerun: runner.csv_to_xls()
    if rerun: runner.standard_import_tool()
    if rerun: runner.compute_model()
    if rerun: runner.graphs()
    # Display other cool plots #
    graphs_dir  = DirectoryPath(project_dir + 'graphs/')
    graphs_dir.create()
    graph_path_pdf = graphs_dir + 'age_along_timestep.pdf'
    graph_path_png = graphs_dir + 'age_along_timestep.png'
    inv_pred = runner.post_processor.predicted_inventory
    fig = pyplot.figure()
    seaborn.scatterplot(x='TimeStep', y='AveAge', hue='Area', data=inv_pred)
    fig.savefig(graph_path_pdf)
    fig.savefig(graph_path_png)