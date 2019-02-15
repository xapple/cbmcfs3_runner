# Built-in modules #
import socket

# Internal modules #
import cbm_runner

# First party modules #
from pymarktex import Template
from plumbing.common import pretty_now

###############################################################################
class ReportTemplate(Template):
    """Things that are common to most reports in cbm_runner."""

    # Process info #
    def project_name(self):      return cbm_runner.project_name
    def project_url(self):       return cbm_runner.project_url
    def project_version(self):   return cbm_runner.__version__
    def now(self):               return pretty_now()
    def hostname(self):          return socket.gethostname()
    def git(self):
        if not cbm_runner.git_repo: return False
        return {'git_hash'  : cbm_runner.git_repo.hash,
                'git_tag'   : cbm_runner.git_repo.tag,
                'git_branch': cbm_runner.git_repo.branch}
