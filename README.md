# WEIS

[![Coverage Status](https://coveralls.io/repos/github/WISDEM/WEIS/badge.svg?branch=develop)](https://coveralls.io/github/WISDEM/WEIS?branch=develop)
[![Actions Status](https://github.com/WISDEM/WEIS/workflows/CI_WEIS/badge.svg?branch=develop)](https://github.com/WISDEM/WEIS/actions)
[![Documentation Status](https://readthedocs.org/projects/weis/badge/?version=develop)](https://weis.readthedocs.io/en/develop/?badge=develop)
[![DOI](https://zenodo.org/badge/289320573.svg)](https://zenodo.org/badge/latestdoi/289320573)

WEIS, Wind Energy with Integrated Servo-control, performs multifidelity co-design of wind turbines. WEIS is a framework that combines multiple NREL-developed tools to enable design optimization of floating offshore wind turbines.

Author: [NREL WISDEM & OpenFAST & Control Teams](mailto:systems.engineering@nrel.gov)

## Version

This software is a version 0.0.1.

## Documentation

See local documentation in the `docs`-directory or access the online version at <https://weis.readthedocs.io/en/latest/>

## Packages

WEIS integrates in a unique workflow four models:
* [WISDEM](https://github.com/WISDEM/WISDEM) is a set of models for assessing overall wind plant cost of energy (COE).
* [OpenFAST](https://github.com/OpenFAST/openfast) is the community model for wind turbine simulation to be developed and used by research laboratories, academia, and industry.
* [TurbSim](https://www.nrel.gov/docs/fy09osti/46198.pdf) is a stochastic, full-field, turbulent-wind simulator.
* [ROSCO](https://github.com/NREL/ROSCO) provides an open, modular and fully adaptable baseline wind turbine controller to the scientific community.

Software Model Versions:
Software        |       Version
---             |       ---
OpenFAST        |       3.5.0
ROSCO           |       develop ([05d7b3b](https://github.com/NREL/ROSCO/commit/05d7b3b948c12ad40892941b6f92f3b08f5c6894))
WISDEM          |       develop ([6f15fc9](https://github.com/WISDEM/WISDEM/commit/6f15fc9ed7f7fd1282d32af5518d2ae37dbc9466))

In addition, three external libraries are added:
* [pCrunch](https://github.com/NREL/pCrunch) is a collection of tools to ease the process of parsing large amounts of OpenFAST output data and conduct loads analysis.
* [pyOptSparse](https://github.com/mdolab/pyoptsparse) is a framework for formulating and efficiently solving nonlinear constrained optimization problems.



The core WEIS modules are:
 * _aeroelasticse_ is a wrapper to call [OpenFAST](https://github.com/OpenFAST/openfast)
 * _control_ contains the routines calling the [ROSCO_Toolbox](https://github.com/NREL/ROSCO_toolbox) and the routines supporting distributed aerodynamic control devices, such trailing edge flaps
 * _gluecode_ contains the scripts glueing together all models and libraries
 * _multifidelity_ contains the codes to run multifidelity design optimizations
 * _optimization_drivers_ contains various optimization drivers
 * _schema_ contains the YAML files and corresponding schemas representing the input files to WEIS

## Installation

On laptop and personal computers, installation with [Anaconda](https://www.anaconda.com) is the recommended approach because of the ability to create self-contained environments suitable for testing and analysis.  WEIS requires [Anaconda 64-bit](https://www.anaconda.com/distribution/). However, the `conda` command has begun to show its age and we now recommend the one-for-one replacement with the [Miniforge3 distribution](https://github.com/conda-forge/miniforge?tab=readme-ov-file#miniforge3), which is much more lightweight and more easily solves for the package dependencies. WEIS is currently supported on Linux, MAC and Windows Sub-system for Linux (WSL). Installing WEIS on native Windows is not yet supported, but planned in 2024.

The installation instructions below use the environment name, "weis-env," but any name is acceptable. For those working behind company firewalls, you may have to change the conda authentication with `conda config --set ssl_verify no`.  Proxy servers can also be set with `conda config --set proxy_servers.http http://id:pw@address:port` and `conda config --set proxy_servers.https https://id:pw@address:port`.

0.  On the DOE HPC system eagle, make sure to start from a clean setup and type

        module purge
        module load conda        

1.  Setup and activate the Anaconda environment from a prompt (WSL terminal on Windows or Terminal.app on Mac)

        conda config --add channels conda-forge
        conda env create --name weis-env -f https://raw.githubusercontent.com/WISDEM/WEIS/develop/environment.yml
        conda activate weis-env                          # (if this does not work, try source activate weis-env)
        sudo apt update                                  # (WSL only, assuming Ubuntu)

2.  Use conda to add platform specific dependencies.

        conda install -y petsc4py mpi4py                                     # (Mac / Linux only)   
        conda install -y compilers                                           # (Mac only)   
        sudo apt install gcc g++ gfortran libblas-dev liblapack-dev  -y      # (WSL only, assuming Ubuntu)

3. Clone the repository and install the software

        git clone https://github.com/WISDEM/WEIS.git
        cd WEIS
        git checkout branch_name                         # (Only if you want to switch branches, say "develop")
        python setup.py develop                          # (The common "pip install -e ." will not work here)

4. Instructions specific for DOE HPC system Eagle.  Before executing the setup script, do:

        module load comp-intel intel-mpi mkl
        module unload gcc
        python setup.py develop

**NOTE:** To use WEIS again after installation is complete, you will always need to activate the conda environment first with `conda activate weis-env` (or `source activate weis-env`). On Eagle, make sure to reload the necessary modules

## Developer guide

If you plan to contribute code to WEIS, please first consult the [developer guide](https://weis.readthedocs.io/en/latest/how_to_contribute_code.html).

## Feedback

For software issues please use <https://github.com/WISDEM/WEIS/issues>.  
