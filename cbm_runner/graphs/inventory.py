# Third party modules #
import pyodbc, pandas, seaborn

# First party modules #
from plumbing.graphs import Graph

###############################################################################
class InventoryBarChart(Graph):
    def plot(self, **kwargs):
        seaborn.barplot(self.x_data, self.y_data)

###############################################################################
# Make a plot #
graph = InventoryBarChart()
graph.plot_and_save()
