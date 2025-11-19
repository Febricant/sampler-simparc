# -*- coding: utf-8 -*-

import pyagrum as gum
from src.utils.sampler.utils import HConsignes
from src.utils.sampler.bayesian_network import bayesian_network
from pathlib import Path
import pandas as pd
import numpy as np
from src.utils.sampler.Mapping import BuildstockBatchArguments, MapHPXML

class Sampler():
    def __init__(self, bayesian_network_path):
        model = bayesian_network()
        model.Load_BN(bayesian_network_path)
        self.bn = model.bn
        self.lst_NOEUD, self.LIST_Dict = model.getBNStructure()
        self.randGenerator = np.random.default_rng(seed=0)


    def draw_GUM_Sample(self, number, Multiplicateur=1, evs={}):
        """
        Generates samples from a Bayesian network using the PyAgrum library.

        Parameters:
            number (int): The base number of samples to generate.
            Multiplicateur (float, optional): A multiplier to adjust the number of samples. Default is 1.
            evs (dict, optional): A dictionary of evidence variables to condition the sampling on. Default is an empty dictionary.

        Returns:
            pandas.DataFrame: A DataFrame containing the generated samples.
        """

        g = gum.BNDatabaseGenerator(self.bn)
        g.setTopologicalVarOrder()

        if int(number * Multiplicateur) == 0:
            number = 1
        else:
            number = int(number * Multiplicateur)
        g.drawSamples(number, evs)
        return g.to_pandas()

    def GUM_Sampling(self, numberOfSamples, evs={}):
        """
        Perform sampling to generate a specified number of samples.
        Parameters:
            numberOfSamples (int): The total number of samples to generate.
            evs (dict, optional): A dictionary of environmental variables to influence the sampling process. Defaults to an empty dictionary.
        Returns:
            pd.DataFrame: A DataFrame containing the sampled data, reset to a new index.
        Notes:
            The function first attempts to generate samples using the draw_GUM_Sample method.
            If the initial sample size is insufficient, it continues to sample until the desired number of samples is reached.
        """

        dfSampling = pd.DataFrame()
        boSampling = False  # boolean flag for sampling completion

        dfTemp = self.draw_GUM_Sample(numberOfSamples, 1, evs=evs)

        if len(dfTemp) >= numberOfSamples:
            dfSampling = dfTemp.sample(n=numberOfSamples, random_state=42)
            boSampling = True

        else:
            dfSampling = pd.concat([dfSampling, dfTemp])
            numberOfSamples_restant = numberOfSamples - len(dfSampling)
            if len(dfSampling) > 0:
                Fact = len(dfSampling) / numberOfSamples
            else:
                Fact = 5

        while not boSampling:
            dfTemp = self.draw_GUM_Sample(numberOfSamples_restant, min(1, max(5, Fact)), evs=evs)
            if len(dfTemp) >= numberOfSamples_restant:
                dfSampling = pd.concat([dfSampling, dfTemp.sample(numberOfSamples_restant, random_state=42)])
                boSampling = True

            else:
                dfSampling = pd.concat([dfSampling, dfTemp])
                numberOfSamples_restant = numberOfSamples - len(dfSampling)
        return dfSampling.reset_index(drop=True)


    
    def resstock_args_sampling(self, lst_dct_args={}):

        BBA = BuildstockBatchArguments()

        lst_dct_args2 = []
        for dctSampler in lst_dct_args:
            dct_args2 = {}
            for Attributs in BBA.listAttributs:
                #for csv file (ne charger qu'une fois) et creer une structure
                dct_dependancy = BBA.dct_housing_characteristics[Attributs]["Dependency"]
                dct_option = BBA.dct_housing_characteristics[Attributs]["Option"]
                df = BBA.dct_housing_characteristics[Attributs]["Table"]


                if len(dct_dependancy) == 0:
                    # If there are no dependencies, sample directly from the options
                    filtered_df = df
                else:
                    filter_dict = {key:{**dctSampler, **dct_args2}[value] for key, value in dct_dependancy.items()}
                    # Dynamic filtering based on the dictionary
                    
                    # Initialize a boolean index
                    filtered_index = pd.Series([True] * len(df), index=df.index)
                    # Loop through filters and update the index
                    for col, values in filter_dict.items():
                        if isinstance(values, list):
                            filtered_index = filtered_index & (df[col].isin(values))
                        else:
                            filtered_index = filtered_index & (df[col] == values)

                    # Apply the filtered index to the DataFrame
                    filtered_df = df[filtered_index]
                
                try:
                    sumlst = sum(filtered_df[dct_option.keys()].values.tolist()[0])
                    listProb = [k/sumlst for k in filtered_df[dct_option.keys()].values.tolist()[0]]
                except:
                    raise Exception("Error in sampling for attribute:" + Attributs)
                

                choiceStr = self.randGenerator.choice(list(dct_option.keys()),p=listProb) #TODO send to stochastic profile generator
                if "Option=" in str(choiceStr):
                    dct_args2[Attributs] = choiceStr.split("Option=")[-1]
                    if Attributs in ["Geometry Stories",
                                     "Geometry Building Number Units"]:
                        dct_args2[Attributs] = int(dct_args2[Attributs])
            

                #ajout des Heures de changement de température (h1 à h4)
                h1, h2, h3, h4= HConsignes()
                dct_args2["Tconsignes_chauffage_H1"] = h1
                dct_args2["Tconsignes_chauffage_H2"] = h2
                dct_args2["Tconsignes_chauffage_H3"] = h3
                dct_args2["Tconsignes_chauffage_H4"] = h4

            lst_dct_args2.append(dct_args2)
        return lst_dct_args2


if __name__ == "__main__":
    # Load the Bayesian Network from the saved file
    file_path  = str(Path(__file__).parents[3] / "data/processed/bayesian_network/BN_EUEMr.XDSL")
    InsClsSampler = Sampler(file_path)
    Nombre_de_Samples = 100
    Evidence = {}

    # Fait un échantillonage - Avant enregistrement
    df1 = InsClsSampler.GUM_Sampling(Nombre_de_Samples, evs = Evidence)
    lst_dct_args = df1.to_dict(orient='records')

    #Ajout de varaible hors BN
    lst_dct_args2 = InsClsSampler.resstock_args_sampling(lst_dct_args)

    lst_dct_args = [ d2 | d1 for d1, d2 in zip(lst_dct_args, lst_dct_args2)]#lst_dct_args prioritaire

    MapSample = MapHPXML()
    lst_dct_HPXML = MapSample.run(lst_dct_args)
    
    print("Nombre d'attributs HPXML: ", len(lst_dct_HPXML[0].keys()))
    pd.DataFrame(lst_dct_HPXML)