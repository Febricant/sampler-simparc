# -*- coding: utf-8 -*-
"""
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

"""
import os
import sys
import yaml
import numpy as np
import pandas as pd
import random
FILE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(FILE_DIR+ "/../" +"/../" + "/../")  # répertoire supérieur
#PACKAGE_DIR = os.path.abspath(PROJECT_DIR+ "/../")
sys.path.append(os.path.join(PROJECT_DIR))

from src.utils.sampler.Master_genereBN import Master_genereBN
from src.utils.hpxml.HPXMLArg import HPXMLArguments

def HConsignes():
    """
        Initialise les paramètres aléatoires pour le setback et les variations horaires.
        Méthode permettant de déterminer les paramètres aléatoires liés au chauffage & à la climatisation.
            1 - self.dev1 : heure setback AM montee température
            2 - self.dev2 : heure setback AM descente température
            3 - self.dev3 : heure setback PM montee température
            4 - self.dev4 : heure setback PM descente température
                           ___TM____              ___TS____                  
                          |         |            |         |                 
              0h___TN___h1|       h2|____TJ____h3|       h4|___TN_____24h    
                

            Nuit (temperature)
                           __TM_________TJ___________TS____                  
                          |                                |
              0h___TN __h1|       h2           h3        h4|___TN______24h   

    """

    # Variations horaires aléatoires
    dev1 = random.uniform(-3, 3)#randnb(3)
    dev2 = random.uniform(-3, 3)
    dev3 = random.uniform(-3, 3)
    dev4 = random.uniform(-3, 3)
    dev5 = random.uniform(-1, 1)
    dev6 = random.uniform(-1, 1)
    
    # Calcul des heures de changement de consigne
    h1 = 6 + 6/60 + (dev1 * 0.75 - dev2 * 0.25)
    h2 = 8 + (dev1 * 0.75 + dev2 * 0.25)
    h3 = 16 + 20/60 + (dev3 * 0.5 - dev4 * 0.5)
    h4 = min(22 + 17/60 + (dev3 * 0.5 + dev4 * 0.5), 23 + 59/60)
    return [h1, h2, h3, h4]


class Sampler(Master_genereBN):
    '''
    Class qui permet d'utiliser réseau bayésien à partir des données EUEMr.
    '''
   
    def __init__(self):
        """
        Initialize the EUEMr class with an optional DataFrame.
        
        :param df: pandas DataFrame containing the data.
        """
        self.lst_NOEUD, self.LIST_Dict = self.getBNStructure()

    def getBNStructure(self, path=PROJECT_DIR+"/data/processed/bayesian_network/Bn.yml",):
        with open(path, 'r') as file:
            lst_NOEUD, LIST_Dict, dict_info = yaml.safe_load(file)
        return lst_NOEUD, LIST_Dict

class BuildstockBatchArguments():
    def __init__(self):
        self.randGenerator = np.random.default_rng(seed=0)
        self.dct_housing_characteristics = self.csv_to_dict()

    def csv_to_dict(self, path = PROJECT_DIR+"/data/processed/housing_characteristics/"):
        """
        Convert a CSV file to a dictionary.
        
        :param path: Path to the CSV file.
        :return: Dictionary with column names as keys and lists of column values as values.
        """
        #dct_name = {"Geometry Stories.csv": "Geometry Stories",
        #            "Geometry Building Number Units.csv": "Geometry Building Number Units",
        #            "Geometry Building Horizontal Location.csv": "Geometry Building Horizontal Location",
        #            "Geometry Building Level.csv" : "Geometry Building Level",
        #            "Infiltration.csv" : "Infiltration",
        #            "Windows.csv" : "Windows",
        #            "Insulation Wall.csv" : "Insulation Wall",
        #            "Insulation Ceiling.csv" : "Insulation Ceiling",
        #            "Insulation Foundation Wall.csv": "Insulation Foundation Wall",
        #            "Geometry Wall Exterior Finish.csv" : "Geometry Wall Exterior Finish",
        #            "Geometry Attic Type.csv": "geometry attic type",
        #            "HVAC Has Shared System.csv": "HVAC Has Shared System",
        #            "HVAC Heating Efficiency.csv": "HVAC Heating Efficiency"}
        dct_housing_characteristics_csv= {}
        dct_housing_characteristics_csv["Geometry Stories.csv"] = {"Name": "Geometry Stories",
                                                   "Description": "Geometry Stories",
                                                   "Source":""}
        dct_housing_characteristics_csv["Geometry Building Number Units.csv"] = {"Name": "Geometry Building Number Units",
                                                   "Description": "Nombre d'unité d'habitation",
                                                   "Source":""}
        dct_housing_characteristics_csv["Geometry Building Horizontal Location.csv"] = {"Name": "Geometry Building Horizontal Location",
                                                   "Description": "Position horizontale de l'habitation",
                                                   "Source":""}
        dct_housing_characteristics_csv["Geometry Building Level.csv"] = {"Name": "Geometry Building Level",
                                                    "Description": "Position verticale de l'habitation",
                                                    "Source":""}
        dct_housing_characteristics_csv["Infiltration.csv"] = {"Name": "Infiltration",
                                                    "Description": "Taux d'infiltration d'air",
                                                    "Source":""}
        dct_housing_characteristics_csv["Windows.csv"] = {"Name": "Windows",
                                                    "Description": "Type de fenêtre",
                                                    "Source":""}
        dct_housing_characteristics_csv["Insulation Wall.csv"] = {"Name": "Insulation Wall",
                                                    "Description": "Type d'isolation des murs",
                                                    "Source":""}
        dct_housing_characteristics_csv["Insulation Ceiling.csv"] = {"Name": "Insulation Ceiling",
                                                    "Description": "Type d'isolation du plafond",
                                                    "Source":""}
        dct_housing_characteristics_csv["Insulation Foundation Wall.csv"] = {"Name": "Insulation Foundation Wall",
                                                    "Description": "Type d'isolation du mur de fondation",
                                                    "Source":""}
        dct_housing_characteristics_csv["Geometry Wall Exterior Finish.csv"] = {"Name": "Geometry Wall Exterior Finish",
                                                    "Description": "Type de revêtement extérieur des murs",
                                                    "Source":""}
        dct_housing_characteristics_csv["Geometry Attic Type.csv"] = {"Name": "geometry attic type",
                                                    "Description": "Type de grenier",
                                                    "Source":""}
        dct_housing_characteristics_csv["HVAC Has Shared System.csv"] = {"Name": "HVAC Has Shared System",
                                                    "Description": "Système de chauffage partagé",
                                                    "Source":""}
        dct_housing_characteristics_csv["HVAC Heating Efficiency.csv"] = {"Name": "HVAC Heating Efficiency",
                                                    "Description": "Efficacité du système de chauffage",
                                                    "Source":""}
        dct_housing_characteristics_csv["Spa ChaufType.csv"] = {"Name": "Spa ChaufType",
                                                    "Description": "Type de chauffage du spa",
                                                    "Source":""}
        dct_housing_characteristics_csv["Usage Level.csv"] = {"Name": "Usage Level",
                                                    "Description": "Usage of major appliances relative to the USA average.",
                                                    "Source":"ResStock"}
        dct_housing_characteristics_csv["Cooking Range Usage Level.csv"] = {"Name": "Cooking Range Usage Level",
                                                    "Description": "Cooking Range energy usage level multiplier.",
                                                    "Source":"ResStock"}
        dct_housing_characteristics_csv["Clothes Washer Usage Level.csv"] = {"Name": "Clothes Washer Usage Level",
                                                    "Description": "Clothes Washer energy usage level multiplier.",
                                                    "Source":"ResStock"}
        dct_housing_characteristics_csv["Clothes Dryer Usage Level.csv"] = {"Name": "Clothes Dryer Usage Level",
                                                    "Description": "Clothes Dryer energy usage level multiplier.",
                                                    "Source":"ResStock"}
        dct_housing_characteristics_csv["Refrigerator Efficiency.csv"] = {"Name": "Refrigerator Efficiency",
                                                    "Description": "Rated efficiency of the primary refrigerator.",
                                                    "Source":"ResStock"}
        dct_housing_characteristics_csv["Freezer Efficiency.csv"] = {"Name": "Freezer Efficiency",
                                                    "Description": "Rated efficiency of the primary freezer.",
                                                    "Source":"ResStock"}
        dct_housing_characteristics_csv["Refrigerator Extra Efficiency.csv"] = {"Name": "Refrigerator Extra Efficiency",
                                                    "Description": "Rated efficiency of the extra refrigerator.",
                                                    "Source":"ResStock"}
        dct_housing_characteristics_csv["Refrigerator Usage Level.csv"] = {"Name": "Refrigerator Usage Level",
                                                    "Description": "Refrigerator energy usage level multiplier.",
                                                    "Source":"ResStock"}
        dct_housing_characteristics_csv["Dishwasher Energy.csv"] = {"Name": "Dishwasher Energy",
                                                    "Description": "Dishwasher energy.",
                                                    "Source":"ResStock"}
        dct_housing_characteristics_csv["Diswasher Usage Level.csv"] = {"Name": "Diswasher Usage Level",
                                                    "Description": "Dishwasher energy usage level multiplier.",
                                                    "Source":"ResStock"}
        dct_housing_characteristics_csv["Lighting Usage Level.csv"] = {"Name": "Lighting Usage Level",
                                                    "Description": "Lighting usage level multiplier. Only 100%",
                                                    "Source":"ResStock"}        
        dct_housing_characteristics_csv["Door Area.csv"] = {"Name": "Door Area",
                                                    "Description": "Door Area",
                                                    "Source":"ResStock"} 
        dct_housing_characteristics_csv["Door Rvalue.csv"] = {"Name": "Door Rvalue",
                                            "Description": "Door Rvalue",
                                            "Source":"ResStock"} 
        dct_housing_characteristics_csv["Geometry Foundation Type.csv"] = {"Name": "Geometry Foundation Type",
                                                    "Description": "Type de fondation géométrique",
                                                    "Source":"ResStock"}
        dct_housing_characteristics_csv["Insulation Floor.csv"] = {"Name": "Insulation Floor",
                                            "Description": "Type d'isolation du plancher",
                                            "Source":""}
        dct_housing_characteristics_csv["Plug Load.csv"] = {"Name": "Plug Load",
                                            "Description": "Charge électrique des appareils aux prises",
                                            "Source":""}                         
        dct_housing_characteristics_csv["Heating Setpoint.csv"] = {"Name": "Heating Setpoint",
                                            "Description": "Consigne de chauffage",
                                            "Source":"Sondage Sensibilisation intégrée"}

        dct_housing_characteristics_csv["Garage Heating Setpoint.csv"] = {"Name": "Garage Heating Setpoint",
                                            "Description": "Consigne de chauffage du garage",
                                            "Source":"Sondage Sensibilisation intégrée"}
        dct_housing_characteristics_csv["Cooling Setpoint.csv"] = {"Name": "Cooling Setpoint",
                                            "Description": "Consigne de climatisation",
                                            "Source":"Sondage Sensibilisation intégrée"}
        dct_housing_characteristics_csv["Basement Heating Setpoint.csv"] = {"Name": "Basement Heating Setpoint",
                                            "Description": "Consigne de chauffage du sous-sol",
                                            "Source":"Sondage Sensibilisation intégrée"}

        #dct_housing_characteristics_csv["Water Heater in Unit.csv"] = {"Name": "Water Heater in Unit",
        #                                            "Description": "Chauffeau dans le logement",
        #                                            "Source":""}
        #dct_housing_characteristics_csv["Water Heater Location.csv"] = {"Name": "Water Heater Location",
        #                                            "Description": "Position du chauffe-eau dans le logement",
        #                                            "Source":""}
        
        

        dct_housing_characteristics = {}
        for file in dct_housing_characteristics_csv.keys():
            if (file in os.listdir(path)):
                pathcsv = os.path.join(path, file)
                name = dct_housing_characteristics_csv[file]["Name"]#file.split(".")[0]
                dct_housing_characteristics[name] = {}
                dct_housing_characteristics[name]["Description"] = dct_housing_characteristics_csv[file]["Description"]
                dct_housing_characteristics[name]["Source"] = dct_housing_characteristics_csv[file]["Source"]
                dct_housing_characteristics[name]["Table"] = pd.read_csv(pathcsv, sep=";")
                dct_housing_characteristics[name]["Dependency"] = {c: c.split("Dependency=")[-1] for c in dct_housing_characteristics[name]["Table"].columns if "Dependency=" in c}
                dct_housing_characteristics[name]["Option"] = {c: c.split("Option=")[-1] for c in dct_housing_characteristics[name]["Table"].columns if "Option=" in c}
        
        return dct_housing_characteristics
    
    def sampling(self, lst_dct_args={}):
        """
        Generate a sample of Buildstock Bach arguments based on the provided evidence.
        
        :param evs: Dictionary containing evidence for the sampling.
        :return: dictionarie representing the sampled arguments.
        """
        # Implement the sampling logic here
        listAttributs = ["Geometry Stories",
                         "Geometry Building Number Units",
                         "Geometry Building Horizontal Location",
                         "Geometry Building Level",
                         "Geometry Foundation Type",
                         #"Infiltration",#Dans le BN
                        "Windows",
                        "Insulation Wall",
                        "Insulation Ceiling",
                        "Insulation Foundation Wall",
                        "Insulation Floor",
                        "Geometry Wall Exterior Finish",
                        "geometry attic type",
                        "HVAC Has Shared System",
                        "HVAC Heating Efficiency",
                        "Spa ChaufType",
                        "Usage Level",
                        "Cooking Range Usage Level",
                        "Clothes Washer Usage Level",
                        "Clothes Dryer Usage Level",
                        "Refrigerator Efficiency",
                        "Refrigerator Extra Efficiency",
                        "Refrigerator Usage Level",
                        "Freezer Efficiency",
                        "Dishwasher Energy",
                        "Diswasher Usage Level",
                        "Lighting Usage Level",
                        "Door Area",
                        "Door Rvalue",
                        "Plug Load",
                        "Heating Setpoint",
                        "Cooling Setpoint",
                        "Garage Heating Setpoint",
                        "Basement Heating Setpoint"]
                        
                        #"Geometry Attic Type",
                        # "Geometry Building Horizontal Location MF",
                        # "Geometry Building Horizontal Location SFA",
                        # "Geometry Building Level MF",
                        # "Geometry Building Number Units MF",
                        # "Geometry Building Number Units SFA",
                        # "Geometry Building Type ACS",
                        # "Geometry Building Type Height",
                        # "Geometry Building Type RECS",
                        # "Geometry Floor Area Bin",
                        # "Geometry Floor Area",
                        # "Geometry Foundation Type", # FAIT "PRESENCESOUSOL"
                        # "Geometry Garage",
                        # "Geometry Space Combination",
                        # "Geometry Stories Low Rise",
                        # "Geometry Stories",
                        # "Geometry Story Bin",
                        # "Geometry Wall Exterior Finish",
                        # "Geometry Wall Type"]
        lst_dct_args2 = []
        for dctSampler in lst_dct_args:
            dct_args2 = {}
            for Attributs in listAttributs:
                #for csv file (ne charger qu'une fois) et creer une structure
                dct_dependancy = self.dct_housing_characteristics[Attributs]["Dependency"]
                dct_option = self.dct_housing_characteristics[Attributs]["Option"]
                df = self.dct_housing_characteristics[Attributs]["Table"]


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

                    #filtered_df = df[
                    #    df[list(filter_dict.keys())].isin(filter_dict.values()).all(axis=1)
                    #]
                
                try:
                    sumlst = sum(filtered_df[dct_option.keys()].values.tolist()[0])
                    listProb = [k/sumlst for k in filtered_df[dct_option.keys()].values.tolist()[0]]
                except:
                    raise Exception("Error in sampling for attribute:" + Attributs)
                

                choiceStr = self.randGenerator.choice(list(dct_option.keys()),p=listProb)
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

class MapHPXML:
    def __init__(self):
        self.HPXMLArg = HPXMLArguments()
    #def Parse_HPXML(self, path="./ParseHQXMLinputs/measure.xml"):
    #    self.ListDictArgs = parse_xml_file(path)
    #def Parse_REsStockXML(self, path = "./ParseHQXMLinputs/ResStockArgument.xml"):
    #    self.ListDictArgs = parse_xml_file(path)
    
    def doMapping(self, dct_args):

        #Initialisation avec les valeurs à ne pas parser
        dct_HPXML = {k: dct_args[k] for k in dct_args.keys() if k in self.HPXMLArg.arguments.keys()} 
        
        #_______________________________________________________________
        #weather_station_epw_filepath
        #Type de Logement
        arg = "Territoire_HQ"
        argHPXML = "weather_station_epw_filepath"
        if (argHPXML not in dct_HPXML.keys()):
            if (arg in dct_args.keys()):
                if dct_args[arg] in ["Est et Nord du Québec"]:
                    dct_HPXML[argHPXML] = "2020s_CAN_QC_Saguenay-Bagotville.AP-CFB.Bagotville.717270_CWEC2016.epw"
                elif dct_args[arg] == "Laurentides":
                    dct_HPXML[argHPXML] = "2020s_CAN_QC_Montreal-McTavish.716120_CWEC2016.epw"
                elif dct_args[arg] == "Montmorency":
                    dct_HPXML[argHPXML] = "2020s_CAN_QC_Quebec-Lesage.Intl.AP.717140_CWEC2016.epw"
                    #dct_HPXML[argHPXML] = 'manufactured home' never create
                elif dct_args[arg] == "Montréal":
                    dct_HPXML[argHPXML] = "2020s_CAN_QC_Montreal-McTavish.716120_CWEC2016.epw"
                elif dct_args[arg] == "Richelieu":
                    dct_HPXML[argHPXML] = "2020s_CAN_QC_Montreal-McTavish.716120_CWEC2016.epw"
            else:
                if self.HPXMLArg.arguments[argHPXML].get("Default Value", "Defaut_Not_Existing")!="Defaut_Not_Existing":
                    dct_HPXML[argHPXML] = self.HPXMLArg.arguments[argHPXML].get("Default Value")
                else:
                    dct_HPXML[argHPXML] = "2020s_CAN_QC_Montreal-McTavish.716120_CWEC2016.epw"

        #simulation_control_daylight_saving_enabled
        argHPXML = "simulation_control_daylight_saving_enabled"
        if (argHPXML not in dct_HPXML.keys()):
            dct_HPXML[argHPXML] = True
        
        #site_time_zone_utc_offset
        argHPXML = "site_time_zone_utc_offset"
        if (argHPXML not in dct_HPXML.keys()):
            dct_HPXML[argHPXML] = True
        dct_HPXML[argHPXML]=-5

        #________________________________________________________________
        #Type de Logement
        arg = "Geometry Building Number Units"
        argHPXML = "geometry_building_num_units"
        if (argHPXML not in dct_HPXML.keys()):
            if (arg in dct_args.keys()):
                dct_HPXML[argHPXML] = dct_args[arg]
        #________________________________________________________________
        #Type de Logement
        arg = "Type_Logement"
        argHPXML = "geometry_unit_type"
        if (argHPXML not in dct_HPXML.keys()):
            if (arg in dct_args.keys()):
                if dct_args[arg] in ["Collective", "Triplex", "Duplex"]:
                    dct_HPXML[argHPXML] = 'apartment unit'

                elif dct_args[arg] == "Maison individuelle":
                    dct_HPXML[argHPXML] = 'single-family detached'

                elif dct_args[arg] == "Maison en rangee":
                    dct_HPXML[argHPXML] = 'single-family attached'
                    #dct_HPXML[argHPXML] = 'manufactured home' never create
            else:
                if self.HPXMLArg.arguments[argHPXML].get("Default Value", "Defaut_Not_Existing")!="Defaut_Not_Existing":
                    dct_HPXML[argHPXML] = self.HPXMLArg.arguments[argHPXML].get("Default Value")
                else:
                    dct_HPXML[argHPXML] = 'single-family detached'

        
        #geometry_average_ceiling_height
        argHPXML = "geometry_average_ceiling_height"
        if (argHPXML not in dct_HPXML.keys()):
            #if self.HPXMLArg.arguments[argHPXML].get("Default Value", "Defaut_Not_Existing")!="Defaut_Not_Existing":
            #        dct_HPXML[argHPXML] = self.HPXMLArg.arguments[argHPXML].get("Default Value")
            #else:
            dct_HPXML[argHPXML] = 8

        #geometry_unit_aspect_ratio
        argHPXML = "geometry_unit_aspect_ratio"
        if (argHPXML not in dct_HPXML.keys()):
            if dct_HPXML.get("geometry_unit_type") =="single-family detached":
                dct_HPXML[argHPXML]=1.8
            elif dct_HPXML.get("geometry_unit_type") =="apartment unit":
                dct_HPXML[argHPXML]=0.5556
            elif dct_HPXML.get("geometry_unit_type") =="single-family attached":
                dct_HPXML[argHPXML]=0.5556
            else:
                if self.HPXMLArg.arguments[argHPXML].get("Default Value", "Defaut_Not_Existing")!="Defaut_Not_Existing":
                    dct_HPXML[argHPXML] = self.HPXMLArg.arguments[argHPXML].get("Default Value")
                else:
                    dct_HPXML[argHPXML]=1.8
        #________________________________________________________________

        arg = "Superficie_Totale"
        argHPXML = "geometry_unit_cfa"
        if (argHPXML not in dct_HPXML.keys()):
            if arg in dct_args.keys():
                match dct_args[arg]:
                    case "[1 - 500)":
                        if dct_args["Type_Logement"] in ["Maison individuelle"]:
                            dct_HPXML[argHPXML] = 298
                        elif dct_args["Type_Logement"] in ["Maison en rangee"]:
                            dct_HPXML[argHPXML] = 273
                        elif dct_args["Type_Logement"] in ["Collective", "Triplex", "Duplex"]:
                            dct_HPXML[argHPXML] = 322
                    case "[500 - 1000)":
                        dct_HPXML[argHPXML] = 750
                    case "[1000 - 1500)":
                        if dct_args["Type_Logement"] in ["Maison individuelle"]:
                            dct_HPXML[argHPXML] = 1228
                        elif dct_args["Type_Logement"] in ["Maison en rangee"]:
                            dct_HPXML[argHPXML] = 1207
                        elif dct_args["Type_Logement"] in ["Collective", "Triplex", "Duplex"]:
                            dct_HPXML[argHPXML] = 1138
                    case "[1500 - 2000)":
                        if dct_args["Type_Logement"] in ["Maison individuelle"]:
                            dct_HPXML[argHPXML] = 1698
                        elif dct_args["Type_Logement"] in ["Maison en rangee"]:
                            dct_HPXML[argHPXML] = 1678
                        elif dct_args["Type_Logement"] in ["Collective", "Triplex", "Duplex"]:
                            dct_HPXML[argHPXML] = 1682
                    case "[2000 - 2500)":
                        if dct_args["Type_Logement"] in ["Maison individuelle"]:
                            dct_HPXML[argHPXML] = 2179
                        elif dct_args["Type_Logement"] in ["Maison en rangee"]:
                            dct_HPXML[argHPXML] = 2152
                        elif dct_args["Type_Logement"] in ["Collective", "Triplex", "Duplex"]:
                            dct_HPXML[argHPXML] = 2115
                    case "[2500 - 3000)":
                        if dct_args["Type_Logement"] in ["Maison individuelle"]:
                            dct_HPXML[argHPXML] = 2678
                        elif dct_args["Type_Logement"] in ["Maison en rangee"]:
                            dct_HPXML[argHPXML] = 2663
                        elif dct_args["Type_Logement"] in ["Collective", "Triplex", "Duplex"]:
                            dct_HPXML[argHPXML] = 2648
                    case "[3000 - 3500)":
                        dct_HPXML[argHPXML] = 3250
                    case "[3500 - 4000)":
                        dct_HPXML[argHPXML] = 3750
                    case "[4000 - 4500)":
                        dct_HPXML[argHPXML] = 4250
                    case "[4500 - 5000)":
                        dct_HPXML[argHPXML] = 4750
                    case ">= 5000":
                        if dct_args["Type_Logement"] in ["Maison individuelle"]:
                            dct_HPXML[argHPXML] = 5587
                        elif dct_args["Type_Logement"] in ["Maison en rangee"]:
                            dct_HPXML[argHPXML] = 7414
                        elif dct_args["Type_Logement"] in ["Collective", "Triplex", "Duplex"]:
                            dct_HPXML[argHPXML] = 6348

            else:
                if self.HPXMLArg.arguments[argHPXML].get("Default Value", "Defaut_Not_Existing")!="Defaut_Not_Existing":
                    dct_HPXML[argHPXML] = self.HPXMLArg.arguments[argHPXML].get("Default Value")
                else:
                    dct_HPXML[argHPXML] = 'single-family detached'
           
        #________________________________________________________________
        # Vintage
        arg = "An_Construction"
        argHPXML = "year_built"
        if (argHPXML not in dct_HPXML.keys()):
            if (arg in dct_args.keys()):
                match dct_args[arg]:
                    case '< 1950':
                        dct_HPXML[argHPXML] = 1940
                    case '[1950 - 1960)':
                        dct_HPXML[argHPXML] = 1955
                    case '[1960 - 1970)':
                        dct_HPXML[argHPXML] = 1965
                    case '[1970 - 1980)':
                        dct_HPXML[argHPXML] = 1975
                    case '[1980 - 1990)':
                        dct_HPXML[argHPXML] = 1985
                    case '[1990 - 2000)':
                        dct_HPXML[argHPXML] = 1995
                    case '[2000 - 2010)':
                        dct_HPXML[argHPXML] = 2005
                    case '[2010 - 2020)':
                        dct_HPXML[argHPXML] = 2015
                    case '>= 2020':
                        dct_HPXML[argHPXML] = 2020
            else:
                if self.HPXMLArg.arguments[argHPXML].get("Default Value", "Defaut_Not_Existing")!="Defaut_Not_Existing":
                    dct_HPXML[argHPXML] = self.HPXMLArg.arguments[argHPXML].get("Default Value")
                else:
                    pass#dct_HPXML[argHPXML] = 2000
        
        #________________________________________________________________
        #geometry_unit_num_bedrooms
        arg = "Nombre_Pieces"
        argHPXML = "geometry_unit_num_bedrooms"
        if (argHPXML not in dct_HPXML.keys()):
            if (arg in dct_args.keys()):
                if dct_args[arg] == "15 et plus":
                    dct_HPXML[argHPXML] = 7
                elif int(dct_args[arg]) in [12,13,14]:
                    dct_HPXML[argHPXML] = 6
                elif int(dct_args[arg]) in [9,10,11]:
                    dct_HPXML[argHPXML] = 5
                elif int(dct_args[arg]) in [7,8]:
                    dct_HPXML[argHPXML] = 4
                elif int(dct_args[arg]) in [5,6]:
                    dct_HPXML[argHPXML] = 3
                elif int(dct_args[arg]) in [3,4]:
                    dct_HPXML[argHPXML] = 2
                elif int(dct_args[arg]) in [1,2]:
                    dct_HPXML[argHPXML] = 1
            else:
                if self.HPXMLArg.arguments[argHPXML].get("Default Value", "Defaut_Not_Existing")!="Defaut_Not_Existing":
                    dct_HPXML[argHPXML] = int(self.HPXMLArg.arguments[argHPXML].get("Default Value"))
                else:
                    dct_HPXML[argHPXML] = 3

        #water_heater_num_bedrooms_served #not requires
        #pv_system_num_bedrooms_served #not requires
        #battery_num_bedrooms_served #not requires

        #________________________________________________________________
        # geometry_unit_num_occupants
        arg = "Nombre_Personnes"
        argHPXML = "geometry_unit_num_occupants"
        if (argHPXML not in dct_HPXML.keys()):
            if (arg in dct_args.keys()):
                if dct_args[arg] == "5 et plus":
                    dct_HPXML[argHPXML] = 5
                else:
                    dct_HPXML[argHPXML] = int(dct_args[arg])
            else:
                if self.HPXMLArg.arguments[argHPXML].get("Default Value", "Defaut_Not_Existing")!="Defaut_Not_Existing":
                    dct_HPXML[argHPXML] = self.HPXMLArg.arguments[argHPXML].get("Default Value")
                else:
                    dct_HPXML[argHPXML] = dct_HPXML.get("geometry_unit_num_bedrooms", 3)

        #_________________________________________________________________
        #Geometry Attic Type
        dct_Geometry_Attic_Type = {}
        dct_Geometry_Attic_Type["Conditioned Attic"] = {"geometry_attic_type":"ConditionedAttic", "geometry_roof_type":"gable", "geometry_roof_pitch":"6:12"}
        dct_Geometry_Attic_Type["Finished Attic or Cathedral Ceilings"] = {"geometry_attic_type":"ConditionedAttic", "geometry_roof_type":"gable", "geometry_roof_pitch":"6:12"}
        dct_Geometry_Attic_Type["None"] = {"geometry_attic_type":"FlatRoof", "geometry_roof_type":"gable", "geometry_roof_pitch":"6:12"}
        dct_Geometry_Attic_Type["Unvented Attic"] = {"geometry_attic_type":"UnventedAttic", "geometry_roof_type":"gable", "geometry_roof_pitch":"6:12"}
        dct_Geometry_Attic_Type["Vented Attic"] = {"geometry_attic_type":"VentedAttic", "geometry_roof_type":"gable", "geometry_roof_pitch":"6:12"}

        #defaut
        arg = "geometry attic type"
        #if (arg in dct_args.keys()):
        #    for args in dct_Geometry_Attic_Type["None"]:
        #        if ((args not in dct_HPXML.keys()) & (dct_Geometry_Attic_Type["None"][args]!="auto")):
        #            dct_HPXML[args] = dct_Geometry_Attic_Type["None"][args]
        arg = "geometry attic type"
        if (arg in dct_args.keys()):
            for args in dct_Geometry_Attic_Type[dct_args[arg]]:
                if ((args not in dct_HPXML.keys()) & (dct_Geometry_Attic_Type[dct_args[arg]][args]!="auto")):
                    dct_HPXML[args] = dct_Geometry_Attic_Type[dct_args[arg]][args]

        #_____________________________________________________________
        #geometry_unit_num_floors_above_grade
        
        #The number of floors above grade in the unit. 
        # Attic type ConditionedAttic is included. 
        # Assumed to be 1 for apartment units.
        additional_floor = 0
        if dct_HPXML["geometry_attic_type"] == "ConditionedAttic":
            additional_floor ==1
        arg = "Nombre_Etages"
        argHPXML = "geometry_unit_num_floors_above_grade"# du logement et non de l'immeuble
        if (argHPXML not in dct_HPXML.keys()):
            if (arg in dct_args.keys()):
                if (dct_HPXML.get("geometry_unit_type") in ["single-family detached", "single-family attached"]):
                    if dct_args[arg] == "Un étage":
                        dct_HPXML[argHPXML] = 1 + additional_floor
                    elif dct_args[arg] == "Deux étages":
                        dct_HPXML[argHPXML] = 2 + additional_floor
                    elif dct_args[arg] == "Trois étages et plus":
                        dct_HPXML[argHPXML] = 3 + additional_floor
                else:#pour les plex et les appart pas d'étage dans le hpxml
                    dct_HPXML[argHPXML] = 1
            else:
                if (dct_HPXML.get("geometry_unit_type") in ["single-family detached", "single-family attached"]):
                    if self.HPXMLArg.arguments[argHPXML].get("Default Value", "Defaut_Not_Existing")!="Defaut_Not_Existing":
                        dct_HPXML[argHPXML] = self.HPXMLArg.arguments[argHPXML].get("Default Value") + additional_floor
                    else:
                        dct_HPXML[argHPXML] = 1 + additional_floor
                else:
                    if self.HPXMLArg.arguments[argHPXML].get("Default Value", "Defaut_Not_Existing")!="Defaut_Not_Existing":
                        dct_HPXML[argHPXML] = self.HPXMLArg.arguments[argHPXML].get("Default Value") + additional_floor
                    else:
                        dct_HPXML[argHPXML] = 1 + additional_floor

        #________________________________________________________________ 
        #Geometry Foundation Type

        dict_Geometry_Foundation_Type = {}
        dict_Geometry_Foundation_Type["Slab"] = {"geometry_foundation_type":"SlabOnGrade", "geometry_foundation_height":0, "geometry_foundation_height_above_grade":0, "geometry_rim_joist_height":0}
        dict_Geometry_Foundation_Type["Unheated Basement"] = {"geometry_foundation_type":"UnconditionedBasement", "geometry_foundation_height":8, "geometry_foundation_height_above_grade":1, "geometry_rim_joist_height":9.25}
        dict_Geometry_Foundation_Type["Vented Crawlspace"] = {"geometry_foundation_type":"VentedCrawlspace", "geometry_foundation_height":4, "geometry_foundation_height_above_grade":1, "geometry_rim_joist_height":9.25}
        dict_Geometry_Foundation_Type["Heated Basement"] = {"geometry_foundation_type":"ConditionedBasement", "geometry_foundation_height":8, "geometry_foundation_height_above_grade":1, "geometry_rim_joist_height":9.25}
        dict_Geometry_Foundation_Type["Conditioned Crawlspace"] = {"geometry_foundation_type":"ConditionedCrawlspace", "geometry_foundation_height":4, "geometry_foundation_height_above_grade":1, "geometry_rim_joist_height":9.25}
        dict_Geometry_Foundation_Type["Ambient"] = {"geometry_foundation_type":"Ambient", "geometry_foundation_height":4, "geometry_foundation_height_above_grade":4, "geometry_rim_joist_height":0}
        dict_Geometry_Foundation_Type["Unvented Crawlspace"] = {"geometry_foundation_type":"UnventedCrawlspace", "geometry_foundation_height":4, "geometry_foundation_height_above_grade":1, "geometry_rim_joist_height":9.25}

        arg = "Geometry Foundation Type"
        #args = "geometry_foundation_type"
        if (arg in dct_args.keys()):
            for args in dict_Geometry_Foundation_Type[dct_args[arg]]:
                if ((args not in dct_HPXML.keys()) & (dict_Geometry_Foundation_Type[dct_args[arg]][args]!="auto")):
                    dct_HPXML[args] = dict_Geometry_Foundation_Type[dct_args[arg]][args]

        #________________________________________________________________

        dct_windows = {}
        dct_windows["Double, Clear, Metal, Air"] = {"window_ufactor":0.76,
                                             "window_shgc":0.67,
                                              "skylight_ufactor":0.37,
                                              "skylight_shgc":0.3,
                                              "skylight_storm_type":"auto",
                                             "window_exterior_shading_summer":"auto",
                                            "window_exterior_shading_winter":"auto",
                                            "window_natvent_availability":"auto",
                                            "window_shading_summer_season":"auto"}
        
        dct_windows["Double, Clear, Metal, Air, Exterior Clear Storm"] = {"window_ufactor":0.55,
                                                "window_shgc":0.51,
                                                "skylight_ufactor":0.37,
                                                "skylight_shgc":0.3,
                                                "skylight_storm_type":"auto",
                                                "window_exterior_shading_summer":"auto",
                                                "window_exterior_shading_winter":"auto",
                                                "window_natvent_availability":"auto",
                                                "window_shading_summer_season":"auto"}
        dct_windows["Double, Clear, Metal, Exterior Low-E Storm"] = {"window_ufactor":0.49,
                                                "window_shgc":0.44,
                                                "skylight_ufactor":0.37,
                                                "skylight_shgc":0.3,
                                                "skylight_storm_type":"auto",
                                                "window_exterior_shading_summer":"auto",
                                                "window_exterior_shading_winter":"auto",
                                                "window_natvent_availability":"auto",
                                                "window_shading_summer_season":"auto"}
        dct_windows["Double, Clear, Non-metal, Air"] = {"window_ufactor":0.49,
                                                "window_shgc":0.56,
                                                "skylight_ufactor":0.37,
                                                "skylight_shgc":0.3,
                                                "skylight_storm_type":"auto",
                                                "window_exterior_shading_summer":"auto",
                                                "window_exterior_shading_winter":"auto",
                                                "window_natvent_availability":"auto",
                                                "window_shading_summer_season":"auto"}
        dct_windows["Double, Clear, Non-metal, Air, Exterior Clear Storm"] = {"window_ufactor":0.34,
                                                "window_shgc":0.49,
                                                "skylight_ufactor":0.37,
                                                "skylight_shgc":0.3,
                                                "skylight_storm_type":"auto",
                                                "window_exterior_shading_summer":"auto",
                                                "window_exterior_shading_winter":"auto",
                                                "window_natvent_availability":"auto",
                                                "window_shading_summer_season":"auto"}
        dct_windows["Double, Clear, Non-metal, Exterior Low-E Storm"] = {"window_ufactor":0.28,
                                                "window_shgc":0.42,
                                                "skylight_ufactor":0.37,
                                                "skylight_shgc":0.3,
                                                "skylight_storm_type":"auto",
                                                "window_exterior_shading_summer":"auto",
                                                "window_exterior_shading_winter":"auto",
                                                "window_natvent_availability":"auto",
                                                "window_shading_summer_season":"auto"}
        dct_windows["Double, Clear, Thermal-Break, Air"] = {"window_ufactor":0.63,
                                                "window_shgc":0.62,
                                                "skylight_ufactor":0.37,
                                                "skylight_shgc":0.3,
                                                "skylight_storm_type":"auto",
                                                "window_exterior_shading_summer":"auto",
                                                "window_exterior_shading_winter":"auto",
                                                "window_natvent_availability":"auto",
                                                "window_shading_summer_season":"auto"}
        dct_windows["Double, Low-E, H-Gain"] = {"window_ufactor":0.29,
                                                "window_shgc":0.56,
                                                "skylight_ufactor":0.37,
                                                "skylight_shgc":0.3,
                                                "skylight_storm_type":"auto",
                                                "window_exterior_shading_summer":"auto",
                                                "window_exterior_shading_winter":"auto",
                                                "window_natvent_availability":"auto",
                                                "window_shading_summer_season":"auto"}
        dct_windows["Double, Low-E, L-Gain"] = {"window_ufactor":0.26,
                                                "window_shgc":0.31,
                                                "skylight_ufactor":0.37,
                                                "skylight_shgc":0.3,
                                                "skylight_storm_type":"auto",
                                                "window_exterior_shading_summer":"auto",
                                                "window_exterior_shading_winter":"auto",
                                                "window_natvent_availability":"auto",
                                                "window_shading_summer_season":"auto"}
        dct_windows["Double, Low-E, Non-metal, Air, L-Gain"] = {"window_ufactor":0.37,
                                                "window_shgc":0.3,
                                                "skylight_ufactor":0.37,
                                                "skylight_shgc":0.3,
                                                "skylight_storm_type":"auto",
                                                "window_exterior_shading_summer":"auto",
                                                "window_exterior_shading_winter":"auto",
                                                "window_natvent_availability":"auto",
                                                "window_shading_summer_season":"auto"}
        dct_windows["Double, Low-E, Non-metal, Air, M-Gain"] = {"window_ufactor":0.38,
                                                "window_shgc":0.44,
                                                "skylight_ufactor":0.37,
                                                "skylight_shgc":0.3,
                                                "skylight_storm_type":"auto",
                                                "window_exterior_shading_summer":"auto",
                                                "window_exterior_shading_winter":"auto",
                                                "window_natvent_availability":"auto",
                                                "window_shading_summer_season":"auto"}
        dct_windows["Single, Clear, Metal"] = {"window_ufactor":1.16,
                                                "window_shgc":0.76,
                                                "skylight_ufactor":0.37,
                                                "skylight_shgc":0.3,
                                                "skylight_storm_type":"auto",
                                                "window_exterior_shading_summer":"auto",
                                                "window_exterior_shading_winter":"auto",
                                                "window_natvent_availability":"auto",
                                                "window_shading_summer_season":"auto"}
        dct_windows["Single, Clear, Metal, Exterior Clear Storm"] = {"window_ufactor":0.67,
                                                "window_shgc":0.56,
                                                "skylight_ufactor":0.37,
                                                "skylight_shgc":0.3,
                                                "skylight_storm_type":"auto",
                                                "window_exterior_shading_summer":"auto",
                                                "window_exterior_shading_winter":"auto",
                                                "window_natvent_availability":"auto",
                                                "window_shading_summer_season":"auto"}
        dct_windows["Single, Clear, Metal, Exterior Low-E Storm"] = {"window_ufactor":0.57,
                                                "window_shgc":0.47,
                                                "skylight_ufactor":0.37,
                                                "skylight_shgc":0.3,
                                                "skylight_storm_type":"auto",
                                                "window_exterior_shading_summer":"auto",
                                                "window_exterior_shading_winter":"auto",
                                                "window_natvent_availability":"auto",
                                                "window_shading_summer_season":"auto"}
        dct_windows["Single, Clear, Non-metal"] = {"window_ufactor":0.84,
                                                "window_shgc":0.63,
                                                "skylight_ufactor":0.37,
                                                "skylight_shgc":0.3,
                                                "skylight_storm_type":"auto",
                                                "window_exterior_shading_summer":"auto",
                                                "window_exterior_shading_winter":"auto",
                                                "window_natvent_availability":"auto",
                                                "window_shading_summer_season":"auto"}
        dct_windows["Single, Clear, Non-metal, Exterior Clear Storm"] = {"window_ufactor":0.47,
                                                "window_shgc":0.54,
                                                "skylight_ufactor":0.37,
                                                "skylight_shgc":0.3,
                                                "skylight_storm_type":"auto",
                                                "window_exterior_shading_summer":"auto",
                                                "window_exterior_shading_winter":"auto",
                                                "window_natvent_availability":"auto",
                                                "window_shading_summer_season":"auto"}
        dct_windows["Single, Clear, Non-metal, Exterior Low-E Storm"] = {"window_ufactor":0.36,
                                                "window_shgc":0.46,
                                                "skylight_ufactor":0.37,
                                                "skylight_shgc":0.3,
                                                "skylight_storm_type":"auto",
                                                "window_exterior_shading_summer":"auto",
                                                "window_exterior_shading_winter":"auto",
                                                "window_natvent_availability":"auto",
                                                "window_shading_summer_season":"auto"}
        dct_windows["Triple, Low-E, Insulated, Argon, H-Gain"] = {"window_ufactor":0.18,
                                                "window_shgc":0.40,
                                                "skylight_ufactor":0.37,
                                                "skylight_shgc":0.3,
                                                "skylight_storm_type":"auto",
                                                "window_exterior_shading_summer":"auto",
                                                "window_exterior_shading_winter":"auto",
                                                "window_natvent_availability":"auto",
                                                "window_shading_summer_season":"auto"}
        dct_windows["Triple, Low-E, Insulated, Argon, L-Gain"] = {"window_ufactor":0.17,
                                                "window_shgc":0.27,
                                                "skylight_ufactor":0.37,
                                                "skylight_shgc":0.3,
                                                "skylight_storm_type":"auto",
                                                "window_exterior_shading_summer":"auto",
                                                "window_exterior_shading_winter":"auto",
                                                "window_natvent_availability":"auto",
                                                "window_shading_summer_season":"auto"}
        dct_windows["Triple, Low-E, Non-metal, Air, L-Gain"] = {"window_ufactor":0.29,
                                                "window_shgc":0.26,
                                                "skylight_ufactor":0.37,
                                                "skylight_shgc":0.3,
                                                "skylight_storm_type":"auto",
                                                "window_exterior_shading_summer":"auto",
                                                "window_exterior_shading_winter":"auto",
                                                "window_natvent_availability":"auto",
                                                "window_shading_summer_season":"auto"}
        dct_windows["No Windows"] = {"window_ufactor":0.84,
                                                "window_shgc":0.63,
                                                "skylight_ufactor":0.37,
                                                "skylight_shgc":0.3,
                                                "skylight_storm_type":"auto",
                                                "window_exterior_shading_summer":"auto",
                                                "window_exterior_shading_winter":"auto",
                                                "window_natvent_availability":"auto",
                                                "window_shading_summer_season":"auto"}
        #windows
        arg = "Windows"
        if (arg in dct_args.keys()):
            for args in dct_windows[dct_args[arg]]:
                if ((args not in dct_HPXML.keys()) & (dct_windows[dct_args[arg]][args]!="auto")):
                    dct_HPXML[args] = dct_windows[dct_args[arg]][args]

        #_________________________________________________________________
        #Insulation wall
        dct_Insulation_Wall ={}
        dct_Insulation_Wall["Brick, 12-in, 3-wythe, R-11"] = {"wall_type":"StructuralBrick", "wall_assembly_r":13.3}
        dct_Insulation_Wall["Brick, 12-in, 3-wythe, R-15"] = {"wall_type":"StructuralBrick", "wall_assembly_r":15.9}
        dct_Insulation_Wall["Brick, 12-in, 3-wythe, R-19"] = {"wall_type":"StructuralBrick", "wall_assembly_r":18.3}
        dct_Insulation_Wall["Brick, 12-in, 3-wythe, R-7"] = {"wall_type":"StructuralBrick", "wall_assembly_r":10.3}
        dct_Insulation_Wall["Brick, 12-in, 3-wythe, Uninsulated"] = {"wall_type":"StructuralBrick", "wall_assembly_r":4.9}
        dct_Insulation_Wall["CMU, 12-in Hollow"] = {"wall_type":"ConcreteMasonryUnit", "wall_assembly_r":4.9}
        dct_Insulation_Wall["CMU, 12-in Hollow, R-10"] = {"wall_type":"ConcreteMasonryUnit", "wall_assembly_r":12.9}
        dct_Insulation_Wall["CMU, 6-in Concrete Filled"] = {"wall_type":"ConcreteMasonryUnit", "wall_assembly_r":3.7}
        dct_Insulation_Wall["CMU, 6-in Concrete-Filled, R-10"] = {"wall_type":"ConcreteMasonryUnit", "wall_assembly_r":11.4}
        dct_Insulation_Wall["CMU, 6-in Hollow, R-11"] = {"wall_type":"ConcreteMasonryUnit", "wall_assembly_r":12.4}
        dct_Insulation_Wall["CMU, 6-in Hollow, R-15"] = {"wall_type":"ConcreteMasonryUnit", "wall_assembly_r":15}
        dct_Insulation_Wall["CMU, 6-in Hollow, R-19"] = {"wall_type":"ConcreteMasonryUnit", "wall_assembly_r":17.4}
        dct_Insulation_Wall["CMU, 6-in Hollow, R-7"] = {"wall_type":"ConcreteMasonryUnit", "wall_assembly_r":9.4}
        dct_Insulation_Wall["CMU, 6-in Hollow, Uninsulated"] = {"wall_type":"ConcreteMasonryUnit", "wall_assembly_r":4}
        dct_Insulation_Wall["Double Wood Stud, R-33"] = {"wall_type":"DoubleWoodStud", "wall_assembly_r":28.1}
        dct_Insulation_Wall["Double Wood Stud, R-45, Grade 3"] = {"wall_type":"DoubleWoodStud", "wall_assembly_r":25.1}
        dct_Insulation_Wall["Generic, 10-in Grid ICF"] = {"wall_type":"WoodStud", "wall_assembly_r":12.4}
        dct_Insulation_Wall["Generic, T-Mass Wall w/Metal Ties"] = {"wall_type":"WoodStud", "wall_assembly_r":9}
        dct_Insulation_Wall["ICF, 2-in EPS, 12-in Concrete, 2-in EPS"] = {"wall_type":"InsulatedConcreteForms", "wall_assembly_r":22.5}
        dct_Insulation_Wall["ICF, 2-in EPS, 4-in Concrete, 2-in EPS"] = {"wall_type":"InsulatedConcreteForms", "wall_assembly_r":20.4}
        dct_Insulation_Wall["SIP, 3.6 in EPS Core, OSB int."] = {"wall_type":"StructuralInsulatedPanel", "wall_assembly_r":15.5}
        dct_Insulation_Wall["SIP, 9.4 in EPS Core, Gypsum int."] = {"wall_type":"StructuralInsulatedPanel", "wall_assembly_r":35.8}
        dct_Insulation_Wall["SIP, 9.4 in EPS Core, OSB int."] = {"wall_type":"StructuralInsulatedPanel", "wall_assembly_r":36}
        dct_Insulation_Wall["Steel Stud, R-13"] = {"wall_type":"SteelFrame", "wall_assembly_r":7.9}
        dct_Insulation_Wall["Steel Stud, R-25, Grade 3"] = {"wall_type":"SteelFrame", "wall_assembly_r":10.4}
        dct_Insulation_Wall["Steel Stud, Uninsulated"] = {"wall_type":"SteelFrame", "wall_assembly_r":3}
        dct_Insulation_Wall["Wood Stud, R-11"] = {"wall_type":"WoodStud", "wall_assembly_r":10.3}
        dct_Insulation_Wall["Wood Stud, R-11, R-5 Sheathing"] = {"wall_type":"WoodStud", "wall_assembly_r":15.3}
        dct_Insulation_Wall["Wood Stud, R-13"] = {"wall_type":"WoodStud", "wall_assembly_r":11.3}
        dct_Insulation_Wall["Wood Stud, R-13, R-5 Sheathing"] = {"wall_type":"WoodStud", "wall_assembly_r":16.3}
        dct_Insulation_Wall["Wood Stud, R-15"] = {"wall_type":"WoodStud", "wall_assembly_r":12.1}
        dct_Insulation_Wall["Wood Stud, R-15, R-5 Sheathing"] = {"wall_type":"WoodStud", "wall_assembly_r":17.1}
        dct_Insulation_Wall["Wood Stud, R-19"] = {"wall_type":"WoodStud", "wall_assembly_r":15.4}
        dct_Insulation_Wall["Wood Stud, R-19, Grade 2"] = {"wall_type":"WoodStud", "wall_assembly_r":14.5}
        dct_Insulation_Wall["Wood Stud, R-19, Grade 2, R-5 Sheathing"] = {"wall_type":"WoodStud", "wall_assembly_r":19.5}
        dct_Insulation_Wall["Wood Stud, R-19, Grade 3"] = {"wall_type":"WoodStud", "wall_assembly_r":13.4}
        dct_Insulation_Wall["Wood Stud, R-19, Grade 3, R-5 Sheathing"] = {"wall_type":"WoodStud", "wall_assembly_r":18.4}
        dct_Insulation_Wall["Wood Stud, R-19, R-5 Sheathing"] = {"wall_type":"WoodStud", "wall_assembly_r":20.4}
        dct_Insulation_Wall["Wood Stud, R-23 Closed Cell Spray Foam, 2x4, 16 in o.c."] = {"wall_type":"WoodStud", "wall_assembly_r":14.7}
        dct_Insulation_Wall["Wood Stud, R-23 Closed Cell Spray Foam, 2x4, 16 in o.c., R-5 Sheathing"] = {"wall_type":"WoodStud", "wall_assembly_r":19.7}
        dct_Insulation_Wall["Wood Stud, R-36"] = {"wall_type":"WoodStud", "wall_assembly_r":22.3}
        dct_Insulation_Wall["Wood Stud, R-36, R-5 Sheathing"] = {"wall_type":"WoodStud", "wall_assembly_r":27.3}
        dct_Insulation_Wall["Wood Stud, R-7"] = {"wall_type":"WoodStud", "wall_assembly_r":8.7}
        dct_Insulation_Wall["Wood Stud, R-7, R-5 Sheathing"] = {"wall_type":"WoodStud", "wall_assembly_r":13.7}
        dct_Insulation_Wall["Wood Stud, Uninsulated"] = {"wall_type":"WoodStud", "wall_assembly_r":3.4}
        dct_Insulation_Wall["Wood Stud, Uninsulated, R-5 Sheathing"] = {"wall_type":"WoodStud", "wall_assembly_r":8.4}
        
        dct_Insulation_Wall["QC_WoodStud-R12.2"]={"wall_type":"WoodStud", "wall_assembly_r":12.2}
        dct_Insulation_Wall["QC_WoodStud-R12.6"]={"wall_type":"WoodStud", "wall_assembly_r":12.6}
        dct_Insulation_Wall["QC_WoodStud-R14"]={"wall_type":"WoodStud", "wall_assembly_r":14.0}
        dct_Insulation_Wall["QC_WoodStud-R14.5"]={"wall_type":"WoodStud", "wall_assembly_r":14.5}
        dct_Insulation_Wall["QC_WoodStud-R17.2"]={"wall_type":"WoodStud", "wall_assembly_r":17.2}
        dct_Insulation_Wall["QC_WoodStud-R18.9"]={"wall_type":"WoodStud", "wall_assembly_r":18.9}
        dct_Insulation_Wall["QC_WoodStud-R20.7"]={"wall_type":"WoodStud", "wall_assembly_r":20.7}
        dct_Insulation_Wall["QC_WoodStud-R24.5"]={"wall_type":"WoodStud", "wall_assembly_r":24.5}

        arg = "Insulation Wall"
        
        if (arg in dct_args.keys()):
            for args in dct_Insulation_Wall[dct_args[arg]]:
                if ((args not in dct_HPXML.keys()) & (dct_Insulation_Wall[dct_args[arg]][args]!="auto")):
                    dct_HPXML[args] = dct_Insulation_Wall[dct_args[arg]][args]
        #_________________________________________________________________
        #Insulation ceiling
        dct_Insulation_Ceiling = {}
        dct_Insulation_Ceiling["Uninsulated"] = {"ceiling_assembly_r":2.1, "ceiling_insulation_r":0}
        dct_Insulation_Ceiling["R-7"] = {"ceiling_assembly_r":8.7, "ceiling_insulation_r":7}
        dct_Insulation_Ceiling["R-13"] = {"ceiling_assembly_r":14.6, "ceiling_insulation_r":13}
        dct_Insulation_Ceiling["R-19"] = {"ceiling_assembly_r":20.6, "ceiling_insulation_r":19}
        dct_Insulation_Ceiling["R-30"] = {"ceiling_assembly_r":31.6, "ceiling_insulation_r":30}
        dct_Insulation_Ceiling["R-38"] = {"ceiling_assembly_r":39.6, "ceiling_insulation_r":38}
        dct_Insulation_Ceiling["R-49"] = {"ceiling_assembly_r":50.6, "ceiling_insulation_r":49}
        dct_Insulation_Ceiling["R-60"] = {"ceiling_assembly_r":61.6, "ceiling_insulation_r":60}

        dct_Insulation_Ceiling["QC_R12.5"] = {"ceiling_assembly_r":14.1, "ceiling_insulation_r":12.5}
        dct_Insulation_Ceiling["QC_R19.6"] = {"ceiling_assembly_r":21.2, "ceiling_insulation_r":19.6}
        dct_Insulation_Ceiling["QC_R24.6"] = {"ceiling_assembly_r":26.2, "ceiling_insulation_r":24.6}
        dct_Insulation_Ceiling["QC_R27.3"] = {"ceiling_assembly_r":28.9, "ceiling_insulation_r":27.3}
        dct_Insulation_Ceiling["QC_R30.9"] = {"ceiling_assembly_r":32.5, "ceiling_insulation_r":30.9}
        dct_Insulation_Ceiling["QC_R41"] = {"ceiling_assembly_r":42.6, "ceiling_insulation_r":41}
        dct_Insulation_Ceiling["QC_R18.3"] = {"ceiling_assembly_r":19.9, "ceiling_insulation_r":18.3}
        dct_Insulation_Ceiling["QC_R29.8"] = {"ceiling_assembly_r":31.4, "ceiling_insulation_r":29.8}
        
        dct_Insulation_Ceiling["None"] = {"ceiling_assembly_r":0, "ceiling_insulation_r":0} #defaut

        #defaut
        arg = "Insulation Ceiling"
       
        #if (arg in dct_args.keys()):
        #    for args in dct_Insulation_Ceiling["None"]:
        #        if ((args not in dct_HPXML.keys()) & (dct_Insulation_Ceiling["None"][args]!="auto")):
        #            dct_HPXML[args] = dct_Insulation_Ceiling["None"][args]

        arg = "Insulation Ceiling"
        if (arg in dct_args.keys()):
            for args in dct_Insulation_Ceiling[dct_args[arg]]:
                if ((args not in dct_HPXML.keys()) & (dct_Insulation_Ceiling[dct_args[arg]][args]!="auto")):
                    dct_HPXML[args] = dct_Insulation_Ceiling[dct_args[arg]][args]

        #_________________________________________________________________
        #Insulation Foundation Wall
        dct_Insulation_Foundation_Wall = {}
        dct_Insulation_Foundation_Wall["Wall R-10, Exterior"] = {"foundation_wall_type":"solid concrete",
                                                                  "foundation_wall_thickness":"auto",
                                                                  "foundation_wall_insulation_r":10,
                                                                  "foundation_wall_insulation_location":"exterior",
                                                                  "foundation_wall_insulation_distance_to_top":0,
                                                                  "foundation_wall_insulation_distance_to_bottom":"auto",
                                                                  "foundation_wall_assembly_r":"auto",
                                                                  "rim_joist_continuous_exterior_r":10,
                                                                  "rim_joist_continuous_interior_r":0,
                                                                  "rim_joist_assembly_interior_r":0,
                                                                  "rim_joist_assembly_r":"auto"}
        
        dct_Insulation_Foundation_Wall["Wall R-13, Interior"] = {"foundation_wall_type":"solid concrete",
                                                                 "foundation_wall_thickness":"auto",
                                                                 "foundation_wall_insulation_r":13,
                                                                 "foundation_wall_insulation_location":"interior",
                                                                 "foundation_wall_insulation_distance_to_top":0,
                                                                 "foundation_wall_insulation_distance_to_bottom":"auto",
                                                                 "foundation_wall_assembly_r":"auto",
                                                                 "rim_joist_continuous_exterior_r":0,
                                                                 "rim_joist_continuous_interior_r":13,
                                                                 "rim_joist_assembly_interior_r":10.4,
                                                                 "rim_joist_assembly_r":"auto"}
        
        dct_Insulation_Foundation_Wall["Wall R-15, Exterior"] = {"foundation_wall_type":"solid concrete",
                                                                 "foundation_wall_thickness":"auto",
                                                                 "foundation_wall_insulation_r":15,
                                                                 "foundation_wall_insulation_location":"exterior",
                                                                 "foundation_wall_insulation_distance_to_top":0,
                                                                 "foundation_wall_insulation_distance_to_bottom":"auto",
                                                                 "foundation_wall_assembly_r":"auto",
                                                                 "rim_joist_continuous_exterior_r":15,
                                                                 "rim_joist_continuous_interior_r":0,
                                                                 "rim_joist_assembly_interior_r":0,
                                                                 "rim_joist_assembly_r":"auto"}
        
        dct_Insulation_Foundation_Wall["Wall R-5, Exterior"] = {"foundation_wall_type":"solid concrete",
                                                                "foundation_wall_thickness":"auto",
                                                                "foundation_wall_insulation_r":5,
                                                                "foundation_wall_insulation_location":"exterior",
                                                                "foundation_wall_insulation_distance_to_top":0,
                                                                "foundation_wall_insulation_distance_to_bottom":"auto",
                                                                "foundation_wall_assembly_r":"auto",
                                                                "rim_joist_continuous_exterior_r":5,
                                                                "rim_joist_continuous_interior_r":0,
                                                                "rim_joist_assembly_interior_r":0,
                                                                "rim_joist_assembly_r":"auto"}
        
        
        dct_Insulation_Foundation_Wall["Uninsulated"] = {"foundation_wall_type":"solid concrete",
                                                         "foundation_wall_thickness":"auto",
                                                         "foundation_wall_insulation_r":0,
                                                         "foundation_wall_insulation_location":"exterior",
                                                         "foundation_wall_insulation_distance_to_top":0,
                                                         "foundation_wall_insulation_distance_to_bottom":0,
                                                         "foundation_wall_assembly_r":"auto",
                                                         "rim_joist_continuous_exterior_r":0,
                                                         "rim_joist_continuous_interior_r":0,
                                                         "rim_joist_assembly_interior_r":0,
                                                         "rim_joist_assembly_r":"auto"} # defaut ?
        

        dct_Insulation_Foundation_Wall["None"] = {"foundation_wall_type":"solid concrete",
                                                  "foundation_wall_thickness":"auto",
                                                  "foundation_wall_insulation_r":0,
                                                  "foundation_wall_insulation_location":"exterior",
                                                  "foundation_wall_insulation_distance_to_top":0,
                                                  "foundation_wall_insulation_distance_to_bottom":0,
                                                  "foundation_wall_assembly_r":"auto",
                                                  "rim_joist_continuous_exterior_r":0,
                                                    "rim_joist_continuous_interior_r":0,
                                                    "rim_joist_assembly_interior_r":0,
                                                    "rim_joist_assembly_r":"auto"} # defaut ?
        
        dct_Insulation_Foundation_Wall["QC_Wall-R10.1, interior"]=  {"foundation_wall_type":"solid concrete",
                                                                 "foundation_wall_thickness":"auto",
                                                                 "foundation_wall_insulation_r":10.1,
                                                                 "foundation_wall_insulation_location":"interior",
                                                                 "foundation_wall_insulation_distance_to_top":0,
                                                                 "foundation_wall_insulation_distance_to_bottom":"auto",
                                                                 "foundation_wall_assembly_r":"auto",
                                                                 "rim_joist_continuous_exterior_r":0,
                                                                 "rim_joist_continuous_interior_r":10.1,
                                                                 "rim_joist_assembly_interior_r":10.1,#8.32,#LLb a verifier *0.8
                                                                 "rim_joist_assembly_r":"auto"}
        
        dct_Insulation_Foundation_Wall["QC_Wall-R12, interior"]= {"foundation_wall_type":"solid concrete",
                                                                 "foundation_wall_thickness":"auto",
                                                                 "foundation_wall_insulation_r":12,
                                                                 "foundation_wall_insulation_location":"interior",
                                                                 "foundation_wall_insulation_distance_to_top":0,
                                                                 "foundation_wall_insulation_distance_to_bottom":"auto",
                                                                 "foundation_wall_assembly_r":"auto",
                                                                 "rim_joist_continuous_exterior_r":0,
                                                                 "rim_joist_continuous_interior_r":12,
                                                                 "rim_joist_assembly_interior_r":12,#9.6, #LLb a verifier *0.8
                                                                 "rim_joist_assembly_r":"auto"}
        
        dct_Insulation_Foundation_Wall["QC_Wall-R14.4, interior"]= {"foundation_wall_type":"solid concrete",
                                                                 "foundation_wall_thickness":"auto",
                                                                 "foundation_wall_insulation_r":14.4,
                                                                 "foundation_wall_insulation_location":"interior",
                                                                 "foundation_wall_insulation_distance_to_top":0,
                                                                 "foundation_wall_insulation_distance_to_bottom":"auto",
                                                                 "foundation_wall_assembly_r":"auto",
                                                                 "rim_joist_continuous_exterior_r":0,
                                                                 "rim_joist_continuous_interior_r":14.4,
                                                                 "rim_joist_assembly_interior_r":14.4,#11.52, #LLb a verifier *0.8
                                                                 "rim_joist_assembly_r":"auto"}
        
        dct_Insulation_Foundation_Wall["QC_Wall-R17.1, interior"]= {"foundation_wall_type":"solid concrete",
                                                                 "foundation_wall_thickness":"auto",
                                                                 "foundation_wall_insulation_r":17.1,
                                                                 "foundation_wall_insulation_location":"interior",
                                                                 "foundation_wall_insulation_distance_to_top":0,
                                                                 "foundation_wall_insulation_distance_to_bottom":"auto",
                                                                 "foundation_wall_assembly_r":"auto",
                                                                 "rim_joist_continuous_exterior_r":0,
                                                                 "rim_joist_continuous_interior_r":17.1,
                                                                 "rim_joist_assembly_interior_r":17.1,#13.68, #LLb a verifier *0.8
                                                                 "rim_joist_assembly_r":"auto"}
        
        dct_Insulation_Foundation_Wall["QC_Wall-R17, interior"]=  {"foundation_wall_type":"solid concrete",
                                                                 "foundation_wall_thickness":"auto",
                                                                 "foundation_wall_insulation_r":17,
                                                                 "foundation_wall_insulation_location":"interior",
                                                                 "foundation_wall_insulation_distance_to_top":0,
                                                                 "foundation_wall_insulation_distance_to_bottom":"auto",
                                                                 "foundation_wall_assembly_r":"auto",
                                                                 "rim_joist_continuous_exterior_r":0,
                                                                 "rim_joist_continuous_interior_r":17,
                                                                 "rim_joist_assembly_interior_r":17,#13.6, #LLb a verifier *0.8
                                                                 "rim_joist_assembly_r":"auto"}
        
        arg = "Insulation Foundation Wall"
        if (arg in dct_args.keys()):
            for args in dct_Insulation_Foundation_Wall[dct_args[arg]]:
                if ((args not in dct_HPXML.keys()) & (dct_Insulation_Foundation_Wall[dct_args[arg]][args]!="auto")):
                    dct_HPXML[args] = dct_Insulation_Foundation_Wall[dct_args[arg]][args]
        #defaut
        #arg = "Insulation Foundation Wall"
        #if (arg in dct_args.keys()):
        #    for args in dct_Insulation_Foundation_Wall["None"]:
        #        if ((args not in dct_HPXML.keys()) & (dct_Insulation_Foundation_Wall["None"][args]!="auto")):
        #            dct_HPXML[args] = dct_Insulation_Foundation_Wall["None"][args]

        #_________________________________________________________________
        # Insulation Floor
        dct_Insulation_Floor = {}
        dct_Insulation_Floor["Uninsulated"] = {"floor_type":"WoodFrame", "floor_over_foundation_assembly_r":5.3, "floor_over_garage_assembly_r":5.3}
        dct_Insulation_Floor["Ceiling R-19"] = {"floor_type":"WoodFrame", "floor_over_foundation_assembly_r":22.6, "floor_over_garage_assembly_r":22.6}
        dct_Insulation_Floor["Ceiling R-30"] = {"floor_type":"WoodFrame", "floor_over_foundation_assembly_r":30.3, "floor_over_garage_assembly_r":30.3}
        dct_Insulation_Floor["Ceiling R-38"] = {"floor_type":"WoodFrame", "floor_over_foundation_assembly_r":35.1, "floor_over_garage_assembly_r":35.1}
        dct_Insulation_Floor["None"] = {"floor_type":"WoodFrame", "floor_over_foundation_assembly_r":0, "floor_over_garage_assembly_r":5.3} # defaut
        dct_Insulation_Floor["Ceiling R-13"] = {"floor_type":"WoodFrame", "floor_over_foundation_assembly_r":17.8, "floor_over_garage_assembly_r":17.8}

        arg = "Insulation Floor"
        if (arg in dct_args.keys()):
            for args in dct_Insulation_Floor[dct_args[arg]]:
                if ((args not in dct_HPXML.keys()) & (dct_Insulation_Floor[dct_args[arg]][args]!="auto")):
                    dct_HPXML[args] = dct_Insulation_Floor[dct_args[arg]][args]
        #_________________________________________________________________
        #Geometry Wall Exterior Finish
        #Geometry_Wall_Exterior_Finish
        dct_Geometry_Wall_Exterior_Finish = {}
        dct_Geometry_Wall_Exterior_Finish["Aluminum, Light"] = {"wall_siding_type":"aluminum siding", "wall_color":"light", "exterior_finish_r":0.6}
        dct_Geometry_Wall_Exterior_Finish["Brick, Light"] = {"wall_siding_type":"brick veneer", "wall_color":"light", "exterior_finish_r":0.7}
        dct_Geometry_Wall_Exterior_Finish["Brick, Medium/Dark"] = {"wall_siding_type":"brick veneer", "wall_color":"medium dark", "exterior_finish_r":0.7}
        dct_Geometry_Wall_Exterior_Finish["Fiber-Cement, Light"] = {"wall_siding_type":"fiber cement siding", "wall_color":"light", "exterior_finish_r":0.2}
        dct_Geometry_Wall_Exterior_Finish["Shingle, Asbestos, Medium"] = {"wall_siding_type":"asbestos siding", "wall_color":"medium", "exterior_finish_r":0.6}
        dct_Geometry_Wall_Exterior_Finish["Shingle, Composition, Medium"] = {"wall_siding_type":"composite shingle siding", "wall_color":"medium", "exterior_finish_r":0.6}
        dct_Geometry_Wall_Exterior_Finish["Stucco, Light"] = {"wall_siding_type":"stucco", "wall_color":"light", "exterior_finish_r":0.2}
        dct_Geometry_Wall_Exterior_Finish["Stucco, Medium/Dark"] = {"wall_siding_type":"stucco", "wall_color":"medium dark", "exterior_finish_r":0.2}
        dct_Geometry_Wall_Exterior_Finish["Vinyl, Light"] = {"wall_siding_type":"vinyl siding", "wall_color":"light", "exterior_finish_r":0.6}
        dct_Geometry_Wall_Exterior_Finish["Wood, Medium/Dark"] = {"wall_siding_type":"wood siding", "wall_color":"medium dark", "exterior_finish_r":1.4}
        dct_Geometry_Wall_Exterior_Finish["None"] = {"wall_siding_type":"none", "wall_color":"medium", "exterior_finish_r":0}  # defaut

        arg = "Geometry Wall Exterior Finish"
        if (arg in dct_args.keys()):
            for args in dct_Geometry_Wall_Exterior_Finish[dct_args[arg]]:
                if ((args not in dct_HPXML.keys()) & (dct_Geometry_Wall_Exterior_Finish[dct_args[arg]][args]!="auto")):
                    dct_HPXML[args] = dct_Geometry_Wall_Exterior_Finish[dct_args[arg]][args]
        #defaut
        #arg = "Geometry Wall Exterior Finish"
        #if (arg in dct_args.keys()):
        #    for args in dct_Geometry_Wall_Exterior_Finish["None"]:
        #        if ((args not in dct_HPXML.keys()) & (dct_Geometry_Wall_Exterior_Finish["None"][args]!="auto")):
        #            dct_HPXML[args] = dct_Geometry_Wall_Exterior_Finish["None"][args]
        
        #________________________________________________________________
        #geometry_garage_width
        #The width of the garage. Enter zero for no garage. Only applies to single-family detached units.	
        #Plex : Ne pas ajouter de de garage
        #geometry_garage_depth

        #geometry_garage_protrusion
        argHPXML = "geometry_garage_protrusion"
        if (argHPXML not in dct_HPXML.keys()):
            if dct_HPXML.get("geometry_unit_cfa") < 750:
                dct_HPXML[argHPXML]=0.75
            else:
                dct_HPXML[argHPXML]=0.5   
        # Certains logements créés des problèmes de geometry (>2étages) 
        # Resstick considère qu'il n'y a pas de garage pour de nombreux cas(Geometry Garage csv)
        # On change la protusion pour éviter des erreur de geometry 
        if dct_HPXML.get("geometry_unit_num_floors_above_grade")>=2:
            dct_HPXML[argHPXML]=1

        if ((dct_HPXML.get("geometry_foundation_type") == "ConditionedBasement") and (dct_HPXML.get("geometry_attic_type") == "ConditionedAttic")):
            num_floors = dct_HPXML.get("geometry_unit_num_floors_above_grade") +1-1
        elif (dct_HPXML.get("geometry_foundation_type") == "ConditionedBasement"):
            num_floors = dct_HPXML.get("geometry_unit_num_floors_above_grade") + 1
        elif (dct_HPXML.get("geometry_attic_type") == "ConditionedAttic"):
            num_floors = dct_HPXML.get("geometry_unit_num_floors_above_grade") -1
        else:
            num_floors = dct_HPXML.get("geometry_unit_num_floors_above_grade")

        fb = ((dct_HPXML["geometry_unit_cfa"] /num_floors) *dct_HPXML["geometry_unit_aspect_ratio"])**0.5
        lr = (dct_HPXML["geometry_unit_cfa"] / num_floors) / fb
        length = fb
        width = lr
        #Si protusion de 1 on suppose que le garage est détaché 
        if dct_HPXML["geometry_garage_protrusion"]==1:
            garage_width = 12
            garage_depth = 22
            if garage_width>width:
                garage_width = width*0.75
            if garage_depth>length:
                garage_depth = length*0.75
        else:
            max_garage_depth = width / (1.0 - dct_HPXML["geometry_garage_protrusion"]) -1#length -1
            max_garage_width = length-1 #width / (1.0 - dct_HPXML["geometry_garage_protrusion"]) -1
            if max_garage_depth>24:
                garage_depth = 24 #12 / 24 / 36 taille du garage
            else:
                garage_depth = max_garage_depth*0.9

            #if max_garage_width>36:
            #    garage_width = 36 #12 / 24 / 36 taille du garage
            if max_garage_width>24:
                garage_width = 24
            elif max_garage_width>12:
                garage_width = 12
            else:
                garage_width = max_garage_width *0.8

            if dct_HPXML["geometry_unit_cfa"] <=2000:
                if garage_depth>12:
                    garage_depth =12
                if garage_width>20:
                    garage_width =20

        arg = "Presence_Garage"
        argHPXML = "geometry_garage_width"
        if (argHPXML not in dct_HPXML.keys()):
            if (arg in dct_args.keys()):
                if (dct_args[arg] in ["Garage non chauffé",
                                      "Garage chauffé à électricité",
                                      "Garage chauffé à autre source"]):
                    if (dct_HPXML.get("geometry_unit_type") in ["single-family detached"]):#, "single-family attached"]): Pas supporté pour les attached
                        dct_HPXML[argHPXML] = garage_width #12 / 24 / 36 taille du garage
                        #geometry_garage_depth
                        dct_HPXML["geometry_garage_depth"] = garage_depth
                        #geometry_garage_position
                        dct_HPXML["geometry_garage_position"] = "Right"
                    else:
                        dct_HPXML[argHPXML] = 0 #Pas de garage pour les plex/appartemnt # on pourrait les ajouter avec une protusion de 1 (garage détaché)
                        dct_HPXML["geometry_garage_depth"] = 0
                        #geometry_garage_position
                        dct_HPXML["geometry_garage_position"] = "Right"
                else:
                    dct_HPXML[argHPXML] = 0
                    dct_HPXML["geometry_garage_depth"] = 0
                    #geometry_garage_position
                    dct_HPXML["geometry_garage_position"] = "Right"
            else:
                if self.HPXMLArg.arguments[argHPXML].get("Default Value", "Defaut_Not_Existing")!="Defaut_Not_Existing":
                    dct_HPXML[argHPXML] = self.HPXMLArg.arguments[argHPXML].get("Default Value")
                    dct_HPXML["geometry_garage_depth"] = 0
                    #geometry_garage_position
                    dct_HPXML["geometry_garage_position"] = "Right"
                else:
                    dct_HPXML[argHPXML] = 0 #No garage
                    dct_HPXML["geometry_garage_depth"] = 0
                    #geometry_garage_position
                    dct_HPXML["geometry_garage_position"] = "Right"
   
            
        #_________________________________________________________________
        #"HVAC_Has_Shared_System"

        #_________________________________________________________________

        #_________________________________________________________________
        #Infiltration
        arg = "Infiltration"
        args = "air_leakage_units"
        if (args not in dct_HPXML.keys()):
            if (arg in dct_args.keys()):
                if dct_args[arg] in ["1 ACH50","2 ACH50","3 ACH50","4 ACH50","5 ACH50","6 ACH50","7 ACH50","8 ACH50","10 ACH50","15 ACH50","20 ACH50","25 ACH50","30 ACH50","40 ACH50","50 ACH50"]:
                    dct_HPXML[args] = 'ACH'
                else:   #defaut
                    if self.HPXMLArg.arguments[args].get("Default Value", "Defaut_Not_Existing")!="Defaut_Not_Existing":
                        dct_HPXML[args] = self.HPXMLArg.arguments[args].get("Default Value")
                    else:
                        dct_HPXML[args] = 'ACH'
            else:
                if self.HPXMLArg.arguments[args].get("Default Value", "Defaut_Not_Existing")!="Defaut_Not_Existing":
                    dct_HPXML[args] = self.HPXMLArg.arguments[args].get("Default Value")
                else:
                    dct_HPXML[args] = 'ACH'

        arg = "Infiltration"
        args = "air_leakage_house_pressure"
        if (args not in dct_HPXML.keys()):
            if (arg in dct_args.keys()):
                if dct_args[arg] in ["1 ACH50","2 ACH50","3 ACH50","4 ACH50","5 ACH50","6 ACH50","7 ACH50","8 ACH50","10 ACH50","15 ACH50","20 ACH50","25 ACH50","30 ACH50","40 ACH50","50 ACH50"]:
                    dct_HPXML[args] = 50
                else:
                    if self.HPXMLArg.arguments[args].get("Default Value", "Defaut_Not_Existing")!="Defaut_Not_Existing":
                        dct_HPXML[args] = self.HPXMLArg.arguments[args].get("Default Value")
                    else:
                        dct_HPXML[args] = 50
            else:
                if self.HPXMLArg.arguments[args].get("Default Value", "Defaut_Not_Existing")!="Defaut_Not_Existing":
                    dct_HPXML[args] = self.HPXMLArg.arguments[args].get("Default Value")
                else:
                    dct_HPXML[args] = 50

        arg = "Infiltration"
        args = "air_leakage_value"
        if (args not in dct_HPXML.keys()):
            if (arg in dct_args.keys()):
                if dct_args[arg] in ["1 ACH50","2 ACH50","3 ACH50","4 ACH50","5 ACH50","6 ACH50","7 ACH50","8 ACH50","10 ACH50","15 ACH50","20 ACH50","25 ACH50","30 ACH50","40 ACH50","50 ACH50"]:
                    dct_HPXML[args] = int(dct_args[arg].split(" ")[0]) #1,2,3,4,5,6,7,8,10,15,20,25,30,40,50
                else:#defaut
                    if self.HPXMLArg.arguments[args].get("Default Value", "Defaut_Not_Existing")!="Defaut_Not_Existing":
                        dct_HPXML[args] = self.HPXMLArg.arguments[args].get("Default Value")
                    else:
                        dct_HPXML[args] = 5#arbitraire

        #air_leakage_type
        arg = "Infiltration"
        args = "air_leakage_type"
        if (args not in dct_HPXML.keys()):
            if (arg in dct_args.keys()):
                if dct_args[arg] in ["Unit exterior only", "Unit exterior and interior"]:
                    dct_HPXML[args] = 'unit exterior only'
                else:
                    if self.HPXMLArg.arguments[args].get("Default Value", "Defaut_Not_Existing")!="Defaut_Not_Existing":
                        dct_HPXML[args] = self.HPXMLArg.arguments[args].get("Default Value")
                    else:
                        dct_HPXML[args] = 'unit exterior only'
            else:
                if self.HPXMLArg.arguments[args].get("Default Value", "Defaut_Not_Existing")!="Defaut_Not_Existing":
                    dct_HPXML[args] = self.HPXMLArg.arguments[args].get("Default Value")
                else:
                    dct_HPXML[args] = 'unit exterior only'
        
        #site_shielding_of_home
        arg = "Infiltration"
        args = "site_shielding_of_home"
        if (args not in dct_HPXML.keys()):
            if (arg in dct_args.keys()):
                if dct_args[arg] in ["Normal", "Windy"]:
                    dct_HPXML[args] = 'normal'
                else:
                    if self.HPXMLArg.arguments[args].get("Default Value", "Defaut_Not_Existing")!="Defaut_Not_Existing":
                        dct_HPXML[args] = self.HPXMLArg.arguments[args].get("Default Value")
                    else:
                        dct_HPXML[args] = 'normal'
            else:
                if self.HPXMLArg.arguments[args].get("Default Value", "Defaut_Not_Existing")!="Defaut_Not_Existing":
                    dct_HPXML[args] = self.HPXMLArg.arguments[args].get("Default Value")
                else:
                    dct_HPXML[args] = 'normal'


        #_________________________________________________________________
        # Wall Assembly R-Value

        dct_HPXML["wall_assembly_r"] += dct_HPXML["exterior_finish_r"]

        if "wall_continuous_exterior_r" in args and dct_HPXML["wall_continuous_exterior_r"] is not None:
            dct_HPXML["wall_assembly_r"] += dct_HPXML["wall_continuous_exterior_r"]

        dct_HPXML["rim_joist_assembly_r"] = 0
        if float(dct_HPXML["geometry_rim_joist_height"]) > 0:
            drywall_assembly_r = 0.9
            uninsulated_wall_assembly_r = 3.4

            assembly_exterior_r = dct_HPXML["exterior_finish_r"] + dct_HPXML["rim_joist_continuous_exterior_r"]

            if dct_HPXML["rim_joist_continuous_interior_r"] > 0 and dct_HPXML["rim_joist_assembly_interior_r"] > 0:
                # rim joist assembly = siding + half continuous interior insulation + half rim joist assembly - drywall
                # (rim joist assembly = nominal cavity + 1/2 in sheathing + 1/2 in drywall)
                assembly_interior_r = (
                    (dct_HPXML["rim_joist_continuous_interior_r"] + uninsulated_wall_assembly_r - drywall_assembly_r) / 2.0
                )  # parallel to floor joists
                assembly_interior_r += dct_HPXML["rim_joist_assembly_interior_r"] / 2.0  # derated
            elif dct_HPXML["rim_joist_continuous_interior_r"] > 0 or dct_HPXML["rim_joist_assembly_interior_r"] > 0:
                raise ValueError(
                    "ResStockArguments: For rim joist interior insulation, must provide both continuous and assembly R-values."
                )
            else:# uninsulated interior
                # rim joist assembly = siding + continuous foundation insulation + uninsulated wall - drywall
                # (uninsulated wall is nominal cavity + 1/2 in sheathing + 1/2 in drywall)
                assembly_interior_r = uninsulated_wall_assembly_r - drywall_assembly_r

            rim_joist_assembly_r = assembly_exterior_r + assembly_interior_r
            dct_HPXML["rim_joist_assembly_r"] = rim_joist_assembly_r

        #_________________________________________________________________
        #__________________________________________________________________


        #____________________________________________________________
        #Corridor #source : fichier corridor.tsv 
        if (dct_args["Type_Logement"] in ["Collective"]):
            Corridor = "Double-Loaded Interior"
        elif (dct_args["Type_Logement"] in ["Duplex", "Triplex"]):
            Corridor = "Single Exterior Front"
        else:
            Corridor = "Not Applicable"

        #source : mesure.rb resstockargument
        if Corridor == "Double Exterior":
            geometry_corridor_position = "Double Exterior"
            geometry_corridor_width = 10
        elif Corridor == "Double-Loaded Interior":
            geometry_corridor_position = "Double-Loaded Interior"
            geometry_corridor_width = 10
        elif Corridor == "None":
            geometry_corridor_position = "None"
            geometry_corridor_width = 0
        elif Corridor == "Not Applicable":
            geometry_corridor_position = "None"
            geometry_corridor_width = 0
        elif Corridor == "Single Exterior Front":
            geometry_corridor_position = "Single Exterior (Front)"
            geometry_corridor_width = 10
   
        # Adiabatic Walls
        #simplification de measure.rb
        
        dct_HPXML["geometry_unit_left_wall_is_adiabatic"] = False
        dct_HPXML["geometry_unit_right_wall_is_adiabatic"] = False
        dct_HPXML["geometry_unit_front_wall_is_adiabatic"] = False
        dct_HPXML["geometry_unit_back_wall_is_adiabatic"] = False

        #old version
        #if (dct_HPXML.get("geometry_unit_type") in ["Collective"]):
        #    if geometry_corridor_position == "Double Exterior":
        #        dct_HPXML["geometry_unit_back_wall_is_adiabatic"] = True
        #    elif geometry_corridor_position == "Double-Loaded Interior":
        #        dct_HPXML["geometry_unit_front_wall_is_adiabatic"] = True
        #    elif geometry_corridor_position == "Single Exterior (Front)":
        #        dct_HPXML["geometry_unit_front_wall_is_adiabatic"] = False
        #    else:
        #        pass
        # afinir
        
        if dct_HPXML.get("geometry_unit_type") in ["apartment unit", "single-family attached" ]:#["Collective", "Triplex", "Duplex", "Maison en rangee"]:
            n_floors = dct_args["Geometry Stories"]
            n_units = dct_args["Geometry Building Number Units"]
            horiz_location = dct_args["Geometry Building Horizontal Location"]

            if (dct_HPXML.get("geometry_unit_type") in ["apartment unit"]):# ["Collective", "Triplex", "Duplex"]):
                n_units_per_floor = n_units / n_floors
                if ((n_units_per_floor >= 4) & ((geometry_corridor_position == 'Double Exterior') | (geometry_corridor_position == 'None'))):
                    has_rear_units = True
                    dct_HPXML["geometry_unit_back_wall_is_adiabatic"] = True
                elif ((n_units_per_floor >= 4) & (geometry_corridor_position == 'Double-Loaded Interior')):
                    has_rear_units = True
                    dct_HPXML["geometry_unit_front_wall_is_adiabatic"] = True
                elif ((n_units_per_floor == 2) & (horiz_location == 'None') & ((geometry_corridor_position == 'Double Exterior') | (geometry_corridor_position == 'None'))):
                    has_rear_units = True
                    dct_HPXML["geometry_unit_back_wall_is_adiabatic"] = True
                elif ((n_units_per_floor == 2) & (horiz_location == 'None') & (geometry_corridor_position == 'Double-Loaded Interior')):
                    has_rear_units = True
                    dct_HPXML["geometry_unit_front_wall_is_adiabatic"] = True
                elif (geometry_corridor_position == 'Single Exterior (Front)'):
                    has_rear_units = False
                    dct_HPXML["geometry_unit_front_wall_is_adiabatic"] = False
                else:
                    has_rear_units = False
                    dct_HPXML["geometry_unit_front_wall_is_adiabatic"] = False

                # Model exterior corridors as overhangs
                if (("Exterior" in geometry_corridor_position) and (geometry_corridor_width > 0)):
                    dct_HPXML["overhangs_front_depth"] = geometry_corridor_width
                    dct_HPXML["overhangs_front_distance_to_top_of_window"] = 1

            elif dct_HPXML.get("geometry_unit_type") in ["single-family attached"]:#["Maison en rangee"]:
                n_units_per_floor = n_units #n_units / n_floors
                has_rear_units = False
            else:
                pass
            if has_rear_units:
                unit_width = n_units_per_floor / 2
            else:
                unit_width = n_units_per_floor
            
            if (unit_width <= 1) & (horiz_location != 'None'):
                #runner.registerWarning("No #{horiz_location} location exists, setting horizontal location to 'None'")
                horiz_location = 'None'

            # Infiltration adjustment for SFA/MF units
            # Calculate exposed wall area ratio for the unit (unit exposed wall area
            # divided by average unit exposed wall area)

            ##A FAIRE
            if (n_units_per_floor <= 2) | (n_units_per_floor == 4 & has_rear_units): # No middle unit(s)
                exposed_wall_area_ratio = 1.0 # all units have same exterior wall area
            else: # Has middle unit(s)
                if has_rear_units:
                    n_end_units = 4 * n_floors
                    n_mid_units = n_units - n_end_units
                    n_bldg_fronts_backs = n_end_units + n_mid_units
                    n_bldg_sides = n_end_units
                else:
                    n_end_units = 2 * n_floors
                    n_mid_units = n_units - n_end_units
                    n_bldg_fronts_backs = n_end_units * 2 + n_mid_units * 2
                    n_bldg_sides = n_end_units
                
                if has_rear_units:
                    n_unit_fronts_backs = 1
                else:
                    n_unit_fronts_backs = 2
                
                if horiz_location in ['Middle']:
                    n_unit_sides = 0
                elif horiz_location in ['Left', 'Right']:
                    n_unit_sides = 1
                
                n_bldg_sides_equivalent = n_bldg_sides + n_bldg_fronts_backs * dct_HPXML["geometry_unit_aspect_ratio"]
                n_unit_sides_equivalent = n_unit_sides + n_unit_fronts_backs * dct_HPXML["geometry_unit_aspect_ratio"]
                exposed_wall_area_ratio = n_unit_sides_equivalent / (n_bldg_sides_equivalent / n_units)

            # Apply adjustment to infiltration value
            args = "air_leakage_value"
            if args in dct_HPXML.keys():
                dct_HPXML[args] = dct_HPXML[args] * exposed_wall_area_ratio


            if horiz_location == 'Left':
                dct_HPXML["geometry_unit_right_wall_is_adiabatic"] = True
            elif horiz_location == 'Middle':
                dct_HPXML["geometry_unit_left_wall_is_adiabatic"]  = True
                dct_HPXML["geometry_unit_right_wall_is_adiabatic"] = True
            elif horiz_location == 'Right':
                dct_HPXML["geometry_unit_left_wall_is_adiabatic"]  = True
            
        # Infiltration Reduction
        if "air_leakage_percent_reduction" in dct_HPXML.keys():
            if "air_leakage_value" in dct_HPXML.keys():
                dct_HPXML["air_leakage_value"] = dct_HPXML["air_leakage_value"] * (1.0 - dct_HPXML["air_leakage_percent_reduction"] / 100.0)
        
        #geometry_unit_level n'est pas dans le HPXML. variable intermédiaire
        # Adiabatic Floor/Ceiling
        #site_shielding_of_home
        #arg = "Geometry Building Level"
        #args = "geometry_unit_level"Geometry Building Level
        #if (args not in dct_HPXML.keys()):
        #    if (arg in dct_args.keys()):
        #        if dct_args[arg] in ["Bottom"]:
        #            dct_HPXML[args] = 'Bottom'
        #        elif dct_args[arg] in ["Top"]:
        #            dct_HPXML[args] = 'Top'
        #        elif dct_args[arg] in ["Middle"]:
        #            dct_HPXML[args] = 'Middle'
        #        else:
        #            pass
        #remplace dct_HPXML["geometry_unit_level"] par dct_args.get(arg)
        arg = ""
        if dct_args.get(arg) == 'Bottom':
            if dct_HPXML.get("geometry_unit_num_floors_above_grade") > 1: # this could be "bottom" of a 1-story building
                dct_HPXML["geometry_attic_type"] = "BelowApartment"
        elif dct_args.get(arg) == 'Middle':
            dct_HPXML["geometry_foundation_type"] = "AboveApartment"
            dct_HPXML["geometry_attic_type"] = "BelowApartment"
        elif dct_args.get(arg) == 'Top':
            dct_HPXML["geometry_foundation_type"] = "AboveApartment"

    #________________________________________________________________
    #geometry_corridor_position

    #corridor_position

    #FAIRE Les murs adiabatiques

                #"Territoire_HQ",
                #FAIT "Type_Logement",
                #FAIT "Nombre_Pieces",
                #FAIT "Nombre_Etages",
                #FAIT # "Superficie_Totale",
                #FAIT "Presence_SousSol",
                #FAIT "Nombre_Personnes",
                #FAIT "Presence_Garage",
                # "Mode_Occupation",
                # #"ConsoElecAn",
                # FAIT "An_Construction",
                # "Source_Energie_Chauf"
               
        
        #________________________________________________________________
        #geometry_corridor_width
        # apres les etage


                
        #Ajout de variables ResStockArguments similaire à optionlookup


        #Conversion de certaines logiques du code ResStockArguments en HPXMLArguments
        
        #conversion format des variable (str double...)
        #_________________________________________________________________
        #chauffage principale

        #Make dict only based on data - from code parse option_lookup
        dct_HVAC_Heating = {}
        dct_HVAC_Heating["ASHP, SEER 10, 6.2 HSPF"] = {"heating_system_type": "none", "heating_system_heating_efficiency": 0.0, "heating_system_heating_capacity": "auto", "heating_system_heating_autosizing_limit": "auto", "heating_system_fraction_heat_load_served": 1.0, "heating_system_has_flue_or_chimney": "auto", "heat_pump_type": "air-to-air", "heat_pump_heating_efficiency_type": "HSPF", "heat_pump_heating_efficiency": 6.2, "heat_pump_cooling_efficiency_type": "SEER", "heat_pump_cooling_efficiency": 10.0, "heat_pump_sizing_methodology": "ACCA", "heat_pump_sizing_is_duct_limited": "false", "heat_pump_backup_sizing_methodology": "auto", "heat_pump_heating_capacity": "auto", "heat_pump_heating_autosizing_limit": "auto", "heat_pump_fraction_heat_load_served": 1.0, "heat_pump_cooling_capacity": "auto", "heat_pump_cooling_autosizing_limit": "auto", "heat_pump_fraction_cool_load_served": 1.0, "heat_pump_backup_use_existing_system": "false", "heat_pump_backup_type": "integrated", "heat_pump_backup_fuel": "electricity", "heat_pump_backup_heating_efficiency": 1.0, "heat_pump_backup_heating_capacity": "auto", "heat_pump_backup_heating_autosizing_limit": "auto", "heat_pump_heating_capacity_retention_fraction": "auto", "heat_pump_heating_capacity_retention_temp": "auto", "heat_pump_is_ducted": "true", "heat_pump_backup_heating_lockout_temp": "auto", "heat_pump_compressor_lockout_temp": "auto", "heat_pump_cooling_compressor_type": "single stage", "heat_pump_cooling_sensible_heat_fraction": "auto", "heat_pump_crankcase_heater_watts": "auto", "geothermal_loop_configuration": "none", "geothermal_loop_borefield_configuration": "auto", "geothermal_loop_loop_flow": "auto", "geothermal_loop_boreholes_count": "auto", "geothermal_loop_boreholes_length": "auto", "geothermal_loop_boreholes_spacing": "auto", "geothermal_loop_boreholes_diameter": "auto", "geothermal_loop_grout_type": "auto", "geothermal_loop_pipe_type": "auto", "geothermal_loop_pipe_diameter": "auto"}
        dct_HVAC_Heating["ASHP, SEER 10.3, 7.0 HSPF"] = {"heating_system_type": "none", "heating_system_heating_efficiency": 0.0, "heating_system_heating_capacity": "auto", "heating_system_heating_autosizing_limit": "auto", "heating_system_fraction_heat_load_served": 1.0, "heating_system_has_flue_or_chimney": "auto", "heat_pump_type": "air-to-air", "heat_pump_heating_efficiency_type": "HSPF", "heat_pump_heating_efficiency": 7.0, "heat_pump_cooling_efficiency_type": "SEER", "heat_pump_cooling_efficiency": 10.3, "heat_pump_sizing_methodology": "ACCA", "heat_pump_sizing_is_duct_limited": "false", "heat_pump_backup_sizing_methodology": "auto", "heat_pump_heating_capacity": "auto", "heat_pump_heating_autosizing_limit": "auto", "heat_pump_fraction_heat_load_served": 1.0, "heat_pump_cooling_capacity": "auto", "heat_pump_cooling_autosizing_limit": "auto", "heat_pump_fraction_cool_load_served": 1.0, "heat_pump_backup_use_existing_system": "false", "heat_pump_backup_type": "integrated", "heat_pump_backup_fuel": "electricity", "heat_pump_backup_heating_efficiency": 1.0, "heat_pump_backup_heating_capacity": "auto", "heat_pump_backup_heating_autosizing_limit": "auto", "heat_pump_heating_capacity_retention_fraction": "auto", "heat_pump_heating_capacity_retention_temp": "auto", "heat_pump_is_ducted": "true", "heat_pump_backup_heating_lockout_temp": "auto", "heat_pump_compressor_lockout_temp": "auto", "heat_pump_cooling_compressor_type": "single stage", "heat_pump_cooling_sensible_heat_fraction": "auto", "heat_pump_crankcase_heater_watts": "auto", "geothermal_loop_configuration": "none", "geothermal_loop_borefield_configuration": "auto", "geothermal_loop_loop_flow": "auto", "geothermal_loop_boreholes_count": "auto", "geothermal_loop_boreholes_length": "auto", "geothermal_loop_boreholes_spacing": "auto", "geothermal_loop_boreholes_diameter": "auto", "geothermal_loop_grout_type": "auto", "geothermal_loop_pipe_type": "auto", "geothermal_loop_pipe_diameter": "auto"}
        dct_HVAC_Heating["ASHP, SEER 11.5, 7.5 HSPF"] = {"heating_system_type": "none", "heating_system_heating_efficiency": 0.0, "heating_system_heating_capacity": "auto", "heating_system_heating_autosizing_limit": "auto", "heating_system_fraction_heat_load_served": 1.0, "heating_system_has_flue_or_chimney": "auto", "heat_pump_type": "air-to-air", "heat_pump_heating_efficiency_type": "HSPF", "heat_pump_heating_efficiency": 7.5, "heat_pump_cooling_efficiency_type": "SEER", "heat_pump_cooling_efficiency": 11.5, "heat_pump_sizing_methodology": "ACCA", "heat_pump_sizing_is_duct_limited": "false", "heat_pump_backup_sizing_methodology": "auto", "heat_pump_heating_capacity": "auto", "heat_pump_heating_autosizing_limit": "auto", "heat_pump_fraction_heat_load_served": 1.0, "heat_pump_cooling_capacity": "auto", "heat_pump_cooling_autosizing_limit": "auto", "heat_pump_fraction_cool_load_served": 1.0, "heat_pump_backup_use_existing_system": "false", "heat_pump_backup_type": "integrated", "heat_pump_backup_fuel": "electricity", "heat_pump_backup_heating_efficiency": 1.0, "heat_pump_backup_heating_capacity": "auto", "heat_pump_backup_heating_autosizing_limit": "auto", "heat_pump_heating_capacity_retention_fraction": "auto", "heat_pump_heating_capacity_retention_temp": "auto", "heat_pump_is_ducted": "true", "heat_pump_backup_heating_lockout_temp": "auto", "heat_pump_compressor_lockout_temp": "auto", "heat_pump_cooling_compressor_type": "single stage", "heat_pump_cooling_sensible_heat_fraction": "auto", "heat_pump_crankcase_heater_watts": "auto", "geothermal_loop_configuration": "none", "geothermal_loop_borefield_configuration": "auto", "geothermal_loop_loop_flow": "auto", "geothermal_loop_boreholes_count": "auto", "geothermal_loop_boreholes_length": "auto", "geothermal_loop_boreholes_spacing": "auto", "geothermal_loop_boreholes_diameter": "auto", "geothermal_loop_grout_type": "auto", "geothermal_loop_pipe_type": "auto", "geothermal_loop_pipe_diameter": "auto"}
        dct_HVAC_Heating["ASHP, SEER 13, 7.7 HSPF"] = {"heating_system_type": "none", "heating_system_heating_efficiency": 0.0, "heating_system_heating_capacity": "auto", "heating_system_heating_autosizing_limit": "auto", "heating_system_fraction_heat_load_served": 1.0, "heating_system_has_flue_or_chimney": "auto", "heat_pump_type": "air-to-air", "heat_pump_heating_efficiency_type": "HSPF", "heat_pump_heating_efficiency": 7.7, "heat_pump_cooling_efficiency_type": "SEER", "heat_pump_cooling_efficiency": 13.0, "heat_pump_sizing_methodology": "ACCA", "heat_pump_sizing_is_duct_limited": "false", "heat_pump_backup_sizing_methodology": "auto", "heat_pump_heating_capacity": "auto", "heat_pump_heating_autosizing_limit": "auto", "heat_pump_fraction_heat_load_served": 1.0, "heat_pump_cooling_capacity": "auto", "heat_pump_cooling_autosizing_limit": "auto", "heat_pump_fraction_cool_load_served": 1.0, "heat_pump_backup_use_existing_system": "false", "heat_pump_backup_type": "integrated", "heat_pump_backup_fuel": "electricity", "heat_pump_backup_heating_efficiency": 1.0, "heat_pump_backup_heating_capacity": "auto", "heat_pump_backup_heating_autosizing_limit": "auto", "heat_pump_heating_capacity_retention_fraction": "auto", "heat_pump_heating_capacity_retention_temp": "auto", "heat_pump_is_ducted": "true", "heat_pump_backup_heating_lockout_temp": "auto", "heat_pump_compressor_lockout_temp": "auto", "heat_pump_cooling_compressor_type": "single stage", "heat_pump_cooling_sensible_heat_fraction": "auto", "heat_pump_crankcase_heater_watts": "auto", "geothermal_loop_configuration": "none", "geothermal_loop_borefield_configuration": "auto", "geothermal_loop_loop_flow": "auto", "geothermal_loop_boreholes_count": "auto", "geothermal_loop_boreholes_length": "auto", "geothermal_loop_boreholes_spacing": "auto", "geothermal_loop_boreholes_diameter": "auto", "geothermal_loop_grout_type": "auto", "geothermal_loop_pipe_type": "auto", "geothermal_loop_pipe_diameter": "auto"}
        dct_HVAC_Heating["ASHP, SEER 13, 8.0 HSPF"] = {"heating_system_type": "none", "heating_system_heating_efficiency": 0.0, "heating_system_heating_capacity": "auto", "heating_system_heating_autosizing_limit": "auto", "heating_system_fraction_heat_load_served": 1.0, "heating_system_has_flue_or_chimney": "auto", "heat_pump_type": "air-to-air", "heat_pump_heating_efficiency_type": "HSPF", "heat_pump_heating_efficiency": 8.0, "heat_pump_cooling_efficiency_type": "SEER", "heat_pump_cooling_efficiency": 13.0, "heat_pump_sizing_methodology": "ACCA", "heat_pump_sizing_is_duct_limited": "false", "heat_pump_backup_sizing_methodology": "auto", "heat_pump_heating_capacity": "auto", "heat_pump_heating_autosizing_limit": "auto", "heat_pump_fraction_heat_load_served": 1.0, "heat_pump_cooling_capacity": "auto", "heat_pump_cooling_autosizing_limit": "auto", "heat_pump_fraction_cool_load_served": 1.0, "heat_pump_backup_use_existing_system": "false", "heat_pump_backup_type": "integrated", "heat_pump_backup_fuel": "electricity", "heat_pump_backup_heating_efficiency": 1.0, "heat_pump_backup_heating_capacity": "auto", "heat_pump_backup_heating_autosizing_limit": "auto", "heat_pump_heating_capacity_retention_fraction": "auto", "heat_pump_heating_capacity_retention_temp": "auto", "heat_pump_is_ducted": "true", "heat_pump_backup_heating_lockout_temp": "auto", "heat_pump_compressor_lockout_temp": "auto", "heat_pump_cooling_compressor_type": "single stage", "heat_pump_cooling_sensible_heat_fraction": "auto", "heat_pump_crankcase_heater_watts": "auto", "geothermal_loop_configuration": "none", "geothermal_loop_borefield_configuration": "auto", "geothermal_loop_loop_flow": "auto", "geothermal_loop_boreholes_count": "auto", "geothermal_loop_boreholes_length": "auto", "geothermal_loop_boreholes_spacing": "auto", "geothermal_loop_boreholes_diameter": "auto", "geothermal_loop_grout_type": "auto", "geothermal_loop_pipe_type": "auto", "geothermal_loop_pipe_diameter": "auto"}
        dct_HVAC_Heating["ASHP, SEER 14, 8.2 HSPF"] = {"heating_system_type": "none", "heating_system_heating_efficiency": 0.0, "heating_system_heating_capacity": "auto", "heating_system_heating_autosizing_limit": "auto", "heating_system_fraction_heat_load_served": 1.0, "heating_system_has_flue_or_chimney": "auto", "heat_pump_type": "air-to-air", "heat_pump_heating_efficiency_type": "HSPF", "heat_pump_heating_efficiency": 8.2, "heat_pump_cooling_efficiency_type": "SEER", "heat_pump_cooling_efficiency": 14.0, "heat_pump_sizing_methodology": "ACCA", "heat_pump_sizing_is_duct_limited": "false", "heat_pump_backup_sizing_methodology": "auto", "heat_pump_heating_capacity": "auto", "heat_pump_heating_autosizing_limit": "auto", "heat_pump_fraction_heat_load_served": 1.0, "heat_pump_cooling_capacity": "auto", "heat_pump_cooling_autosizing_limit": "auto", "heat_pump_fraction_cool_load_served": 1.0, "heat_pump_backup_use_existing_system": "false", "heat_pump_backup_type": "integrated", "heat_pump_backup_fuel": "electricity", "heat_pump_backup_heating_efficiency": 1.0, "heat_pump_backup_heating_capacity": "auto", "heat_pump_backup_heating_autosizing_limit": "auto", "heat_pump_heating_capacity_retention_fraction": "auto", "heat_pump_heating_capacity_retention_temp": "auto", "heat_pump_is_ducted": "true", "heat_pump_backup_heating_lockout_temp": "auto", "heat_pump_compressor_lockout_temp": "auto", "heat_pump_cooling_compressor_type": "single stage", "heat_pump_cooling_sensible_heat_fraction": "auto", "heat_pump_crankcase_heater_watts": "auto", "geothermal_loop_configuration": "none", "geothermal_loop_borefield_configuration": "auto", "geothermal_loop_loop_flow": "auto", "geothermal_loop_boreholes_count": "auto", "geothermal_loop_boreholes_length": "auto", "geothermal_loop_boreholes_spacing": "auto", "geothermal_loop_boreholes_diameter": "auto", "geothermal_loop_grout_type": "auto", "geothermal_loop_pipe_type": "auto", "geothermal_loop_pipe_diameter": "auto"}
        dct_HVAC_Heating["ASHP, SEER 14.3, 8.5 HSPF"] = {"heating_system_type": "none", "heating_system_heating_efficiency": 0.0, "heating_system_heating_capacity": "auto", "heating_system_heating_autosizing_limit": "auto", "heating_system_fraction_heat_load_served": 1.0, "heating_system_has_flue_or_chimney": "auto", "heat_pump_type": "air-to-air", "heat_pump_heating_efficiency_type": "HSPF", "heat_pump_heating_efficiency": 8.5, "heat_pump_cooling_efficiency_type": "SEER", "heat_pump_cooling_efficiency": 14.3, "heat_pump_sizing_methodology": "ACCA", "heat_pump_sizing_is_duct_limited": "false", "heat_pump_backup_sizing_methodology": "auto", "heat_pump_heating_capacity": "auto", "heat_pump_heating_autosizing_limit": "auto", "heat_pump_fraction_heat_load_served": 1.0, "heat_pump_cooling_capacity": "auto", "heat_pump_cooling_autosizing_limit": "auto", "heat_pump_fraction_cool_load_served": 1.0, "heat_pump_backup_use_existing_system": "false", "heat_pump_backup_type": "integrated", "heat_pump_backup_fuel": "electricity", "heat_pump_backup_heating_efficiency": 1.0, "heat_pump_backup_heating_capacity": "auto", "heat_pump_backup_heating_autosizing_limit": "auto", "heat_pump_heating_capacity_retention_fraction": "auto", "heat_pump_heating_capacity_retention_temp": "auto", "heat_pump_is_ducted": "true", "heat_pump_backup_heating_lockout_temp": "auto", "heat_pump_compressor_lockout_temp": "auto", "heat_pump_cooling_compressor_type": "single stage", "heat_pump_cooling_sensible_heat_fraction": "auto", "heat_pump_crankcase_heater_watts": "auto", "geothermal_loop_configuration": "none", "geothermal_loop_borefield_configuration": "auto", "geothermal_loop_loop_flow": "auto", "geothermal_loop_boreholes_count": "auto", "geothermal_loop_boreholes_length": "auto", "geothermal_loop_boreholes_spacing": "auto", "geothermal_loop_boreholes_diameter": "auto", "geothermal_loop_grout_type": "auto", "geothermal_loop_pipe_type": "auto", "geothermal_loop_pipe_diameter": "auto"}
        dct_HVAC_Heating["ASHP, SEER 15, 8.5 HSPF"] = {"heating_system_type": "none", "heating_system_heating_efficiency": 0.0, "heating_system_heating_capacity": "auto", "heating_system_heating_autosizing_limit": "auto", "heating_system_fraction_heat_load_served": 1.0, "heating_system_has_flue_or_chimney": "auto", "heat_pump_type": "air-to-air", "heat_pump_heating_efficiency_type": "HSPF", "heat_pump_heating_efficiency": 8.5, "heat_pump_cooling_efficiency_type": "SEER", "heat_pump_cooling_efficiency": 15.0, "heat_pump_sizing_methodology": "ACCA", "heat_pump_sizing_is_duct_limited": "false", "heat_pump_backup_sizing_methodology": "auto", "heat_pump_heating_capacity": "auto", "heat_pump_heating_autosizing_limit": "auto", "heat_pump_fraction_heat_load_served": 1.0, "heat_pump_cooling_capacity": "auto", "heat_pump_cooling_autosizing_limit": "auto", "heat_pump_fraction_cool_load_served": 1.0, "heat_pump_backup_use_existing_system": "false", "heat_pump_backup_type": "integrated", "heat_pump_backup_fuel": "electricity", "heat_pump_backup_heating_efficiency": 1.0, "heat_pump_backup_heating_capacity": "auto", "heat_pump_backup_heating_autosizing_limit": "auto", "heat_pump_heating_capacity_retention_fraction": "auto", "heat_pump_heating_capacity_retention_temp": "auto", "heat_pump_is_ducted": "true", "heat_pump_backup_heating_lockout_temp": "auto", "heat_pump_compressor_lockout_temp": "auto", "heat_pump_cooling_compressor_type": "single stage", "heat_pump_cooling_sensible_heat_fraction": "auto", "heat_pump_crankcase_heater_watts": "auto", "geothermal_loop_configuration": "none", "geothermal_loop_borefield_configuration": "auto", "geothermal_loop_loop_flow": "auto", "geothermal_loop_boreholes_count": "auto", "geothermal_loop_boreholes_length": "auto", "geothermal_loop_boreholes_spacing": "auto", "geothermal_loop_boreholes_diameter": "auto", "geothermal_loop_grout_type": "auto", "geothermal_loop_pipe_type": "auto", "geothermal_loop_pipe_diameter": "auto"}
        dct_HVAC_Heating["ASHP, SEER 15, 9.0 HSPF"] = {"heating_system_type": "none", "heating_system_heating_efficiency": 0.0, "heating_system_heating_capacity": "auto", "heating_system_heating_autosizing_limit": "auto", "heating_system_fraction_heat_load_served": 1.0, "heating_system_has_flue_or_chimney": "auto", "heat_pump_type": "air-to-air", "heat_pump_heating_efficiency_type": "HSPF", "heat_pump_heating_efficiency": 9.0, "heat_pump_cooling_efficiency_type": "SEER", "heat_pump_cooling_efficiency": 15.0, "heat_pump_sizing_methodology": "ACCA", "heat_pump_sizing_is_duct_limited": "false", "heat_pump_backup_sizing_methodology": "auto", "heat_pump_heating_capacity": "auto", "heat_pump_heating_autosizing_limit": "auto", "heat_pump_fraction_heat_load_served": 1.0, "heat_pump_cooling_capacity": "auto", "heat_pump_cooling_autosizing_limit": "auto", "heat_pump_fraction_cool_load_served": 1.0, "heat_pump_backup_use_existing_system": "false", "heat_pump_backup_type": "integrated", "heat_pump_backup_fuel": "electricity", "heat_pump_backup_heating_efficiency": 1.0, "heat_pump_backup_heating_capacity": "auto", "heat_pump_backup_heating_autosizing_limit": "auto", "heat_pump_heating_capacity_retention_fraction": "auto", "heat_pump_heating_capacity_retention_temp": "auto", "heat_pump_is_ducted": "true", "heat_pump_backup_heating_lockout_temp": "auto", "heat_pump_compressor_lockout_temp": "auto", "heat_pump_cooling_compressor_type": "single stage", "heat_pump_cooling_sensible_heat_fraction": "auto", "heat_pump_crankcase_heater_watts": "auto", "geothermal_loop_configuration": "none", "geothermal_loop_borefield_configuration": "auto", "geothermal_loop_loop_flow": "auto", "geothermal_loop_boreholes_count": "auto", "geothermal_loop_boreholes_length": "auto", "geothermal_loop_boreholes_spacing": "auto", "geothermal_loop_boreholes_diameter": "auto", "geothermal_loop_grout_type": "auto", "geothermal_loop_pipe_type": "auto", "geothermal_loop_pipe_diameter": "auto"}
        dct_HVAC_Heating["ASHP, SEER 16, 9.0 HSPF"] = {"heating_system_type": "none", "heating_system_heating_efficiency": 0.0, "heating_system_heating_capacity": "auto", "heating_system_heating_autosizing_limit": "auto", "heating_system_fraction_heat_load_served": 1.0, "heating_system_has_flue_or_chimney": "auto", "heat_pump_type": "air-to-air", "heat_pump_heating_efficiency_type": "HSPF", "heat_pump_heating_efficiency": 9.0, "heat_pump_cooling_efficiency_type": "SEER", "heat_pump_cooling_efficiency": 16.0, "heat_pump_sizing_methodology": "ACCA", "heat_pump_sizing_is_duct_limited": "false", "heat_pump_backup_sizing_methodology": "auto", "heat_pump_heating_capacity": "auto", "heat_pump_heating_autosizing_limit": "auto", "heat_pump_fraction_heat_load_served": 1.0, "heat_pump_cooling_capacity": "auto", "heat_pump_cooling_autosizing_limit": "auto", "heat_pump_fraction_cool_load_served": 1.0, "heat_pump_backup_use_existing_system": "false", "heat_pump_backup_type": "integrated", "heat_pump_backup_fuel": "electricity", "heat_pump_backup_heating_efficiency": 1.0, "heat_pump_backup_heating_capacity": "auto", "heat_pump_backup_heating_autosizing_limit": "auto", "heat_pump_heating_capacity_retention_fraction": "auto", "heat_pump_heating_capacity_retention_temp": "auto", "heat_pump_is_ducted": "true", "heat_pump_backup_heating_lockout_temp": "auto", "heat_pump_compressor_lockout_temp": "auto", "heat_pump_cooling_compressor_type": "single stage", "heat_pump_cooling_sensible_heat_fraction": "auto", "heat_pump_crankcase_heater_watts": "auto", "geothermal_loop_configuration": "none", "geothermal_loop_borefield_configuration": "auto", "geothermal_loop_loop_flow": "auto", "geothermal_loop_boreholes_count": "auto", "geothermal_loop_boreholes_length": "auto", "geothermal_loop_boreholes_spacing": "auto", "geothermal_loop_boreholes_diameter": "auto", "geothermal_loop_grout_type": "auto", "geothermal_loop_pipe_type": "auto", "geothermal_loop_pipe_diameter": "auto"}
        dct_HVAC_Heating["ASHP, SEER 16, 9.2 HSPF"] = {"heating_system_type": "none", "heating_system_heating_efficiency": 0.0, "heating_system_heating_capacity": "auto", "heating_system_heating_autosizing_limit": "auto", "heating_system_fraction_heat_load_served": 1.0, "heating_system_has_flue_or_chimney": "auto", "heat_pump_type": "air-to-air", "heat_pump_heating_efficiency_type": "HSPF", "heat_pump_heating_efficiency": 9.2, "heat_pump_cooling_efficiency_type": "SEER", "heat_pump_cooling_efficiency": 16.0, "heat_pump_sizing_methodology": "ACCA", "heat_pump_sizing_is_duct_limited": "false", "heat_pump_backup_sizing_methodology": "auto", "heat_pump_heating_capacity": "auto", "heat_pump_heating_autosizing_limit": "auto", "heat_pump_fraction_heat_load_served": 1.0, "heat_pump_cooling_capacity": "auto", "heat_pump_cooling_autosizing_limit": "auto", "heat_pump_fraction_cool_load_served": 1.0, "heat_pump_backup_use_existing_system": "false", "heat_pump_backup_type": "integrated", "heat_pump_backup_fuel": "electricity", "heat_pump_backup_heating_efficiency": 1.0, "heat_pump_backup_heating_capacity": "auto", "heat_pump_backup_heating_autosizing_limit": "auto", "heat_pump_heating_capacity_retention_fraction": 0.5, "heat_pump_heating_capacity_retention_temp": 5.0, "heat_pump_is_ducted": "true", "heat_pump_backup_heating_lockout_temp": "auto", "heat_pump_compressor_lockout_temp": "auto", "heat_pump_cooling_compressor_type": "single stage", "heat_pump_cooling_sensible_heat_fraction": "auto", "heat_pump_crankcase_heater_watts": "auto", "geothermal_loop_configuration": "none", "geothermal_loop_borefield_configuration": "auto", "geothermal_loop_loop_flow": "auto", "geothermal_loop_boreholes_count": "auto", "geothermal_loop_boreholes_length": "auto", "geothermal_loop_boreholes_spacing": "auto", "geothermal_loop_boreholes_diameter": "auto", "geothermal_loop_grout_type": "auto", "geothermal_loop_pipe_type": "auto", "geothermal_loop_pipe_diameter": "auto"}
        dct_HVAC_Heating["ASHP, SEER 16, 9.2 HSPF, Duct Limited"] = {"heating_system_type": "none", "heating_system_heating_efficiency": 0.0, "heating_system_heating_capacity": "auto", "heating_system_heating_autosizing_limit": "auto", "heating_system_fraction_heat_load_served": 1.0, "heating_system_has_flue_or_chimney": "auto", "heat_pump_type": "air-to-air", "heat_pump_heating_efficiency_type": "HSPF", "heat_pump_heating_efficiency": 9.2, "heat_pump_cooling_efficiency_type": "SEER", "heat_pump_cooling_efficiency": 16.0, "heat_pump_sizing_methodology": "ACCA", "heat_pump_sizing_is_duct_limited": "true", "heat_pump_backup_sizing_methodology": "auto", "heat_pump_heating_capacity": "auto", "heat_pump_heating_autosizing_limit": "auto", "heat_pump_fraction_heat_load_served": 1.0, "heat_pump_cooling_capacity": "auto", "heat_pump_cooling_autosizing_limit": "auto", "heat_pump_fraction_cool_load_served": 1.0, "heat_pump_backup_use_existing_system": "false", "heat_pump_backup_type": "integrated", "heat_pump_backup_fuel": "electricity", "heat_pump_backup_heating_efficiency": 1.0, "heat_pump_backup_heating_capacity": "auto", "heat_pump_backup_heating_autosizing_limit": "auto", "heat_pump_heating_capacity_retention_fraction": 0.5, "heat_pump_heating_capacity_retention_temp": 5.0, "heat_pump_is_ducted": "true", "heat_pump_backup_heating_lockout_temp": "auto", "heat_pump_compressor_lockout_temp": "auto", "heat_pump_cooling_compressor_type": "single stage", "heat_pump_cooling_sensible_heat_fraction": "auto", "heat_pump_crankcase_heater_watts": "auto", "geothermal_loop_configuration": "none", "geothermal_loop_borefield_configuration": "auto", "geothermal_loop_loop_flow": "auto", "geothermal_loop_boreholes_count": "auto", "geothermal_loop_boreholes_length": "auto", "geothermal_loop_boreholes_spacing": "auto", "geothermal_loop_boreholes_diameter": "auto", "geothermal_loop_grout_type": "auto", "geothermal_loop_pipe_type": "auto", "geothermal_loop_pipe_diameter": "auto"}
        dct_HVAC_Heating["ASHP, SEER 16, 9.2 HSPF, Existing Backup"] = {"heating_system_type": "none", "heating_system_heating_efficiency": 0.0, "heating_system_heating_capacity": "auto", "heating_system_heating_autosizing_limit": "auto", "heating_system_fraction_heat_load_served": 1.0, "heating_system_has_flue_or_chimney": "auto", "heat_pump_type": "air-to-air", "heat_pump_heating_efficiency_type": "HSPF", "heat_pump_heating_efficiency": 9.2, "heat_pump_cooling_efficiency_type": "SEER", "heat_pump_cooling_efficiency": 16.0, "heat_pump_sizing_methodology": "ACCA", "heat_pump_sizing_is_duct_limited": "false", "heat_pump_backup_sizing_methodology": "auto", "heat_pump_heating_capacity": "auto", "heat_pump_heating_autosizing_limit": "auto", "heat_pump_fraction_heat_load_served": 1.0, "heat_pump_cooling_capacity": "auto", "heat_pump_cooling_autosizing_limit": "auto", "heat_pump_fraction_cool_load_served": 1.0, "heat_pump_backup_use_existing_system": "true", "heat_pump_backup_type": "auto", "heat_pump_backup_fuel": "auto", "heat_pump_backup_heating_efficiency": "auto", "heat_pump_backup_heating_capacity": "auto", "heat_pump_backup_heating_autosizing_limit": "auto", "heat_pump_heating_capacity_retention_fraction": 0.5, "heat_pump_heating_capacity_retention_temp": 5.0, "heat_pump_is_ducted": "true", "heat_pump_backup_heating_lockout_temp": "auto", "heat_pump_compressor_lockout_temp": -20.0, "heat_pump_cooling_compressor_type": "single stage", "heat_pump_cooling_sensible_heat_fraction": "auto", "heat_pump_crankcase_heater_watts": "auto", "geothermal_loop_configuration": "none", "geothermal_loop_borefield_configuration": "auto", "geothermal_loop_loop_flow": "auto", "geothermal_loop_boreholes_count": "auto", "geothermal_loop_boreholes_length": "auto", "geothermal_loop_boreholes_spacing": "auto", "geothermal_loop_boreholes_diameter": "auto", "geothermal_loop_grout_type": "auto", "geothermal_loop_pipe_type": "auto", "geothermal_loop_pipe_diameter": "auto"}
        dct_HVAC_Heating["ASHP, SEER 16, 9.2 HSPF, Existing Backup, 5F-40F switchover band"] = {"heating_system_type": "none", "heating_system_heating_efficiency": 0.0, "heating_system_heating_capacity": "auto", "heating_system_heating_autosizing_limit": "auto", "heating_system_fraction_heat_load_served": 1.0, "heating_system_has_flue_or_chimney": "auto", "heat_pump_type": "air-to-air", "heat_pump_heating_efficiency_type": "HSPF", "heat_pump_heating_efficiency": 9.2, "heat_pump_cooling_efficiency_type": "SEER", "heat_pump_cooling_efficiency": 16.0, "heat_pump_sizing_methodology": "ACCA", "heat_pump_sizing_is_duct_limited": "false", "heat_pump_backup_sizing_methodology": "auto", "heat_pump_heating_capacity": "auto", "heat_pump_heating_autosizing_limit": "auto", "heat_pump_fraction_heat_load_served": 1.0, "heat_pump_cooling_capacity": "auto", "heat_pump_cooling_autosizing_limit": "auto", "heat_pump_fraction_cool_load_served": 1.0, "heat_pump_backup_use_existing_system": "true", "heat_pump_backup_type": "auto", "heat_pump_backup_fuel": "auto", "heat_pump_backup_heating_efficiency": "auto", "heat_pump_backup_heating_capacity": "auto", "heat_pump_backup_heating_autosizing_limit": "auto", "heat_pump_heating_capacity_retention_fraction": 0.5, "heat_pump_heating_capacity_retention_temp": 5.0, "heat_pump_is_ducted": "true", "heat_pump_backup_heating_lockout_temp": 40.0, "heat_pump_compressor_lockout_temp": 5.0, "heat_pump_cooling_compressor_type": "single stage", "heat_pump_cooling_sensible_heat_fraction": "auto", "heat_pump_crankcase_heater_watts": "auto", "geothermal_loop_configuration": "none", "geothermal_loop_borefield_configuration": "auto", "geothermal_loop_loop_flow": "auto", "geothermal_loop_boreholes_count": "auto", "geothermal_loop_boreholes_length": "auto", "geothermal_loop_boreholes_spacing": "auto", "geothermal_loop_boreholes_diameter": "auto", "geothermal_loop_grout_type": "auto", "geothermal_loop_pipe_type": "auto", "geothermal_loop_pipe_diameter": "auto"}
        dct_HVAC_Heating["ASHP, SEER 16, 9.2 HSPF, Existing Separate Backup"] = {"heating_system_type": "none", "heating_system_heating_efficiency": 0.0, "heating_system_heating_capacity": "auto", "heating_system_heating_autosizing_limit": "auto", "heating_system_fraction_heat_load_served": 1.0, "heating_system_has_flue_or_chimney": "auto", "heat_pump_type": "air-to-air", "heat_pump_heating_efficiency_type": "HSPF", "heat_pump_heating_efficiency": 9.2, "heat_pump_cooling_efficiency_type": "SEER", "heat_pump_cooling_efficiency": 16.0, "heat_pump_sizing_methodology": "ACCA", "heat_pump_sizing_is_duct_limited": "false", "heat_pump_backup_sizing_methodology": "auto", "heat_pump_heating_capacity": "auto", "heat_pump_heating_autosizing_limit": "auto", "heat_pump_fraction_heat_load_served": 1.0, "heat_pump_cooling_capacity": "auto", "heat_pump_cooling_autosizing_limit": "auto", "heat_pump_fraction_cool_load_served": 1.0, "heat_pump_backup_use_existing_system": "true", "heat_pump_backup_type": "separate", "heat_pump_backup_fuel": "auto", "heat_pump_backup_heating_efficiency": "auto", "heat_pump_backup_heating_capacity": "auto", "heat_pump_backup_heating_autosizing_limit": "auto", "heat_pump_heating_capacity_retention_fraction": 0.5, "heat_pump_heating_capacity_retention_temp": 5.0, "heat_pump_is_ducted": "true", "heat_pump_backup_heating_lockout_temp": "auto", "heat_pump_compressor_lockout_temp": -20.0, "heat_pump_cooling_compressor_type": "single stage", "heat_pump_cooling_sensible_heat_fraction": "auto", "heat_pump_crankcase_heater_watts": "auto", "geothermal_loop_configuration": "none", "geothermal_loop_borefield_configuration": "auto", "geothermal_loop_loop_flow": "auto", "geothermal_loop_boreholes_count": "auto", "geothermal_loop_boreholes_length": "auto", "geothermal_loop_boreholes_spacing": "auto", "geothermal_loop_boreholes_diameter": "auto", "geothermal_loop_grout_type": "auto", "geothermal_loop_pipe_type": "auto", "geothermal_loop_pipe_diameter": "auto"}
        dct_HVAC_Heating["ASHP, SEER 17, 8.7 HSPF"] = {"heating_system_type": "none", "heating_system_heating_efficiency": 0.0, "heating_system_heating_capacity": "auto", "heating_system_heating_autosizing_limit": "auto", "heating_system_fraction_heat_load_served": 1.0, "heating_system_has_flue_or_chimney": "auto", "heat_pump_type": "air-to-air", "heat_pump_heating_efficiency_type": "HSPF", "heat_pump_heating_efficiency": 8.7, "heat_pump_cooling_efficiency_type": "SEER", "heat_pump_cooling_efficiency": 17.0, "heat_pump_sizing_methodology": "ACCA", "heat_pump_sizing_is_duct_limited": "false", "heat_pump_backup_sizing_methodology": "auto", "heat_pump_heating_capacity": "auto", "heat_pump_heating_autosizing_limit": "auto", "heat_pump_fraction_heat_load_served": 1.0, "heat_pump_cooling_capacity": "auto", "heat_pump_cooling_autosizing_limit": "auto", "heat_pump_fraction_cool_load_served": 1.0, "heat_pump_backup_use_existing_system": "false", "heat_pump_backup_type": "integrated", "heat_pump_backup_fuel": "electricity", "heat_pump_backup_heating_efficiency": 1.0, "heat_pump_backup_heating_capacity": "auto", "heat_pump_backup_heating_autosizing_limit": "auto", "heat_pump_heating_capacity_retention_fraction": "auto", "heat_pump_heating_capacity_retention_temp": "auto", "heat_pump_is_ducted": "true", "heat_pump_backup_heating_lockout_temp": "auto", "heat_pump_compressor_lockout_temp": "auto", "heat_pump_cooling_compressor_type": "two stage", "heat_pump_cooling_sensible_heat_fraction": "auto", "heat_pump_crankcase_heater_watts": "auto", "geothermal_loop_configuration": "none", "geothermal_loop_borefield_configuration": "auto", "geothermal_loop_loop_flow": "auto", "geothermal_loop_boreholes_count": "auto", "geothermal_loop_boreholes_length": "auto", "geothermal_loop_boreholes_spacing": "auto", "geothermal_loop_boreholes_diameter": "auto", "geothermal_loop_grout_type": "auto", "geothermal_loop_pipe_type": "auto", "geothermal_loop_pipe_diameter": "auto"}
        dct_HVAC_Heating["ASHP, SEER 18, 9.3 HSPF"] = {"heating_system_type": "none", "heating_system_heating_efficiency": 0.0, "heating_system_heating_capacity": "auto", "heating_system_heating_autosizing_limit": "auto", "heating_system_fraction_heat_load_served": 1.0, "heating_system_has_flue_or_chimney": "auto", "heat_pump_type": "air-to-air", "heat_pump_heating_efficiency_type": "HSPF", "heat_pump_heating_efficiency": 9.3, "heat_pump_cooling_efficiency_type": "SEER", "heat_pump_cooling_efficiency": 18.0, "heat_pump_sizing_methodology": "ACCA", "heat_pump_sizing_is_duct_limited": "false", "heat_pump_backup_sizing_methodology": "auto", "heat_pump_heating_capacity": "auto", "heat_pump_heating_autosizing_limit": "auto", "heat_pump_fraction_heat_load_served": 1.0, "heat_pump_cooling_capacity": "auto", "heat_pump_cooling_autosizing_limit": "auto", "heat_pump_fraction_cool_load_served": 1.0, "heat_pump_backup_use_existing_system": "false", "heat_pump_backup_type": "integrated", "heat_pump_backup_fuel": "electricity", "heat_pump_backup_heating_efficiency": 1.0, "heat_pump_backup_heating_capacity": "auto", "heat_pump_backup_heating_autosizing_limit": "auto", "heat_pump_heating_capacity_retention_fraction": "auto", "heat_pump_heating_capacity_retention_temp": "auto", "heat_pump_is_ducted": "true", "heat_pump_backup_heating_lockout_temp": "auto", "heat_pump_compressor_lockout_temp": "auto", "heat_pump_cooling_compressor_type": "two stage", "heat_pump_cooling_sensible_heat_fraction": "auto", "heat_pump_crankcase_heater_watts": "auto", "geothermal_loop_configuration": "none", "geothermal_loop_borefield_configuration": "auto", "geothermal_loop_loop_flow": "auto", "geothermal_loop_boreholes_count": "auto", "geothermal_loop_boreholes_length": "auto", "geothermal_loop_boreholes_spacing": "auto", "geothermal_loop_boreholes_diameter": "auto", "geothermal_loop_grout_type": "auto", "geothermal_loop_pipe_type": "auto", "geothermal_loop_pipe_diameter": "auto"}
        dct_HVAC_Heating["ASHP, SEER 20, 11 HSPF, CCHP, Max Load"] = {"heating_system_type": "none", "heating_system_heating_efficiency": 0.0, "heating_system_heating_capacity": "auto", "heating_system_heating_autosizing_limit": "auto", "heating_system_fraction_heat_load_served": 1.0, "heating_system_has_flue_or_chimney": "auto", "heat_pump_type": "air-to-air", "heat_pump_heating_efficiency_type": "HSPF", "heat_pump_heating_efficiency": 11.0, "heat_pump_cooling_efficiency_type": "SEER", "heat_pump_cooling_efficiency": 20.0, "heat_pump_sizing_methodology": "MaxLoad", "heat_pump_sizing_is_duct_limited": "false", "heat_pump_backup_sizing_methodology": "auto", "heat_pump_heating_capacity": "auto", "heat_pump_heating_autosizing_limit": "auto", "heat_pump_fraction_heat_load_served": 1.0, "heat_pump_cooling_capacity": "auto", "heat_pump_cooling_autosizing_limit": "auto", "heat_pump_fraction_cool_load_served": 1.0, "heat_pump_backup_use_existing_system": "false", "heat_pump_backup_type": "integrated", "heat_pump_backup_fuel": "electricity", "heat_pump_backup_heating_efficiency": 1.0, "heat_pump_backup_heating_capacity": "auto", "heat_pump_backup_heating_autosizing_limit": "auto", "heat_pump_heating_capacity_retention_fraction": 0.9, "heat_pump_heating_capacity_retention_temp": 5.0, "heat_pump_is_ducted": "true", "heat_pump_backup_heating_lockout_temp": "auto", "heat_pump_compressor_lockout_temp": "auto", "heat_pump_cooling_compressor_type": "variable speed", "heat_pump_cooling_sensible_heat_fraction": "auto", "heat_pump_crankcase_heater_watts": "auto", "geothermal_loop_configuration": "none", "geothermal_loop_borefield_configuration": "auto", "geothermal_loop_loop_flow": "auto", "geothermal_loop_boreholes_count": "auto", "geothermal_loop_boreholes_length": "auto", "geothermal_loop_boreholes_spacing": "auto", "geothermal_loop_boreholes_diameter": "auto", "geothermal_loop_grout_type": "auto", "geothermal_loop_pipe_type": "auto", "geothermal_loop_pipe_diameter": "auto"}
        dct_HVAC_Heating["ASHP, SEER 22, 10 HSPF"] = {"heating_system_type": "none", "heating_system_heating_efficiency": 0.0, "heating_system_heating_capacity": "auto", "heating_system_heating_autosizing_limit": "auto", "heating_system_fraction_heat_load_served": 1.0, "heating_system_has_flue_or_chimney": "auto", "heat_pump_type": "air-to-air", "heat_pump_heating_efficiency_type": "HSPF", "heat_pump_heating_efficiency": 10.0, "heat_pump_cooling_efficiency_type": "SEER", "heat_pump_cooling_efficiency": 22.0, "heat_pump_sizing_methodology": "ACCA", "heat_pump_sizing_is_duct_limited": "false", "heat_pump_backup_sizing_methodology": "auto", "heat_pump_heating_capacity": "auto", "heat_pump_heating_autosizing_limit": "auto", "heat_pump_fraction_heat_load_served": 1.0, "heat_pump_cooling_capacity": "auto", "heat_pump_cooling_autosizing_limit": "auto", "heat_pump_fraction_cool_load_served": 1.0, "heat_pump_backup_use_existing_system": "false", "heat_pump_backup_type": "integrated", "heat_pump_backup_fuel": "electricity", "heat_pump_backup_heating_efficiency": 1.0, "heat_pump_backup_heating_capacity": "auto", "heat_pump_backup_heating_autosizing_limit": "auto", "heat_pump_heating_capacity_retention_fraction": "auto", "heat_pump_heating_capacity_retention_temp": "auto", "heat_pump_is_ducted": "true", "heat_pump_backup_heating_lockout_temp": "auto", "heat_pump_compressor_lockout_temp": "auto", "heat_pump_cooling_compressor_type": "variable speed", "heat_pump_cooling_sensible_heat_fraction": "auto", "heat_pump_crankcase_heater_watts": "auto", "geothermal_loop_configuration": "none", "geothermal_loop_borefield_configuration": "auto", "geothermal_loop_loop_flow": "auto", "geothermal_loop_boreholes_count": "auto", "geothermal_loop_boreholes_length": "auto", "geothermal_loop_boreholes_spacing": "auto", "geothermal_loop_boreholes_diameter": "auto", "geothermal_loop_grout_type": "auto", "geothermal_loop_pipe_type": "auto", "geothermal_loop_pipe_diameter": "auto"}
        dct_HVAC_Heating["ASHP, SEER 24, 13 HSPF, Max Load"] = {"heating_system_type": "none", "heating_system_heating_efficiency": 0.0, "heating_system_heating_capacity": "auto", "heating_system_heating_autosizing_limit": "auto", "heating_system_fraction_heat_load_served": 1.0, "heating_system_has_flue_or_chimney": "auto", "heat_pump_type": "air-to-air", "heat_pump_heating_efficiency_type": "HSPF", "heat_pump_heating_efficiency": 13.0, "heat_pump_cooling_efficiency_type": "SEER", "heat_pump_cooling_efficiency": 24.0, "heat_pump_sizing_methodology": "MaxLoad", "heat_pump_sizing_is_duct_limited": "false", "heat_pump_backup_sizing_methodology": "auto", "heat_pump_heating_capacity": "auto", "heat_pump_heating_autosizing_limit": "auto", "heat_pump_fraction_heat_load_served": 1.0, "heat_pump_cooling_capacity": "auto", "heat_pump_cooling_autosizing_limit": "auto", "heat_pump_fraction_cool_load_served": 1.0, "heat_pump_backup_use_existing_system": "false", "heat_pump_backup_type": "integrated", "heat_pump_backup_fuel": "electricity", "heat_pump_backup_heating_efficiency": 1.0, "heat_pump_backup_heating_capacity": "auto", "heat_pump_backup_heating_autosizing_limit": "auto", "heat_pump_heating_capacity_retention_fraction": 0.9, "heat_pump_heating_capacity_retention_temp": 5.0, "heat_pump_is_ducted": "true", "heat_pump_backup_heating_lockout_temp": "auto", "heat_pump_compressor_lockout_temp": "auto", "heat_pump_cooling_compressor_type": "variable speed", "heat_pump_cooling_sensible_heat_fraction": "auto", "heat_pump_crankcase_heater_watts": "auto", "geothermal_loop_configuration": "none", "geothermal_loop_borefield_configuration": "auto", "geothermal_loop_loop_flow": "auto", "geothermal_loop_boreholes_count": "auto", "geothermal_loop_boreholes_length": "auto", "geothermal_loop_boreholes_spacing": "auto", "geothermal_loop_boreholes_diameter": "auto", "geothermal_loop_grout_type": "auto", "geothermal_loop_pipe_type": "auto", "geothermal_loop_pipe_diameter": "auto"}
        dct_HVAC_Heating["ASHP, SEER 24, 13 HSPF, Max Load, Duct Limited"] = {"heating_system_type": "none", "heating_system_heating_efficiency": 0.0, "heating_system_heating_capacity": "auto", "heating_system_heating_autosizing_limit": "auto", "heating_system_fraction_heat_load_served": 1.0, "heating_system_has_flue_or_chimney": "auto", "heat_pump_type": "air-to-air", "heat_pump_heating_efficiency_type": "HSPF", "heat_pump_heating_efficiency": 13.0, "heat_pump_cooling_efficiency_type": "SEER", "heat_pump_cooling_efficiency": 24.0, "heat_pump_sizing_methodology": "MaxLoad", "heat_pump_sizing_is_duct_limited": "true", "heat_pump_backup_sizing_methodology": "auto", "heat_pump_heating_capacity": "auto", "heat_pump_heating_autosizing_limit": "auto", "heat_pump_fraction_heat_load_served": 1.0, "heat_pump_cooling_capacity": "auto", "heat_pump_cooling_autosizing_limit": "auto", "heat_pump_fraction_cool_load_served": 1.0, "heat_pump_backup_use_existing_system": "false", "heat_pump_backup_type": "integrated", "heat_pump_backup_fuel": "electricity", "heat_pump_backup_heating_efficiency": 1.0, "heat_pump_backup_heating_capacity": "auto", "heat_pump_backup_heating_autosizing_limit": "auto", "heat_pump_heating_capacity_retention_fraction": 0.9, "heat_pump_heating_capacity_retention_temp": 5.0, "heat_pump_is_ducted": "true", "heat_pump_backup_heating_lockout_temp": "auto", "heat_pump_compressor_lockout_temp": "auto", "heat_pump_cooling_compressor_type": "variable speed", "heat_pump_cooling_sensible_heat_fraction": "auto", "heat_pump_crankcase_heater_watts": "auto", "geothermal_loop_configuration": "none", "geothermal_loop_borefield_configuration": "auto", "geothermal_loop_loop_flow": "auto", "geothermal_loop_boreholes_count": "auto", "geothermal_loop_boreholes_length": "auto", "geothermal_loop_boreholes_spacing": "auto", "geothermal_loop_boreholes_diameter": "auto", "geothermal_loop_grout_type": "auto", "geothermal_loop_pipe_type": "auto", "geothermal_loop_pipe_diameter": "auto"}
        dct_HVAC_Heating["ASHP, SEER2 17.5, 8.5 HSPF2, Typical Cold Climate"] = {"heating_system_type": "none", "heating_system_heating_efficiency": 0.0, "heating_system_heating_capacity": "auto", "heating_system_heating_autosizing_limit": "auto", "heating_system_fraction_heat_load_served": 1.0, "heating_system_has_flue_or_chimney": "auto", "heat_pump_type": "air-to-air", "heat_pump_heating_efficiency_type": "HSPF2", "heat_pump_heating_efficiency": 8.5, "heat_pump_cooling_efficiency_type": "SEER2", "heat_pump_cooling_efficiency": 17.5, "heat_pump_sizing_methodology": "MaxLoad", "heat_pump_sizing_is_duct_limited": "false", "heat_pump_backup_sizing_methodology": "auto", "heat_pump_heating_capacity": "auto", "heat_pump_heating_autosizing_limit": "auto", "heat_pump_fraction_heat_load_served": 1.0, "heat_pump_cooling_capacity": "auto", "heat_pump_cooling_autosizing_limit": "auto", "heat_pump_fraction_cool_load_served": 1.0, "heat_pump_backup_use_existing_system": "false", "heat_pump_backup_type": "integrated", "heat_pump_backup_fuel": "electricity", "heat_pump_backup_heating_efficiency": 1.0, "heat_pump_backup_heating_capacity": "auto", "heat_pump_backup_heating_autosizing_limit": "auto", "heat_pump_heating_capacity_retention_fraction": 0.7, "heat_pump_heating_capacity_retention_temp": 5.0, "heat_pump_is_ducted": "true", "heat_pump_backup_heating_lockout_temp": "auto", "heat_pump_compressor_lockout_temp": -15.0, "heat_pump_cooling_compressor_type": "variable speed", "heat_pump_cooling_sensible_heat_fraction": "auto", "heat_pump_crankcase_heater_watts": "auto", "geothermal_loop_configuration": "none", "geothermal_loop_borefield_configuration": "auto", "geothermal_loop_loop_flow": "auto", "geothermal_loop_boreholes_count": "auto", "geothermal_loop_boreholes_length": "auto", "geothermal_loop_boreholes_spacing": "auto", "geothermal_loop_boreholes_diameter": "auto", "geothermal_loop_grout_type": "auto", "geothermal_loop_pipe_type": "auto", "geothermal_loop_pipe_diameter": "auto"}
        dct_HVAC_Heating["Dual-Fuel ASHP, SEER 14, 8.2 HSPF"] = {"heating_system_type": "none", "heating_system_heating_efficiency": 0.0, "heating_system_heating_capacity": "auto", "heating_system_heating_autosizing_limit": "auto", "heating_system_fraction_heat_load_served": 1.0, "heating_system_has_flue_or_chimney": "auto", "heat_pump_type": "air-to-air", "heat_pump_heating_efficiency_type": "HSPF", "heat_pump_heating_efficiency": 8.2, "heat_pump_cooling_efficiency_type": "SEER", "heat_pump_cooling_efficiency": 14.0, "heat_pump_sizing_methodology": "ACCA", "heat_pump_sizing_is_duct_limited": "false", "heat_pump_backup_sizing_methodology": "auto", "heat_pump_heating_capacity": "auto", "heat_pump_heating_autosizing_limit": "auto", "heat_pump_fraction_heat_load_served": 1.0, "heat_pump_cooling_capacity": "auto", "heat_pump_cooling_autosizing_limit": "auto", "heat_pump_fraction_cool_load_served": 1.0, "heat_pump_backup_use_existing_system": "false", "heat_pump_backup_type": "integrated", "heat_pump_backup_fuel": "natural gas", "heat_pump_backup_heating_efficiency": 1.0, "heat_pump_backup_heating_capacity": "auto", "heat_pump_backup_heating_autosizing_limit": "auto", "heat_pump_heating_capacity_retention_fraction": "auto", "heat_pump_heating_capacity_retention_temp": "auto", "heat_pump_is_ducted": "true", "heat_pump_backup_heating_lockout_temp": "auto", "heat_pump_compressor_lockout_temp": "auto", "heat_pump_cooling_compressor_type": "single stage", "heat_pump_cooling_sensible_heat_fraction": "auto", "heat_pump_crankcase_heater_watts": "auto", "geothermal_loop_configuration": "none", "geothermal_loop_borefield_configuration": "auto", "geothermal_loop_loop_flow": "auto", "geothermal_loop_boreholes_count": "auto", "geothermal_loop_boreholes_length": "auto", "geothermal_loop_boreholes_spacing": "auto", "geothermal_loop_boreholes_diameter": "auto", "geothermal_loop_grout_type": "auto", "geothermal_loop_pipe_type": "auto", "geothermal_loop_pipe_diameter": "auto"}
        dct_HVAC_Heating["Electric Baseboard, 100% Efficiency"] = {"heating_system_type": "ElectricResistance", "heating_system_heating_efficiency": 1.0, "heating_system_heating_capacity": "auto", "heating_system_heating_autosizing_limit": "auto", "heating_system_fraction_heat_load_served": 1.0, "heating_system_has_flue_or_chimney": "auto", "heat_pump_type": "none", "heat_pump_heating_efficiency_type": "HSPF", "heat_pump_heating_efficiency": 0.0, "heat_pump_cooling_efficiency_type": "SEER", "heat_pump_cooling_efficiency": 0.0, "heat_pump_sizing_methodology": "ACCA", "heat_pump_sizing_is_duct_limited": "false", "heat_pump_backup_sizing_methodology": "auto", "heat_pump_heating_capacity": "auto", "heat_pump_heating_autosizing_limit": "auto", "heat_pump_fraction_heat_load_served": 1.0, "heat_pump_cooling_capacity": "auto", "heat_pump_cooling_autosizing_limit": "auto", "heat_pump_fraction_cool_load_served": 1.0, "heat_pump_backup_use_existing_system": "false", "heat_pump_backup_type": "none", "heat_pump_backup_fuel": "electricity", "heat_pump_backup_heating_efficiency": 1.0, "heat_pump_backup_heating_capacity": "auto", "heat_pump_backup_heating_autosizing_limit": "auto", "geothermal_loop_configuration": "none", "geothermal_loop_borefield_configuration": "auto", "geothermal_loop_loop_flow": "auto", "geothermal_loop_boreholes_count": "auto", "geothermal_loop_boreholes_length": "auto", "geothermal_loop_boreholes_spacing": "auto", "geothermal_loop_boreholes_diameter": "auto", "geothermal_loop_grout_type": "auto", "geothermal_loop_pipe_type": "auto", "geothermal_loop_pipe_diameter": "auto"}
        dct_HVAC_Heating["Electric Boiler, 100% AFUE"] = {"heating_system_type": "Boiler", "heating_system_heating_efficiency": 1.0, "heating_system_heating_capacity": "auto", "heating_system_heating_autosizing_limit": "auto", "heating_system_fraction_heat_load_served": 1.0, "heating_system_has_flue_or_chimney": "auto", "heat_pump_type": "none", "heat_pump_heating_efficiency_type": "HSPF", "heat_pump_heating_efficiency": 0.0, "heat_pump_cooling_efficiency_type": "SEER", "heat_pump_cooling_efficiency": 0.0, "heat_pump_sizing_methodology": "ACCA", "heat_pump_sizing_is_duct_limited": "false", "heat_pump_backup_sizing_methodology": "auto", "heat_pump_heating_capacity": "auto", "heat_pump_heating_autosizing_limit": "auto", "heat_pump_fraction_heat_load_served": 1.0, "heat_pump_cooling_capacity": "auto", "heat_pump_cooling_autosizing_limit": "auto", "heat_pump_fraction_cool_load_served": 1.0, "heat_pump_backup_use_existing_system": "false", "heat_pump_backup_type": "none", "heat_pump_backup_fuel": "electricity", "heat_pump_backup_heating_efficiency": 1.0, "heat_pump_backup_heating_capacity": "auto", "heat_pump_backup_heating_autosizing_limit": "auto", "geothermal_loop_configuration": "none", "geothermal_loop_borefield_configuration": "auto", "geothermal_loop_loop_flow": "auto", "geothermal_loop_boreholes_count": "auto", "geothermal_loop_boreholes_length": "auto", "geothermal_loop_boreholes_spacing": "auto", "geothermal_loop_boreholes_diameter": "auto", "geothermal_loop_grout_type": "auto", "geothermal_loop_pipe_type": "auto", "geothermal_loop_pipe_diameter": "auto"}
        dct_HVAC_Heating["Electric Furnace, 100% AFUE"] = {"heating_system_type": "Furnace", "heating_system_heating_efficiency": 1.0, "heating_system_heating_capacity": "auto", "heating_system_heating_autosizing_limit": "auto", "heating_system_fraction_heat_load_served": 1.0, "heating_system_has_flue_or_chimney": "auto", "heat_pump_type": "none", "heat_pump_heating_efficiency_type": "HSPF", "heat_pump_heating_efficiency": 0.0, "heat_pump_cooling_efficiency_type": "SEER", "heat_pump_cooling_efficiency": 0.0, "heat_pump_sizing_methodology": "ACCA", "heat_pump_sizing_is_duct_limited": "false", "heat_pump_backup_sizing_methodology": "auto", "heat_pump_heating_capacity": "auto", "heat_pump_heating_autosizing_limit": "auto", "heat_pump_fraction_heat_load_served": 1.0, "heat_pump_cooling_capacity": "auto", "heat_pump_cooling_autosizing_limit": "auto", "heat_pump_fraction_cool_load_served": 1.0, "heat_pump_backup_use_existing_system": "false", "heat_pump_backup_type": "none", "heat_pump_backup_fuel": "electricity", "heat_pump_backup_heating_efficiency": 1.0, "heat_pump_backup_heating_capacity": "auto", "heat_pump_backup_heating_autosizing_limit": "auto", "geothermal_loop_configuration": "none", "geothermal_loop_borefield_configuration": "auto", "geothermal_loop_loop_flow": "auto", "geothermal_loop_boreholes_count": "auto", "geothermal_loop_boreholes_length": "auto", "geothermal_loop_boreholes_spacing": "auto", "geothermal_loop_boreholes_diameter": "auto", "geothermal_loop_grout_type": "auto", "geothermal_loop_pipe_type": "auto", "geothermal_loop_pipe_diameter": "auto"}
        dct_HVAC_Heating["Electric Wall Furnace, 100% AFUE"] = {"heating_system_type": "WallFurnace", "heating_system_heating_efficiency": 1.0, "heating_system_heating_capacity": "auto", "heating_system_heating_autosizing_limit": "auto", "heating_system_fraction_heat_load_served": 1.0, "heating_system_has_flue_or_chimney": "auto", "heat_pump_type": "none", "heat_pump_heating_efficiency_type": "HSPF", "heat_pump_heating_efficiency": 0.0, "heat_pump_cooling_efficiency_type": "SEER", "heat_pump_cooling_efficiency": 0.0, "heat_pump_sizing_methodology": "ACCA", "heat_pump_sizing_is_duct_limited": "false", "heat_pump_backup_sizing_methodology": "auto", "heat_pump_heating_capacity": "auto", "heat_pump_heating_autosizing_limit": "auto", "heat_pump_fraction_heat_load_served": 1.0, "heat_pump_cooling_capacity": "auto", "heat_pump_cooling_autosizing_limit": "auto", "heat_pump_fraction_cool_load_served": 1.0, "heat_pump_backup_use_existing_system": "false", "heat_pump_backup_type": "none", "heat_pump_backup_fuel": "electricity", "heat_pump_backup_heating_efficiency": 1.0, "heat_pump_backup_heating_capacity": "auto", "heat_pump_backup_heating_autosizing_limit": "auto", "geothermal_loop_configuration": "none", "geothermal_loop_borefield_configuration": "auto", "geothermal_loop_loop_flow": "auto", "geothermal_loop_boreholes_count": "auto", "geothermal_loop_boreholes_length": "auto", "geothermal_loop_boreholes_spacing": "auto", "geothermal_loop_boreholes_diameter": "auto", "geothermal_loop_grout_type": "auto", "geothermal_loop_pipe_type": "auto", "geothermal_loop_pipe_diameter": "auto"}
        dct_HVAC_Heating["Fuel Boiler, 72% AFUE"] = {"heating_system_type": "Boiler", "heating_system_heating_efficiency": 0.72, "heating_system_heating_capacity": "auto", "heating_system_heating_autosizing_limit": "auto", "heating_system_fraction_heat_load_served": 1.0, "heating_system_has_flue_or_chimney": "auto", "heat_pump_type": "none", "heat_pump_heating_efficiency_type": "HSPF", "heat_pump_heating_efficiency": 0.0, "heat_pump_cooling_efficiency_type": "SEER", "heat_pump_cooling_efficiency": 0.0, "heat_pump_sizing_methodology": "ACCA", "heat_pump_sizing_is_duct_limited": "false", "heat_pump_backup_sizing_methodology": "auto", "heat_pump_heating_capacity": "auto", "heat_pump_heating_autosizing_limit": "auto", "heat_pump_fraction_heat_load_served": 1.0, "heat_pump_cooling_capacity": "auto", "heat_pump_cooling_autosizing_limit": "auto", "heat_pump_fraction_cool_load_served": 1.0, "heat_pump_backup_use_existing_system": "false", "heat_pump_backup_type": "none", "heat_pump_backup_fuel": "electricity", "heat_pump_backup_heating_efficiency": 1.0, "heat_pump_backup_heating_capacity": "auto", "heat_pump_backup_heating_autosizing_limit": "auto", "heating_system_pilot_light": "auto", "geothermal_loop_configuration": "none", "geothermal_loop_borefield_configuration": "auto", "geothermal_loop_loop_flow": "auto", "geothermal_loop_boreholes_count": "auto", "geothermal_loop_boreholes_length": "auto", "geothermal_loop_boreholes_spacing": "auto", "geothermal_loop_boreholes_diameter": "auto", "geothermal_loop_grout_type": "auto", "geothermal_loop_pipe_type": "auto", "geothermal_loop_pipe_diameter": "auto"}
        dct_HVAC_Heating["Fuel Boiler, 76% AFUE"] = {"heating_system_type": "Boiler", "heating_system_heating_efficiency": 0.76, "heating_system_heating_capacity": "auto", "heating_system_heating_autosizing_limit": "auto", "heating_system_fraction_heat_load_served": 1.0, "heating_system_has_flue_or_chimney": "auto", "heat_pump_type": "none", "heat_pump_heating_efficiency_type": "HSPF", "heat_pump_heating_efficiency": 0.0, "heat_pump_cooling_efficiency_type": "SEER", "heat_pump_cooling_efficiency": 0.0, "heat_pump_sizing_methodology": "ACCA", "heat_pump_sizing_is_duct_limited": "false", "heat_pump_backup_sizing_methodology": "auto", "heat_pump_heating_capacity": "auto", "heat_pump_heating_autosizing_limit": "auto", "heat_pump_fraction_heat_load_served": 1.0, "heat_pump_cooling_capacity": "auto", "heat_pump_cooling_autosizing_limit": "auto", "heat_pump_fraction_cool_load_served": 1.0, "heat_pump_backup_use_existing_system": "false", "heat_pump_backup_type": "none", "heat_pump_backup_fuel": "electricity", "heat_pump_backup_heating_efficiency": 1.0, "heat_pump_backup_heating_capacity": "auto", "heat_pump_backup_heating_autosizing_limit": "auto", "heating_system_pilot_light": "auto", "geothermal_loop_configuration": "none", "geothermal_loop_borefield_configuration": "auto", "geothermal_loop_loop_flow": "auto", "geothermal_loop_boreholes_count": "auto", "geothermal_loop_boreholes_length": "auto", "geothermal_loop_boreholes_spacing": "auto", "geothermal_loop_boreholes_diameter": "auto", "geothermal_loop_grout_type": "auto", "geothermal_loop_pipe_type": "auto", "geothermal_loop_pipe_diameter": "auto"}
        dct_HVAC_Heating["Fuel Boiler, 80% AFUE"] = {"heating_system_type": "Boiler", "heating_system_heating_efficiency": 0.8, "heating_system_heating_capacity": "auto", "heating_system_heating_autosizing_limit": "auto", "heating_system_fraction_heat_load_served": 1.0, "heating_system_has_flue_or_chimney": "auto", "heat_pump_type": "none", "heat_pump_heating_efficiency_type": "HSPF", "heat_pump_heating_efficiency": 0.0, "heat_pump_cooling_efficiency_type": "SEER", "heat_pump_cooling_efficiency": 0.0, "heat_pump_sizing_methodology": "ACCA", "heat_pump_sizing_is_duct_limited": "false", "heat_pump_backup_sizing_methodology": "auto", "heat_pump_heating_capacity": "auto", "heat_pump_heating_autosizing_limit": "auto", "heat_pump_fraction_heat_load_served": 1.0, "heat_pump_cooling_capacity": "auto", "heat_pump_cooling_autosizing_limit": "auto", "heat_pump_fraction_cool_load_served": 1.0, "heat_pump_backup_use_existing_system": "false", "heat_pump_backup_type": "none", "heat_pump_backup_fuel": "electricity", "heat_pump_backup_heating_efficiency": 1.0, "heat_pump_backup_heating_capacity": "auto", "heat_pump_backup_heating_autosizing_limit": "auto", "heating_system_pilot_light": "auto", "geothermal_loop_configuration": "none", "geothermal_loop_borefield_configuration": "auto", "geothermal_loop_loop_flow": "auto", "geothermal_loop_boreholes_count": "auto", "geothermal_loop_boreholes_length": "auto", "geothermal_loop_boreholes_spacing": "auto", "geothermal_loop_boreholes_diameter": "auto", "geothermal_loop_grout_type": "auto", "geothermal_loop_pipe_type": "auto", "geothermal_loop_pipe_diameter": "auto"}
        dct_HVAC_Heating["Fuel Boiler, 82% AFUE"] = {"heating_system_type": "Boiler", "heating_system_heating_efficiency": 0.82, "heating_system_heating_capacity": "auto", "heating_system_heating_autosizing_limit": "auto", "heating_system_fraction_heat_load_served": 1.0, "heating_system_has_flue_or_chimney": "auto", "heat_pump_type": "none", "heat_pump_heating_efficiency_type": "HSPF", "heat_pump_heating_efficiency": 0.0, "heat_pump_cooling_efficiency_type": "SEER", "heat_pump_cooling_efficiency": 0.0, "heat_pump_sizing_methodology": "ACCA", "heat_pump_sizing_is_duct_limited": "false", "heat_pump_backup_sizing_methodology": "auto", "heat_pump_heating_capacity": "auto", "heat_pump_heating_autosizing_limit": "auto", "heat_pump_fraction_heat_load_served": 1.0, "heat_pump_cooling_capacity": "auto", "heat_pump_cooling_autosizing_limit": "auto", "heat_pump_fraction_cool_load_served": 1.0, "heat_pump_backup_use_existing_system": "false", "heat_pump_backup_type": "none", "heat_pump_backup_fuel": "electricity", "heat_pump_backup_heating_efficiency": 1.0, "heat_pump_backup_heating_capacity": "auto", "heat_pump_backup_heating_autosizing_limit": "auto", "heating_system_pilot_light": "auto", "geothermal_loop_configuration": "none", "geothermal_loop_borefield_configuration": "auto", "geothermal_loop_loop_flow": "auto", "geothermal_loop_boreholes_count": "auto", "geothermal_loop_boreholes_length": "auto", "geothermal_loop_boreholes_spacing": "auto", "geothermal_loop_boreholes_diameter": "auto", "geothermal_loop_grout_type": "auto", "geothermal_loop_pipe_type": "auto", "geothermal_loop_pipe_diameter": "auto"}
        dct_HVAC_Heating["Fuel Boiler, 85% AFUE"] = {"heating_system_type": "Boiler", "heating_system_heating_efficiency": 0.85, "heating_system_heating_capacity": "auto", "heating_system_heating_autosizing_limit": "auto", "heating_system_fraction_heat_load_served": 1.0, "heating_system_has_flue_or_chimney": "auto", "heat_pump_type": "none", "heat_pump_heating_efficiency_type": "HSPF", "heat_pump_heating_efficiency": 0.0, "heat_pump_cooling_efficiency_type": "SEER", "heat_pump_cooling_efficiency": 0.0, "heat_pump_sizing_methodology": "ACCA", "heat_pump_sizing_is_duct_limited": "false", "heat_pump_backup_sizing_methodology": "auto", "heat_pump_heating_capacity": "auto", "heat_pump_heating_autosizing_limit": "auto", "heat_pump_fraction_heat_load_served": 1.0, "heat_pump_cooling_capacity": "auto", "heat_pump_cooling_autosizing_limit": "auto", "heat_pump_fraction_cool_load_served": 1.0, "heat_pump_backup_use_existing_system": "false", "heat_pump_backup_type": "none", "heat_pump_backup_fuel": "electricity", "heat_pump_backup_heating_efficiency": 1.0, "heat_pump_backup_heating_capacity": "auto", "heat_pump_backup_heating_autosizing_limit": "auto", "heating_system_pilot_light": "auto", "geothermal_loop_configuration": "none", "geothermal_loop_borefield_configuration": "auto", "geothermal_loop_loop_flow": "auto", "geothermal_loop_boreholes_count": "auto", "geothermal_loop_boreholes_length": "auto", "geothermal_loop_boreholes_spacing": "auto", "geothermal_loop_boreholes_diameter": "auto", "geothermal_loop_grout_type": "auto", "geothermal_loop_pipe_type": "auto", "geothermal_loop_pipe_diameter": "auto"}
        dct_HVAC_Heating["Fuel Boiler, 90% AFUE"] = {"heating_system_type": "Boiler", "heating_system_heating_efficiency": 0.9, "heating_system_heating_capacity": "auto", "heating_system_heating_autosizing_limit": "auto", "heating_system_fraction_heat_load_served": 1.0, "heating_system_has_flue_or_chimney": "auto", "heat_pump_type": "none", "heat_pump_heating_efficiency_type": "HSPF", "heat_pump_heating_efficiency": 0.0, "heat_pump_cooling_efficiency_type": "SEER", "heat_pump_cooling_efficiency": 0.0, "heat_pump_sizing_methodology": "ACCA", "heat_pump_sizing_is_duct_limited": "false", "heat_pump_backup_sizing_methodology": "auto", "heat_pump_heating_capacity": "auto", "heat_pump_heating_autosizing_limit": "auto", "heat_pump_fraction_heat_load_served": 1.0, "heat_pump_cooling_capacity": "auto", "heat_pump_cooling_autosizing_limit": "auto", "heat_pump_fraction_cool_load_served": 1.0, "heat_pump_backup_use_existing_system": "false", "heat_pump_backup_type": "none", "heat_pump_backup_fuel": "electricity", "heat_pump_backup_heating_efficiency": 1.0, "heat_pump_backup_heating_capacity": "auto", "heat_pump_backup_heating_autosizing_limit": "auto", "heating_system_pilot_light": "auto", "geothermal_loop_configuration": "none", "geothermal_loop_borefield_configuration": "auto", "geothermal_loop_loop_flow": "auto", "geothermal_loop_boreholes_count": "auto", "geothermal_loop_boreholes_length": "auto", "geothermal_loop_boreholes_spacing": "auto", "geothermal_loop_boreholes_diameter": "auto", "geothermal_loop_grout_type": "auto", "geothermal_loop_pipe_type": "auto", "geothermal_loop_pipe_diameter": "auto"}
        dct_HVAC_Heating["Fuel Boiler, 95% AFUE, OAT Reset"] = {"heating_system_type": "Boiler", "heating_system_heating_efficiency": 0.95, "heating_system_heating_capacity": "auto", "heating_system_heating_autosizing_limit": "auto", "heating_system_fraction_heat_load_served": 1.0, "heating_system_has_flue_or_chimney": "auto", "heat_pump_type": "none", "heat_pump_heating_efficiency_type": "HSPF", "heat_pump_heating_efficiency": 0.0, "heat_pump_cooling_efficiency_type": "SEER", "heat_pump_cooling_efficiency": 0.0, "heat_pump_sizing_methodology": "ACCA", "heat_pump_sizing_is_duct_limited": "false", "heat_pump_backup_sizing_methodology": "auto", "heat_pump_heating_capacity": "auto", "heat_pump_heating_autosizing_limit": "auto", "heat_pump_fraction_heat_load_served": 1.0, "heat_pump_cooling_capacity": "auto", "heat_pump_cooling_autosizing_limit": "auto", "heat_pump_fraction_cool_load_served": 1.0, "heat_pump_backup_use_existing_system": "false", "heat_pump_backup_type": "none", "heat_pump_backup_fuel": "electricity", "heat_pump_backup_heating_efficiency": 1.0, "heat_pump_backup_heating_capacity": "auto", "heat_pump_backup_heating_autosizing_limit": "auto", "heating_system_pilot_light": "auto", "geothermal_loop_configuration": "none", "geothermal_loop_borefield_configuration": "auto", "geothermal_loop_loop_flow": "auto", "geothermal_loop_boreholes_count": "auto", "geothermal_loop_boreholes_length": "auto", "geothermal_loop_boreholes_spacing": "auto", "geothermal_loop_boreholes_diameter": "auto", "geothermal_loop_grout_type": "auto", "geothermal_loop_pipe_type": "auto", "geothermal_loop_pipe_diameter": "auto"}
        dct_HVAC_Heating["Fuel Boiler, 96% AFUE"] = {"heating_system_type": "Boiler", "heating_system_heating_efficiency": 0.96, "heating_system_heating_capacity": "auto", "heating_system_heating_autosizing_limit": "auto", "heating_system_fraction_heat_load_served": 1.0, "heating_system_has_flue_or_chimney": "auto", "heat_pump_type": "none", "heat_pump_heating_efficiency_type": "HSPF", "heat_pump_heating_efficiency": 0.0, "heat_pump_cooling_efficiency_type": "SEER", "heat_pump_cooling_efficiency": 0.0, "heat_pump_sizing_methodology": "ACCA", "heat_pump_sizing_is_duct_limited": "false", "heat_pump_backup_sizing_methodology": "auto", "heat_pump_heating_capacity": "auto", "heat_pump_heating_autosizing_limit": "auto", "heat_pump_fraction_heat_load_served": 1.0, "heat_pump_cooling_capacity": "auto", "heat_pump_cooling_autosizing_limit": "auto", "heat_pump_fraction_cool_load_served": 1.0, "heat_pump_backup_use_existing_system": "false", "heat_pump_backup_type": "none", "heat_pump_backup_fuel": "electricity", "heat_pump_backup_heating_efficiency": 1.0, "heat_pump_backup_heating_capacity": "auto", "heat_pump_backup_heating_autosizing_limit": "auto", "heating_system_pilot_light": "auto", "geothermal_loop_configuration": "none", "geothermal_loop_borefield_configuration": "auto", "geothermal_loop_loop_flow": "auto", "geothermal_loop_boreholes_count": "auto", "geothermal_loop_boreholes_length": "auto", "geothermal_loop_boreholes_spacing": "auto", "geothermal_loop_boreholes_diameter": "auto", "geothermal_loop_grout_type": "auto", "geothermal_loop_pipe_type": "auto", "geothermal_loop_pipe_diameter": "auto"}
        dct_HVAC_Heating["Fuel Furnace, 60% AFUE"] = {"heating_system_type": "Furnace", "heating_system_heating_efficiency": 0.6, "heating_system_heating_capacity": "auto", "heating_system_heating_autosizing_limit": "auto", "heating_system_fraction_heat_load_served": 1.0, "heating_system_has_flue_or_chimney": "auto", "heat_pump_type": "none", "heat_pump_heating_efficiency_type": "HSPF", "heat_pump_heating_efficiency": 0.0, "heat_pump_cooling_efficiency_type": "SEER", "heat_pump_cooling_efficiency": 0.0, "heat_pump_sizing_methodology": "ACCA", "heat_pump_sizing_is_duct_limited": "false", "heat_pump_backup_sizing_methodology": "auto", "heat_pump_heating_capacity": "auto", "heat_pump_heating_autosizing_limit": "auto", "heat_pump_fraction_heat_load_served": 1.0, "heat_pump_cooling_capacity": "auto", "heat_pump_cooling_autosizing_limit": "auto", "heat_pump_fraction_cool_load_served": 1.0, "heat_pump_backup_use_existing_system": "false", "heat_pump_backup_type": "none", "heat_pump_backup_fuel": "electricity", "heat_pump_backup_heating_efficiency": 1.0, "heat_pump_backup_heating_capacity": "auto", "heat_pump_backup_heating_autosizing_limit": "auto", "heating_system_pilot_light": "auto", "geothermal_loop_configuration": "none", "geothermal_loop_borefield_configuration": "auto", "geothermal_loop_loop_flow": "auto", "geothermal_loop_boreholes_count": "auto", "geothermal_loop_boreholes_length": "auto", "geothermal_loop_boreholes_spacing": "auto", "geothermal_loop_boreholes_diameter": "auto", "geothermal_loop_grout_type": "auto", "geothermal_loop_pipe_type": "auto", "geothermal_loop_pipe_diameter": "auto"}
        dct_HVAC_Heating["Fuel Furnace, 68% AFUE"] = {"heating_system_type": "Furnace", "heating_system_heating_efficiency": 0.68, "heating_system_heating_capacity": "auto", "heating_system_heating_autosizing_limit": "auto", "heating_system_fraction_heat_load_served": 1.0, "heating_system_has_flue_or_chimney": "auto", "heat_pump_type": "none", "heat_pump_heating_efficiency_type": "HSPF", "heat_pump_heating_efficiency": 0.0, "heat_pump_cooling_efficiency_type": "SEER", "heat_pump_cooling_efficiency": 0.0, "heat_pump_sizing_methodology": "ACCA", "heat_pump_sizing_is_duct_limited": "false", "heat_pump_backup_sizing_methodology": "auto", "heat_pump_heating_capacity": "auto", "heat_pump_heating_autosizing_limit": "auto", "heat_pump_fraction_heat_load_served": 1.0, "heat_pump_cooling_capacity": "auto", "heat_pump_cooling_autosizing_limit": "auto", "heat_pump_fraction_cool_load_served": 1.0, "heat_pump_backup_use_existing_system": "false", "heat_pump_backup_type": "none", "heat_pump_backup_fuel": "electricity", "heat_pump_backup_heating_efficiency": 1.0, "heat_pump_backup_heating_capacity": "auto", "heat_pump_backup_heating_autosizing_limit": "auto", "heating_system_pilot_light": "auto", "geothermal_loop_configuration": "none", "geothermal_loop_borefield_configuration": "auto", "geothermal_loop_loop_flow": "auto", "geothermal_loop_boreholes_count": "auto", "geothermal_loop_boreholes_length": "auto", "geothermal_loop_boreholes_spacing": "auto", "geothermal_loop_boreholes_diameter": "auto", "geothermal_loop_grout_type": "auto", "geothermal_loop_pipe_type": "auto", "geothermal_loop_pipe_diameter": "auto"}
        dct_HVAC_Heating["Fuel Furnace, 72% AFUE"] = {"heating_system_type": "Furnace", "heating_system_heating_efficiency": 0.72, "heating_system_heating_capacity": "auto", "heating_system_heating_autosizing_limit": "auto", "heating_system_fraction_heat_load_served": 1.0, "heating_system_has_flue_or_chimney": "auto", "heat_pump_type": "none", "heat_pump_heating_efficiency_type": "HSPF", "heat_pump_heating_efficiency": 0.0, "heat_pump_cooling_efficiency_type": "SEER", "heat_pump_cooling_efficiency": 0.0, "heat_pump_sizing_methodology": "ACCA", "heat_pump_sizing_is_duct_limited": "false", "heat_pump_backup_sizing_methodology": "auto", "heat_pump_heating_capacity": "auto", "heat_pump_heating_autosizing_limit": "auto", "heat_pump_fraction_heat_load_served": 1.0, "heat_pump_cooling_capacity": "auto", "heat_pump_cooling_autosizing_limit": "auto", "heat_pump_fraction_cool_load_served": 1.0, "heat_pump_backup_use_existing_system": "false", "heat_pump_backup_type": "none", "heat_pump_backup_fuel": "electricity", "heat_pump_backup_heating_efficiency": 1.0, "heat_pump_backup_heating_capacity": "auto", "heat_pump_backup_heating_autosizing_limit": "auto", "heating_system_pilot_light": "auto", "geothermal_loop_configuration": "none", "geothermal_loop_borefield_configuration": "auto", "geothermal_loop_loop_flow": "auto", "geothermal_loop_boreholes_count": "auto", "geothermal_loop_boreholes_length": "auto", "geothermal_loop_boreholes_spacing": "auto", "geothermal_loop_boreholes_diameter": "auto", "geothermal_loop_grout_type": "auto", "geothermal_loop_pipe_type": "auto", "geothermal_loop_pipe_diameter": "auto"}
        dct_HVAC_Heating["Fuel Furnace, 76% AFUE"] = {"heating_system_type": "Furnace", "heating_system_heating_efficiency": 0.76, "heating_system_heating_capacity": "auto", "heating_system_heating_autosizing_limit": "auto", "heating_system_fraction_heat_load_served": 1.0, "heating_system_has_flue_or_chimney": "auto", "heat_pump_type": "none", "heat_pump_heating_efficiency_type": "HSPF", "heat_pump_heating_efficiency": 0.0, "heat_pump_cooling_efficiency_type": "SEER", "heat_pump_cooling_efficiency": 0.0, "heat_pump_sizing_methodology": "ACCA", "heat_pump_sizing_is_duct_limited": "false", "heat_pump_backup_sizing_methodology": "auto", "heat_pump_heating_capacity": "auto", "heat_pump_heating_autosizing_limit": "auto", "heat_pump_fraction_heat_load_served": 1.0, "heat_pump_cooling_capacity": "auto", "heat_pump_cooling_autosizing_limit": "auto", "heat_pump_fraction_cool_load_served": 1.0, "heat_pump_backup_use_existing_system": "false", "heat_pump_backup_type": "none", "heat_pump_backup_fuel": "electricity", "heat_pump_backup_heating_efficiency": 1.0, "heat_pump_backup_heating_capacity": "auto", "heat_pump_backup_heating_autosizing_limit": "auto", "heating_system_pilot_light": "auto", "geothermal_loop_configuration": "none", "geothermal_loop_borefield_configuration": "auto", "geothermal_loop_loop_flow": "auto", "geothermal_loop_boreholes_count": "auto", "geothermal_loop_boreholes_length": "auto", "geothermal_loop_boreholes_spacing": "auto", "geothermal_loop_boreholes_diameter": "auto", "geothermal_loop_grout_type": "auto", "geothermal_loop_pipe_type": "auto", "geothermal_loop_pipe_diameter": "auto"}
        dct_HVAC_Heating["Fuel Furnace, 80% AFUE"] = {"heating_system_type": "Furnace", "heating_system_heating_efficiency": 0.8, "heating_system_heating_capacity": "auto", "heating_system_heating_autosizing_limit": "auto", "heating_system_fraction_heat_load_served": 1.0, "heating_system_has_flue_or_chimney": "auto", "heat_pump_type": "none", "heat_pump_heating_efficiency_type": "HSPF", "heat_pump_heating_efficiency": 0.0, "heat_pump_cooling_efficiency_type": "SEER", "heat_pump_cooling_efficiency": 0.0, "heat_pump_sizing_methodology": "ACCA", "heat_pump_sizing_is_duct_limited": "false", "heat_pump_backup_sizing_methodology": "auto", "heat_pump_heating_capacity": "auto", "heat_pump_heating_autosizing_limit": "auto", "heat_pump_fraction_heat_load_served": 1.0, "heat_pump_cooling_capacity": "auto", "heat_pump_cooling_autosizing_limit": "auto", "heat_pump_fraction_cool_load_served": 1.0, "heat_pump_backup_use_existing_system": "false", "heat_pump_backup_type": "none", "heat_pump_backup_fuel": "electricity", "heat_pump_backup_heating_efficiency": 1.0, "heat_pump_backup_heating_capacity": "auto", "heat_pump_backup_heating_autosizing_limit": "auto", "heating_system_pilot_light": "auto", "geothermal_loop_configuration": "none", "geothermal_loop_borefield_configuration": "auto", "geothermal_loop_loop_flow": "auto", "geothermal_loop_boreholes_count": "auto", "geothermal_loop_boreholes_length": "auto", "geothermal_loop_boreholes_spacing": "auto", "geothermal_loop_boreholes_diameter": "auto", "geothermal_loop_grout_type": "auto", "geothermal_loop_pipe_type": "auto", "geothermal_loop_pipe_diameter": "auto"}
        dct_HVAC_Heating["Fuel Furnace, 85% AFUE"] = {"heating_system_type": "Furnace", "heating_system_heating_efficiency": 0.85, "heating_system_heating_capacity": "auto", "heating_system_heating_autosizing_limit": "auto", "heating_system_fraction_heat_load_served": 1.0, "heating_system_has_flue_or_chimney": "auto", "heat_pump_type": "none", "heat_pump_heating_efficiency_type": "HSPF", "heat_pump_heating_efficiency": 0.0, "heat_pump_cooling_efficiency_type": "SEER", "heat_pump_cooling_efficiency": 0.0, "heat_pump_sizing_methodology": "ACCA", "heat_pump_sizing_is_duct_limited": "false", "heat_pump_backup_sizing_methodology": "auto", "heat_pump_heating_capacity": "auto", "heat_pump_heating_autosizing_limit": "auto", "heat_pump_fraction_heat_load_served": 1.0, "heat_pump_cooling_capacity": "auto", "heat_pump_cooling_autosizing_limit": "auto", "heat_pump_fraction_cool_load_served": 1.0, "heat_pump_backup_use_existing_system": "false", "heat_pump_backup_type": "none", "heat_pump_backup_fuel": "electricity", "heat_pump_backup_heating_efficiency": 1.0, "heat_pump_backup_heating_capacity": "auto", "heat_pump_backup_heating_autosizing_limit": "auto", "heating_system_pilot_light": "auto", "geothermal_loop_configuration": "none", "geothermal_loop_borefield_configuration": "auto", "geothermal_loop_loop_flow": "auto", "geothermal_loop_boreholes_count": "auto", "geothermal_loop_boreholes_length": "auto", "geothermal_loop_boreholes_spacing": "auto", "geothermal_loop_boreholes_diameter": "auto", "geothermal_loop_grout_type": "auto", "geothermal_loop_pipe_type": "auto", "geothermal_loop_pipe_diameter": "auto"}
        dct_HVAC_Heating["Fuel Furnace, 90% AFUE"] = {"heating_system_type": "Furnace", "heating_system_heating_efficiency": 0.9, "heating_system_heating_capacity": "auto", "heating_system_heating_autosizing_limit": "auto", "heating_system_fraction_heat_load_served": 1.0, "heating_system_has_flue_or_chimney": "auto", "heat_pump_type": "none", "heat_pump_heating_efficiency_type": "HSPF", "heat_pump_heating_efficiency": 0.0, "heat_pump_cooling_efficiency_type": "SEER", "heat_pump_cooling_efficiency": 0.0, "heat_pump_sizing_methodology": "ACCA", "heat_pump_sizing_is_duct_limited": "false", "heat_pump_backup_sizing_methodology": "auto", "heat_pump_heating_capacity": "auto", "heat_pump_heating_autosizing_limit": "auto", "heat_pump_fraction_heat_load_served": 1.0, "heat_pump_cooling_capacity": "auto", "heat_pump_cooling_autosizing_limit": "auto", "heat_pump_fraction_cool_load_served": 1.0, "heat_pump_backup_use_existing_system": "false", "heat_pump_backup_type": "none", "heat_pump_backup_fuel": "electricity", "heat_pump_backup_heating_efficiency": 1.0, "heat_pump_backup_heating_capacity": "auto", "heat_pump_backup_heating_autosizing_limit": "auto", "heating_system_pilot_light": "auto", "geothermal_loop_configuration": "none", "geothermal_loop_borefield_configuration": "auto", "geothermal_loop_loop_flow": "auto", "geothermal_loop_boreholes_count": "auto", "geothermal_loop_boreholes_length": "auto", "geothermal_loop_boreholes_spacing": "auto", "geothermal_loop_boreholes_diameter": "auto", "geothermal_loop_grout_type": "auto", "geothermal_loop_pipe_type": "auto", "geothermal_loop_pipe_diameter": "auto"}
        dct_HVAC_Heating["Fuel Furnace, 92.5% AFUE"] = {"heating_system_type": "Furnace", "heating_system_heating_efficiency": 0.925, "heating_system_heating_capacity": "auto", "heating_system_heating_autosizing_limit": "auto", "heating_system_fraction_heat_load_served": 1.0, "heating_system_has_flue_or_chimney": "auto", "heat_pump_type": "none", "heat_pump_heating_efficiency_type": "HSPF", "heat_pump_heating_efficiency": 0.0, "heat_pump_cooling_efficiency_type": "SEER", "heat_pump_cooling_efficiency": 0.0, "heat_pump_sizing_methodology": "ACCA", "heat_pump_sizing_is_duct_limited": "false", "heat_pump_backup_sizing_methodology": "auto", "heat_pump_heating_capacity": "auto", "heat_pump_heating_autosizing_limit": "auto", "heat_pump_fraction_heat_load_served": 1.0, "heat_pump_cooling_capacity": "auto", "heat_pump_cooling_autosizing_limit": "auto", "heat_pump_fraction_cool_load_served": 1.0, "heat_pump_backup_use_existing_system": "false", "heat_pump_backup_type": "none", "heat_pump_backup_fuel": "electricity", "heat_pump_backup_heating_efficiency": 1.0, "heat_pump_backup_heating_capacity": "auto", "heat_pump_backup_heating_autosizing_limit": "auto", "heating_system_pilot_light": "auto", "geothermal_loop_configuration": "none", "geothermal_loop_borefield_configuration": "auto", "geothermal_loop_loop_flow": "auto", "geothermal_loop_boreholes_count": "auto", "geothermal_loop_boreholes_length": "auto", "geothermal_loop_boreholes_spacing": "auto", "geothermal_loop_boreholes_diameter": "auto", "geothermal_loop_grout_type": "auto", "geothermal_loop_pipe_type": "auto", "geothermal_loop_pipe_diameter": "auto"}
        dct_HVAC_Heating["Fuel Furnace, 96% AFUE"] = {"heating_system_type": "Furnace", "heating_system_heating_efficiency": 0.96, "heating_system_heating_capacity": "auto", "heating_system_heating_autosizing_limit": "auto", "heating_system_fraction_heat_load_served": 1.0, "heating_system_has_flue_or_chimney": "auto", "heat_pump_type": "none", "heat_pump_heating_efficiency_type": "HSPF", "heat_pump_heating_efficiency": 0.0, "heat_pump_cooling_efficiency_type": "SEER", "heat_pump_cooling_efficiency": 0.0, "heat_pump_sizing_methodology": "ACCA", "heat_pump_sizing_is_duct_limited": "false", "heat_pump_backup_sizing_methodology": "auto", "heat_pump_heating_capacity": "auto", "heat_pump_heating_autosizing_limit": "auto", "heat_pump_fraction_heat_load_served": 1.0, "heat_pump_cooling_capacity": "auto", "heat_pump_cooling_autosizing_limit": "auto", "heat_pump_fraction_cool_load_served": 1.0, "heat_pump_backup_use_existing_system": "false", "heat_pump_backup_type": "none", "heat_pump_backup_fuel": "electricity", "heat_pump_backup_heating_efficiency": 1.0, "heat_pump_backup_heating_capacity": "auto", "heat_pump_backup_heating_autosizing_limit": "auto", "heating_system_pilot_light": "auto", "geothermal_loop_configuration": "none", "geothermal_loop_borefield_configuration": "auto", "geothermal_loop_loop_flow": "auto", "geothermal_loop_boreholes_count": "auto", "geothermal_loop_boreholes_length": "auto", "geothermal_loop_boreholes_spacing": "auto", "geothermal_loop_boreholes_diameter": "auto", "geothermal_loop_grout_type": "auto", "geothermal_loop_pipe_type": "auto", "geothermal_loop_pipe_diameter": "auto"}
        dct_HVAC_Heating["Fuel Wall/Floor Furnace, 60% AFUE"] = {"heating_system_type": "WallFurnace", "heating_system_heating_efficiency": 0.6, "heating_system_heating_capacity": "auto", "heating_system_heating_autosizing_limit": "auto", "heating_system_fraction_heat_load_served": 1.0, "heating_system_has_flue_or_chimney": "auto", "heat_pump_type": "none", "heat_pump_heating_efficiency_type": "HSPF", "heat_pump_heating_efficiency": 0.0, "heat_pump_cooling_efficiency_type": "SEER", "heat_pump_cooling_efficiency": 0.0, "heat_pump_sizing_methodology": "ACCA", "heat_pump_sizing_is_duct_limited": "false", "heat_pump_backup_sizing_methodology": "auto", "heat_pump_heating_capacity": "auto", "heat_pump_heating_autosizing_limit": "auto", "heat_pump_fraction_heat_load_served": 1.0, "heat_pump_cooling_capacity": "auto", "heat_pump_cooling_autosizing_limit": "auto", "heat_pump_fraction_cool_load_served": 1.0, "heat_pump_backup_use_existing_system": "false", "heat_pump_backup_type": "none", "heat_pump_backup_fuel": "electricity", "heat_pump_backup_heating_efficiency": 1.0, "heat_pump_backup_heating_capacity": "auto", "heat_pump_backup_heating_autosizing_limit": "auto", "heating_system_pilot_light": "auto", "geothermal_loop_configuration": "none", "geothermal_loop_borefield_configuration": "auto", "geothermal_loop_loop_flow": "auto", "geothermal_loop_boreholes_count": "auto", "geothermal_loop_boreholes_length": "auto", "geothermal_loop_boreholes_spacing": "auto", "geothermal_loop_boreholes_diameter": "auto", "geothermal_loop_grout_type": "auto", "geothermal_loop_pipe_type": "auto", "geothermal_loop_pipe_diameter": "auto"}
        dct_HVAC_Heating["Fuel Wall/Floor Furnace, 68% AFUE"] = {"heating_system_type": "WallFurnace", "heating_system_heating_efficiency": 0.68, "heating_system_heating_capacity": "auto", "heating_system_heating_autosizing_limit": "auto", "heating_system_fraction_heat_load_served": 1.0, "heating_system_has_flue_or_chimney": "auto", "heat_pump_type": "none", "heat_pump_heating_efficiency_type": "HSPF", "heat_pump_heating_efficiency": 0.0, "heat_pump_cooling_efficiency_type": "SEER", "heat_pump_cooling_efficiency": 0.0, "heat_pump_sizing_methodology": "ACCA", "heat_pump_sizing_is_duct_limited": "false", "heat_pump_backup_sizing_methodology": "auto", "heat_pump_heating_capacity": "auto", "heat_pump_heating_autosizing_limit": "auto", "heat_pump_fraction_heat_load_served": 1.0, "heat_pump_cooling_capacity": "auto", "heat_pump_cooling_autosizing_limit": "auto", "heat_pump_fraction_cool_load_served": 1.0, "heat_pump_backup_use_existing_system": "false", "heat_pump_backup_type": "none", "heat_pump_backup_fuel": "electricity", "heat_pump_backup_heating_efficiency": 1.0, "heat_pump_backup_heating_capacity": "auto", "heat_pump_backup_heating_autosizing_limit": "auto", "heating_system_pilot_light": "auto", "geothermal_loop_configuration": "none", "geothermal_loop_borefield_configuration": "auto", "geothermal_loop_loop_flow": "auto", "geothermal_loop_boreholes_count": "auto", "geothermal_loop_boreholes_length": "auto", "geothermal_loop_boreholes_spacing": "auto", "geothermal_loop_boreholes_diameter": "auto", "geothermal_loop_grout_type": "auto", "geothermal_loop_pipe_type": "auto", "geothermal_loop_pipe_diameter": "auto"}
        dct_HVAC_Heating["GSHP, EER 16.6, COP 3.6"] = {"heating_system_type": "none", "heating_system_heating_efficiency": 0.0, "heating_system_heating_capacity": "auto", "heating_system_heating_autosizing_limit": "auto", "heating_system_fraction_heat_load_served": 1.0, "heating_system_has_flue_or_chimney": "auto", "heat_pump_type": "ground-to-air", "heat_pump_heating_efficiency_type": "COP", "heat_pump_heating_efficiency": 3.6, "heat_pump_cooling_efficiency_type": "EER", "heat_pump_cooling_efficiency": 16.6, "heat_pump_sizing_methodology": "ACCA", "heat_pump_sizing_is_duct_limited": "false", "heat_pump_backup_sizing_methodology": "auto", "heat_pump_heating_capacity": "auto", "heat_pump_heating_autosizing_limit": "auto", "heat_pump_fraction_heat_load_served": 1.0, "heat_pump_cooling_capacity": "auto", "heat_pump_cooling_autosizing_limit": "auto", "heat_pump_fraction_cool_load_served": 1.0, "heat_pump_backup_use_existing_system": "false", "heat_pump_backup_type": "integrated", "heat_pump_backup_fuel": "electricity", "heat_pump_backup_heating_efficiency": 1.0, "heat_pump_backup_heating_capacity": "auto", "heat_pump_backup_heating_autosizing_limit": "auto", "heat_pump_heating_capacity_retention_fraction": "auto", "heat_pump_heating_capacity_retention_temp": "auto", "heat_pump_is_ducted": "true", "heat_pump_backup_heating_lockout_temp": "auto", "heat_pump_compressor_lockout_temp": "auto", "heat_pump_cooling_compressor_type": "single stage", "heat_pump_cooling_sensible_heat_fraction": "auto", "heat_pump_crankcase_heater_watts": "auto", "geothermal_loop_configuration": "vertical", "geothermal_loop_borefield_configuration": "auto", "geothermal_loop_loop_flow": "auto", "geothermal_loop_boreholes_count": "auto", "geothermal_loop_boreholes_length": "auto", "geothermal_loop_boreholes_spacing": "auto", "geothermal_loop_boreholes_diameter": "auto", "geothermal_loop_grout_type": "auto", "geothermal_loop_pipe_type": "auto", "geothermal_loop_pipe_diameter": "auto", "simulation_control_ground_to_air_heat_pump_model_type": "auto"}
        dct_HVAC_Heating["GSHP, EER 18.6, COP 3.8"] = {"heating_system_type": "none", "heating_system_heating_efficiency": 0.0, "heating_system_heating_capacity": "auto", "heating_system_heating_autosizing_limit": "auto", "heating_system_fraction_heat_load_served": 1.0, "heating_system_has_flue_or_chimney": "auto", "heat_pump_type": "ground-to-air", "heat_pump_heating_efficiency_type": "COP", "heat_pump_heating_efficiency": 3.8, "heat_pump_cooling_efficiency_type": "EER", "heat_pump_cooling_efficiency": 18.6, "heat_pump_sizing_methodology": "MaxLoad", "heat_pump_sizing_is_duct_limited": "false", "heat_pump_backup_sizing_methodology": "auto", "heat_pump_heating_capacity": "auto", "heat_pump_heating_autosizing_limit": "auto", "heat_pump_fraction_heat_load_served": 1.0, "heat_pump_cooling_capacity": "auto", "heat_pump_cooling_autosizing_limit": "auto", "heat_pump_fraction_cool_load_served": 1.0, "heat_pump_backup_use_existing_system": "false", "heat_pump_backup_type": "none", "heat_pump_backup_fuel": "electricity", "heat_pump_backup_heating_efficiency": 1.0, "heat_pump_backup_heating_capacity": "auto", "heat_pump_backup_heating_autosizing_limit": "auto", "heat_pump_heating_capacity_retention_fraction": "auto", "heat_pump_heating_capacity_retention_temp": "auto", "heat_pump_is_ducted": "true", "heat_pump_backup_heating_lockout_temp": "auto", "heat_pump_compressor_lockout_temp": "auto", "heat_pump_cooling_compressor_type": "single stage", "heat_pump_cooling_sensible_heat_fraction": "auto", "heat_pump_crankcase_heater_watts": "auto", "geothermal_loop_configuration": "vertical", "geothermal_loop_borefield_configuration": "auto", "geothermal_loop_loop_flow": "auto", "geothermal_loop_boreholes_count": "auto", "geothermal_loop_boreholes_length": "auto", "geothermal_loop_boreholes_spacing": "auto", "geothermal_loop_boreholes_diameter": "auto", "geothermal_loop_grout_type": "thermally enhanced", "geothermal_loop_pipe_type": "thermally enhanced", "geothermal_loop_pipe_diameter": "auto", "simulation_control_ground_to_air_heat_pump_model_type": "experimental"}
        dct_HVAC_Heating["GSHP, EER 20.2, COP 4.2"] = {"heating_system_type": "none", "heating_system_heating_efficiency": 0.0, "heating_system_heating_capacity": "auto", "heating_system_heating_autosizing_limit": "auto", "heating_system_fraction_heat_load_served": 1.0, "heating_system_has_flue_or_chimney": "auto", "heat_pump_type": "ground-to-air", "heat_pump_heating_efficiency_type": "COP", "heat_pump_heating_efficiency": 4.2, "heat_pump_cooling_efficiency_type": "EER", "heat_pump_cooling_efficiency": 20.2, "heat_pump_sizing_methodology": "ACCA", "heat_pump_sizing_is_duct_limited": "false", "heat_pump_backup_sizing_methodology": "auto", "heat_pump_heating_capacity": "auto", "heat_pump_heating_autosizing_limit": "auto", "heat_pump_fraction_heat_load_served": 1.0, "heat_pump_cooling_capacity": "auto", "heat_pump_cooling_autosizing_limit": "auto", "heat_pump_fraction_cool_load_served": 1.0, "heat_pump_backup_use_existing_system": "false", "heat_pump_backup_type": "integrated", "heat_pump_backup_fuel": "electricity", "heat_pump_backup_heating_efficiency": 1.0, "heat_pump_backup_heating_capacity": "auto", "heat_pump_backup_heating_autosizing_limit": "auto", "heat_pump_heating_capacity_retention_fraction": "auto", "heat_pump_heating_capacity_retention_temp": "auto", "heat_pump_is_ducted": "true", "heat_pump_backup_heating_lockout_temp": "auto", "heat_pump_compressor_lockout_temp": "auto", "heat_pump_cooling_compressor_type": "two stage", "heat_pump_cooling_sensible_heat_fraction": "auto", "heat_pump_crankcase_heater_watts": "auto", "geothermal_loop_configuration": "vertical", "geothermal_loop_borefield_configuration": "auto", "geothermal_loop_loop_flow": "auto", "geothermal_loop_boreholes_count": "auto", "geothermal_loop_boreholes_length": "auto", "geothermal_loop_boreholes_spacing": "auto", "geothermal_loop_boreholes_diameter": "auto", "geothermal_loop_grout_type": "auto", "geothermal_loop_pipe_type": "auto", "geothermal_loop_pipe_diameter": "auto", "simulation_control_ground_to_air_heat_pump_model_type": "auto"}
        dct_HVAC_Heating["GSHP, EER 20.5, COP 4.0"] = {"heating_system_type": "none", "heating_system_heating_efficiency": 0.0, "heating_system_heating_capacity": "auto", "heating_system_heating_autosizing_limit": "auto", "heating_system_fraction_heat_load_served": 1.0, "heating_system_has_flue_or_chimney": "auto", "heat_pump_type": "ground-to-air", "heat_pump_heating_efficiency_type": "COP", "heat_pump_heating_efficiency": 4.0, "heat_pump_cooling_efficiency_type": "EER", "heat_pump_cooling_efficiency": 20.5, "heat_pump_sizing_methodology": "MaxLoad", "heat_pump_sizing_is_duct_limited": "false", "heat_pump_backup_sizing_methodology": "auto", "heat_pump_heating_capacity": "auto", "heat_pump_heating_autosizing_limit": "auto", "heat_pump_fraction_heat_load_served": 1.0, "heat_pump_cooling_capacity": "auto", "heat_pump_cooling_autosizing_limit": "auto", "heat_pump_fraction_cool_load_served": 1.0, "heat_pump_backup_use_existing_system": "false", "heat_pump_backup_type": "none", "heat_pump_backup_fuel": "electricity", "heat_pump_backup_heating_efficiency": 1.0, "heat_pump_backup_heating_capacity": "auto", "heat_pump_backup_heating_autosizing_limit": "auto", "heat_pump_heating_capacity_retention_fraction": "auto", "heat_pump_heating_capacity_retention_temp": "auto", "heat_pump_is_ducted": "true", "heat_pump_backup_heating_lockout_temp": "auto", "heat_pump_compressor_lockout_temp": "auto", "heat_pump_cooling_compressor_type": "two stage", "heat_pump_cooling_sensible_heat_fraction": "auto", "heat_pump_crankcase_heater_watts": "auto", "geothermal_loop_configuration": "vertical", "geothermal_loop_borefield_configuration": "auto", "geothermal_loop_loop_flow": "auto", "geothermal_loop_boreholes_count": "auto", "geothermal_loop_boreholes_length": "auto", "geothermal_loop_boreholes_spacing": "auto", "geothermal_loop_boreholes_diameter": "auto", "geothermal_loop_grout_type": "thermally enhanced", "geothermal_loop_pipe_type": "thermally enhanced", "geothermal_loop_pipe_diameter": "auto", "simulation_control_ground_to_air_heat_pump_model_type": "experimental"}
        dct_HVAC_Heating["GSHP, EER 30.9, COP 4.4"] = {"heating_system_type": "none", "heating_system_heating_efficiency": 0.0, "heating_system_heating_capacity": "auto", "heating_system_heating_autosizing_limit": "auto", "heating_system_fraction_heat_load_served": 1.0, "heating_system_has_flue_or_chimney": "auto", "heat_pump_type": "ground-to-air", "heat_pump_heating_efficiency_type": "COP", "heat_pump_heating_efficiency": 4.4, "heat_pump_cooling_efficiency_type": "EER", "heat_pump_cooling_efficiency": 30.9, "heat_pump_sizing_methodology": "MaxLoad", "heat_pump_sizing_is_duct_limited": "false", "heat_pump_backup_sizing_methodology": "auto", "heat_pump_heating_capacity": "auto", "heat_pump_heating_autosizing_limit": "auto", "heat_pump_fraction_heat_load_served": 1.0, "heat_pump_cooling_capacity": "auto", "heat_pump_cooling_autosizing_limit": "auto", "heat_pump_fraction_cool_load_served": 1.0, "heat_pump_backup_use_existing_system": "false", "heat_pump_backup_type": "none", "heat_pump_backup_fuel": "electricity", "heat_pump_backup_heating_efficiency": 1.0, "heat_pump_backup_heating_capacity": "auto", "heat_pump_backup_heating_autosizing_limit": "auto", "heat_pump_heating_capacity_retention_fraction": "auto", "heat_pump_heating_capacity_retention_temp": "auto", "heat_pump_is_ducted": "true", "heat_pump_backup_heating_lockout_temp": "auto", "heat_pump_compressor_lockout_temp": "auto", "heat_pump_cooling_compressor_type": "variable speed", "heat_pump_cooling_sensible_heat_fraction": "auto", "heat_pump_crankcase_heater_watts": "auto", "geothermal_loop_configuration": "vertical", "geothermal_loop_borefield_configuration": "auto", "geothermal_loop_loop_flow": "auto", "geothermal_loop_boreholes_count": "auto", "geothermal_loop_boreholes_length": "auto", "geothermal_loop_boreholes_spacing": "auto", "geothermal_loop_boreholes_diameter": "auto", "geothermal_loop_grout_type": "thermally enhanced", "geothermal_loop_pipe_type": "thermally enhanced", "geothermal_loop_pipe_diameter": "auto", "simulation_control_ground_to_air_heat_pump_model_type": "experimental"}
        dct_HVAC_Heating["MSHP, SEER 14.5, 8.2 HSPF"] = {"heating_system_type": "none", "heating_system_heating_efficiency": 0.0, "heating_system_heating_capacity": "auto", "heating_system_heating_autosizing_limit": "auto", "heating_system_fraction_heat_load_served": 1.0, "heating_system_has_flue_or_chimney": "auto", "heat_pump_type": "mini-split", "heat_pump_heating_efficiency_type": "HSPF", "heat_pump_heating_efficiency": 8.2, "heat_pump_cooling_efficiency_type": "SEER", "heat_pump_cooling_efficiency": 14.5, "heat_pump_sizing_methodology": "ACCA", "heat_pump_sizing_is_duct_limited": "false", "heat_pump_backup_sizing_methodology": "auto", "heat_pump_heating_capacity": "auto", "heat_pump_heating_autosizing_limit": "auto", "heat_pump_fraction_heat_load_served": 1.0, "heat_pump_cooling_capacity": "auto", "heat_pump_cooling_autosizing_limit": "auto", "heat_pump_fraction_cool_load_served": 1.0, "heat_pump_backup_use_existing_system": "false", "heat_pump_backup_type": "integrated", "heat_pump_backup_fuel": "electricity", "heat_pump_backup_heating_efficiency": 1.0, "heat_pump_backup_heating_capacity": "auto", "heat_pump_backup_heating_autosizing_limit": "auto", "heat_pump_heating_capacity_retention_fraction": 0.25, "heat_pump_heating_capacity_retention_temp": -5.0, "heat_pump_is_ducted": "false", "heat_pump_backup_heating_lockout_temp": "auto", "heat_pump_compressor_lockout_temp": "auto", "heat_pump_cooling_compressor_type": "variable speed", "heat_pump_cooling_sensible_heat_fraction": "auto", "heat_pump_crankcase_heater_watts": "auto", "geothermal_loop_configuration": "none", "geothermal_loop_borefield_configuration": "auto", "geothermal_loop_loop_flow": "auto", "geothermal_loop_boreholes_count": "auto", "geothermal_loop_boreholes_length": "auto", "geothermal_loop_boreholes_spacing": "auto", "geothermal_loop_boreholes_diameter": "auto", "geothermal_loop_grout_type": "auto", "geothermal_loop_pipe_type": "auto", "geothermal_loop_pipe_diameter": "auto"}
        dct_HVAC_Heating["MSHP, SEER 14.5, 8.2 HSPF, Ducted"] = {"heating_system_type": "none", "heating_system_heating_efficiency": 0.0, "heating_system_heating_capacity": "auto", "heating_system_heating_autosizing_limit": "auto", "heating_system_fraction_heat_load_served": 1.0, "heating_system_has_flue_or_chimney": "auto", "heat_pump_type": "mini-split", "heat_pump_heating_efficiency_type": "HSPF", "heat_pump_heating_efficiency": 8.2, "heat_pump_cooling_efficiency_type": "SEER", "heat_pump_cooling_efficiency": 14.5, "heat_pump_sizing_methodology": "ACCA", "heat_pump_sizing_is_duct_limited": "false", "heat_pump_backup_sizing_methodology": "auto", "heat_pump_heating_capacity": "auto", "heat_pump_heating_autosizing_limit": "auto", "heat_pump_fraction_heat_load_served": 1.0, "heat_pump_cooling_capacity": "auto", "heat_pump_cooling_autosizing_limit": "auto", "heat_pump_fraction_cool_load_served": 1.0, "heat_pump_backup_use_existing_system": "false", "heat_pump_backup_type": "integrated", "heat_pump_backup_fuel": "electricity", "heat_pump_backup_heating_efficiency": 1.0, "heat_pump_backup_heating_capacity": "auto", "heat_pump_backup_heating_autosizing_limit": "auto", "heat_pump_heating_capacity_retention_fraction": 0.25, "heat_pump_heating_capacity_retention_temp": -5.0, "heat_pump_is_ducted": "true", "heat_pump_backup_heating_lockout_temp": "auto", "heat_pump_compressor_lockout_temp": "auto", "heat_pump_cooling_compressor_type": "variable speed", "heat_pump_cooling_sensible_heat_fraction": "auto", "heat_pump_crankcase_heater_watts": "auto", "geothermal_loop_configuration": "none", "geothermal_loop_borefield_configuration": "auto", "geothermal_loop_loop_flow": "auto", "geothermal_loop_boreholes_count": "auto", "geothermal_loop_boreholes_length": "auto", "geothermal_loop_boreholes_spacing": "auto", "geothermal_loop_boreholes_diameter": "auto", "geothermal_loop_grout_type": "auto", "geothermal_loop_pipe_type": "auto", "geothermal_loop_pipe_diameter": "auto"}
        dct_HVAC_Heating["MSHP, SEER 16, 9.2 HSPF, Existing Backup, Max Load"] = {"heating_system_type": "none", "heating_system_heating_efficiency": 0.0, "heating_system_heating_capacity": "auto", "heating_system_heating_autosizing_limit": "auto", "heating_system_fraction_heat_load_served": 1.0, "heating_system_has_flue_or_chimney": "auto", "heat_pump_type": "mini-split", "heat_pump_heating_efficiency_type": "HSPF", "heat_pump_heating_efficiency": 9.2, "heat_pump_cooling_efficiency_type": "SEER", "heat_pump_cooling_efficiency": 16.0, "heat_pump_sizing_methodology": "MaxLoad", "heat_pump_sizing_is_duct_limited": "false", "heat_pump_backup_sizing_methodology": "auto", "heat_pump_heating_capacity": "auto", "heat_pump_heating_autosizing_limit": "auto", "heat_pump_fraction_heat_load_served": 1.0, "heat_pump_cooling_capacity": "auto", "heat_pump_cooling_autosizing_limit": "auto", "heat_pump_fraction_cool_load_served": 1.0, "heat_pump_backup_use_existing_system": "true", "heat_pump_backup_type": "auto", "heat_pump_backup_fuel": "auto", "heat_pump_backup_heating_efficiency": "auto", "heat_pump_backup_heating_capacity": "auto", "heat_pump_backup_heating_autosizing_limit": "auto", "heat_pump_heating_capacity_retention_fraction": 0.5, "heat_pump_heating_capacity_retention_temp": 5.0, "heat_pump_is_ducted": "false", "heat_pump_backup_heating_lockout_temp": "auto", "heat_pump_compressor_lockout_temp": -20.0, "heat_pump_cooling_compressor_type": "variable speed", "heat_pump_cooling_sensible_heat_fraction": "auto", "heat_pump_crankcase_heater_watts": "auto", "geothermal_loop_configuration": "none", "geothermal_loop_borefield_configuration": "auto", "geothermal_loop_loop_flow": "auto", "geothermal_loop_boreholes_count": "auto", "geothermal_loop_boreholes_length": "auto", "geothermal_loop_boreholes_spacing": "auto", "geothermal_loop_boreholes_diameter": "auto", "geothermal_loop_grout_type": "auto", "geothermal_loop_pipe_type": "auto", "geothermal_loop_pipe_diameter": "auto"}
        dct_HVAC_Heating["MSHP, SEER 16, 9.2 HSPF, Max Load"] = {"heating_system_type": "none", "heating_system_heating_efficiency": 0.0, "heating_system_heating_capacity": "auto", "heating_system_heating_autosizing_limit": "auto", "heating_system_fraction_heat_load_served": 1.0, "heating_system_has_flue_or_chimney": "auto", "heat_pump_type": "mini-split", "heat_pump_heating_efficiency_type": "HSPF", "heat_pump_heating_efficiency": 9.2, "heat_pump_cooling_efficiency_type": "SEER", "heat_pump_cooling_efficiency": 16.0, "heat_pump_sizing_methodology": "MaxLoad", "heat_pump_sizing_is_duct_limited": "false", "heat_pump_backup_sizing_methodology": "auto", "heat_pump_heating_capacity": "auto", "heat_pump_heating_autosizing_limit": "auto", "heat_pump_fraction_heat_load_served": 1.0, "heat_pump_cooling_capacity": "auto", "heat_pump_cooling_autosizing_limit": "auto", "heat_pump_fraction_cool_load_served": 1.0, "heat_pump_backup_use_existing_system": "false", "heat_pump_backup_type": "integrated", "heat_pump_backup_fuel": "electricity", "heat_pump_backup_heating_efficiency": 1.0, "heat_pump_backup_heating_capacity": "auto", "heat_pump_backup_heating_autosizing_limit": "auto", "heat_pump_heating_capacity_retention_fraction": 0.5, "heat_pump_heating_capacity_retention_temp": 5.0, "heat_pump_is_ducted": "false", "heat_pump_backup_heating_lockout_temp": "auto", "heat_pump_compressor_lockout_temp": "auto", "heat_pump_cooling_compressor_type": "variable speed", "heat_pump_cooling_sensible_heat_fraction": "auto", "heat_pump_crankcase_heater_watts": "auto", "geothermal_loop_configuration": "none", "geothermal_loop_borefield_configuration": "auto", "geothermal_loop_loop_flow": "auto", "geothermal_loop_boreholes_count": "auto", "geothermal_loop_boreholes_length": "auto", "geothermal_loop_boreholes_spacing": "auto", "geothermal_loop_boreholes_diameter": "auto", "geothermal_loop_grout_type": "auto", "geothermal_loop_pipe_type": "auto", "geothermal_loop_pipe_diameter": "auto"}
        dct_HVAC_Heating["MSHP, SEER 17, 9.5 HSPF"] = {"heating_system_type": "none", "heating_system_heating_efficiency": 0.0, "heating_system_heating_capacity": "auto", "heating_system_heating_autosizing_limit": "auto", "heating_system_fraction_heat_load_served": 1.0, "heating_system_has_flue_or_chimney": "auto", "heat_pump_type": "mini-split", "heat_pump_heating_efficiency_type": "HSPF", "heat_pump_heating_efficiency": 9.5, "heat_pump_cooling_efficiency_type": "SEER", "heat_pump_cooling_efficiency": 17.0, "heat_pump_sizing_methodology": "ACCA", "heat_pump_sizing_is_duct_limited": "false", "heat_pump_backup_sizing_methodology": "auto", "heat_pump_heating_capacity": "auto", "heat_pump_heating_autosizing_limit": "auto", "heat_pump_fraction_heat_load_served": 1.0, "heat_pump_cooling_capacity": "auto", "heat_pump_cooling_autosizing_limit": "auto", "heat_pump_fraction_cool_load_served": 1.0, "heat_pump_backup_use_existing_system": "false", "heat_pump_backup_type": "integrated", "heat_pump_backup_fuel": "electricity", "heat_pump_backup_heating_efficiency": 1.0, "heat_pump_backup_heating_capacity": "auto", "heat_pump_backup_heating_autosizing_limit": "auto", "heat_pump_heating_capacity_retention_fraction": 0.25, "heat_pump_heating_capacity_retention_temp": -5.0, "heat_pump_is_ducted": "false", "heat_pump_backup_heating_lockout_temp": "auto", "heat_pump_compressor_lockout_temp": "auto", "heat_pump_cooling_compressor_type": "variable speed", "heat_pump_cooling_sensible_heat_fraction": "auto", "heat_pump_crankcase_heater_watts": "auto", "geothermal_loop_configuration": "none", "geothermal_loop_borefield_configuration": "auto", "geothermal_loop_loop_flow": "auto", "geothermal_loop_boreholes_count": "auto", "geothermal_loop_boreholes_length": "auto", "geothermal_loop_boreholes_spacing": "auto", "geothermal_loop_boreholes_diameter": "auto", "geothermal_loop_grout_type": "auto", "geothermal_loop_pipe_type": "auto", "geothermal_loop_pipe_diameter": "auto"}
        dct_HVAC_Heating["MSHP, SEER 17, 9.5 HSPF, Ducted"] = {"heating_system_type": "none", "heating_system_heating_efficiency": 0.0, "heating_system_heating_capacity": "auto", "heating_system_heating_autosizing_limit": "auto", "heating_system_fraction_heat_load_served": 1.0, "heating_system_has_flue_or_chimney": "auto", "heat_pump_type": "mini-split", "heat_pump_heating_efficiency_type": "HSPF", "heat_pump_heating_efficiency": 9.5, "heat_pump_cooling_efficiency_type": "SEER", "heat_pump_cooling_efficiency": 17.0, "heat_pump_sizing_methodology": "ACCA", "heat_pump_sizing_is_duct_limited": "false", "heat_pump_backup_sizing_methodology": "auto", "heat_pump_heating_capacity": "auto", "heat_pump_heating_autosizing_limit": "auto", "heat_pump_fraction_heat_load_served": 1.0, "heat_pump_cooling_capacity": "auto", "heat_pump_cooling_autosizing_limit": "auto", "heat_pump_fraction_cool_load_served": 1.0, "heat_pump_backup_use_existing_system": "false", "heat_pump_backup_type": "integrated", "heat_pump_backup_fuel": "electricity", "heat_pump_backup_heating_efficiency": 1.0, "heat_pump_backup_heating_capacity": "auto", "heat_pump_backup_heating_autosizing_limit": "auto", "heat_pump_heating_capacity_retention_fraction": 0.25, "heat_pump_heating_capacity_retention_temp": -5.0, "heat_pump_is_ducted": "true", "heat_pump_backup_heating_lockout_temp": "auto", "heat_pump_compressor_lockout_temp": "auto", "heat_pump_cooling_compressor_type": "variable speed", "heat_pump_cooling_sensible_heat_fraction": "auto", "heat_pump_crankcase_heater_watts": "auto", "geothermal_loop_configuration": "none", "geothermal_loop_borefield_configuration": "auto", "geothermal_loop_loop_flow": "auto", "geothermal_loop_boreholes_count": "auto", "geothermal_loop_boreholes_length": "auto", "geothermal_loop_boreholes_spacing": "auto", "geothermal_loop_boreholes_diameter": "auto", "geothermal_loop_grout_type": "auto", "geothermal_loop_pipe_type": "auto", "geothermal_loop_pipe_diameter": "auto"}
        dct_HVAC_Heating["MSHP, SEER 18.0, 9.6 HSPF, 60% Conditioned"] = {"heating_system_type": "none", "heating_system_heating_efficiency": 0.0, "heating_system_heating_capacity": "auto", "heating_system_heating_autosizing_limit": "auto", "heating_system_fraction_heat_load_served": 1.0, "heating_system_has_flue_or_chimney": "auto", "heat_pump_type": "mini-split", "heat_pump_heating_efficiency_type": "HSPF", "heat_pump_heating_efficiency": 9.6, "heat_pump_cooling_efficiency_type": "SEER", "heat_pump_cooling_efficiency": 18.0, "heat_pump_sizing_methodology": "ACCA", "heat_pump_sizing_is_duct_limited": "false", "heat_pump_backup_sizing_methodology": "auto", "heat_pump_heating_capacity": "auto", "heat_pump_heating_autosizing_limit": "auto", "heat_pump_fraction_heat_load_served": 0.6, "heat_pump_cooling_capacity": "auto", "heat_pump_cooling_autosizing_limit": "auto", "heat_pump_fraction_cool_load_served": 0.6, "heat_pump_backup_use_existing_system": "false", "heat_pump_backup_type": "integrated", "heat_pump_backup_fuel": "electricity", "heat_pump_backup_heating_efficiency": 1.0, "heat_pump_backup_heating_capacity": "auto", "heat_pump_backup_heating_autosizing_limit": "auto", "heat_pump_heating_capacity_retention_fraction": 0.25, "heat_pump_heating_capacity_retention_temp": -5.0, "heat_pump_is_ducted": "false", "heat_pump_backup_heating_lockout_temp": "auto", "heat_pump_compressor_lockout_temp": "auto", "heat_pump_cooling_compressor_type": "variable speed", "heat_pump_cooling_sensible_heat_fraction": "auto", "heat_pump_crankcase_heater_watts": "auto", "geothermal_loop_configuration": "none", "geothermal_loop_borefield_configuration": "auto", "geothermal_loop_loop_flow": "auto", "geothermal_loop_boreholes_count": "auto", "geothermal_loop_boreholes_length": "auto", "geothermal_loop_boreholes_spacing": "auto", "geothermal_loop_boreholes_diameter": "auto", "geothermal_loop_grout_type": "auto", "geothermal_loop_pipe_type": "auto", "geothermal_loop_pipe_diameter": "auto"}
        dct_HVAC_Heating["MSHP, SEER 18.0, 9.6 HSPF, 60% Conditioned, Ducted"] = {"heating_system_type": "none", "heating_system_heating_efficiency": 0.0, "heating_system_heating_capacity": "auto", "heating_system_heating_autosizing_limit": "auto", "heating_system_fraction_heat_load_served": 1.0, "heating_system_has_flue_or_chimney": "auto", "heat_pump_type": "mini-split", "heat_pump_heating_efficiency_type": "HSPF", "heat_pump_heating_efficiency": 9.6, "heat_pump_cooling_efficiency_type": "SEER", "heat_pump_cooling_efficiency": 18.0, "heat_pump_sizing_methodology": "ACCA", "heat_pump_sizing_is_duct_limited": "false", "heat_pump_backup_sizing_methodology": "auto", "heat_pump_heating_capacity": "auto", "heat_pump_heating_autosizing_limit": "auto", "heat_pump_fraction_heat_load_served": 0.6, "heat_pump_cooling_capacity": "auto", "heat_pump_cooling_autosizing_limit": "auto", "heat_pump_fraction_cool_load_served": 0.6, "heat_pump_backup_use_existing_system": "false", "heat_pump_backup_type": "integrated", "heat_pump_backup_fuel": "electricity", "heat_pump_backup_heating_efficiency": 1.0, "heat_pump_backup_heating_capacity": "auto", "heat_pump_backup_heating_autosizing_limit": "auto", "heat_pump_heating_capacity_retention_fraction": 0.25, "heat_pump_heating_capacity_retention_temp": -5.0, "heat_pump_is_ducted": "true", "heat_pump_backup_heating_lockout_temp": "auto", "heat_pump_compressor_lockout_temp": "auto", "heat_pump_cooling_compressor_type": "variable speed", "heat_pump_cooling_sensible_heat_fraction": "auto", "heat_pump_crankcase_heater_watts": "auto", "geothermal_loop_configuration": "none", "geothermal_loop_borefield_configuration": "auto", "geothermal_loop_loop_flow": "auto", "geothermal_loop_boreholes_count": "auto", "geothermal_loop_boreholes_length": "auto", "geothermal_loop_boreholes_spacing": "auto", "geothermal_loop_boreholes_diameter": "auto", "geothermal_loop_grout_type": "auto", "geothermal_loop_pipe_type": "auto", "geothermal_loop_pipe_diameter": "auto"}
        dct_HVAC_Heating["MSHP, SEER 20, 11 HSPF, CCHP, Max Load"] = {"heating_system_type": "none", "heating_system_heating_efficiency": 0.0, "heating_system_heating_capacity": "auto", "heating_system_heating_autosizing_limit": "auto", "heating_system_fraction_heat_load_served": 1.0, "heating_system_has_flue_or_chimney": "auto", "heat_pump_type": "mini-split", "heat_pump_heating_efficiency_type": "HSPF", "heat_pump_heating_efficiency": 11.0, "heat_pump_cooling_efficiency_type": "SEER", "heat_pump_cooling_efficiency": 20.0, "heat_pump_sizing_methodology": "MaxLoad", "heat_pump_sizing_is_duct_limited": "false", "heat_pump_backup_sizing_methodology": "auto", "heat_pump_heating_capacity": "auto", "heat_pump_heating_autosizing_limit": "auto", "heat_pump_fraction_heat_load_served": 1.0, "heat_pump_cooling_capacity": "auto", "heat_pump_cooling_autosizing_limit": "auto", "heat_pump_fraction_cool_load_served": 1.0, "heat_pump_backup_use_existing_system": "false", "heat_pump_backup_type": "integrated", "heat_pump_backup_fuel": "electricity", "heat_pump_backup_heating_efficiency": 1.0, "heat_pump_backup_heating_capacity": "auto", "heat_pump_backup_heating_autosizing_limit": "auto", "heat_pump_heating_capacity_retention_fraction": 0.9, "heat_pump_heating_capacity_retention_temp": 5.0, "heat_pump_is_ducted": "false", "heat_pump_backup_heating_lockout_temp": "auto", "heat_pump_compressor_lockout_temp": "auto", "heat_pump_cooling_compressor_type": "variable speed", "heat_pump_cooling_sensible_heat_fraction": "auto", "heat_pump_crankcase_heater_watts": "auto", "geothermal_loop_configuration": "none", "geothermal_loop_borefield_configuration": "auto", "geothermal_loop_loop_flow": "auto", "geothermal_loop_boreholes_count": "auto", "geothermal_loop_boreholes_length": "auto", "geothermal_loop_boreholes_spacing": "auto", "geothermal_loop_boreholes_diameter": "auto", "geothermal_loop_grout_type": "auto", "geothermal_loop_pipe_type": "auto", "geothermal_loop_pipe_diameter": "auto"}
        dct_HVAC_Heating["MSHP, SEER 24, 13 HSPF, Max Load"] = {"heating_system_type": "none", "heating_system_heating_efficiency": 0.0, "heating_system_heating_capacity": "auto", "heating_system_heating_autosizing_limit": "auto", "heating_system_fraction_heat_load_served": 1.0, "heating_system_has_flue_or_chimney": "auto", "heat_pump_type": "mini-split", "heat_pump_heating_efficiency_type": "HSPF", "heat_pump_heating_efficiency": 13.0, "heat_pump_cooling_efficiency_type": "SEER", "heat_pump_cooling_efficiency": 24.0, "heat_pump_sizing_methodology": "MaxLoad", "heat_pump_sizing_is_duct_limited": "false", "heat_pump_backup_sizing_methodology": "auto", "heat_pump_heating_capacity": "auto", "heat_pump_heating_autosizing_limit": "auto", "heat_pump_fraction_heat_load_served": 1.0, "heat_pump_cooling_capacity": "auto", "heat_pump_cooling_autosizing_limit": "auto", "heat_pump_fraction_cool_load_served": 1.0, "heat_pump_backup_use_existing_system": "false", "heat_pump_backup_type": "integrated", "heat_pump_backup_fuel": "electricity", "heat_pump_backup_heating_efficiency": 1.0, "heat_pump_backup_heating_capacity": "auto", "heat_pump_backup_heating_autosizing_limit": "auto", "heat_pump_heating_capacity_retention_fraction": 0.9, "heat_pump_heating_capacity_retention_temp": 5.0, "heat_pump_is_ducted": "false", "heat_pump_backup_heating_lockout_temp": "auto", "heat_pump_compressor_lockout_temp": "auto", "heat_pump_cooling_compressor_type": "variable speed", "heat_pump_cooling_sensible_heat_fraction": "auto", "heat_pump_crankcase_heater_watts": "auto", "geothermal_loop_configuration": "none", "geothermal_loop_borefield_configuration": "auto", "geothermal_loop_loop_flow": "auto", "geothermal_loop_boreholes_count": "auto", "geothermal_loop_boreholes_length": "auto", "geothermal_loop_boreholes_spacing": "auto", "geothermal_loop_boreholes_diameter": "auto", "geothermal_loop_grout_type": "auto", "geothermal_loop_pipe_type": "auto", "geothermal_loop_pipe_diameter": "auto"}
        dct_HVAC_Heating["MSHP, SEER 25, 12.7 HSPF"] = {"heating_system_type": "none", "heating_system_heating_efficiency": 0.0, "heating_system_heating_capacity": "auto", "heating_system_heating_autosizing_limit": "auto", "heating_system_fraction_heat_load_served": 1.0, "heating_system_has_flue_or_chimney": "auto", "heat_pump_type": "mini-split", "heat_pump_heating_efficiency_type": "HSPF", "heat_pump_heating_efficiency": 12.7, "heat_pump_cooling_efficiency_type": "SEER", "heat_pump_cooling_efficiency": 25.0, "heat_pump_sizing_methodology": "ACCA", "heat_pump_sizing_is_duct_limited": "false", "heat_pump_backup_sizing_methodology": "auto", "heat_pump_heating_capacity": "auto", "heat_pump_heating_autosizing_limit": "auto", "heat_pump_fraction_heat_load_served": 1.0, "heat_pump_cooling_capacity": "auto", "heat_pump_cooling_autosizing_limit": "auto", "heat_pump_fraction_cool_load_served": 1.0, "heat_pump_backup_use_existing_system": "false", "heat_pump_backup_type": "integrated", "heat_pump_backup_fuel": "electricity", "heat_pump_backup_heating_efficiency": 1.0, "heat_pump_backup_heating_capacity": "auto", "heat_pump_backup_heating_autosizing_limit": "auto", "heat_pump_heating_capacity_retention_fraction": 0.5, "heat_pump_heating_capacity_retention_temp": -15.0, "heat_pump_is_ducted": "false", "heat_pump_backup_heating_lockout_temp": "auto", "heat_pump_compressor_lockout_temp": "auto", "heat_pump_cooling_compressor_type": "variable speed", "heat_pump_cooling_sensible_heat_fraction": "auto", "heat_pump_crankcase_heater_watts": "auto", "geothermal_loop_configuration": "none", "geothermal_loop_borefield_configuration": "auto", "geothermal_loop_loop_flow": "auto", "geothermal_loop_boreholes_count": "auto", "geothermal_loop_boreholes_length": "auto", "geothermal_loop_boreholes_spacing": "auto", "geothermal_loop_boreholes_diameter": "auto", "geothermal_loop_grout_type": "auto", "geothermal_loop_pipe_type": "auto", "geothermal_loop_pipe_diameter": "auto"}
        dct_HVAC_Heating["MSHP, SEER 25, 12.7 HSPF, Ducted"] = {"heating_system_type": "none", "heating_system_heating_efficiency": 0.0, "heating_system_heating_capacity": "auto", "heating_system_heating_autosizing_limit": "auto", "heating_system_fraction_heat_load_served": 1.0, "heating_system_has_flue_or_chimney": "auto", "heat_pump_type": "mini-split", "heat_pump_heating_efficiency_type": "HSPF", "heat_pump_heating_efficiency": 12.7, "heat_pump_cooling_efficiency_type": "SEER", "heat_pump_cooling_efficiency": 25.0, "heat_pump_sizing_methodology": "ACCA", "heat_pump_sizing_is_duct_limited": "false", "heat_pump_backup_sizing_methodology": "auto", "heat_pump_heating_capacity": "auto", "heat_pump_heating_autosizing_limit": "auto", "heat_pump_fraction_heat_load_served": 1.0, "heat_pump_cooling_capacity": "auto", "heat_pump_cooling_autosizing_limit": "auto", "heat_pump_fraction_cool_load_served": 1.0, "heat_pump_backup_use_existing_system": "false", "heat_pump_backup_type": "integrated", "heat_pump_backup_fuel": "electricity", "heat_pump_backup_heating_efficiency": 1.0, "heat_pump_backup_heating_capacity": "auto", "heat_pump_backup_heating_autosizing_limit": "auto", "heat_pump_heating_capacity_retention_fraction": 0.5, "heat_pump_heating_capacity_retention_temp": -15.0, "heat_pump_is_ducted": "true", "heat_pump_backup_heating_lockout_temp": "auto", "heat_pump_compressor_lockout_temp": "auto", "heat_pump_cooling_compressor_type": "variable speed", "heat_pump_cooling_sensible_heat_fraction": "auto", "heat_pump_crankcase_heater_watts": "auto", "geothermal_loop_configuration": "none", "geothermal_loop_borefield_configuration": "auto", "geothermal_loop_loop_flow": "auto", "geothermal_loop_boreholes_count": "auto", "geothermal_loop_boreholes_length": "auto", "geothermal_loop_boreholes_spacing": "auto", "geothermal_loop_boreholes_diameter": "auto", "geothermal_loop_grout_type": "auto", "geothermal_loop_pipe_type": "auto", "geothermal_loop_pipe_diameter": "auto"}
        dct_HVAC_Heating["MSHP, SEER 29.3, 14 HSPF"] = {"heating_system_type": "none", "heating_system_heating_efficiency": 0.0, "heating_system_heating_capacity": "auto", "heating_system_heating_autosizing_limit": "auto", "heating_system_fraction_heat_load_served": 1.0, "heating_system_has_flue_or_chimney": "auto", "heat_pump_type": "mini-split", "heat_pump_heating_efficiency_type": "HSPF", "heat_pump_heating_efficiency": 14.0, "heat_pump_cooling_efficiency_type": "SEER", "heat_pump_cooling_efficiency": 29.3, "heat_pump_sizing_methodology": "ACCA", "heat_pump_sizing_is_duct_limited": "false", "heat_pump_backup_sizing_methodology": "auto", "heat_pump_heating_capacity": "auto", "heat_pump_heating_autosizing_limit": "auto", "heat_pump_fraction_heat_load_served": 1.0, "heat_pump_cooling_capacity": "auto", "heat_pump_cooling_autosizing_limit": "auto", "heat_pump_fraction_cool_load_served": 1.0, "heat_pump_backup_use_existing_system": "false", "heat_pump_backup_type": "integrated", "heat_pump_backup_fuel": "electricity", "heat_pump_backup_heating_efficiency": 1.0, "heat_pump_backup_heating_capacity": "auto", "heat_pump_backup_heating_autosizing_limit": "auto", "heat_pump_heating_capacity_retention_fraction": 0.5, "heat_pump_heating_capacity_retention_temp": -15.0, "heat_pump_is_ducted": "false", "heat_pump_backup_heating_lockout_temp": "auto", "heat_pump_compressor_lockout_temp": "auto", "heat_pump_cooling_compressor_type": "variable speed", "heat_pump_cooling_sensible_heat_fraction": "auto", "heat_pump_crankcase_heater_watts": "auto", "geothermal_loop_configuration": "none", "geothermal_loop_borefield_configuration": "auto", "geothermal_loop_loop_flow": "auto", "geothermal_loop_boreholes_count": "auto", "geothermal_loop_boreholes_length": "auto", "geothermal_loop_boreholes_spacing": "auto", "geothermal_loop_boreholes_diameter": "auto", "geothermal_loop_grout_type": "auto", "geothermal_loop_pipe_type": "auto", "geothermal_loop_pipe_diameter": "auto"}
        dct_HVAC_Heating["MSHP, SEER 29.3, 14 HSPF, Ducted"] = {"heating_system_type": "none", "S": 0.0, "heating_system_heating_capacity": "auto", "heating_system_heating_autosizing_limit": "auto", "heating_system_fraction_heat_load_served": 1.0, "heating_system_has_flue_or_chimney": "auto", "heat_pump_type": "mini-split", "heat_pump_heating_efficiency_type": "HSPF", "heat_pump_heating_efficiency": 14.0, "heat_pump_cooling_efficiency_type": "SEER", "heat_pump_cooling_efficiency": 29.3, "heat_pump_sizing_methodology": "ACCA", "heat_pump_sizing_is_duct_limited": "false", "heat_pump_backup_sizing_methodology": "auto", "heat_pump_heating_capacity": "auto", "heat_pump_heating_autosizing_limit": "auto", "heat_pump_fraction_heat_load_served": 1.0, "heat_pump_cooling_capacity": "auto", "heat_pump_cooling_autosizing_limit": "auto", "heat_pump_fraction_cool_load_served": 1.0, "heat_pump_backup_use_existing_system": "false", "heat_pump_backup_type": "integrated", "heat_pump_backup_fuel": "electricity", "heat_pump_backup_heating_efficiency": 1.0, "heat_pump_backup_heating_capacity": "auto", "heat_pump_backup_heating_autosizing_limit": "auto", "heat_pump_heating_capacity_retention_fraction": 0.5, "heat_pump_heating_capacity_retention_temp": -15.0, "heat_pump_is_ducted": "true", "heat_pump_backup_heating_lockout_temp": "auto", "heat_pump_compressor_lockout_temp": "auto", "heat_pump_cooling_compressor_type": "variable speed", "heat_pump_cooling_sensible_heat_fraction": "auto", "heat_pump_crankcase_heater_watts": "auto", "geothermal_loop_configuration": "none", "geothermal_loop_borefield_configuration": "auto", "geothermal_loop_loop_flow": "auto", "geothermal_loop_boreholes_count": "auto", "geothermal_loop_boreholes_length": "auto", "geothermal_loop_boreholes_spacing": "auto", "geothermal_loop_boreholes_diameter": "auto", "geothermal_loop_grout_type": "auto", "geothermal_loop_pipe_type": "auto", "geothermal_loop_pipe_diameter": "auto"}
        dct_HVAC_Heating["MSHP, SEER 33, 13.3 HSPF"] = {"heating_system_type": "none", "heating_system_heating_efficiency": 0.0, "heating_system_heating_capacity": "auto", "heating_system_heating_autosizing_limit": "auto", "heating_system_fraction_heat_load_served": 1.0, "heating_system_has_flue_or_chimney": "auto", "heat_pump_type": "mini-split", "heat_pump_heating_efficiency_type": "HSPF", "heat_pump_heating_efficiency": 13.3, "heat_pump_cooling_efficiency_type": "SEER", "heat_pump_cooling_efficiency": 33.0, "heat_pump_sizing_methodology": "ACCA", "heat_pump_sizing_is_duct_limited": "false", "heat_pump_backup_sizing_methodology": "auto", "heat_pump_heating_capacity": "auto", "heat_pump_heating_autosizing_limit": "auto", "heat_pump_fraction_heat_load_served": 1.0, "heat_pump_cooling_capacity": "auto", "heat_pump_cooling_autosizing_limit": "auto", "heat_pump_fraction_cool_load_served": 1.0, "heat_pump_backup_use_existing_system": "false", "heat_pump_backup_type": "integrated", "heat_pump_backup_fuel": "electricity", "heat_pump_backup_heating_efficiency": 1.0, "heat_pump_backup_heating_capacity": "auto", "heat_pump_backup_heating_autosizing_limit": "auto", "heat_pump_heating_capacity_retention_fraction": 0.5, "heat_pump_heating_capacity_retention_temp": -15.0, "heat_pump_is_ducted": "false", "heat_pump_backup_heating_lockout_temp": "auto", "heat_pump_compressor_lockout_temp": "auto", "heat_pump_cooling_compressor_type": "variable speed", "heat_pump_cooling_sensible_heat_fraction": "auto", "heat_pump_crankcase_heater_watts": "auto", "geothermal_loop_configuration": "none", "geothermal_loop_borefield_configuration": "auto", "geothermal_loop_loop_flow": "auto", "geothermal_loop_boreholes_count": "auto", "geothermal_loop_boreholes_length": "auto", "geothermal_loop_boreholes_spacing": "auto", "geothermal_loop_boreholes_diameter": "auto", "geothermal_loop_grout_type": "auto", "geothermal_loop_pipe_type": "auto", "geothermal_loop_pipe_diameter": "auto"}
        dct_HVAC_Heating["MSHP, SEER 33, 13.3 HSPF, Ducted"] = {"heating_system_type": "none", "heating_system_heating_efficiency": 0.0, "heating_system_heating_capacity": "auto", "heating_system_heating_autosizing_limit": "auto", "heating_system_fraction_heat_load_served": 1.0, "heating_system_has_flue_or_chimney": "auto", "heat_pump_type": "mini-split", "heat_pump_heating_efficiency_type": "HSPF", "heat_pump_heating_efficiency": 13.3, "heat_pump_cooling_efficiency_type": "SEER", "heat_pump_cooling_efficiency": 33.0, "heat_pump_sizing_methodology": "ACCA", "heat_pump_sizing_is_duct_limited": "false", "heat_pump_backup_sizing_methodology": "auto", "heat_pump_heating_capacity": "auto", "heat_pump_heating_autosizing_limit": "auto", "heat_pump_fraction_heat_load_served": 1.0, "heat_pump_cooling_capacity": "auto", "heat_pump_cooling_autosizing_limit": "auto", "heat_pump_fraction_cool_load_served": 1.0, "heat_pump_backup_use_existing_system": "false", "heat_pump_backup_type": "integrated", "heat_pump_backup_fuel": "electricity", "heat_pump_backup_heating_efficiency": 1.0, "heat_pump_backup_heating_capacity": "auto", "heat_pump_backup_heating_autosizing_limit": "auto", "heat_pump_heating_capacity_retention_fraction": 0.5, "heat_pump_heating_capacity_retention_temp": -15.0, "heat_pump_is_ducted": "true", "heat_pump_backup_heating_lockout_temp": "auto", "heat_pump_compressor_lockout_temp": "auto", "heat_pump_cooling_compressor_type": "variable speed", "heat_pump_cooling_sensible_heat_fraction": "auto", "heat_pump_crankcase_heater_watts": "auto", "geothermal_loop_configuration": "none", "geothermal_loop_borefield_configuration": "auto", "geothermal_loop_loop_flow": "auto", "geothermal_loop_boreholes_count": "auto", "geothermal_loop_boreholes_length": "auto", "geothermal_loop_boreholes_spacing": "auto", "geothermal_loop_boreholes_diameter": "auto", "geothermal_loop_grout_type": "auto", "geothermal_loop_pipe_type": "auto", "geothermal_loop_pipe_diameter": "auto"}
        dct_HVAC_Heating["MSHP, SEER2 22.7, 10.3 HSPF2, Typical Cold Climate"] = {"heating_system_type": "none", "heating_system_heating_efficiency": 0.0, "heating_system_heating_capacity": "auto", "heating_system_heating_autosizing_limit": "auto", "heating_system_fraction_heat_load_served": 1.0, "heating_system_has_flue_or_chimney": "auto", "heat_pump_type": "mini-split", "heat_pump_heating_efficiency_type": "HSPF2", "heat_pump_heating_efficiency": 10.3, "heat_pump_cooling_efficiency_type": "SEER2", "heat_pump_cooling_efficiency": 22.7, "heat_pump_sizing_methodology": "ACCA", "heat_pump_sizing_is_duct_limited": "false", "heat_pump_backup_sizing_methodology": "auto", "heat_pump_heating_capacity": "auto", "heat_pump_heating_autosizing_limit": "auto", "heat_pump_fraction_heat_load_served": 1.0, "heat_pump_cooling_capacity": "auto", "heat_pump_cooling_autosizing_limit": "auto", "heat_pump_fraction_cool_load_served": 1.0, "heat_pump_backup_use_existing_system": "false", "heat_pump_backup_type": "integrated", "heat_pump_backup_fuel": "electricity", "heat_pump_backup_heating_efficiency": 1.0, "heat_pump_backup_heating_capacity": "auto", "heat_pump_backup_heating_autosizing_limit": "auto", "heat_pump_heating_capacity_retention_fraction": "auto", "heat_pump_heating_capacity_retention_temp": "auto", "heat_pump_is_ducted": "false", "heat_pump_backup_heating_lockout_temp": "auto", "heat_pump_compressor_lockout_temp": -15.0, "heat_pump_cooling_compressor_type": "variable speed", "heat_pump_cooling_sensible_heat_fraction": "auto", "heat_pump_crankcase_heater_watts": "auto", "geothermal_loop_configuration": "none", "geothermal_loop_borefield_configuration": "auto", "geothermal_loop_loop_flow": "auto", "geothermal_loop_boreholes_count": "auto", "geothermal_loop_boreholes_length": "auto", "geothermal_loop_boreholes_spacing": "auto", "geothermal_loop_boreholes_diameter": "auto", "geothermal_loop_grout_type": "auto", "geothermal_loop_pipe_type": "auto", "geothermal_loop_pipe_diameter": "auto"}
        dct_HVAC_Heating["None"] = {"heating_system_type": "none", "heating_system_heating_efficiency": 0.0, "heating_system_heating_capacity": "auto", "heating_system_heating_autosizing_limit": "auto", "heating_system_fraction_heat_load_served": 1.0, "heating_system_has_flue_or_chimney": "auto", "heat_pump_type": "none", "heat_pump_heating_efficiency_type": "HSPF", "heat_pump_heating_efficiency": 6.2, "heat_pump_cooling_efficiency_type": "SEER", "heat_pump_cooling_efficiency": 10.0, "heat_pump_sizing_methodology": "ACCA", "heat_pump_sizing_is_duct_limited": "false", "heat_pump_backup_sizing_methodology": "auto", "heat_pump_heating_capacity": "auto", "heat_pump_heating_autosizing_limit": "auto", "heat_pump_fraction_heat_load_served": 1.0, "heat_pump_cooling_capacity": "auto", "heat_pump_cooling_autosizing_limit": "auto", "heat_pump_fraction_cool_load_served": 1.0, "heat_pump_backup_use_existing_system": "false", "heat_pump_backup_type": "none", "heat_pump_backup_fuel": "electricity", "heat_pump_backup_heating_efficiency": 1.0, "heat_pump_backup_heating_capacity": "auto", "heat_pump_backup_heating_autosizing_limit": "auto", "geothermal_loop_configuration": "none", "geothermal_loop_borefield_configuration": "auto", "geothermal_loop_loop_flow": "auto", "geothermal_loop_boreholes_count": "auto", "geothermal_loop_boreholes_length": "auto", "geothermal_loop_boreholes_spacing": "auto", "geothermal_loop_boreholes_diameter": "auto", "geothermal_loop_grout_type": "auto", "geothermal_loop_pipe_type": "auto", "geothermal_loop_pipe_diameter": "auto"}
        dct_HVAC_Heating["Shared Heating"] = {}
        dct_HVAC_Heating["Void"] = {}
        
        #bois  #TODO: ajouter les autres types de chauffage
        dct_HVAC_Heating["Fuel Boiler, 72% AFUE & Electric Baseboard, 100% Efficiency"] = dct_HVAC_Heating["Fuel Boiler, 72% AFUE"].copy()
        dct_HVAC_Heating["Fuel Boiler, 72% AFUE & Electric Wall Furnace, 100% AFUE"] = dct_HVAC_Heating["Fuel Boiler, 72% AFUE"].copy()
        dct_HVAC_Heating["Fuel Boiler, 72% AFUE & Electric Furnace, 100% AFUE"] = dct_HVAC_Heating["Fuel Boiler, 72% AFUE"].copy()
        dct_HVAC_Heating["Fuel Boiler, 72% AFUE & Electric Boiler, 100% AFUE"] = dct_HVAC_Heating["Fuel Boiler, 72% AFUE"].copy()
        dct_HVAC_Heating["Fuel Boiler, 72% AFUE & Electric Wall Furnace, 100% AFUE.1"] = dct_HVAC_Heating["Fuel Boiler, 72% AFUE"].copy()
        dct_HVAC_Heating["Fuel Boiler, 72% AFUE & Fuel Furnace, 80% AFUE"] = dct_HVAC_Heating["Fuel Boiler, 72% AFUE"].copy()
        dct_HVAC_Heating["Fuel Boiler, 72% AFUE & Fuel Boiler, 80% AFUE"] = dct_HVAC_Heating["Fuel Boiler, 72% AFUE"].copy()

        for key_syst in ["ASHP, SEER 10, 6.2 HSPF",
                        "ASHP, SEER 10.3, 7.0 HSPF",
                        "ASHP, SEER 11.5, 7.5 HSPF",
                        "ASHP, SEER 13, 7.7 HSPF",
                        "ASHP, SEER 13, 8.0 HSPF",
                        "ASHP, SEER 14, 8.2 HSPF",
                        "ASHP, SEER 14.3, 8.5 HSPF",
                        "ASHP, SEER 15, 8.5 HSPF",
                        "ASHP, SEER 15, 9.0 HSPF",
                        "ASHP, SEER 16, 9.0 HSPF",
                        "ASHP, SEER 16, 9.2 HSPF"]:
            #TODO : add heat pump
            dct_HVAC_Heating["Fuel Boiler, 72% AFUE & "+key_syst] = dct_HVAC_Heating["Fuel Boiler, 72% AFUE"].copy()

            # bienergie PAC + Gz ou mazout app
            dct_HVAC_Heating["Fuel Furnace, 80% AFUE & "+key_syst] = dct_HVAC_Heating[key_syst].copy()
            dct_HVAC_Heating["Fuel Furnace, 80% AFUE & "+key_syst]["heat_pump_type"] = "air-to-air"
            dct_HVAC_Heating["Fuel Furnace, 80% AFUE & "+key_syst]["heat_pump_compressor_lockout_temp"] = 10.4 #F =-12C
            dct_HVAC_Heating["Fuel Furnace, 80% AFUE & "+key_syst]["heat_pump_backup_type"] = "integrated"
            dct_HVAC_Heating["Fuel Furnace, 80% AFUE & "+key_syst]["heat_pump_backup_fuel"] = "fuel oil"
            dct_HVAC_Heating["Fuel Furnace, 80% AFUE & "+key_syst]["heat_pump_backup_heating_efficiency"] = 0.8
            dct_HVAC_Heating["Fuel Furnace, 80% AFUE & "+key_syst]["heat_pump_backup_heating_capacity"] = "auto"

        # bienergie Élec+Mazout/Gaz (air) #TODO : ajouter les autres types de chauffage
        dct_HVAC_Heating["Electric Furnace, 100% AFUE & Fuel Furnace, 80% AFUE"] = dct_HVAC_Heating["Electric Furnace, 100% AFUE"].copy()
        
        # bienergie Élec+Mazout/Gaz (eau) #TODO : ajouter les autres types de chauffage
        dct_HVAC_Heating["Electric Boiler, 100% AFUE & Fuel Boiler, 80% AFUE"] = dct_HVAC_Heating["Electric Boiler, 100% AFUE"].copy()
        
                #windows
        arg = "HVAC Heating Efficiency"
        if (arg in dct_args.keys()):
            for args in dct_HVAC_Heating[dct_args[arg]]:
                if ((args not in dct_HPXML.keys()) & (dct_HVAC_Heating[dct_args[arg]][args]!="auto")):
                    dct_HPXML[args] = dct_HVAC_Heating[dct_args[arg]][args]
        #
        #bienergie : 90% à 95.6% au Mazout+elec
        #Bois en combinaison : 

        #arg = "Chauffage_Logement"
        #if (arg in dct_args.keys()):
        #    if dct_args[arg] in ["  "]:
        #        dctsysCh = dct_HVAC_Heating["  "]
        #        for args in dctsysCh[dct_args[arg]]:
        #            if ((args not in dct_HPXML.keys()) & (dctsysCh[dct_args[arg]][args]!="auto")):
        #                dct_HPXML[args] = dctsysCh[dct_args[arg]][args]

        #Chauffage_Logement: faire un csv pour avoir l'efficacité
        #'0': "Plinthes \xE9lectriques"
        #'1': "Unit\xE9s convecteurs, plancher ou plafond radiant"
        #'10': "Fournaise ou po\xEAle \xE0 bois et Syst\xE8me central \xE0 air chaud"
        #'11': "Fournaise ou po\xEAle \xE0 bois et Syst\xE8me central \xE0 eau chaude"
        #'12': "Fournaise ou po\xEAle \xE0 bois et Fournaise murale ou de plancher"
        #'2': Thermopompe
        #'3': "Syst\xE8me central \xE0 air chaud"
        #'4': "Syst\xE8me central \xE0 eau chaude"
        #'5': "Fournaise ou po\xEAle \xE0 bois"
        #'6': Fournaise murale ou de plancher
        #'7': "Fournaise ou po\xEAle \xE0 bois et Plinthes \xE9lectriques"
        #'8': "Fournaise ou po\xEAle \xE0 bois et Unit\xE9s convecteurs, plancher ou plafond\
        #\ radiant"
        #'9': "Fournaise ou po\xEAle \xE0 bois et Thermopompe"

        #heating_system_type	Heating System: Type	The type of heating system. Use 'none' if there is no heating system or if there is a heat pump serving a heating load.	Choice	true	['none', 'Furnace', 'WallFurnace', 'FloorFurnace', 'Boiler', 'ElectricResistance', 'Stove', 'SpaceHeater', 'Fireplace', 'Shared Boiler w/ Baseboard', 'Shared Boiler w/ Ductless Fan Coil']		Furnace
        #heating_system_fuel	Heating System: Fuel Type	The fuel type of the heating system. Ignored for ElectricResistance.	Choice	true	['electricity', 'natural gas', 'fuel oil', 'propane', 'wood', 'wood pellets', 'coal']		natural gas
        #heating_system_heating_efficiency	Heating System: Rated AFUE or Percent	The rated heating efficiency value of the heating system.	Double	true		Frac	0.78
        
        #heating_system_fuel
        arg = "Source_Energie_Chauf"
        args = "heating_system_fuel"
        if (args not in dct_HPXML.keys()):
            if (arg in dct_args.keys()):
                if dct_args[arg] in ["Electricite"]:
                    dct_HPXML[args] = 'electricity'
                elif dct_args[arg] in ["Mazout"]:
                    dct_HPXML[args] = 'fuel oil'
                elif dct_args[arg] in ["Gaz naturel"]:
                    dct_HPXML[args] = 'natural gas'
                elif dct_args[arg] in ["Bi-energie"]:
                    dct_HPXML[args] = 'natural gas'#à faire
                elif dct_args[arg] in ["Bois"]:
                    dct_HPXML[args] = 'wood'
        #_________________________________________________________________
        #climatisation
        if dct_HPXML.get("heat_pump_cooling_compressor_type") != None:
            dct_HPXML["cooling_system_type"] = 'none'
        else:
            arg = "Climatisation"
            args = "cooling_system_type"
            args2 = "cooling_system_cooling_compressor_type"
            if (args not in dct_HPXML.keys()):
                if (arg in dct_args.keys()):
                    if dct_args[arg] in ["Centrale"]:
                        dct_HPXML[args] = 'central air conditioner'
                        dct_HPXML[args2] = 'single stage'
                    elif dct_args[arg] in ["Murale"]:
                        dct_HPXML[args] = "mini-split"
                        dct_HPXML[args2] = 'variable speed'
                    elif dct_args[arg] in ["Fenetre, mobile, portable"]:
                        dct_HPXML[args] = "room air conditioner"
                        dct_HPXML[args2] = 'single stage'
                    elif dct_args[arg] in ["Aucune"]:
                        dct_HPXML[args] = 'none'
                    else:
                        if self.HPXMLArg.arguments[args].get("Default Value", "Defaut_Not_Existing")!="Defaut_Not_Existing":
                            dct_HPXML[args] = self.HPXMLArg.arguments[args].get("Default Value")
                            dct_HPXML[args2] = 'single stage'
                        else:
                            dct_HPXML[args] = 'none'
                else:
                    if self.HPXMLArg.arguments[args].get("Default Value", "Defaut_Not_Existing")!="Defaut_Not_Existing":
                        dct_HPXML[args] = self.HPXMLArg.arguments[args].get("Default Value")
                        dct_HPXML[args2] = 'single stage'
                    else:
                        dct_HPXML[args] = 'none'

            arg = "Climatisation"
            args = "cooling_system_cooling_compressor_type"

            if (args not in dct_HPXML.keys()):
                dct_HPXML[args] = None#'single stage' #defaut
                if (arg in dct_args.keys()):
                    if dct_args[arg] in ["Centrale"]:
                        dct_HPXML[args] = 'single stage'
                    elif dct_args[arg] in ["Murale"]:
                        dct_HPXML[args] = 'variable speed'
                    elif dct_args[arg] in ["Fenetre, mobile, portable"]:
                        dct_HPXML[args] = 'single stage'
                    elif dct_args[arg] in ["Aucune"]:
                        pass#dct_HPXML[args] = 'none'
                    else:
                        pass
                        #if self.HPXMLArg.arguments[args].get("Default Value", "Defaut_Not_Existing")!="Defaut_Not_Existing":
                        #    dct_HPXML[args] = self.HPXMLArg.arguments[args].get("Default Value")
                        #else:
                        #    pass#    dct_HPXML[args] = 'none'
                else:
                    pass
                    #if self.HPXMLArg.arguments[args].get("Default Value", "Defaut_Not_Existing")!="Defaut_Not_Existing":
                    #    dct_HPXML[args] = self.HPXMLArg.arguments[args].get("Default Value")
                    #    dct_HPXML[args2] = 'single stage'
                    #else:
                    #    dct_HPXML[args] = 'none'

        #_____________________________________________________________
        #misc_plug_loads_vehicle_present      
        arg = "Vehicule_Presence"
        argHPXML = "misc_plug_loads_vehicle_present"# du logement et non de l'immeuble
        ConsoVE = 3274 #kWh/an Provient du modèle de l'OPE
        ConsoVHR = 2248 #kWh/an Provient du modèle de l'OPE


        if (argHPXML not in dct_HPXML.keys()):
            if (arg in dct_args.keys()):
                if dct_args[arg] == "Aucune_VE_Aucune_VHR":
                    dct_HPXML[argHPXML] = False
                    dct_HPXML["misc_plug_loads_vehicle_usage_multiplier"]=0
                    dct_HPXML["misc_plug_loads_vehicle_2_usage_multiplier"] = 0
                else:
                    dct_HPXML[argHPXML] = True
                    if dct_args[arg] == "Une_VE_Aucune_VHR":
                        dct_HPXML["misc_plug_loads_vehicle_annual_kwh"] = ConsoVE
                        dct_HPXML["misc_plug_loads_vehicle_usage_multiplier"]=1
                        misc_plug_loads_vehicle_2_usage_multiplier = 1
                    elif dct_args[arg] == "Deux_VE_Aucune_VHR":
                        dct_HPXML["misc_plug_loads_vehicle_annual_kwh"] = ConsoVE
                        dct_HPXML["misc_plug_loads_vehicle_usage_multiplier"]=1
                        misc_plug_loads_vehicle_2_usage_multiplier = 1
                    elif dct_args[arg] == "Trois_VE_Aucune_VHR":
                        dct_HPXML["misc_plug_loads_vehicle_annual_kwh"] = ConsoVE
                        dct_HPXML["misc_plug_loads_vehicle_usage_multiplier"]=1
                        misc_plug_loads_vehicle_2_usage_multiplier = 1
                    elif dct_args[arg] == "Aucune_VE_Une_VHR":
                        dct_HPXML["misc_plug_loads_vehicle_annual_kwh"] = ConsoVHR
                        dct_HPXML["misc_plug_loads_vehicle_usage_multiplier"]=1
                        misc_plug_loads_vehicle_2_usage_multiplier = 1
                    elif dct_args[arg] == "Une_VE_Une_VHR":
                        dct_HPXML["misc_plug_loads_vehicle_annual_kwh"] = ConsoVE
                        dct_HPXML["misc_plug_loads_vehicle_usage_multiplier"]=1
                        misc_plug_loads_vehicle_2_usage_multiplier = 1
                    elif dct_args[arg] == "Deux_VE_Une_VHR":
                        dct_HPXML["misc_plug_loads_vehicle_annual_kwh"] = ConsoVE
                        dct_HPXML["misc_plug_loads_vehicle_usage_multiplier"]=1
                        misc_plug_loads_vehicle_2_usage_multiplier = 1
                    elif dct_args[arg] == "Trois_VE_Une_VHR":
                        dct_HPXML["misc_plug_loads_vehicle_annual_kwh"] = ConsoVE
                        dct_HPXML["misc_plug_loads_vehicle_usage_multiplier"]=1
                        misc_plug_loads_vehicle_2_usage_multiplier = 1
                    elif dct_args[arg] == "Aucune_VE_Deux_VHR":
                        dct_HPXML["misc_plug_loads_vehicle_annual_kwh"] = ConsoVHR
                        dct_HPXML["misc_plug_loads_vehicle_usage_multiplier"]=1
                        misc_plug_loads_vehicle_2_usage_multiplier = 1
                    elif dct_args[arg] == "Une_VE_Deux_VHR":
                        dct_HPXML["misc_plug_loads_vehicle_annual_kwh"] = ConsoVE
                        dct_HPXML["misc_plug_loads_vehicle_usage_multiplier"]=1
                        misc_plug_loads_vehicle_2_usage_multiplier = 1
                    elif dct_args[arg] == "Deux_VE_Deux_VHR":
                        dct_HPXML["misc_plug_loads_vehicle_annual_kwh"] = ConsoVE
                        dct_HPXML["misc_plug_loads_vehicle_usage_multiplier"]=1
                        misc_plug_loads_vehicle_2_usage_multiplier = 1
                    elif dct_args[arg] == "Trois_VE_Deux_VHR":
                        dct_HPXML["misc_plug_loads_vehicle_annual_kwh"] = ConsoVE
                        dct_HPXML["misc_plug_loads_vehicle_usage_multiplier"]=1
                        misc_plug_loads_vehicle_2_usage_multiplier = 1

                    dct_HPXML["misc_plug_loads_vehicle_usage_multiplier"]=dct_HPXML["misc_plug_loads_vehicle_usage_multiplier"] * misc_plug_loads_vehicle_2_usage_multiplier
            else:
                dct_HPXML[argHPXML] = False

       #_____________________________________________________________
        #permanent_spa_present      
        arg = "Spa_Presence"
        argHPXML = "permanent_spa_present"# du logement et non de l'immeuble
        #permanent_spa_present=True
        #permanent_spa_pump_annual_kwh=auto
        #permanent_spa_pump_usage_multiplier=1.0
        #permanent_spa_heater_type=electric resistance
        #permanent_spa_heater_annual_kwh=auto
        #permanent_spa_heater_annual_therm=0
        #permanent_spa_heater_usage_multiplier=1.0#permanent_spa_pump_annual_kwh = "auto"
        #permanent_spa_pump_usage_multiplier=1.0
        
        if (argHPXML not in dct_HPXML.keys()):
            if (arg in dct_args.keys()):
                if dct_args[arg] == "Oui":
                    dct_HPXML[argHPXML] = True
                    dct_HPXML["permanent_spa_pump_annual_kwh"] = 0
                    dct_HPXML["permanent_spa_heater_annual_kwh"] =  49/0.048*(0.5+0.25*dct_HPXML['geometry_unit_num_bedrooms']/3+0.25*dct_HPXML['geometry_unit_cfa']/1920)
                else:
                    dct_HPXML[argHPXML] = False
            else:
                dct_HPXML[argHPXML] = False
                #permanent_spa_present      
        
        arg = "Spa ChaufType"
        argHPXML = "permanent_spa_heater_type"# du logement et non de l'immeuble
        if (argHPXML not in dct_HPXML.keys()):
            if (arg in dct_args.keys()):
                dct_HPXML[argHPXML] = dct_args[arg]
            else:
                dct_HPXML[argHPXML] = None

        #_____________________________________________________________
        #pool_present
        arg = "Piscine_Presence"
        argHPXML = "pool_present"# du logement et non de l'immeuble
        if (argHPXML not in dct_HPXML.keys()):
            if (arg in dct_args.keys()):
                if dct_args[arg] == "Oui":
                    dct_HPXML[argHPXML] = True
                else:
                    dct_HPXML[argHPXML] = False
            else:
                dct_HPXML[argHPXML] = False

        #_____________________________________________________________
        #pool_heater_type
        #pool_heater_annual_kwh=auto
        #pool_heater_annual_therm=0
        #pool_heater_usage_multiplier=0.8
        arg = "Piscine_ChaufType"
        argHPXML = "pool_heater_type"# du logement et non de l'immeuble
        if (argHPXML not in dct_HPXML.keys()):
            if (arg in dct_args.keys()):
                if dct_args[arg] in ["Electrique"]:
                    dct_HPXML[argHPXML] = "electric resistance"
                elif dct_args[arg] in ["Gaz Naturel", "Propane"]:
                    dct_HPXML[argHPXML] = "gas fired"
                elif dct_args[arg] in ["Thermopompe"]:
                    dct_HPXML[argHPXML] = "heat pump"
                elif dct_args[arg] in ["Aucun", "Ne sait pas", "Capteur Solaire", "Bois", "Mazout"]:
                    dct_HPXML[argHPXML] = None
            else:
                dct_HPXML[argHPXML] = None
        #_____________________________________________________________
        #Piscine_Toile
        arg = "Piscine_Toile"
        argHPXML = "pool_heater_usage_multiplier"# du logement et non de l'immeuble
        if (argHPXML not in dct_HPXML.keys()):
            if (arg in dct_args.keys()):
                if dct_args[arg] in ["Oui"]:
                    dct_HPXML[argHPXML] = 0.3
                elif dct_args[arg] in ["Non"]:
                    dct_HPXML[argHPXML] = 1
                else:
                    dct_HPXML[argHPXML] = 1
            else:
                dct_HPXML[argHPXML] = 1

        #_____________________________________________________________
        #Piscine_Minuterie
        arg = "Piscine_Minuterie"
        argHPXML = "pool_pump_usage_multiplier"# du logement et non de l'immeuble
        if (argHPXML not in dct_HPXML.keys()):
            if (arg in dct_args.keys()):
                if dct_args[arg] in ["Oui"]:
                    dct_HPXML[argHPXML] = 0.45 # site web hq 2025-09-04
                elif dct_args[arg] in ["Non"]:
                    dct_HPXML[argHPXML] = 1
                else:
                    dct_HPXML[argHPXML] = 1
            else:
                dct_HPXML[argHPXML] = 1

        #_____________________________________________________________
        #Water Heater
        #water_heater_type
        #water_heater_fuel_type
        #water_heater_location
        #water_heater_tank_volume

        arg = "ChaufEau_ChaufType"
        argHPXML = "water_heater_fuel_type"# du logement et non de l'immeuble
        if (argHPXML not in dct_HPXML.keys()):
            if (arg in dct_args.keys()):
                if dct_args[arg] in ["Electrique"]:
                    dct_HPXML[argHPXML] = "electricity"
                    dct_HPXML["water_heater_efficiency_type"]="EnergyFactor"
                    if dct_args["ChaufEau_Type"]=="Chauffe-eau sans réservoir":
                        dct_HPXML["water_heater_efficiency"]=0.99
                    else:
                        dct_HPXML["water_heater_efficiency"]=0.92
                    dct_HPXML["water_heater_recovery_efficiency"]=0
                    dct_HPXML["water_heater_standby_loss"]=0
                    dct_HPXML["water_heater_jacket_rvalue"]=0
                    dct_HPXML["water_heater_setpoint_temperature"]=125
                elif dct_args[arg] in ["Propane"]:
                    dct_HPXML[argHPXML] = "propane"
                    dct_HPXML["water_heater_efficiency_type"]="EnergyFactor"
                    dct_HPXML["water_heater_efficiency"]=0.59
                    dct_HPXML["water_heater_recovery_efficiency"]=0.76
                    dct_HPXML["water_heater_standby_loss"]=0
                    dct_HPXML["water_heater_jacket_rvalue"]=0
                    dct_HPXML["water_heater_setpoint_temperature"]=125
                elif dct_args[arg] in ["Gaz Naturel"]:
                    dct_HPXML[argHPXML] = "natural gas"
                    dct_HPXML["water_heater_efficiency_type"]="EnergyFactor"
                    dct_HPXML["water_heater_efficiency"]=0.59
                    dct_HPXML["water_heater_recovery_efficiency"]=0.76
                    dct_HPXML["water_heater_standby_loss"]=0
                    dct_HPXML["water_heater_jacket_rvalue"]=0
                    dct_HPXML["water_heater_setpoint_temperature"]=125
                elif dct_args[arg] in ["Mazout"]:
                    dct_HPXML[argHPXML] = "fuel oil"
                    dct_HPXML["water_heater_efficiency_type"]="EnergyFactor"
                    dct_HPXML["water_heater_efficiency"]=0.62
                    dct_HPXML["water_heater_recovery_efficiency"]=0.78
                    dct_HPXML["water_heater_standby_loss"]=0
                    dct_HPXML["water_heater_jacket_rvalue"]=0
                    dct_HPXML["water_heater_setpoint_temperature"]=125
                elif dct_args[arg] in ["Bois"]:
                    dct_HPXML[argHPXML] = "Wood Pellets"
                    dct_HPXML["water_heater_efficiency_type"]="EnergyFactor"
                    dct_HPXML["water_heater_efficiency"]=0.59
                    dct_HPXML["water_heater_recovery_efficiency"]=0.76
                    dct_HPXML["water_heater_standby_loss"]=0
                    dct_HPXML["water_heater_jacket_rvalue"]=0
                    dct_HPXML["water_heater_setpoint_temperature"]=125
                else:
                    dct_HPXML[argHPXML] = "electricity"
                    if dct_args["ChaufEau_Type"]=="Chauffe-eau sans réservoir":
                        dct_HPXML["water_heater_efficiency"]=0.99
                    else:
                        dct_HPXML["water_heater_efficiency"]=0.92
                    dct_HPXML["water_heater_recovery_efficiency"]=0
                    dct_HPXML["water_heater_standby_loss"]=0
                    dct_HPXML["water_heater_jacket_rvalue"]=0
                    dct_HPXML["water_heater_setpoint_temperature"]=125
            else:
                dct_HPXML[argHPXML] = 1
        
        arg = "ChaufEau_Type"
        argHPXML = "water_heater_type"# du logement et non de l'immeuble
        if (argHPXML not in dct_HPXML.keys()):
            if (arg in dct_args.keys()):
                if dct_args[arg] in ["Non definit","Ne sait pas"]:
                    if dct_args["ChaufEau_Presence"] == "Aucun":
                        dct_HPXML[argHPXML] = None
                    elif dct_args["ChaufEau_Presence"] == "Central":
                        dct_HPXML[argHPXML] = "storage water heater"
                    else: #elif dct_args["ChaufEau_Presence"] == "Logement":
                        dct_HPXML[argHPXML] = "storage water heater"
                elif dct_args[arg] in ["Chauffe-eau sans réservoir"]:
                    dct_HPXML[argHPXML] = "instantaneous water heater"
                else:
                    dct_HPXML[argHPXML] = "storage water heater"
            else:
                dct_HPXML[argHPXML] = "storage water heater"


        arg = "ChaufEau_Presence"
        argHPXML = "water_heater_location"# du logement et non de l'immeuble
        if (argHPXML not in dct_HPXML.keys()):
            if (arg in dct_args.keys()):
                if dct_args[arg] in ["Logement"]:
                    dct_HPXML[argHPXML] = "conditioned space"
                elif dct_args[arg] in ["Central"]:
                    dct_HPXML[argHPXML] = "other multifamily buffer space"
                else:
                    if dct_args["Type_Logement"] in ["Maison individuelle"]:
                        dct_HPXML[argHPXML] = "conditioned space"
                    elif dct_args["Type_Logement"] in ["Maison en rangee","Collective", "Triplex", "Duplex"]:
                        dct_HPXML[argHPXML] = "other multifamily buffer space"
                    #dct_HPXML[argHPXML] = None
                    #dct_HPXML["water_heater_type"] = None #if no water heater

        arg = "ChaufEau_Type"
        argHPXML = "water_heater_tank_volume"# du logement et non de l'immeuble
        if (argHPXML not in dct_HPXML.keys()):
            if (arg in dct_args.keys()):
                if dct_args[arg] in ["Moins de 22 gallons"]:
                    dct_HPXML[argHPXML] = 15 #gallons
                elif dct_args[arg] in ["22 gallons"]:
                    dct_HPXML[argHPXML] = 22
                elif dct_args[arg] in ["23-40 gallons"]:
                    dct_HPXML[argHPXML] = 26
                elif dct_args[arg] in ["40 gallons"]:
                    dct_HPXML[argHPXML] = 40
                elif dct_args[arg] in ["41-59 gallons"]:
                    dct_HPXML[argHPXML] = 50
                elif dct_args[arg] in ["60 gallons"]:
                    dct_HPXML[argHPXML] = 60
                elif dct_args[arg] in ["60 et plus gallons"]:
                    dct_HPXML[argHPXML] = 70
                elif dct_args[arg] in ["Chauffe-eau sans réservoi"]:
                    dct_HPXML[argHPXML] = 0

        # Clothes dryer
        #Make dict only based on data - from code parse option_lookup
        dct_ClothesDryer = {}
        dct_ClothesDryer["Electric, Heat Pump, Ventless"] = {"clothes_dryer_present": True, "clothes_dryer_location": "auto", "clothes_dryer_fuel_type": "electricity", "clothes_dryer_efficiency_type": "CombinedEnergyFactor", "clothes_dryer_efficiency": 4.5, "clothes_dryer_vented_flow_rate": 0}
        dct_ClothesDryer["Electric, Premium"] = {"clothes_dryer_present": True, "clothes_dryer_location": "auto", "clothes_dryer_fuel_type": "electricity", "clothes_dryer_efficiency_type": "CombinedEnergyFactor", "clothes_dryer_efficiency": 3.42, "clothes_dryer_vented_flow_rate": "auto"}
        dct_ClothesDryer["Electric, Premium, EnergyStar"] = {"clothes_dryer_present": True, "clothes_dryer_location": "auto", "clothes_dryer_fuel_type": "electricity", "clothes_dryer_efficiency_type": "CombinedEnergyFactor", "clothes_dryer_efficiency": 3.93, "clothes_dryer_vented_flow_rate": "auto"}
        dct_ClothesDryer["Electric, Premium, Heat Pump, Ventless"] = {"clothes_dryer_present": True, "clothes_dryer_location": "auto", "clothes_dryer_fuel_type": "electricity", "clothes_dryer_efficiency_type": "CombinedEnergyFactor", "clothes_dryer_efficiency": 5.2, "clothes_dryer_vented_flow_rate": 0}
        dct_ClothesDryer["Gas, Premium"] = {"clothes_dryer_present": True, "clothes_dryer_location": "auto", "clothes_dryer_fuel_type": "natural gas", "clothes_dryer_efficiency_type": "CombinedEnergyFactor", "clothes_dryer_efficiency": 3.03, "clothes_dryer_vented_flow_rate": "auto"}
        dct_ClothesDryer["Electric"] = {"clothes_dryer_present": True, "clothes_dryer_location": "auto", "clothes_dryer_fuel_type": "electricity", "clothes_dryer_efficiency_type": "CombinedEnergyFactor", "clothes_dryer_efficiency": 2.70, "clothes_dryer_vented_flow_rate": "auto"}
        dct_ClothesDryer["Gas"] = {"clothes_dryer_present": True, "clothes_dryer_location": "auto", "clothes_dryer_fuel_type": "natural gas", "clothes_dryer_efficiency_type": "CombinedEnergyFactor", "clothes_dryer_efficiency": 2.39, "clothes_dryer_vented_flow_rate": "auto"}
        dct_ClothesDryer["None"] = {"clothes_dryer_present": False, "clothes_dryer_location": "auto", "clothes_dryer_fuel_type": "natural gas", "clothes_dryer_efficiency_type": "CombinedEnergyFactor", "clothes_dryer_efficiency": 2.70, "clothes_dryer_vented_flow_rate": "auto"}
        dct_ClothesDryer["Propane"] = {"clothes_dryer_present": True, "clothes_dryer_location": "auto", "clothes_dryer_fuel_type": "propane", "clothes_dryer_efficiency_type": "CombinedEnergyFactor", "clothes_dryer_efficiency": 2.39, "clothes_dryer_vented_flow_rate": "auto"}
        #dct_ClothesDryer["Void"] = {}
        
        arg = "SecheLinge_Presence"
        if (arg in dct_args.keys()):
            if dct_args[arg] in ["Oui"]:
                args_value = "Electric"
            else:
                args_value = "None"
            for args in dct_ClothesDryer[args_value]:
                if ((args not in dct_HPXML.keys()) & (dct_ClothesDryer[args_value][args]!="auto")):
                    dct_HPXML[args] = dct_ClothesDryer[args_value][args]

        dct_ClothesDryer_Usage = {}
        dct_ClothesDryer_Usage["100% Usage"] = {"clothes_dryer_usage_multiplier": 1.0}
        dct_ClothesDryer_Usage["120% Usage"] = {"clothes_dryer_usage_multiplier": 1.2}
        dct_ClothesDryer_Usage["80% Usage"] = {"clothes_dryer_usage_multiplier": 0.8}
        arg = "Clothes Dryer Usage Level"
        for args in dct_ClothesDryer_Usage[dct_args[arg]]:
            if ((args not in dct_HPXML.keys()) & (dct_ClothesDryer_Usage[dct_args[arg]][args]!="auto")):
                dct_HPXML[args] = dct_ClothesDryer_Usage[dct_args[arg]][args]


        dct_ClothesWasher = {}
        dct_ClothesWasher["EnergyStar, Cold Only"] = {"clothes_washer_location": "auto", "clothes_washer_efficiency_type": "IntegratedModifiedEnergyFactor", "clothes_washer_efficiency": 2.07, "clothes_washer_rated_annual_kwh": 123, "clothes_washer_label_electric_rate": 0.1065, "clothes_washer_label_gas_rate": 1.218, "clothes_washer_label_annual_gas_cost": 9, "clothes_washer_label_usage": 7.538462, "clothes_washer_capacity": 3.68}
        dct_ClothesWasher["CEE Advanced Tier"] = {"clothes_washer_location": "auto", "clothes_washer_efficiency_type": "IntegratedModifiedEnergyFactor", "clothes_washer_efficiency": 3.1, "clothes_washer_rated_annual_kwh": 120, "clothes_washer_label_electric_rate": 0.121, "clothes_washer_label_gas_rate": 1.087, "clothes_washer_label_annual_gas_cost": 14, "clothes_washer_label_usage": 7.538462, "clothes_washer_capacity": 5.8}
        dct_ClothesWasher["EnergyStar"] = {"clothes_washer_location": "auto", "clothes_washer_efficiency_type": "IntegratedModifiedEnergyFactor", "clothes_washer_efficiency": 2.07, "clothes_washer_rated_annual_kwh": 123, "clothes_washer_label_electric_rate": 0.1065, "clothes_washer_label_gas_rate": 1.218, "clothes_washer_label_annual_gas_cost": 9, "clothes_washer_label_usage": 7.538462, "clothes_washer_capacity": 3.68}
        dct_ClothesWasher["EnergyStar More Efficient"] = {"clothes_washer_location": "auto", "clothes_washer_efficiency_type": "IntegratedModifiedEnergyFactor", "clothes_washer_efficiency": 2.83, "clothes_washer_rated_annual_kwh": 90, "clothes_washer_label_electric_rate": 0.121, "clothes_washer_label_gas_rate": 1.087, "clothes_washer_label_annual_gas_cost": 8, "clothes_washer_label_usage": 7.538462, "clothes_washer_capacity": 4.5}
        dct_ClothesWasher["EnergyStar Most Efficient"] = {"clothes_washer_location": "auto", "clothes_washer_efficiency_type": "IntegratedModifiedEnergyFactor", "clothes_washer_efficiency": 2.92, "clothes_washer_rated_annual_kwh": 75, "clothes_washer_label_electric_rate": 0.121, "clothes_washer_label_gas_rate": 1.087, "clothes_washer_label_annual_gas_cost": 7, "clothes_washer_label_usage": 7.538462, "clothes_washer_capacity": 4.5}
        dct_ClothesWasher["None"] = {"clothes_washer_location": "auto", "clothes_washer_efficiency_type": "IntegratedModifiedEnergyFactor", "clothes_washer_efficiency": 0, "clothes_washer_rated_annual_kwh": 0, "clothes_washer_label_electric_rate": 0, "clothes_washer_label_gas_rate": 0, "clothes_washer_label_annual_gas_cost": 0, "clothes_washer_label_usage": 0, "clothes_washer_capacity": 0}
        dct_ClothesWasher["Standard"] = {"clothes_washer_location": "auto", "clothes_washer_efficiency_type": "IntegratedModifiedEnergyFactor", "clothes_washer_efficiency": 0.95, "clothes_washer_rated_annual_kwh": 387, "clothes_washer_label_electric_rate": 0.1065, "clothes_washer_label_gas_rate": 1.218, "clothes_washer_label_annual_gas_cost": 24, "clothes_washer_label_usage": 7.538462, "clothes_washer_capacity": 3.5}
        #dct_ClothesWasher["Void"] = {}
        arg = "LaveLinge_Type"
        if (arg in dct_args.keys()):
            if dct_args[arg] in ["Aucun"]:
                args_value = "None"
            elif dct_args[arg] in ["Traditionnelle", "Frontale"]:
                args_value = "Standard"
            for args in dct_ClothesWasher[args_value]:
                if ((args not in dct_HPXML.keys()) & (dct_ClothesWasher[args_value][args]!="auto")):
                    dct_HPXML[args] = dct_ClothesWasher[args_value][args]

        dct_ClothesWasher_Present = {}
        dct_ClothesWasher_Present["None"] = {"clothes_washer_present": False}
        dct_ClothesWasher_Present["Void"] = {}
        dct_ClothesWasher_Present["Yes"] = {"clothes_washer_present": True}
        arg = "LaveLinge_Type"
        if (arg in dct_args.keys()):
            if dct_args[arg] in ["Aucun"]:
                args_value = "None"
            elif dct_args[arg] in ["Traditionnelle", "Frontale"]:
                args_value = "Yes"
            for args in dct_ClothesWasher_Present[args_value]:
                if ((args not in dct_HPXML.keys()) & (dct_ClothesWasher_Present[args_value][args]!="auto")):
                    dct_HPXML[args] = dct_ClothesWasher_Present[args_value][args]

        dct_ClothesWasher_Usage = {}
        dct_ClothesWasher_Usage["100% Usage"] = {"clothes_washer_usage_multiplier": 1.0}
        dct_ClothesWasher_Usage["120% Usage"] = {"clothes_washer_usage_multiplier": 1.2}
        dct_ClothesWasher_Usage["80% Usage"] = {"clothes_washer_usage_multiplier": 0.8}
        arg = "Clothes Washer Usage Level"
        for args in dct_ClothesWasher_Usage[dct_args[arg]]:
            if ((args not in dct_HPXML.keys()) & (dct_ClothesWasher_Usage[dct_args[arg]][args]!="auto")):
                dct_HPXML[args] = dct_ClothesWasher_Usage[dct_args[arg]][args]

        #_____________________________________________________________
        dct_CookingRange = {}
        dct_CookingRange["Electric Induction"] = {"cooking_range_oven_present": True, "cooking_range_oven_location": "auto", "cooking_range_oven_fuel_type": "electricity", "cooking_range_oven_is_induction": True, "cooking_range_oven_is_convection": "auto"}
        dct_CookingRange["Electric Resistance"] = {"cooking_range_oven_present": True, "cooking_range_oven_location": "auto", "cooking_range_oven_fuel_type": "electricity", "cooking_range_oven_is_induction": False, "cooking_range_oven_is_convection": "auto"}
        dct_CookingRange["Gas"] = {"cooking_range_oven_present": True, "cooking_range_oven_location": "auto", "cooking_range_oven_fuel_type": "natural gas", "cooking_range_oven_is_induction": False, "cooking_range_oven_is_convection": "auto"}
        dct_CookingRange["None"] = {"cooking_range_oven_present": False, "cooking_range_oven_location": "auto", "cooking_range_oven_fuel_type": "natural gas", "cooking_range_oven_is_induction": False, "cooking_range_oven_is_convection": "auto"}
        dct_CookingRange["Propane"] = {"cooking_range_oven_present": True, "cooking_range_oven_location": "auto", "cooking_range_oven_fuel_type": "propane", "cooking_range_oven_is_induction": False, "cooking_range_oven_is_convection": "auto"}
        #dct_CookingRange["Void"] = {}
        arg = "Cuisiniere_Energie"
        if (arg in dct_args.keys()):
            if dct_args[arg] in ["Electrique", "Ne sait pas", "Autre"]:
                args_value = "Electric Resistance"
            elif dct_args[arg] in ["Gaz"]:
                args_value = "Gas"
            elif dct_args[arg] in ["Aucun"]:
                args_value = "None"
            for args in dct_CookingRange[args_value]:
                if ((args not in dct_HPXML.keys()) & (dct_CookingRange[args_value][args]!="auto")):
                    dct_HPXML[args] = dct_CookingRange[args_value][args]

        dct_CookingRang_Usage = {}
        dct_CookingRang_Usage["100% Usage"] = {"cooking_range_oven_usage_multiplier": 1.0}
        dct_CookingRang_Usage["120% Usage"] = {"cooking_range_oven_usage_multiplier": 1.2}
        dct_CookingRang_Usage["80% Usage"] = {"cooking_range_oven_usage_multiplier": 0.8}
        arg = "Cooking Range Usage Level"
        for args in dct_CookingRang_Usage[dct_args[arg]]:
            if ((args not in dct_HPXML.keys()) & (dct_CookingRang_Usage[dct_args[arg]][args]!="auto")):
                dct_HPXML[args] = dct_CookingRang_Usage[dct_args[arg]][args]

        #_____________________________________________________________
        dct_Dishwasher = {}
        dct_Dishwasher["144 Rated kWh"] = {"dishwasher_present": True, "dishwasher_location": "auto", "dishwasher_efficiency_type": "RatedAnnualkWh", "dishwasher_efficiency": 144, "dishwasher_label_electric_rate": 0.12, "dishwasher_label_gas_rate": 1.09, "dishwasher_label_annual_gas_cost": 13, "dishwasher_label_usage": 4, "dishwasher_place_setting_capacity": 12}
        dct_Dishwasher["199 Rated kWh"] = {"dishwasher_present": True, "dishwasher_location": "auto", "dishwasher_efficiency_type": "RatedAnnualkWh", "dishwasher_efficiency": 199, "dishwasher_label_electric_rate": 0.12, "dishwasher_label_gas_rate": 1.09, "dishwasher_label_annual_gas_cost": 18, "dishwasher_label_usage": 4, "dishwasher_place_setting_capacity": 12}
        dct_Dishwasher["220 Rated kWh"] = {"dishwasher_present": True, "dishwasher_location": "auto", "dishwasher_efficiency_type": "RatedAnnualkWh", "dishwasher_efficiency": 220, "dishwasher_label_electric_rate": 0.12, "dishwasher_label_gas_rate": 1.09, "dishwasher_label_annual_gas_cost": 19, "dishwasher_label_usage": 4, "dishwasher_place_setting_capacity": 12}
        dct_Dishwasher["255 Rated kWh"] = {"dishwasher_present": True, "dishwasher_location": "auto", "dishwasher_efficiency_type": "RatedAnnualkWh", "dishwasher_efficiency": 255, "dishwasher_label_electric_rate": 0.12, "dishwasher_label_gas_rate": 1.09, "dishwasher_label_annual_gas_cost": 21, "dishwasher_label_usage": 4, "dishwasher_place_setting_capacity": 12}
        dct_Dishwasher["270 Rated kWh"] = {"dishwasher_present": True, "dishwasher_location": "auto", "dishwasher_efficiency_type": "RatedAnnualkWh", "dishwasher_efficiency": 270, "dishwasher_label_electric_rate": 0.12, "dishwasher_label_gas_rate": 1.09, "dishwasher_label_annual_gas_cost": 22, "dishwasher_label_usage": 4, "dishwasher_place_setting_capacity": 12}
        dct_Dishwasher["290 Rated kWh"] = {"dishwasher_present": True, "dishwasher_location": "auto", "dishwasher_efficiency_type": "RatedAnnualkWh", "dishwasher_efficiency": 290, "dishwasher_label_electric_rate": 0.12, "dishwasher_label_gas_rate": 1.09, "dishwasher_label_annual_gas_cost": 23, "dishwasher_label_usage": 4, "dishwasher_place_setting_capacity": 12}
        dct_Dishwasher["318 Rated kWh"] = {"dishwasher_present": True, "dishwasher_location": "auto", "dishwasher_efficiency_type": "RatedAnnualkWh", "dishwasher_efficiency": 318, "dishwasher_label_electric_rate": 0.12, "dishwasher_label_gas_rate": 1.09, "dishwasher_label_annual_gas_cost": 25, "dishwasher_label_usage": 4, "dishwasher_place_setting_capacity": 12}
        dct_Dishwasher["None"] = {"dishwasher_present": False, "dishwasher_location": "auto", "dishwasher_efficiency_type": "RatedAnnualkWh", "dishwasher_efficiency": 0, "dishwasher_label_electric_rate": 0, "dishwasher_label_gas_rate": 0, "dishwasher_label_annual_gas_cost": 0, "dishwasher_label_usage": 0, "dishwasher_place_setting_capacity": 0}
        #dct_Dishwasher["Void"] = {}
        arg = "Dishwasher Energy"
        if (arg in dct_args.keys()):
            if dct_args["LaveVaisselle_Presence"] in ["Oui"]:
                for args in dct_Dishwasher[dct_args[arg]]:
                    if ((args not in dct_HPXML.keys()) & (dct_Dishwasher[dct_args[arg]][args]!="auto")):
                        dct_HPXML[args] = dct_Dishwasher[dct_args[arg]][args]
            else:
                args_value = "None"
                for args in dct_Dishwasher[args_value]:
                    if ((args not in dct_HPXML.keys()) & (dct_Dishwasher[args_value][args]!="auto")):
                        dct_HPXML[args] = dct_Dishwasher[args_value][args]
                
        dct_Dishwasher_Usage = {}
        dct_Dishwasher_Usage["100% Usage"] = {"cooking_range_oven_usage_multiplier": 1.0}
        dct_Dishwasher_Usage["120% Usage"] = {"cooking_range_oven_usage_multiplier": 1.2}
        dct_Dishwasher_Usage["80% Usage"] = {"cooking_range_oven_usage_multiplier": 0.8}
        arg = "Diswasher Usage Level"
        for args in dct_Dishwasher_Usage[dct_args[arg]]:
            if ((args not in dct_HPXML.keys()) & (dct_Dishwasher_Usage[dct_args[arg]][args]!="auto")):
                dct_HPXML[args] = dct_Dishwasher_Usage[dct_args[arg]][args]
        #_____________________________________________________________
        #TODO : Refrigerator
        #TODO : Meisc Extra Refrigerator
        #TODO : Misc Freezer

        dct_ExtraRefrigerator = {}
        dct_ExtraRefrigerator["EF 15.9, Fed Standard, bottom freezer-reference fridge"] = {"extra_refrigerator_present": True, "extra_refrigerator_location": "auto", "extra_refrigerator_rated_annual_kwh": 573, "extra_refrigerator_usage_multiplier": 1.0}
        dct_ExtraRefrigerator["EF 19.8, bottom freezer"] = {"extra_refrigerator_present": True, "extra_refrigerator_location": "auto", "extra_refrigerator_rated_annual_kwh": 458, "extra_refrigerator_usage_multiplier": 1.0}
        dct_ExtraRefrigerator["EF 6.9, Average Installed"] = {"extra_refrigerator_present": True, "extra_refrigerator_location": "auto", "extra_refrigerator_rated_annual_kwh": 1102, "extra_refrigerator_usage_multiplier": 1.0}
        dct_ExtraRefrigerator["EF 6.9, National Average"] = {"extra_refrigerator_present": True, "extra_refrigerator_location": "auto", "extra_refrigerator_rated_annual_kwh": 1102, "extra_refrigerator_usage_multiplier": 0.221}
        dct_ExtraRefrigerator["EF 10.2"] = {"extra_refrigerator_present": True, "extra_refrigerator_location": "auto", "extra_refrigerator_rated_annual_kwh": 748, "extra_refrigerator_usage_multiplier": 1.0}
        dct_ExtraRefrigerator["EF 10.5"] = {"extra_refrigerator_present": True, "extra_refrigerator_location": "auto", "extra_refrigerator_rated_annual_kwh": 727, "extra_refrigerator_usage_multiplier": 1.0}
        dct_ExtraRefrigerator["EF 15.9"] = {"extra_refrigerator_present": True, "extra_refrigerator_location": "auto", "extra_refrigerator_rated_annual_kwh": 480, "extra_refrigerator_usage_multiplier": 1.0}
        dct_ExtraRefrigerator["EF 17.6"] = {"extra_refrigerator_present": True, "extra_refrigerator_location": "auto", "extra_refrigerator_rated_annual_kwh": 433, "extra_refrigerator_usage_multiplier": 1.0}
        dct_ExtraRefrigerator["EF 19.9"] = {"extra_refrigerator_present": True, "extra_refrigerator_location": "auto", "extra_refrigerator_rated_annual_kwh": 383, "extra_refrigerator_usage_multiplier": 1.0}
        dct_ExtraRefrigerator["EF 21.9"] = {"extra_refrigerator_present": True, "extra_refrigerator_location": "auto", "extra_refrigerator_rated_annual_kwh": 348, "extra_refrigerator_usage_multiplier": 1.0}
        dct_ExtraRefrigerator["EF 6.7"] = {"extra_refrigerator_present": True, "extra_refrigerator_location": "auto", "extra_refrigerator_rated_annual_kwh": 1139, "extra_refrigerator_usage_multiplier": 1.0}
        dct_ExtraRefrigerator["None"] = {"extra_refrigerator_present": False, "extra_refrigerator_location": "auto", "extra_refrigerator_rated_annual_kwh": 0, "extra_refrigerator_usage_multiplier": 0}
        #dct_ExtraRefrigerator["Void"] = {}

        dict_Refrigerator = {}
        dict_Refrigerator["EF 10.2"] = {"refrigerator_present": True, "refrigerator_location": "auto", "refrigerator_rated_annual_kwh": 748}
        dict_Refrigerator["EF 10.5"] = {"refrigerator_present": True, "refrigerator_location": "auto", "refrigerator_rated_annual_kwh": 727}
        dict_Refrigerator["EF 15.9"] = {"refrigerator_present": True, "refrigerator_location": "auto", "refrigerator_rated_annual_kwh": 480}
        dict_Refrigerator["EF 17.6"] = {"refrigerator_present": True, "refrigerator_location": "auto", "refrigerator_rated_annual_kwh": 433}
        dict_Refrigerator["EF 19.9"] = {"refrigerator_present": True, "refrigerator_location": "auto", "refrigerator_rated_annual_kwh": 383}
        dict_Refrigerator["EF 21.9"] = {"refrigerator_present": True, "refrigerator_location": "auto", "refrigerator_rated_annual_kwh": 348}
        dict_Refrigerator["EF 6.7"] = {"refrigerator_present": True, "refrigerator_location": "auto", "refrigerator_rated_annual_kwh": 1139}
        dict_Refrigerator["None"] = {"refrigerator_present": False, "refrigerator_location": "auto", "refrigerator_rated_annual_kwh": 0}
        #dict_Refrigerator["Void"] = {}

        dict_Refrigerator_Usage = {}
        dict_Refrigerator_Usage["100% Usage"] = {"refrigerator_usage_multiplier": 1.0}
        dict_Refrigerator_Usage["105% Usage"] = {"refrigerator_usage_multiplier": 1.05}
        dict_Refrigerator_Usage["95% Usage"] = {"refrigerator_usage_multiplier": 0.95}
			
        #Refrigerateur Principal
        arg = "Refrigerateur_Nombre"
        if (arg in dct_args.keys()):
            if dct_args[arg] in ['1', '2', '3', '4 et plus']:
                args_value = dct_args["Refrigerator Efficiency"]
                for args in dict_Refrigerator[args_value]:
                    if ((args not in dct_HPXML.keys()) & (dict_Refrigerator[args_value][args]!="auto")):
                        dct_HPXML[args] = dict_Refrigerator[args_value][args]
            else: #'Aucun', 
                args_value = "None"
                for args in dict_Refrigerator[args_value]:
                    if ((args not in dct_HPXML.keys()) & (dict_Refrigerator[args_value][args]!="auto")):
                        dct_HPXML[args] = dict_Refrigerator[args_value][args]
        
        #Extra refrigerateur
        arg = "Refrigerateur_Nombre"
        if (arg in dct_args.keys()):
            if dct_args[arg] in ['2', '3', '4 et plus']:
                args_value = dct_args["Refrigerator Extra Efficiency"]
                for args in dct_ExtraRefrigerator[args_value]:
                    if ((args not in dct_HPXML.keys()) & (dct_ExtraRefrigerator[args_value][args]!="auto")):
                        dct_HPXML[args] = dct_ExtraRefrigerator[args_value][args]
            else: #'Aucun', 
                args_value = "None"#, '1'
                for args in dct_ExtraRefrigerator[args_value]:
                    if ((args not in dct_HPXML.keys()) & (dct_ExtraRefrigerator[args_value][args]!="auto")):
                        dct_HPXML[args] = dct_ExtraRefrigerator[args_value][args]

        dct_Congelateur = {}
        dct_Congelateur["EF 12, Average Installed"] = {"freezer_present": True, "freezer_location": "auto", "freezer_rated_annual_kwh": 935, "freezer_usage_multiplier": 1.0}
        dct_Congelateur["EF 12, National Average"] = {"freezer_present": True, "freezer_location": "auto", "freezer_rated_annual_kwh": 935, "freezer_usage_multiplier": 0.342}
        dct_Congelateur["EF 16, 2001 Fed Standard-reference freezer"] = {"freezer_present": True, "freezer_location": "auto", "freezer_rated_annual_kwh": 712, "freezer_usage_multiplier": 1.0}
        dct_Congelateur["EF 18, 2008 Energy Star"] = {"freezer_present": True, "freezer_location": "auto", "freezer_rated_annual_kwh": 641, "freezer_usage_multiplier": 1.0}
        dct_Congelateur["EF 20, 2008 Energy Star Most Efficient"] = {"freezer_present": True, "freezer_location": "auto", "freezer_rated_annual_kwh": 568, "freezer_usage_multiplier": 1.0}
        dct_Congelateur["None"] = {"freezer_present": False, "freezer_location": "auto", "freezer_rated_annual_kwh": 0, "freezer_usage_multiplier": 0}
        #dct_Congelateur["Void"] = {}
        
        #Congelateur
        arg = "Congelateur_Nombre"
        if (arg in dct_args.keys()):
            if dct_args[arg] in ['1', '2', '3', '4', '5', '6']:
                args_value = dct_args["Freezer Efficiency"]
                for args in dct_Congelateur[args_value]:
                    if ((args not in dct_HPXML.keys()) & (dct_Congelateur[args_value][args]!="auto")):
                        dct_HPXML[args] = dct_Congelateur[args_value][args]
            else: #'Aucun', 
                args_value = "None"
                for args in dct_Congelateur[args_value]:
                    if ((args not in dct_HPXML.keys()) & (dct_Congelateur[args_value][args]!="auto")):
                        dct_HPXML[args] = dct_Congelateur[args_value][args]

        #_____________________________________________________________
        # Lighting Usage Level
        # Eclairage_LED
        dct_Eclairage = {}
        dct_Eclairage["0%"] = {"lighting_present":True, "lighting_interior_fraction_cfl":0, "lighting_interior_fraction_lfl":0, "lighting_interior_fraction_led":0, "lighting_exterior_fraction_cfl": 0, "lighting_exterior_fraction_lfl":0, "lighting_exterior_fraction_led":0, "lighting_garage_fraction_cfl":0, "lighting_garage_fraction_lfl":0, "lighting_garage_fraction_led":0}
        dct_Eclairage["1 à 24 %"] = {"lighting_present":True, "lighting_interior_fraction_cfl":0, "lighting_interior_fraction_lfl":0.0, "lighting_interior_fraction_led":0.12, "lighting_exterior_fraction_cfl": 0, "lighting_exterior_fraction_lfl":0, "lighting_exterior_fraction_led":0.12, "lighting_garage_fraction_cfl":0, "lighting_garage_fraction_lfl":0, "lighting_garage_fraction_led":0.12}
        dct_Eclairage["25 à 50 %"] = {"lighting_present":True, "lighting_interior_fraction_cfl":0, "lighting_interior_fraction_lfl":0.0, "lighting_interior_fraction_led":0.37, "lighting_exterior_fraction_cfl": 0, "lighting_exterior_fraction_lfl":0, "lighting_exterior_fraction_led":0.37, "lighting_garage_fraction_cfl":0, "lighting_garage_fraction_lfl":0, "lighting_garage_fraction_led":0.37}
        dct_Eclairage["Plus de 50 %"] = {"lighting_present":True, "lighting_interior_fraction_cfl":0, "lighting_interior_fraction_lfl":0.0, "lighting_interior_fraction_led":0.75, "lighting_exterior_fraction_cfl": 0, "lighting_exterior_fraction_lfl":0, "lighting_exterior_fraction_led":0.75, "lighting_garage_fraction_cfl":0, "lighting_garage_fraction_lfl":0, "lighting_garage_fraction_led":0.75}                 
        dct_Eclairage["Ne sait pas"] = dct_Eclairage["1 à 24 %"]

        dct_EclairageUsage = {}
        dct_EclairageUsage["105% Usage"] = {"lighting_interior_usage_multiplier": 1.05}
        dct_EclairageUsage["100% Usage"] = {"lighting_interior_usage_multiplier": 1.0}
        dct_EclairageUsage["95% Usage"] = {"lighting_interior_usage_multiplier": 0.95}
        
        arg = "Eclairage_LED"
        if (arg in dct_args.keys()):
            for args in dct_Eclairage[dct_args[arg]]:
                if ((args not in dct_HPXML.keys()) & (dct_Eclairage[dct_args[arg]][args]!="auto")):
                    dct_HPXML[args] = dct_Eclairage[dct_args[arg]][args]
        
        arg = "Lighting Usage Level"
        for args in dct_EclairageUsage[dct_args[arg]]:
            if ((args not in dct_HPXML.keys()) & (dct_EclairageUsage[dct_args[arg]][args]!="auto")):
                dct_HPXML[args] = dct_EclairageUsage[dct_args[arg]][args]

        #_____________________________________________________________
        # Doors
        dct_Doors = {}
        dct_Doors["Fiberglass"] = {"door_rvalue": 5}
        dct_Doors["Steel"] = {"door_rvalue": 5}
        dct_Doors["Wood"] = {"door_rvalue": 2.1}

        dct_DoorsArea = {}
        dct_DoorsArea["20 ft^2"] = {"door_area": 20}
        dct_DoorsArea["30 ft^2"] = {"door_area": 30}
        dct_DoorsArea["40 ft^2"] = {"door_area": 40}

        arg = "Door Rvalue"
        if (arg in dct_args.keys()):
            for args in dct_Doors[dct_args[arg]]:
                if ((args not in dct_HPXML.keys()) & (dct_Doors[dct_args[arg]][args]!="auto")):
                    dct_HPXML[args] = dct_Doors[dct_args[arg]][args]

        arg = "Door Area"
        if (arg in dct_args.keys()):
            for args in dct_DoorsArea[dct_args[arg]]:
                if ((args not in dct_HPXML.keys()) & (dct_DoorsArea[dct_args[arg]][args]!="auto")):
                    dct_HPXML[args] = dct_DoorsArea[dct_args[arg]][args]


        #if args[:misc_plug_loads_other_annual_kwh].to_s == Constants.Auto
        #    if [HPXML::ResidentialTypeSFD].include?(args[:geometry_unit_type])
        #        args[:misc_plug_loads_other_annual_kwh] = 1146.95 + 296.94 * args[:geometry_unit_num_occupants] + 0.3 * args[:geometry_unit_cfa] # RECS 2015
        #    elsif [HPXML::ResidentialTypeSFA].include?(args[:geometry_unit_type])
        #        args[:misc_plug_loads_other_annual_kwh] = 1395.84 + 136.53 * args[:geometry_unit_num_occupants] + 0.16 * args[:geometry_unit_cfa] # RECS 2015
        #    elsif [HPXML::ResidentialTypeApartment].include?(args[:geometry_unit_type])
        #        args[:misc_plug_loads_other_annual_kwh] = 875.22 + 184.11 * args[:geometry_unit_num_occupants] + 0.38 * args[:geometry_unit_cfa] # RECS 2015
        #    end
        #    end
        #traduction du code
        # Plug Load
        
        dict_PlugLoadsUsage = {}
        dict_PlugLoadsUsage["78%"] = {"misc_plug_loads_other_annual_kwh": "auto", "misc_plug_loads_other_frac_sensible": 0.93, "misc_plug_loads_other_frac_latent": 0.021, "misc_plug_loads_other_usage_multiplier": 0.78, "misc_plug_loads_television_present": False}
        dict_PlugLoadsUsage["79%"] = {"misc_plug_loads_other_annual_kwh": "auto", "misc_plug_loads_other_frac_sensible": 0.93, "misc_plug_loads_other_frac_latent": 0.021, "misc_plug_loads_other_usage_multiplier": 0.79, "misc_plug_loads_television_present": False}
        dict_PlugLoadsUsage["82%"] = {"misc_plug_loads_other_annual_kwh": "auto", "misc_plug_loads_other_frac_sensible": 0.93, "misc_plug_loads_other_frac_latent": 0.021, "misc_plug_loads_other_usage_multiplier": 0.82, "misc_plug_loads_television_present": False}
        dict_PlugLoadsUsage["84%"] = {"misc_plug_loads_other_annual_kwh": "auto", "misc_plug_loads_other_frac_sensible": 0.93, "misc_plug_loads_other_frac_latent": 0.021, "misc_plug_loads_other_usage_multiplier": 0.84, "misc_plug_loads_television_present": False}
        dict_PlugLoadsUsage["85%"] = {"misc_plug_loads_other_annual_kwh": "auto", "misc_plug_loads_other_frac_sensible": 0.93, "misc_plug_loads_other_frac_latent": 0.021, "misc_plug_loads_other_usage_multiplier": 0.85, "misc_plug_loads_television_present": False}
        dict_PlugLoadsUsage["86%"] = {"misc_plug_loads_other_annual_kwh": "auto", "misc_plug_loads_other_frac_sensible": 0.93, "misc_plug_loads_other_frac_latent": 0.021, "misc_plug_loads_other_usage_multiplier": 0.86, "misc_plug_loads_television_present": False}
        dict_PlugLoadsUsage["89%"] = {"misc_plug_loads_other_annual_kwh": "auto", "misc_plug_loads_other_frac_sensible": 0.93, "misc_plug_loads_other_frac_latent": 0.021, "misc_plug_loads_other_usage_multiplier": 0.89, "misc_plug_loads_television_present": False}
        dict_PlugLoadsUsage["91%"] = {"misc_plug_loads_other_annual_kwh": "auto", "misc_plug_loads_other_frac_sensible": 0.93, "misc_plug_loads_other_frac_latent": 0.021, "misc_plug_loads_other_usage_multiplier": 0.91, "misc_plug_loads_television_present": False}
        dict_PlugLoadsUsage["93%"] = {"misc_plug_loads_other_annual_kwh": "auto", "misc_plug_loads_other_frac_sensible": 0.93, "misc_plug_loads_other_frac_latent": 0.021, "misc_plug_loads_other_usage_multiplier": 0.93, "misc_plug_loads_television_present": False}
        dict_PlugLoadsUsage["94%"] = {"misc_plug_loads_other_annual_kwh": "auto", "misc_plug_loads_other_frac_sensible": 0.93, "misc_plug_loads_other_frac_latent": 0.021, "misc_plug_loads_other_usage_multiplier": 0.94, "misc_plug_loads_television_present": False}
        dict_PlugLoadsUsage["95%"] = {"misc_plug_loads_other_annual_kwh": "auto", "misc_plug_loads_other_frac_sensible": 0.93, "misc_plug_loads_other_frac_latent": 0.021, "misc_plug_loads_other_usage_multiplier": 0.95, "misc_plug_loads_television_present": False}
        dict_PlugLoadsUsage["96%"] = {"misc_plug_loads_other_annual_kwh": "auto", "misc_plug_loads_other_frac_sensible": 0.93, "misc_plug_loads_other_frac_latent": 0.021, "misc_plug_loads_other_usage_multiplier": 0.96, "misc_plug_loads_television_present": False}
        dict_PlugLoadsUsage["97%"] = {"misc_plug_loads_other_annual_kwh": "auto", "misc_plug_loads_other_frac_sensible": 0.93, "misc_plug_loads_other_frac_latent": 0.021, "misc_plug_loads_other_usage_multiplier": 0.97, "misc_plug_loads_television_present": False}
        dict_PlugLoadsUsage["99%"] = {"misc_plug_loads_other_annual_kwh": "auto", "misc_plug_loads_other_frac_sensible": 0.93, "misc_plug_loads_other_frac_latent": 0.021, "misc_plug_loads_other_usage_multiplier": 0.99, "misc_plug_loads_television_present": False}
        dict_PlugLoadsUsage["100%"] = {"misc_plug_loads_other_annual_kwh": "auto", "misc_plug_loads_other_frac_sensible": 0.93, "misc_plug_loads_other_frac_latent": 0.021, "misc_plug_loads_other_usage_multiplier": 1.0, "misc_plug_loads_television_present": False}
        dict_PlugLoadsUsage["101%"] = {"misc_plug_loads_other_annual_kwh": "auto", "misc_plug_loads_other_frac_sensible": 0.93, "misc_plug_loads_other_frac_latent": 0.021, "misc_plug_loads_other_usage_multiplier": 1.01, "misc_plug_loads_television_present": False}
        dict_PlugLoadsUsage["102%"] = {"misc_plug_loads_other_annual_kwh": "auto", "misc_plug_loads_other_frac_sensible": 0.93, "misc_plug_loads_other_frac_latent": 0.021, "misc_plug_loads_other_usage_multiplier": 1.02, "misc_plug_loads_television_present": False}
        dict_PlugLoadsUsage["103%"] = {"misc_plug_loads_other_annual_kwh": "auto", "misc_plug_loads_other_frac_sensible": 0.93, "misc_plug_loads_other_frac_latent": 0.021, "misc_plug_loads_other_usage_multiplier": 1.03, "misc_plug_loads_television_present": False}
        dict_PlugLoadsUsage["104%"] = {"misc_plug_loads_other_annual_kwh": "auto", "misc_plug_loads_other_frac_sensible": 0.93, "misc_plug_loads_other_frac_latent": 0.021, "misc_plug_loads_other_usage_multiplier": 1.04, "misc_plug_loads_television_present": False}
        dict_PlugLoadsUsage["105%"] = {"misc_plug_loads_other_annual_kwh": "auto", "misc_plug_loads_other_frac_sensible": 0.93, "misc_plug_loads_other_frac_latent": 0.021, "misc_plug_loads_other_usage_multiplier": 1.05, "misc_plug_loads_television_present": False}
        dict_PlugLoadsUsage["106%"] = {"misc_plug_loads_other_annual_kwh": "auto", "misc_plug_loads_other_frac_sensible": 0.93, "misc_plug_loads_other_frac_latent": 0.021, "misc_plug_loads_other_usage_multiplier": 1.06, "misc_plug_loads_television_present": False}
        dict_PlugLoadsUsage["108%"] = {"misc_plug_loads_other_annual_kwh": "auto", "misc_plug_loads_other_frac_sensible": 0.93, "misc_plug_loads_other_frac_latent": 0.021, "misc_plug_loads_other_usage_multiplier": 1.08, "misc_plug_loads_television_present": False}
        dict_PlugLoadsUsage["110%"] = {"misc_plug_loads_other_annual_kwh": "auto", "misc_plug_loads_other_frac_sensible": 0.93, "misc_plug_loads_other_frac_latent": 0.021, "misc_plug_loads_other_usage_multiplier": 1.1, "misc_plug_loads_television_present": False}
        dict_PlugLoadsUsage["113%"] = {"misc_plug_loads_other_annual_kwh": "auto", "misc_plug_loads_other_frac_sensible": 0.93, "misc_plug_loads_other_frac_latent": 0.021, "misc_plug_loads_other_usage_multiplier": 1.13, "misc_plug_loads_television_present": False}
        dict_PlugLoadsUsage["119%"] = {"misc_plug_loads_other_annual_kwh": "auto", "misc_plug_loads_other_frac_sensible": 0.93, "misc_plug_loads_other_frac_latent": 0.021, "misc_plug_loads_other_usage_multiplier": 1.19, "misc_plug_loads_television_present": False}
        dict_PlugLoadsUsage["121%"] = {"misc_plug_loads_other_annual_kwh": "auto", "misc_plug_loads_other_frac_sensible": 0.93, "misc_plug_loads_other_frac_latent": 0.021, "misc_plug_loads_other_usage_multiplier": 1.21, "misc_plug_loads_television_present": False}
        dict_PlugLoadsUsage["123%"] = {"misc_plug_loads_other_annual_kwh": "auto", "misc_plug_loads_other_frac_sensible": 0.93, "misc_plug_loads_other_frac_latent": 0.021, "misc_plug_loads_other_usage_multiplier": 1.23, "misc_plug_loads_television_present": False}
        dict_PlugLoadsUsage["134%"] = {"misc_plug_loads_other_annual_kwh": "auto", "misc_plug_loads_other_frac_sensible": 0.93, "misc_plug_loads_other_frac_latent": 0.021, "misc_plug_loads_other_usage_multiplier": 1.34, "misc_plug_loads_television_present": False}
        dict_PlugLoadsUsage["137%"] = {"misc_plug_loads_other_annual_kwh": "auto", "misc_plug_loads_other_frac_sensible": 0.93, "misc_plug_loads_other_frac_latent": 0.021, "misc_plug_loads_other_usage_multiplier": 1.37, "misc_plug_loads_television_present": False}
        dict_PlugLoadsUsage["140%"] = {"misc_plug_loads_other_annual_kwh": "auto", "misc_plug_loads_other_frac_sensible": 0.93, "misc_plug_loads_other_frac_latent": 0.021, "misc_plug_loads_other_usage_multiplier": 1.4, "misc_plug_loads_television_present": False}
        dict_PlugLoadsUsage["144%"] = {"misc_plug_loads_other_annual_kwh": "auto", "misc_plug_loads_other_frac_sensible": 0.93, "misc_plug_loads_other_frac_latent": 0.021, "misc_plug_loads_other_usage_multiplier": 1.44, "misc_plug_loads_television_present": False}
        dict_PlugLoadsUsage["166%"] = {"misc_plug_loads_other_annual_kwh": "auto", "misc_plug_loads_other_frac_sensible": 0.93, "misc_plug_loads_other_frac_latent": 0.021, "misc_plug_loads_other_usage_multiplier": 1.66, "misc_plug_loads_television_present": False}

        arg = "Plug Loads"
        if (arg in dct_args.keys()):
            for args in dict_PlugLoadsUsage[dct_args[arg]]:
                if ((args not in dct_HPXML.keys()) & (dict_PlugLoadsUsage[dct_args[arg]][args]!="auto")):
                    dct_HPXML["misc_plug_loads_television_annual_kwh"] = 0.0 # "other" now accounts for television
                    dct_HPXML["misc_plug_loads_television_usage_multiplier"] = 0.0 # "other" now accounts for television

                    dct_HPXML[args] = dict_PlugLoadsUsage[dct_args[arg]][args]
                    
                    if dct_args["Type_Logement"] in ["Maison individuelle"]:
                        dct_HPXML["misc_plug_loads_other_annual_kwh"] = 1146.95 + 296.94 * dct_args["Nombre_Occupants"] + 0.3 * dct_args["geometry_unit_cfa"] # RECS 2015
                    elif dct_args["Type_Logement"] in ["Maison mitoyenne"]:
                        dct_HPXML["misc_plug_loads_other_annual_kwh"] = 1395.84 + 136.53 * dct_args["Nombre_Occupants"] + 0.16 * dct_args["geometry_unit_cfa"] # RECS 2015
                    elif dct_args["Type_Logement"] in ["Appartement"]:
                        dct_HPXML["misc_plug_loads_other_annual_kwh"] = 875.22 + 184.11 * dct_args["Nombre_Occupants"] + 0.38 * dct_args["geometry_unit_cfa"] # RECS 2015

            # Traitement de misc_plug_loads_other_annual_kwh car auto  
            # Plug Loads
             #dct_HPXML["misc_plug_loads_other_usage_multiplier"] = float(dct_HPXML.get("misc_plug_loads_other_usage_multiplier",1)) * float(dct_HPXML.get("misc_plug_loads_other_2_usage_multiplier", 1.0))
            #dct_HPXML["misc_plug_loads_well_pump_usage_multiplier"] = float(dct_HPXML.get("misc_plug_loads_well_pump_usage_multiplier",1)) * float(dct_HPXML.get("misc_plug_loads_well_pump_2_usage_multiplier", 1.0))
            #dct_HPXML["misc_plug_loads_vehicle_usage_multiplier"] = float(dct_HPXML.get("misc_plug_loads_vehicle_usage_multiplier",1)) * float(dct_HPXML.get("misc_plug_loads_vehicle_2_usage_multiplier", 1.0))

        #Simplify hourly heating setpoint if not using stochastic profiles
        pdtempo_H = pd.Series([0.0,1.0,2.0,3.0,4.0,5.0,6.0,7.0,8.0,9.0,10.0,11.0,12.0,13.0,14.0,15.0,16.0,17.0,18.0,19.0,20.0,21.0,22.0,23.0])
    
        filtre_Tnuit = (pdtempo_H < dct_args["Tconsignes_chauffage_H1"]) | (pdtempo_H >= dct_args["Tconsignes_chauffage_H4"])
        filtre_Tjour = (pdtempo_H >= dct_args["Tconsignes_chauffage_H2"]) & (pdtempo_H < dct_args["Tconsignes_chauffage_H3"])
        filtre_Tmatin = (pdtempo_H >= dct_args["Tconsignes_chauffage_H1"]) & (pdtempo_H < dct_args["Tconsignes_chauffage_H2"])
        filtre_Tsoir = (pdtempo_H >= dct_args["Tconsignes_chauffage_H3"]) & (pdtempo_H < dct_args["Tconsignes_chauffage_H4"])

        Tnuit = float(eval(dct_args['Heating Setpoint'])[2])*9/5+32 #F
        Tmatin = float(eval(dct_args['Heating Setpoint'])[1])*9/5+32 #F
        Tjour = float(eval(dct_args['Heating Setpoint'])[0])*9/5+32 #F
        Tsoir = float(eval(dct_args['Heating Setpoint'])[1])*9/5+32 #F
        
        pdtempo_T= pdtempo_H.copy()
        pdtempo_T.loc[filtre_Tnuit] = Tnuit
        pdtempo_T.loc[filtre_Tjour] = Tjour
        pdtempo_T.loc[filtre_Tmatin] = Tmatin
        pdtempo_T.loc[filtre_Tsoir] = Tsoir
        pdtempo_T.tolist()
        separator = ","
        [str(element) for element in pdtempo_T.tolist()]
        hvac_control_heating_setpoint = separator.join([str(element) for element in pdtempo_T.tolist()])
        
        arg = "Heating Setpoint"
        args = "hvac_control_heating_weekday_setpoint"
        
        if (args not in dct_HPXML.keys()):
            if (arg in dct_args.keys()):
                dct_HPXML[args] = hvac_control_heating_setpoint

        arg = "Heating Setpoint"
        args = "hvac_control_heating_weekend_setpoint"
        if (args not in dct_HPXML.keys()):
            if (arg in dct_args.keys()):
                #convert list to str
                dct_HPXML[args] = hvac_control_heating_setpoint

        arg = "Cooling Setpoint"
        args = "hvac_control_cooling_weekday_setpoint"
        if (args not in dct_HPXML.keys()):
            if (arg in dct_args.keys()):
                dct_HPXML[args] = separator.join([str(float(dct_args[arg]) *9/5+32)]*24) # conversion C to F , Tjour

        arg = "Cooling Setpoint"
        args = "hvac_control_cooling_weekend_setpoint"
        if (args not in dct_HPXML.keys()):
            if (arg in dct_args.keys()):
                dct_HPXML[args] = separator.join([str(float(dct_args[arg]) *9/5+32)]*24) # conversion C to F , Tjour

        # ajout des Valeurs par défaut du HPXML si cle n'existe pas
        k_missing = list(set(self.HPXMLArg.arguments.keys()) - set(dct_HPXML.keys()))
        dct_HPXML_missing ={}# {k: self.HPXMLArg.arguments[k].get("Default Value", None) for k in k_missing if self.HPXMLArg.arguments[k].get("Default Value", "Defaut_Not_Existing")!="Defaut_Not_Existing"} 

        dct_HPXML = {**dct_HPXML, **dct_HPXML_missing}
        # ne pas traiter les variables exclues (cf. MapHPXML.py)  
        Exclude = ["air_leakage_leakiness_description",
                   "ceiling_insulation_r",
                   "rim_joist_continuous_exterior_r",
                   "rim_joist_continuous_interior_r",
                   "rim_joist_assembly_interior_r",
                   "exterior_finish_r"]
        dct_HPXML = {k: v for k, v in dct_HPXML.items() if k not in Exclude}
        return dct_HPXML
    def run(self, lst_dct_args):
        lst_dct_HPXML = []
        for dct_args in lst_dct_args: # pour chaque logements
            lst_dct_HPXML.append(self.doMapping(dct_args))
        return lst_dct_HPXML



if __name__ == "__main__":
    import pandas as pd

    # Load the Bayesian Network from the saved file
    InsClsSampler = Sampler()
    path = PROJECT_DIR+"/data/processed/bayesian_network/BN_EUEMr.XDSL"
    InsClsSampler.Load_BN(path)

    # Display the Bayesian Network - Avant enregistrement
    #gnb.showInference(InsClsSampler.bn,evs={},size = '30')

    Nombre_de_Samples = 100
    Evidence = {}#"Type_Logement": "Collective",
                #"Nombre_Pieces": "1"}#{"Mode_Occupation": "Proprietaire"}

    # Fait un échantillonage - Avant enregistrement
    df1 = InsClsSampler.do_Sampling(Nombre_de_Samples, evs = Evidence)
    lst_dct_args = df1.to_dict(orient='records')
    # Affiche les échantillons - Avant enregistrement
    
    #s.getBNStructure()
    #print(s.lst_NOEUD, s.LIST_Dict)

    #Ajout de varaible hors BN
    Bba = BuildstockBatchArguments()
    lst_dct_args2 = Bba.sampling( lst_dct_args)

    lst_dct_args = [ d2 | d1 for d1, d2 in zip(lst_dct_args, lst_dct_args2)]#lst_dct_args prioritaire

    MapSample = MapHPXML()
    lst_dct_HPXML = MapSample.run(lst_dct_args)
    
    print("Nombre d'attributs HPXML: ", len(lst_dct_HPXML[0].keys()))
    pd.DataFrame(lst_dct_HPXML)