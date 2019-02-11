import setuptools
from distutils.core import setup

setup(
        name             = 'cbm_runner',
        version          = '0.1.0',
        description      = 'cbm_runner is a python package for running carbon budget simulations.',
        long_description = open('README.md').read(),
        license          = 'MIT',
        author           = 'Lucas Sinclair',
        author_email     = 'lucas.sinclair@me.com',
        install_requires = ['autopaths', 'sh', 'pbs'],
        packages         = ['cbm_runner'],
    )
