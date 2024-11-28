**REMARK!! This is an outdated version of the project repository and has been archived. Refer to https://github.com/open-energy-transition/form-energy-storage for the updated project PyPSA-Eur fork** 
# The Role of Energy Storage in Germany
This repository offers a reproducible workflow for the analysis of the role of short-, medium- and long-duration energy storages in Germany 2035.

## Cloning the repository

The repository is structured to contain the OET fork of the PyPSA-Eur model. 

There are two ways to clone the repository (1) Recursive cloning of the repository including the submodules or (2) Cloning the main and submodules independently

(1) To recursively clone the modules, the flag `--recurse-submodules` is to be used along with the `git clone` command. The repository can be cloned either using the ssh / http clone commands

    git clone --recurse-submodules git@github.com:open-energy-transition/form-energy-storage.git

OR 

    git clone --recurse-submodules https://github.com/open-energy-transition/form-energy-storage.git

(2) To independently clone the modules,

Firstly, the repository is cloned using the `git clone` command. The modules can be cloned either using the ssh / http clone commands

    git clone git@github.com:open-energy-transition/form-energy-storage.git
OR 

    git clone https://github.com/open-energy-transition/form-energy-storage.git

and then using the `git submodule` command:

    git submodule update --init --recursive

The new commits of the submodule can be fetched and updated using the command:

    git submodule update --remote
