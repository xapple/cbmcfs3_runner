



# Installation steps on windows

## Set environment variables

Set the environment variable that tells cbmcfs3_runner where the data is located

    setx CBMCFS3_DATA "C:\CBM\cbmcfs3_data"

Display it

    echo %CBMCFS3_DATA%

[How to update a windows environment variable without
rebooting](https://serverfault.com/questions/8855/how-do-you-add-a-windows-environment-variable-without-rebooting)


## Python dependencies

As visible from ~/rp/cbmcfs3_runner/setup.py under the `install_requires` variable.

    pip install autopaths
    # Install an old version of plumbing that still has the multi_index_pivot
    pip install -Iv plumbing==2.6.7 
    pip install pymarktex
    pip install pbs3
    pip install pandas
    pip install pystache
    pip install pyexcel
    pip install pyexcel-xlsx
    pip install seaborn
    pip install xlrd
    pip install xlsxwriter
    pip install simplejson
    pip install brewer2mpl
    pip install matplotlib==3.0.3
    pip install tabulate
    pip install tqdm
    pip install numpy
    pip install six
    pip install requests


## Accessing the input data of one country

Importing the continent object

    from cbmcfs3_runner.core.continent import continent

Fails with 



## Running for one country


