# Built-in modules #
import socket

# Internal modules #
import cbmcfs3_runner

# First party modules #
from pymarktex import Template
from plumbing.common import pretty_now

###############################################################################
class ReportTemplate(Template):
    """Things that are common to most reports in cbmcfs3_runner."""

    # Process info #
    def project_name(self):      return cbmcfs3_runner.project_name
    def project_url(self):       return cbmcfs3_runner.project_url
    def project_version(self):   return cbmcfs3_runner.__version__
    def now(self):               return pretty_now()
    def hostname(self):          return socket.gethostname()
    def git(self):
        if not cbmcfs3_runner.git_repo: return False
        return {'git_hash'  : cbmcfs3_runner.git_repo.hash,
                'git_tag'   : cbmcfs3_runner.git_repo.tag,
                'git_branch': cbmcfs3_runner.git_repo.branch}
