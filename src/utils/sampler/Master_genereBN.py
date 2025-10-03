# -*- coding: utf-8 -*-
"""
Master_genereBN.py
==================
Master_genereBN class for generating and manipulating Bayesian Networks (BN) using the pyAgrum library.
This class provides methods to save, load, plot Bayesian Networks, and load data from CSV or Excel files. 
It also includes functionality for sampling from the Bayesian Network.
Methods:
    __init__(): Initializes the Master_genereBN object.
    Save_BN(pathfile): Saves the current Bayesian Network to the specified file path.
    Load_BN(pathfile): Loads a Bayesian Network from the specified file path.
    Plot_BN(): Plots the current Bayesian Network using the appropriate visualization library.
    Load_csv(stFileName, sep=','): Loads data from a CSV file into a DataFrame.
    Load_excel(stFileName, sheet_name=None): Loads data from an Excel file into a DataFrame.
    Gum_Sampling(number, Multiplicateur=1, evs={}): Generates samples from the Bayesian Network based on the specified number and multiplier.
    do_Sampling(numberOfSamples, evs={}): Performs sampling from the Bayesian Network, ensuring the specified number of samples is returned.
Attributes:
    bn: The Bayesian Network object.
    dfcsv: The DataFrame containing loaded data from CSV or Excel files.

This module defines the `Master_genereBN` class, which provides functionality for:
1. Loading and saving Bayesian Networks (BNs) using the `pyAgrum` library.
2. Visualizing Bayesian Networks.
3. Loading data from CSV and Excel files.
4. Performing sampling on Bayesian Networks.

Dependencies:
-------------
- pandas
- pyAgrum

Author:
-------
[cv1751 - Brice Le Lostec]

"""

import os
current_path = os.environ.get("PATH")
os.environ["PATH"] = current_path + ";C:\\Brice\\Graphviz2.38\\bin"


import pandas as pd

import pyagrum as gum
try:
    import pyagrum.lib.ipython as gnb
except:
    import pyagrum.lib.notebook as gnb


FILE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(FILE_DIR+ "/../")  # répertoire supérieur

