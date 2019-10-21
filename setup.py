from setuptools import setup, find_packages

setup(
        name             = 'cbmcfs3_runner',
        version          = '0.4.1',
        description      = 'cbmcfs3_runner is a python package for running carbon budget simulations.',
        long_description = open('README.md').read(),
        license          = 'MIT',
        url              = 'https://github.com/xapple/cbmcfs3_runner',
        author           = 'Lucas Sinclair',
        author_email     = 'lucas.sinclair@me.com',
        packages         = find_packages(),
        install_requires = ['autopaths', 'plumbing', 'pymarktex', 'pbs3', 'pandas', 'pystache',
                            'pyexcel', 'pyexcel-xlsx', 'seaborn', 'xlrd', 'xlsxwriter',
                            'simplejson', 'brewer2mpl', 'matplotlib==3.0.3', 'tabulate', 'tqdm',
                            'numpy'],
    )
