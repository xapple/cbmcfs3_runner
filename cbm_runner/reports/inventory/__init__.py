# Futures #
from __future__ import division

# Built-in modules #

# Internal modules #
from cbm_runner import project_name, project_url

from cbm_runner.reports.template import ReportTemplate

# First party modules #
from plumbing.cache import property_cached
from pymarktex      import Document

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
        self.make_pdf(safe=True)

###############################################################################
class InvTemplate(ReportTemplate):
    """All the parameters to be rendered in the markdown template."""
    delimiters = (u'{{', u'}}')

    def __repr__(self): return '<%s object on %s>' % (self.__class__.__name__, self.parent)

    def __init__(self, report):
        # Attributes #
        self.report, self.parent = report, report

    def short_name(self):
        return self.parent.parent.parent.data_dir.directory.name
