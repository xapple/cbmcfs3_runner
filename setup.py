from setuptools import setup

setup(
        name             = 'cbmcfs3_runner',
        version          = '0.2.1',
        description      = 'cbmcfs3_runner is a python package for running carbon budget simulations.',
        long_description = open('README.md').read(),
        license          = 'MIT',
        author           = 'Lucas Sinclair',
        author_email     = 'lucas.sinclair@me.com',
        install_requires = ['autopaths', 'plumbing', 'pymarktex', 'pandas', 'pbs', 'pystache',
                            'pyexcel', 'pyexcel-xlsx', 'seaborn', 'xlrd', 'xlsxwriter',
                            'simplejson'],
        packages         = ['cbmcfs3_runner'],
    )
