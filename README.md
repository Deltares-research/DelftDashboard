# FloodAdapt Model Builder GUI
This repository contains the FIAT Model Builder GUI, using the [Guitares](https://github.com/Deltares/guitares) GUI framework and [HydroMT-FIAT](https://github.com/Deltares/hydromt_fiat) as back-end.

# Contributing


## Setting up conda

In order to develop on the `FloodAdapt Model Builder GUI` locally, please follow the following steps:

- Download and install [mambaforge](https://mamba.readthedocs.io/en/latest/installation.html#fresh-install).

- Initialize `conda` by running the following in the `Miniconda prompt`:

```
conda init
```

- Depending on your company settings, you might also have to run the following in a Powershell terminal as administrator:

```
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned
```

## Creating (or updating) the environment

- Create (or update) the environment by executing the following in your terminal:

```
cd <location of your repository clone of DelftDashboard> 
mamba env create --file=./src/delftdashboard/env/ddb_FloodAdapt.yml --force
```

## Installing the FloodAdapt Model Builder GUI

- Activate the environment

```
conda activate ddb_FloodAdapt
```

To be able to run the GUI, you need to:
- create an account and generate a personal [mapbox_token.txt](https://www.mapbox.com/)
- generate a personal [census_key.txt] (https://api.census.gov/data/key_signup.html)
- Put 'mapbox_token.txt' and 'census_key.txt' in the same folder and make sure they are named correctly!
- have access to the dependecy repositories (try makeing the environment, will get errors if you dont have access)
- have access to P:\11207949-dhs-phaseii-floodadapt\Model-builder\Installation
Then, in order to develop on the `FloodAdapt Model Builder GUI` locally and have the GUI use your local versions of repositories, run the [install script](src/delftdashboard/install.py).

```
python ./src/delftdashboard/install.py
```