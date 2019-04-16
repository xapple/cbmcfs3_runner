# Futures #
from __future__ import division

# Built-in modules #

# Internal modules #
from cbmcfs3_runner.reports.template import ReportTemplate

# First party modules #
from plumbing.cache    import property_cached
from pymarktex         import Document
from pymarktex.figures import ScaledFigure

###############################################################################
class CountryReport(Document):
    """A report generated in PDF describing a scenario."""

    def __init__(self, parent):
        # Attributes #
        self.parent = parent
        # Paths #
        self.output_path = self.parent.paths.inventory_pdf

    @property_cached
    def template(self): return CountryTemplate(self)

    def generate(self):
        # Dynamic templates #
        self.markdown = unicode(self.template)
        # Render to latex #
        self.make_body()
        self.make_latex({'title': 'Country report'})
        self.make_pdf(safe=False)

###############################################################################
class CountryTemplate(ReportTemplate):
    """All the parameters to be rendered in the markdown template."""
    delimiters = (u'{{', u'}}')

    def __repr__(self): return '<%s object on %s>' % (self.__class__.__name__, self.parent)

    def __init__(self):
        pass