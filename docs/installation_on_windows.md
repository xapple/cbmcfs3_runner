# Installation

Setup of `cbmcfs3_data` and `cbmcfs3_runner`

This guide shows how to set up the `cbmcfs3_data` and `cbmcfs3_runner` projects together on a Windows system to run the 26 EU carbon budget simulations with `cbm3_python` automatically.

It assumes you are using Windows version 10.

### Related documents

Previous versions of the installation procedure and related documents can be found here:

    ~/repos/bioeconomy_notes/models/cbmcfs3/docs/windows_vm_setup.md
    ~/repos/bioeconomy_notes/setup/setup_new_windows_ec2/create_minimal_image.md
    ~/repos/bioeconomy_notes/setup/cbmcfs3_tutorial_install.md

# Install Python 3

Run this command from an administrator shell if you don't already have python:

    $ choco install -y python3 --version=3.9.7

It requires the chocolatey package manager from https://chocolatey.org for windows.
At the end, you will have to reboot.
Finally check the version in a new shell:

    $ python -V

# Install dependencies

Run these commands from an administrator shell to get the "Microsoft Access Database Engine 2010":

    $ choco install -y made2010
    $ choco install -y git

# Enable old features

Run this command from an administrator PowerShell to enable some "dot net" features:

  DISM /Online /Enable-Feature:NetFx3 /All

## Obtain latest CBM-CFS3

The file is located at https://carbon.nfis.org/cbm/downloadFile.action?file_id=1316
But you have to log-in with a user account to have access to the downloads.
Also the website was geo-ip filtered in the past, so you can set your VPN to Canada.

## Install latest CBM-CFS3

Assuming the file you downloaded is in Downloads, run this:

    $ msiexec /i $HOME\Downloads\CBMToolsSetup.msi /q

## Install StandardImportTool

You can grab the latest version from:

https://github.com/cat-cfs/StandardImportToolPlugin/releases

Place it in "Program Files" and add the directory containing the executable to your PATH environment variable.

# Clone essential git repositories

Run this command from an administrator PowerShell:

    $ New-Item -ItemType Directory -Path $HOME/repos
    $ cd $HOME/repos
    $ git clone https://github.com/cat-cfs/cbm3_python.git
    $ git clone https://gitlab.com/bioeconomy/cbmcfs3/cbmcfs3_runner.git
    $ git clone https://gitlab.com/bioeconomy/cbmcfs3/cbmcfs3_data.git
    $ git clone https://gitlab.com/bioeconomy/cbmcfs3/cbmcfs3_aidb.git

## Install python packages

Use pip from an administrator shell:

    $ pip install autopaths
    $ pip install plumbing
    $ pip install pymarktex
    $ pip install pbs3
    $ pip install tzlocal
    $ pip install ipython
    $ pip install pyodbc
    $ pip install matplotlib
    $ pip install seaborn
    $ pip install tqdm
    $ pip install brewer2mpl
    $ pip install tabulate
    $ pip install simplejson
    $ pip install pyexcel
    $ pip install pypiwin32

## Set environment variables

Set the environment variable that tells python where the modules are located:

    $ SETX PYTHONPATH "$HOME/repos/cbmcfs3_runner;$HOME/repos/cbm3_python"

Set the environment variable that tells `cbmcfs3_runner` where the simulation data is located:

    $ SETX CBMCFS3_DATA "$HOME\repos\cbmcfs3_data"

Set the environment variable that tells `cbmcfs3_runner` where the special AIDBs are located:

    $ SETX AIDB_REPO "$HOME\repos\cbmcfs3_aidb"

## Symlink AIDBs

Create symlinks for these special files (requires administrator privileges):

    $ ipython -i -c "from cbmcfs3_runner.core.continent import continent as ct; print([c.aidb.symlink() for c in ct])"

# Run

Run a given country from the historical scenario:

    $ ipython
    from cbmcfs3_runner.core.continent import continent
    runner = continent[('historical', 'LU', 0)]
    runner.run(verbose=True)