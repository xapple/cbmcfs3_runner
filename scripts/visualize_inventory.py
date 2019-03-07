"""
A test script (throw it away later) to visualize the inventory.
"""

# Third party modules #
import pyodbc, pandas, seaborn

# First party modules #
from plumbing.graphs import Graph

# Constants #
db_file = "\\deploy\\cbm_runner\\tests\\tutorial_six\\data\\output\\cbm_formatted_db\\project.mdb"
driver_string = "Driver={Microsoft Access Driver (*.mdb, *.accdb)};User Id='admin';DBQ="

###############################################################################
class InventoryBarChart(Graph):
    def plot(self, **kwargs):
        seaborn.barplot(self.x_data, self.y_data)

###############################################################################
# Get data #
conn  = pyodbc.connect(driver_string + db_file)
query = "SELECT * FROM tblInventory"
df    = pandas.read_sql(query, conn)
conn.close()

# Make a plot #
graph = InventoryBarChart()
graph.x_data     = df['Age']
graph.y_data     = df['Area']
graph.short_name = "initial_inventory"
graph.plot_and_save()
