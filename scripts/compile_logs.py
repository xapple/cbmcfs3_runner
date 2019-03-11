"""
A test script to visualize the tail of the runner log for each country in one
summary markdown document.

Typically you would run this file from a command line like this:

     ipython.exe -i -- /deploy/cbm_runner/scripts/compile_logs.py
"""

# Built-in modules #

# Third party modules #

# First party modules #

# Internal modules #
from cbm_runner.all_countries import continent, cbm_data_repos

###############################################################################
summary = cbm_data_repos + "logs_summary.md"
summary.open(mode='w')
summary.handle.write("# Summary of all log file tails\n\n")
summary.handle.writelines(c.summary for c in continent.all_countries)
summary.close()

###############################################################################
#import pbs
#pandoc = pbs.Command("pandoc")
#pandoc('-s', '-o', summary.replace_extension('pdf'), summary)