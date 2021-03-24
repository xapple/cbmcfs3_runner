

# Installation steps on windows


## Install python and ipython 

Python was installed on the machine.

But the user decided to use Anaconda and the Spyder editor.
Then start ipython and ask what was the location of the interpreter:

    import sys
    sys.argv


## Set environment variables

In the windows start menu environmental variables

- Set Path variable to contain python
- Set PYTHONPATH variable to contain cbmcfs3_data
- Set CBMCFS3_DATA  variables to contain the location of cbmcfs3_data


Set the environment variable that tells cbmcfs3_runner where the data is located

    setx CBMCFS3_DATA "C:\CBM\cbmcfs3_data"

Display it

    echo %CBMCFS3_DATA%

Display environnemental variables from within python

    import os
    print(os.environ['CBMCFS3_DATA'])
    print(os.environ['PYTHONPATH'])

[How to update a windows environment variable without
rebooting](https://serverfault.com/questions/8855/how-do-you-add-a-windows-environment-variable-without-rebooting)

Add the following to your python path

    C:\CBM/cbmcfs3_runner 

Display the python path

    import os
    os.environ['PYTHONPATH'].split(os.pathsep)


## Configure spyder

    pip install spyder-kernels




## Install Python dependencies with pip

As visible from ~/rp/cbmcfs3_runner/setup.py under the `install_requires` variable.

    pip install autopaths
    pip install brewer2mpl
    pip install matplotlib==3.0.3
    pip install numpy
    pip install pandas
    pip install pbs3
    pip install plumbing
    pip install pyexcel
    pip install pyexcel-xlsx
    pip install pymarktex
    pip install pystache
    pip install requests
    pip install seaborn
    pip install simplejson
    pip install six
    pip install tabulate
    pip install tqdm
    pip install xlrd
    pip install xlsxwriter


## Install Python dependencies with anaconda

[how to install pypi packages using 
anacond](https://stackoverflow.com/questions/29286624/how-to-install-pypi-packages-using-anaconda-conda-command)

Since version 4.6.0, Conda has improved its interoperability with pip:

    conda config --set pip_interop_enabled True

So, the way to get PyPI packages into conda (at the time of writing this) seems to be:

    pip install <package>

If you want conda to replace the PyPI packages with its own (where possible), just run:

    conda update --all

Given that the above setting is made. Conda marks its own channels as higher priority than pip, thus packages will be replaced.


# Show input data

    from cbmcfs3_runner.core.continent import continent
    runner_AT    = continent[('static_demand', 'AT', 0)]
    runner_LU    = continent[('static_demand', 'LU', 0)]
    runner_HU    = continent[('static_demand', 'HU', 0)]
    # Inventories #
    inv_AT = runner_AT.country.orig_data.inventory
    inv_LU = runner_LU.country.orig_data.inventory
    # yield
    inv_AT = runner_AT.country.orig_data.yields
    # Disturbances
    inv_AT = runner_AT.country.orig_data.disturbance_events



# Run for one country


