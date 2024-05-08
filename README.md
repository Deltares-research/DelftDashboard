# FloodAdapt Model Builder GUI
This repository contains the FloodAdapt Model Builder GUI, using the [Guitares](https://github.com/Deltares/guitares) GUI framework as frontend, and [HydroMT-SFINCS](https://github.com/Deltares/hydromt_sfincs) and [HydroMT-FIAT](https://github.com/Deltares/hydromt_fiat) as back-ends.

# Contributing


## Installation Guide

In order to develop on the `FloodAdapt Model Builder GUI` locally, please follow the following steps:

- Download and install [mambaforge](https://mamba.readthedocs.io/en/latest/installation.html#fresh-install). `mambaforge` is not mandatory, but is reccomended as it is designed to be faster and more efficient than `(mini)conda`, when dealing with large environments.

- Initialize `conda` by running the following in the `Miniconda prompt`:

```
conda init
```

- Make sure you have `git` installed and added to your system's `PATH` environment variable. You can download a Windows installer [here](https://gitforwindows.org/).

## Windows
- If you are running on a different operating system, continue to creating environment.

- Depending on your company settings, you might also have to run the following in a Powershell terminal as administrator:

```
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned
```

- Older versions of windows need to run the following commands in a Powershell terminal with administrator rights (More information on why: [Windows](https://learn.microsoft.com/en-us/windows/win32/fileio/maximum-file-path-limitation?tabs=registry#enable-long-paths-in-windows-10-version-1607-and-later), [git](https://stackoverflow.com/questions/22575662/filename-too-long-in-git-for-windows)):

```
New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1- PropertyType DWORD -Force
git config --global core.longpaths true
```

## Creating (or updating) the environment

- Create (or update) the environment by executing the following in your terminal:

```
cd <location of your repository clone of DelftDashboard>
mamba env create --file=./src/delftdashboard/env/ddb_floodadapt.yml --force
```

## Installing the FloodAdapt Model Builder GUI

- Activate the environment

```
conda activate ddb_floodadapt
```

To be able to run the `FloodAdapt Model Builder GUI`, you need to:
- Create an account and generate a personal [token](https://www.mapbox.com/), view all your tokens [here](https://account.mapbox.com/access-tokens)
- Create a new folder somewhere (for example `<userFiles>`)
- Copy the token to a file, name it `mapbox_token.txt`, and paste the file in `<userFiles>`
- Request a personal [census_key token](https://api.census.gov/data/key_signup.html) by entering your company name and email adress
- Copy the token to a file, name it `census_key.txt`, and paste the file in `<userFiles>`
- Be a `contributor` on all the dependency repositories
- Be a `member` of the `deltares` and `deltares-research` GitHub organisations
- If you are working remotely, activate your Deltares VPN
- Have access rights to `P:\11207949-dhs-phaseii-floodadapt`, contact [Kathryn Roscoe](kathryn.roscoe@deltares.nl) if you do not have it.

Then, in order to develop on the `FloodAdapt Model Builder GUI` locally and have the GUI use your local versions of repositories, run the [install script](src/delftdashboard/install.py).

```
python ./src/delftdashboard/install.py
```

## Running the FloodAdapt Model Builder GUI
If you have followed all the steps above, you can start the gui by running the following in a terminal:

```
conda activate ddb_floodadapt
cd <location of your repository clone of DelftDashboard>
python ./src/delftdashboard/delftdashboard_gui.py
```