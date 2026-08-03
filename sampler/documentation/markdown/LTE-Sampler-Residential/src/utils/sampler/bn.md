Module LTE-Sampler-Residential.src.utils.sampler.bn
===================================================
Created on 26-06-2025

@author: cv1751 - Brice Le Lostec
@description: Class for generating Bayesian Networks (BN) using pyAgrum.
@note: This class provides methods to save, load, plot Bayesian Networks and load CSV files.
@version: 1.0
python 3.11

Classes
-------

`EUEMr()`
:   Class qui permet de générer un réseau bayésien à partir des données EUEMr.
    
    Initialize the EUEMr class with an optional DataFrame.
    
    :param df: pandas DataFrame containing the data.

    ### Ancestors (in MRO)

    * src.utils.sampler.bayesian_network.bayesian_network

    ### Class variables

    `LIST_Dict`
    :

    `MapEUEMr`
    :

    `NOEUD_EUEMr`
    :

    `dictMapEUEMr`
    :

    `fileEUEMr`
    :

    `key`
    :

    `lst_NOEUD`
    :

    ### Methods

    `Add_Node_Fromcsv(self, dct_housing_characteristics, listAttributs)`
    :

    `Make_BN(self)`
    :

    `Make_csv(self)`
    :