# First party modules #
from plumbing.cache import property_cached
from autopaths.auto_paths import AutoPaths

# Internal modules #
from cbmcfs3_runner.reports.inventory import InventoryReport

###############################################################################
class Reports(object):
    """This class will take care of the production of all the PDF reports.
    These reports are seen as the true deliverable outputs to
    the stakeholders."""

    all_paths = """
    /output/reports/inventory/inventory.pdf
    """

    def __init__(self, parent):
        # Default attributes #
        self.parent = parent
        # Directories #
        self.paths = AutoPaths(self.parent.data_dir, self.all_paths)

    def __call__(self):
        self.inventory_report()

    @property_cached
    def inventory_report(self):
        return InventoryReport(self)

