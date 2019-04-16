#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Written by Lucas Sinclair and Paul Rougieux.

JRC biomass Project.
Unit D1 Bioeconomy.
"""

# Special variables #
__version__ = '0.3.0'

# Built-in modules #
import os, sys

# First party modules #
from autopaths.dir_path import DirectoryPath
from plumbing.git import GitRepo

# Constants #
project_name = 'cbmcfs3_runner'
project_url  = 'https://github.com/xapple/cbmcfs3_runner'

# Get paths to module #
self       = sys.modules[__name__]
module_dir = DirectoryPath(os.path.dirname(self.__file__))

# The repository directory #
repos_dir = module_dir.directory

# The module is maybe in a git repository #
git_repo = GitRepo(repos_dir, empty=True)

# Change the pbs truncate cap for longer stderr #
if os.name == "posix":
    import sh
    sh.ErrorReturnCode.truncate_cap  = 2000
if os.name == "nt":
    import pbs
    pbs.ErrorReturnCode.truncate_cap = 2000