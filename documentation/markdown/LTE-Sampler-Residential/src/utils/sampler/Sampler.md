Module LTE-Sampler-Residential.src.utils.sampler.Sampler
========================================================
Sampler.py
==========

This module defines two classes:
1. **Sampler**: For generating Bayesian Networks (BN) using the `pyAgrum` library.
2. **BuildstockBatchArguments**: For handling housing characteristics and sampling.

Features:
---------
- Save, load, and plot Bayesian Networks.
- Load Bayesian Network structures from YAML files.
- Load housing characteristics from CSV files.
- Generate samples based on Bayesian Networks and housing characteristics.

Classes:
--------
- `Sampler`: Manages Bayesian Networks.
- `BuildstockBatchArguments`: Handles housing characteristics and sampling.

Dependencies:
-------------
- os
- sys
- yaml
- numpy
- pyAgrum

Author:
-------
Brice Le Lostec (cv1751)

Version:
--------
1.0

Python Version:
---------------
3.11

Created:
--------
26-06-2025

Classes
-------

`BuildstockBatchArguments()`
:   

    ### Methods

    `csv_to_dict(self, path='N:\\Mes Documents\\Projets LTE\\Projet archQc\\code\\GITHUB_Repo\\LTE-Sampler-Residential/data/processed/housing_characteristics/')`
    :   Convert a CSV file to a dictionary.
        
        :param path: Path to the CSV file.
        :return: Dictionary with column names as keys and lists of column values as values.

    `sampling(self, lst_dct_args={})`
    :   Generate a sample of Buildstock Bach arguments based on the provided evidence.
        
        :param evs: Dictionary containing evidence for the sampling.
        :return: dictionarie representing the sampled arguments.

`MapHPXML()`
:   

    ### Methods

    `doMapping(self, dct_args)`
    :

    `run(self, lst_dct_args)`
    :

`Sampler()`
:   Class qui permet d'utiliser réseau bayésien à partir des données EUEMr.
    
    Initialize the EUEMr class with an optional DataFrame.
    
    :param df: pandas DataFrame containing the data.

    ### Ancestors (in MRO)

    * src.utils.sampler.Master_genereBN.Master_genereBN

    ### Methods

    `getBNStructure(self, path='N:\\Mes Documents\\Projets LTE\\Projet archQc\\code\\GITHUB_Repo\\LTE-Sampler-Residential/data/processed/bayesian_network/Bn.yml')`
    :