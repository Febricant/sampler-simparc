Module LTE-Sampler-Residential.src.utils.sampler.bayesian_network
=================================================================
bayesian_network.py
==================
bayesian_network class for generating and manipulating Bayesian Networks (BN) using the pyAgrum library.
This class provides methods to save, load, plot Bayesian Networks, and load data from CSV or Excel files. 
It also includes functionality for sampling from the Bayesian Network.
Methods:
    __init__(): Initializes the bayesian_network object.
    Save_BN(pathfile): Saves the current Bayesian Network to the specified file path.
    Load_BN(pathfile): Loads a Bayesian Network from the specified file path.
    Plot_BN(): Plots the current Bayesian Network using the appropriate visualization library.
    Load_csv(stFileName, sep=','): Loads data from a CSV file into a DataFrame.
    Load_excel(stFileName, sheet_name=None): Loads data from an Excel file into a DataFrame.
    draw_GUM_Sample(number, Multiplicateur=1, evs={}): Generates samples from the Bayesian Network based on the specified number and multiplier.
    do_Sampling(numberOfSamples, evs={}): Performs sampling from the Bayesian Network, ensuring the specified number of samples is returned.
Attributes:
    bn: The Bayesian Network object.
    dfcsv: The DataFrame containing loaded data from CSV or Excel files.

This module defines the `bayesian_network` class, which provides functionality for:
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

Classes
-------

`bayesian_network()`
:   bayesian_network class
    A class to manage Bayesian Networks (BNs) using the pyAgrum library.
    
    This class provides methods to:
    - Save and load Bayesian Networks.
    - Visualize Bayesian Networks.
    - Load data from CSV and Excel files.
    - Perform sampling on Bayesian Networks.
    
    Methods:
    - __init__(): Initializes the bayesian_network class.
    - Save_BN(pathfile: str) -> None: Saves the Bayesian Network to a specified file.
    - Load_BN(pathfile: str) -> None: Loads a Bayesian Network from a specified file.
    - Plot_BN() -> None: Visualizes the Bayesian Network.
    - Load_csv(stFileName: str, sep: str = ',') -> None: Loads data from a CSV file into a DataFrame.
    - Load_excel(stFileName: str, sheet_name: str = None) -> None: Loads data from an Excel file into a DataFrame.
    -
    
    Initialize the bayesian_network class.

    ### Methods

    `Load_BN(self, pathfile)`
    :   Load a Bayesian Network from a file.
        
        Parameters:
        -----------
        pathfile : str
            The path to the file containing the Bayesian Network.
        
        Returns:
        --------
        None

    `Load_csv(self, stFileName, sep=',')`
    :   Load a CSV file into a DataFrame.
        
        Parameters:
            stFileName (str): The path to the CSV file to be loaded.
            sep (str, optional): The delimiter to use for separating values. Defaults to ','.
            
        Returns:
            None: The method loads the CSV data into the instance variable `dfcsv`.

    `Load_excel(self, stFileName, sheet_name=None)`
    :   Load an Excel file into a pandas DataFrame.
        
        Parameters:
            stFileName (str): The path to the Excel file to be loaded.
            sheet_name (str, optional): The name of the sheet to load. If None, the first sheet is loaded.
        
        Returns:
            None: The loaded DataFrame is stored in the instance variable `dfcsv`.

    `Plot_BN(self)`
    :   Plot_BN method to visualize the Bayesian Network (BN) inference.
        
        This method utilizes the gnb module to display the inference results of the 
        Bayesian Network stored in the instance variable `self.bn`. The inference is 
        shown with default evidence (empty dictionary) and a specified size for the 
        visualization.
        
        Parameters:
            None
        
        Returns:
            None

    `Save_BN(self, pathfile)`
    :   Save the Bayesian Network to a file.
        
        Parameters:
        -----------
        pathfile : str
            The path to the file where the Bayesian Network will be saved.
        
        Returns:
        --------
        None

    `getBNStructure(self)`
    :