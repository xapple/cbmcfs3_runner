# Third party modules #
import seaborn

# First party modules #
from plumbing.graphs import Graph

###############################################################################
class InventoryBarChart(Graph):
    def plot(self, **kwargs):
        df = self.parent.parent.input_data.inventory
        df = df.set_index('Age').groupby('Age').sum()[['Area']]
        seaborn.barplot(df.index, df['Area'])