class Master_genereBN(object):
    """
    Master_genereBN class
    A class to manage Bayesian Networks (BNs) using the pyAgrum library.

    This class provides methods to:
    - Save and load Bayesian Networks.
    - Visualize Bayesian Networks.
    - Load data from CSV and Excel files.
    - Perform sampling on Bayesian Networks.
    
    Methods:
    - __init__(): Initializes the Master_genereBN class.
    - Save_BN(pathfile: str) -> None: Saves the Bayesian Network to a specified file.
    - Load_BN(pathfile: str) -> None: Loads a Bayesian Network from a specified file.
    - Plot_BN() -> None: Visualizes the Bayesian Network.
    - Load_csv(stFileName: str, sep: str = ',') -> None: Loads data from a CSV file into a DataFrame.
    - Load_excel(stFileName: str, sheet_name: str = None) -> None: Loads data from an Excel file into a DataFrame.
    - Gum_Sampling(number: int, Multiplicateur: int = 1, evs: dict = {}) -> pd.DataFrame: Generates samples from the Bayesian Network.
    - do_Sampling(numberOfSamples: int, evs: dict = {}) -> pd.DataFrame: Performs sampling on the Bayesian Network and returns a DataFrame of samples.


    """
    def __init__(self):
        """
        Initialize the Master_genereBN class.
        """
        pass

    def Save_BN(self, pathfile):
        """
        Save the Bayesian Network to a file.

        Parameters:
        -----------
        pathfile : str
            The path to the file where the Bayesian Network will be saved.

        Returns:
        --------
        None
        """
        gum.saveBN(self.bn,pathfile)
        
    def Load_BN(self, pathfile):
        """
        Load a Bayesian Network from a file.

        Parameters:
        -----------
        pathfile : str
            The path to the file containing the Bayesian Network.

        Returns:
        --------
        None
        """
        self.bn = gum.loadBN(pathfile)

    def Plot_BN(self):
        """
        Plot_BN method to visualize the Bayesian Network (BN) inference.

        This method utilizes the gnb module to display the inference results of the 
        Bayesian Network stored in the instance variable `self.bn`. The inference is 
        shown with default evidence (empty dictionary) and a specified size for the 
        visualization.

        Parameters:
            None

        Returns:
            None
        """
        gnb.showInference(self.bn,evs={},size = '30')
        #gnb.showBN(self.bn,size='10')
    
    def Load_csv(self, stFileName, sep = ','):
        """
        Load a CSV file into a DataFrame.

        Parameters:
            stFileName (str): The path to the CSV file to be loaded.
            sep (str, optional): The delimiter to use for separating values. Defaults to ','.
            
        Returns:
            None: The method loads the CSV data into the instance variable `dfcsv`.
        """
        self.dfcsv = pd.read_csv(stFileName, sep = sep, dtype=str)
        
    def Load_excel(self, stFileName, sheet_name=None):
        """
        Load an Excel file into a pandas DataFrame.

        Parameters:
            stFileName (str): The path to the Excel file to be loaded.
            sheet_name (str, optional): The name of the sheet to load. If None, the first sheet is loaded.

        Returns:
            None: The loaded DataFrame is stored in the instance variable `dfcsv`.
        """
        self.dfcsv = pd.read_excel(stFileName, sheet_name=sheet_name)

    def Gum_Sampling(self, number, Multiplicateur = 1, evs={}):
        """
        Generates samples from a Bayesian network using the Gum library.

        Parameters:
            number (int): The base number of samples to generate.
            Multiplicateur (float, optional): A multiplier to adjust the number of samples. Default is 1.
            evs (dict, optional): A dictionary of evidence variables to condition the sampling on. Default is an empty dictionary.

        Returns:
            pandas.DataFrame: A DataFrame containing the generated samples.
        """
        g=gum.BNDatabaseGenerator(self.bn)
        g.setTopologicalVarOrder()#setRandomVarOrder()
        #g.setDiscretizedLabelModeRandom()
        if int(number * Multiplicateur) == 0:
            number = 1
        else:
            number = int(number * Multiplicateur)
        g.drawSamples(number, evs)
        return g.to_pandas()
    
    def do_Sampling(self, numberOfSamples, evs = {}):
        """
        Perform sampling to generate a specified number of samples.
        Parameters:
            numberOfSamples (int): The total number of samples to generate.
            evs (dict, optional): A dictionary of environmental variables to influence the sampling process. Defaults to an empty dictionary.
        Returns:
            pd.DataFrame: A DataFrame containing the sampled data, reset to a new index.
        Notes:
            The function first attempts to generate samples using the Gum_Sampling method. 
            If the initial sample size is insufficient, it continues to sample until the desired number of samples is reached.
        """

        dfSampling = pd.DataFrame()
        #{'ModeOccupation':'Proprietaire'}
        #numberOfSamples = 1000
        boSampling = False#not finish
        dfTemp = self.Gum_Sampling(numberOfSamples, 1, evs=evs)

        if len(dfTemp)>= numberOfSamples:
            dfSampling = dfTemp.sample(n=numberOfSamples, random_state=42)
            boSampling = True    
        else:
            dfSampling = pd.concat([dfSampling, dfTemp])
            numberOfSamples_restant = numberOfSamples - len(dfSampling)
            if len(dfSampling)>0:
                Fact = len(dfSampling)/numberOfSamples
            else:
                Fact = 5

        while not boSampling:
            dfTemp = self.Gum_Sampling(numberOfSamples_restant, min(1, max(5, Fact)), evs=evs)
            if len(dfTemp)>= numberOfSamples_restant:
                dfSampling = pd.concat([dfSampling, dfTemp.sample(numberOfSamples_restant, random_state=42)])
                boSampling = True

            else:
                dfSampling = pd.concat([dfSampling, dfTemp])
                numberOfSamples_restant = numberOfSamples - len(dfSampling)
        return dfSampling.reset_index(drop=True)

if __name__ == "__main__":
    # Example usage
    #run in interactive windows
    
    bnM = Master_genereBN()
    import pyagrum as gum
    import matplotlib
    matplotlib.use('TkAgg')


    bnM.bn = gum.BayesNet("WaterSprinkler")
    id_c = bnM.bn.add(gum.LabelizedVariable("c", "cloudy ?", 2))
    id_s, id_r, id_w = [
    bnM.bn.add(name, 2) for name in "srw"
    ]  # bn.add(name, 2) === bn.add(gum.LabelizedVariable(name, name, 2))

    bnM.bn.addArc("c", "s")
    for link in [(id_c, id_r), ("s", "w"), ("r", "w")]:
        bnM.bn.addArc(*link)
    bnM.bn.cpt("c").fillWith([0.4, 0.6])

    bnM.bn.cpt("s")[0, :] = 0.5  # equivalent to [0.5,0.5]
    bnM.bn.cpt("s")[1, :] = [0.9, 0.1]
    bnM.bn.cpt("w")[0, 0, :] = [1, 0]  # r=0,s=0
    bnM.bn.cpt("w")[0, 1, :] = [0.1, 0.9]  # r=0,s=1
    bnM.bn.cpt("w")[1, 0, :] = [0.1, 0.9]  # r=1,s=0
    bnM.bn.cpt("w")[1, 1, :] = [0.01, 0.99]  # r=1,s=1
    bnM.bn.cpt("r")[{"c": 0}] = [0.8, 0.2]
    bnM.bn.cpt("r")[{"c": 1}] = [0.2, 0.8]
    #bnM.bn

    #gnb.showInference(bnM.bn,evs={},size = '30')
    gnb.showBN(bnM.bn,size='10')
    #bnM.Plot_BN()
