# FIAT Model Builder GUI
This repository contains the FIAT Model Builder GUI, using the [Guitares](https://github.com/Deltares/guitares) GUI framework and [HydroMT-FIAT](https://github.com/Deltares/hydromt_fiat) as back-end.

# Contributing


## Setting up conda

In order to develop on the `FIAT Model Builder GUI` locally, please follow the following steps:

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
cd <location of your repository clone>\DelftDashboard\src\delftdashboard\env
mamba env create --file=ddb_fiat.yml --force
```

## Installing the FIAT Model Builder GUI

- Activate the environment

```
conda activate ddb_fiat
```

In order to develop on the `FIAT Model Builder GUI` locally, execute the following line inside your virtual environment

```bash
pip install -e .
```
