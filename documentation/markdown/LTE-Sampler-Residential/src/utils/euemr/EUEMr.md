Module LTE-Sampler-Residential.src.utils.euemr.EUEMr
====================================================
Created on 26-06-2025

@author: cv1751 - Brice Le Lostec
@description: Class for generating Bayesian Networks (BN) using pyAgrum.
@note: This class provides methods to save, load, plot Bayesian Networks and load CSV files.
@version: 1.0
python 3.11

Classes
-------

`FormatageEUEMr()`
:   Classe pour transformet les données EUEMr en données pour le BN.

    ### Methods

    `Create_Pond(self, df_toPond_src)`
    :

    `DoAllMapping(self)`
    :   Applique tous les mappings définis dans la classe.

    `DoMapping(self, ColName)`
    :   Retourne le mapping pour la colonne donnée.

    `Load_excel(self, stFileName, sheet_name=None)`
    :

    `Main(self)`
    :   Fonction principale pour exécuter le formatage des données EUEMr.

    `SaveToCSV(self, dfEUEMr, stFileName)`
    :   Sauvegarde le DataFrame formaté en CSV.

    `get_Mapping_Colsrc(self, colName)`
    :

    `get_Mettadata(self)`
    :

    `set_Mapping(self)`
    :   Définit le mapping direct pour les colonnes du DataFrame EUEMr.