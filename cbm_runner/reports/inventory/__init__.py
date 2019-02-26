# Futures #
from __future__ import division

# Built-in modules #

# Internal modules #
from cbm_runner import project_name, project_url

from cbm_runner.reports.template import ReportTemplate

# First party modules #
from plumbing.cache    import property_cached
from pymarktex         import Document
from pymarktex.figures import ScaledFigure

###############################################################################
class InventoryReport(Document):
    """A report generated in PDF describing the forest inventory
    before and after the CBM-CFS3 simulation."""

    def __init__(self, parent):
        # Attributes #
        self.parent = parent
        # Paths #
        self.output_path = self.parent.paths.inventory_pdf

    @property_cached
    def template(self): return InvTemplate(self)

    def generate(self):
        # Dynamic templates #
        self.markdown = unicode(self.template)
        # Render to latex #
        self.make_body()
        self.make_latex({'title': 'Inventory report'})
        self.make_pdf(safe=False)

###############################################################################
class InvTemplate(ReportTemplate):
    """All the parameters to be rendered in the markdown template."""
    delimiters = (u'{{', u'}}')

    def __repr__(self): return '<%s object on %s>' % (self.__class__.__name__, self.parent)

    def __init__(self, report):
        # Attributes #
        self.report, self.parent = report, report
        self.runner = self.parent.parent.parent
        self.graphs = self.runner.graphs

    def short_name(self):
        return self.runner.data_dir.directory.name

    def input_inventory(self):
        caption = "Distribution of total area according to age"
        path    = self.graphs.input_inventory.path
        label   = "input_inventory"
        return str(ScaledFigure(path, caption, label))

    def predicted_inventory(self):
        caption = "Distribution of total area according to age"
        path    = self.graphs.predicted_inventory.path
        label   = "predicted_inventory"
        return str(ScaledFigure(path, caption, label))

