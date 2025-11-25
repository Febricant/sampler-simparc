# -*- coding: utf-8 -*-

import pyagrum as gum
from src.utils.sampler.utils import HConsignes
from src.utils.sampler.bayesian_network import bayesian_network
from pathlib import Path
import pandas as pd
import numpy as np
import time
from datetime import date
from datetime import timedelta
from src.utils.sampler.Mapping import BuildstockBatchArguments, MapHPXML
import argparse, os

class Sampler():
    LOGO = "   _____ _           ____                       _____                       __\n"\
           "  / ___/(_)___ ___  / __ \____ ___________     / ___/____ _____ ___  ____  / /__  _____\n"\
           "  \__ \/ / __ `__ \/ /_/ / __ `/ ___/ ___/     \__ \/ __ `/ __ `__ \/ __ \/ / _ \/ ___/\n"\
           " ___/ / / / / / / / ____/ /_/ / /  / /__      ___/ / /_/ / / / / / / /_/ / /  __/ /    \n"\
           "/____/_/_/ /_/ /_/_/    \__,_/_/   \___/     /____/\__,_/_/ /_/ /_/ .___/_/\___/_/     \n"\
           "                                                                 /_/                   "
    def __init__(self, bayesian_network_path):
        model = bayesian_network()
        model.Load_BN(bayesian_network_path)
        self.bn_filename = Path(bayesian_network_path).name
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

    def run(self, Nombre_de_Samples):
        start_time = time.perf_counter()
        print(self.LOGO)
        print("------------------------------------------------------")
        print("Sampling {} with {} target samples".format(self.bn_filename, Nombre_de_Samples))

        # Load the Bayesian Network from file
        Evidence = {}

        # Fait un échantillonage - Avant enregistrement
        df = self.GUM_Sampling(Nombre_de_Samples, evs=Evidence)
        lst_dct_args = df.to_dict(orient='records')

        # Ajout des variables hors BN
        lst_dct_args2 = self.resstock_args_sampling(lst_dct_args)
        self.lst_dct_args = [d2 | d1 for d1, d2 in zip(lst_dct_args, lst_dct_args2)]  # lst_dct_args prioritaire


        # Mapping vers HPXML
        self.lst_dct_HPXML = MapHPXML().run(self.lst_dct_args)

        duration = timedelta(seconds=time.perf_counter() - start_time)
        print("Sampling Terminé ! - Nombre d'attributs HPXML: {}\nDurée Sampling : {}".format(
            len(self.lst_dct_HPXML[0].keys()), duration))
        print("------------------------------------------------------\n")
        self.sample_number = Nombre_de_Samples
        return self

    def to_df(self):
        dfargs = pd.DataFrame(self.lst_dct_args)
        dfHPXML = pd.DataFrame(self.lst_dct_HPXML)
        dfAll = pd.concat([dfargs, dfHPXML], axis=1)
        return dfAll

    def to_csv(self,output_dir):
        dfAll = self.to_df()
        today = date.today()
        dfAll.to_csv(os.path.join(output_dir, str(self.sample_number)+"_sample_buildings_{}.csv".format(today.isoformat())), index=False)

def main():
    parser = argparse.ArgumentParser(description="Bayesian network sampler for SimParc")
    parser.add_argument("bayesian_network_filepath", type=str, help="Path to the Bayesian network file. (.XDSL)")
    parser.add_argument("samples_number", type=int, help="Number of samples to generate. (Integer)")
    parser.add_argument("output_file_dir",type=str,help="Directory for outputfile. Default: current work directory.",default=os.getcwd(),)
    args = parser.parse_args()
    file_path = args.bayesian_network_filepath
    Sampler(file_path).run(args.samples_number).to_csv(args.output_file_dir)
    return 0

if __name__ == "__main__":
    main()