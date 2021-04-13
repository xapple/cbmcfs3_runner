# Introduction

The approach was to install the cbmcfs3_runner python package. Then work through the
error message and solve the missing dependencies.


See also 

    ~/rp/bioeconomy_notes/models/cbmcfs3/docs/windows_vm_setup.md 

# Installation of Python related tools

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
    print(os.environ['PATH'])

[How to update a windows environment variable without
rebooting](https://serverfault.com/questions/8855/how-do-you-add-a-windows-environment-variable-without-rebooting)

Add the following to your python path

    C:\CBM/cbmcfs3_runner 

Display the python path

    import os
    os.environ['PYTHONPATH'].split(os.pathsep)


## Configure spyder

    pip install spyder-kernels




## Pip install 

Install Python dependencies with pip.

As visible from ~/rp/cbmcfs3_runner/setup.py under the `install_requires` variable.

    pip install autopaths
    pip install brewer2mpl
    pip install cbm3_python
    pip install matplotlib==3.0.3
    pip install numpy
    pip install pandas
    pip install pbs3
    pip install plumbing
    pip install pymarktex
    pip install pyodbc
    pip install pystache
    pip install requests
    pip install seaborn
    pip install simplejson
    pip install six
    pip install tabulate
    pip install tqdm
    pip install xlrd
    pip install xlsxwriter

    # Excel dependency not needed once you load sit from csv files
    pip install pyexcel
    pip install pyexcel-xlsx
    pip install pyexcel-xls

## Conda install

Install Python dependencies with anaconda

[how to install pypi packages using 
anacond](https://stackoverflow.com/questions/29286624/how-to-install-pypi-packages-using-anaconda-conda-command)

Since version 4.6.0, Conda has improved its interoperability with pip:

    conda config --set pip_interop_enabled True

So, the way to get PyPI packages into conda (at the time of writing this) seems to be:

    pip install <package>

If you want conda to replace the PyPI packages with its own (where possible), just run:

    conda update --all

Given that the above setting is made. Conda marks its own channels as higher priority than pip, thus packages will be replaced.


## Jupyter notebooks 

Install Jupyter notebooks and dependencies to explore data, convert to markdown text and
display a table of content.

Install

    pip install jupytext   
    conda install jupyter

Configure juptytext

    python -m jupyter notebook --generate-config
    python -m jupyter nbextension install jupytext --py --user
    python -m jupyter nbextension enable  jupytext --py --user

Start the notebooks

    python -m jupyter notebook


# cbm3_python python and SIT

Create a repos in your user folder on windows

Cbmcfs3_runner depends on a package made by the canadian team called cbm3_python

    git clone https://github.com/cat-cfs/cbm3_python.git 

Download the standard import tool from the releases

    https://github.com/cat-cfs/StandardImportToolPlugin/releases

There was a table import bug when running that version of SIT and we installed an older
version 

    https://github.com/cat-cfs/StandardImportToolPlugin/releases/download/1.3.0.1/Release.zip

Unzip the folder in the machine. Add the location of the folder containing

    StandardImportToolPlugin.exe

Add its location to the environment variables.


# Data

We need: 
- input csv
- Archive index database

Clone the cbmcfs3_data repository make it available to python by entering thet system
environment variable CBMCFS3_DATA as explained above.

Copy the CBM Archive Index database 
https://jrcbox.jrc.ec.europa.eu/index.php/apps/files/?dir=/Forbiomod/SourceData/EFDM/cbmcfs3_data/countries/LU/orig&fileid=12184184


## Show input data

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



# Git usage for cbmcfs3_runner

Current status of your git repository

    git status

Check previous version of the file, for example the documentation folder

Add files describe changes and push to the gitlab repository

    git add file_name
    git commit -m "Describe your changes"
    git push


# Run

## for one country

Run the historical scenario (easier because there is no creation of disturbances) 

    from cbmcfs3_runner.core.continent import continent
    runner = continent[('historical', 'LU', 0)]

## For many countries

Run the historical scenario for all countries

    from cbmcfs3_runner.core.continent import continent
    scenario = continent.scenarios['historical']
    scenario(verbose=True)

See also the script in the `cbmcfs3_runner` repository, under :
`scripts/running/run_all_countries.py` which can be invoked like this from the windows
machine.

    ipython3.exe -i -- /deploy/cbmcfs3_runner/scripts/running/run_all_countries.py


# Debug

## Modify the JSON file to configure SIT
  
    from cbmcfs3_runner.core.continent import continent
    runner    = continent[('historical', 'LU', 0)]
    # The pre processor copies the csv input files
    runner.pre_processor()
    # Show the different yield tables names
    In : runner.default_sit.yield_table_name
    Out: 'yields.csv'
    In : runner.append_sit.yield_table_name
    Out: 'historical_yields.csv'
    # Create a json configuration file to tell SIT the location of the csv files
    runner.default_sit.create_json()


## Modify the transition rules table

Rename columns of the transition rules 
To prevent a SIT error on import 

    Unhandled Exception: System.Data.DuplicateNameException:
       A column named '_1' already belongs to this DataTable.


    from cbmcfs3_runner.core.continent import continent
    runner    = continent[('historical', 'LU', 0)]
    # The pre processor copies the csv input files
    runner.pre_processor()



## Connect to an access database

You might need the [MS Access 2013
runtime](https://www.microsoft.com/en-us/download/details.aspx?id=39358) depending on
your version of office as explained on this [Microsoft trouble shooting
page](https://docs.microsoft.com/en-us/office/troubleshoot/access/cannot-use-odbc-or-oledb). 


The MS Access input database generated by SIT is here

    runner.middle_processor.project_database

Make it possible to change the user name

    runner.middle_processor.project_database.username
    runner.middle_processor.project_database.conn_string

Or change the default user name to os.getlogin() inside the 2 places in the code that
are creating an instance of an access database. Pass os.getlogin() as the username
argument.

Note the output database generated by CBM is here

    from cbmcfs3_runner.core.continent import continent
    runner = continent[('historical', 'LU', 0)]
    runner.launch_cbm.generated_database



# Reflections

- Each country has its specific AIDB because each country has slightly different species
  definitions. Maybe these should be an harmonised AIDB at some point.


