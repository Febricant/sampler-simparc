# -*- coding: utf-8 -*-
"""
Created on 26-06-2025

@author: cv1751 - Brice Le Lostec
@description: Class for generating Bayesian Networks (BN) using pyAgrum.
@note: This class provides methods to save, load, plot Bayesian Networks and load CSV files.
@version: 1.0
python 3.11

"""
import os
import sys
import yaml
import numpy as np
import pandas as pd

FILE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(FILE_DIR+ "/../")  # répertoire supérieur
#PACKAGE_DIR = os.path.abspath(PROJECT_DIR+ "/../")
sys.path.append(os.path.join(PROJECT_DIR))

from utils.Master_genereBN import Master_genereBN
from dataStructure.HPXMLArg import HPXMLArguments


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

    def getBNStructure(self, path=PROJECT_DIR+"/dataStructure/Bn.yml",):
        with open(path, 'r') as file:
            lst_NOEUD, LIST_Dict = yaml.safe_load(file)
        return lst_NOEUD, LIST_Dict

class BuildstockBatchArguments():
    def __init__(self):
        self.randGenerator = np.random.default_rng(seed=0)
        self.dct_housing_characteristics = self.csv_to_dict()

    def csv_to_dict(self, path = PROJECT_DIR+"/data/housing_characteristics/"):
        """
        Convert a CSV file to a dictionary.
        
        :param path: Path to the CSV file.
        :return: Dictionary with column names as keys and lists of column values as values.
        """
        dct_name = {"Geometry Stories.csv": "Geometry Stories",
                    "Geometry Building Number Units.csv": "Geometry Building Number Units",
                    "Geometry Building Horizontal Location.csv": "Geometry Building Horizontal Location",
                    "Infiltration.csv" : "Infiltration",
                    "Windows.csv" : "Windows",
                    "Insulation Wall.csv" : "Insulation Wall",
                    "Insulation Ceiling.csv" : "Insulation Ceiling",
                    "Insulation Foundation Wall.csv": "Insulation Foundation Wall",
                    "Geometry Wall Exterior Finish.csv" : "Geometry Wall Exterior Finish",
                    "Geometry Attic Type.csv": "geometry attic type",
                    "HVAC Has Shared System.csv": "HVAC Has Shared System",
                    "HVAC Heating Efficiency.csv": "HVAC Heating Efficiency"}

        dct_housing_characteristics = {}
        for file in dct_name.keys():
            if (file in os.listdir(path)):
                pathcsv = os.path.join(path, file)
                name = dct_name[file]#file.split(".")[0]
                dct_housing_characteristics[name] = {}
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
                         "Infiltration",
                        "Windows",
                        "Insulation Wall",
                        "Insulation Ceiling",
                        "Insulation Foundation Wall",
                        "Geometry Wall Exterior Finish",
                        "geometry attic type",
                        "HVAC Has Shared System",
                        "HVAC Heating Efficiency"]
                        
                        
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

                sumlst = sum(filtered_df[dct_option.keys()].values.tolist()[0])
                listProb = [k/sumlst for k in filtered_df[dct_option.keys()].values.tolist()[0]]

                choiceStr = self.randGenerator.choice(list(dct_option.keys()),p=listProb)
                if "Option=" in str(choiceStr):
                    dct_args2[Attributs] = choiceStr.split("Option=")[-1]
                    if Attributs in ["Geometry Stories",
                                     "Geometry Building Number Units"]:
                        dct_args2[Attributs] = int(dct_args2[Attributs])
            
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

        #geometry_garage_protrusion
        argHPXML = "geometry_garage_protrusion"
        if (argHPXML not in dct_HPXML.keys()):
            if dct_HPXML.get("geometry_unit_cfa") < 750:
                dct_HPXML[argHPXML]=0.75
            else:
                dct_HPXML[argHPXML]=0.5      
            
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


        #________________________________________________________________
        #geometry_garage_width
        #The width of the garage. Enter zero for no garage. Only applies to single-family detached units.	
        #Plex : Ne pas ajouter de de garage
        #geometry_garage_depth

        #building size (based on buildresidentialhpxml - geometry.rb)
        # calculate the dimensions of the building
        # we have: (1) aspect_ratio = fb / lr, and (2) footprint = fb * lr
        
        fb = (dct_HPXML["geometry_unit_cfa"] *dct_HPXML["geometry_unit_aspect_ratio"])**0.5
        lr = dct_HPXML["geometry_unit_cfa"] / fb
        length = fb
        width = lr

        max_garage_depth = length -1
        max_garage_width =  width / (1.0 - dct_HPXML["geometry_garage_protrusion"]) -1
        if max_garage_depth>24:
            garage_depth = 24 #12 / 24 / 36 taille du garage
        else:
            garage_depth = max_garage_depth

        #if max_garage_width>36:
        #    garage_width = 36 #12 / 24 / 36 taille du garage
        if max_garage_width>24:
            garage_width = 24
        elif max_garage_width>12:
            garage_width = 12
        else:
            garage_width = max_garage_width

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
                        dct_HPXML[argHPXML] = 0 #Pas de garage pour les plex/appartemnt
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



        #_____________________________________________________________
        #geometry_unit_num_floors_above_grade
        
        #The number of floors above grade in the unit. 
        # Attic type ConditionedAttic is included. 
        # Assumed to be 1 for apartment units.
        arg = "Nombre_Etages"
        argHPXML = "geometry_unit_num_floors_above_grade"# du logement et non de l'immeuble
        if (argHPXML not in dct_HPXML.keys()):
            if (arg in dct_args.keys()):
                if (dct_HPXML.get("geometry_unit_type") in ["single-family detached", "single-family attached"]):
                    if dct_args[arg] == "Un étage":
                        dct_HPXML[argHPXML] = 1
                    elif dct_args[arg] == "Deux étages":
                        dct_HPXML[argHPXML] = 2
                    elif dct_args[arg] == "Trois étages et plus":
                        dct_HPXML[argHPXML] = 3
                else:#pour les plex et les appart pas d'étage dans le hpxml
                    dct_HPXML[argHPXML] = 1
            else:
                if self.HPXMLArg.arguments[argHPXML].get("Default Value", "Defaut_Not_Existing")!="Defaut_Not_Existing":
                    dct_HPXML[argHPXML] = self.HPXMLArg.arguments[argHPXML].get("Default Value")
                else:
                    dct_HPXML[argHPXML] = 1

        #________________________________________________________________
        #Geometry Foundation Type
        arg = "Presence_SousSol"
        args = "geometry_foundation_type"
        if (args not in dct_HPXML.keys()):
            if (arg in dct_args.keys()):
                if (dct_HPXML.get("geometry_unit_type") in ["apartment unit"]):
                    if dct_args[arg] == "Sous sol 6 pied":
                        dct_HPXML[args] = "UnconditionedBasement"
                    elif dct_args[arg] == "Vide sanitaire moins 6 pieds":
                        dct_HPXML[args] = "UnventedCrawlspace" #
                    elif dct_args[arg] == "Aucun Sous-sol ou vide sanitaire":
                        dct_HPXML[args] = "SlabOnGrade"
                    elif dct_args[arg] == "Sous-sol et vide sanitaire":
                        dct_HPXML[args] = "UnventedCrawlspace"
                else:
                    if dct_args[arg] == "Sous sol 6 pied":
                        dct_HPXML[args] = "ConditionedBasement"
                    elif dct_args[arg] == "Vide sanitaire moins 6 pieds":
                        dct_HPXML[args] = "UnventedCrawlspace" #"ConditionedCrawlspace"
                    elif dct_args[arg] == "Aucun Sous-sol ou vide sanitaire":
                        dct_HPXML[args] = "SlabOnGrade"
                    elif dct_args[arg] == "Sous-sol et vide sanitaire":
                        dct_HPXML[args] = "UnventedCrawlspace"
            else:
                if self.HPXMLArg.arguments[args].get("Default Value", "Defaut_Not_Existing")!="Defaut_Not_Existing":
                    dct_HPXML[args] = self.HPXMLArg.arguments[args].get("Default Value")
                else:
                    if (dct_HPXML.get("geometry_unit_type") in ["apartment unit"]):
                        dct_HPXML[args] = "UnconditionedBasement"
                    else:
                        dct_HPXML[args] = "ConditionedBasement"

        #geometry_foundation_height
        arg = "Presence_SousSol"
        args = "geometry_foundation_height"
        if (args not in dct_HPXML.keys()):
            if (arg in dct_args.keys()):
                if (dct_HPXML.get("geometry_unit_type") in ["apartment unit"]):
                    if dct_args[arg] == "Sous sol 6 pied":
                        dct_HPXML[args] = 8
                    elif dct_args[arg] == "Vide sanitaire moins 6 pieds":
                        dct_HPXML[args] = 4
                    elif dct_args[arg] == "Aucun Sous-sol ou vide sanitaire":
                        dct_HPXML[args] = 0
                    elif dct_args[arg] == "Sous-sol et vide sanitaire":
                        dct_HPXML[args] = 4
                else:
                    if dct_args[arg] == "Sous sol 6 pied":
                        dct_HPXML[args] = 8
                    elif dct_args[arg] == "Vide sanitaire moins 6 pieds":
                        dct_HPXML[args] = 4
                    elif dct_args[arg] == "Aucun Sous-sol ou vide sanitaire":
                        dct_HPXML[args] = 0
                    elif dct_args[arg] == "Sous-sol et vide sanitaire":
                        dct_HPXML[args] = 4
            else:
                if self.HPXMLArg.arguments[args].get("Default Value", "Defaut_Not_Existing")!="Defaut_Not_Existing":
                    dct_HPXML[args] = self.HPXMLArg.arguments[args].get("Default Value")
                else:
                    if (dct_HPXML.get("geometry_unit_type") in ["apartment unit"]):
                        dct_HPXML[args] = 8
                    else:
                        dct_HPXML[args] = 8

        #geometry_foundation_height_above_grade
        arg = "Presence_SousSol"
        args = "geometry_foundation_height_above_grade"
        if (args not in dct_HPXML.keys()):
            if (arg in dct_args.keys()):
                if (dct_HPXML.get("geometry_unit_type") in ["apartment unit"]):
                    if dct_args[arg] == "Sous sol 6 pied":
                        dct_HPXML[args] = 1
                    elif dct_args[arg] == "Vide sanitaire moins 6 pieds":
                        dct_HPXML[args] = 1
                    elif dct_args[arg] == "Aucun Sous-sol ou vide sanitaire":
                        dct_HPXML[args] = 0
                    elif dct_args[arg] == "Sous-sol et vide sanitaire":
                        dct_HPXML[args] = 1
                else:
                    if dct_args[arg] == "Sous sol 6 pied":
                        dct_HPXML[args] = 1
                    elif dct_args[arg] == "Vide sanitaire moins 6 pieds":
                        dct_HPXML[args] = 1
                    elif dct_args[arg] == "Aucun Sous-sol ou vide sanitaire":
                        dct_HPXML[args] = 0
                    elif dct_args[arg] == "Sous-sol et vide sanitaire":
                        dct_HPXML[args] = 1
            else:
                if self.HPXMLArg.arguments[args].get("Default Value", "Defaut_Not_Existing")!="Defaut_Not_Existing":
                    dct_HPXML[args] = self.HPXMLArg.arguments[args].get("Default Value")
                else:
                    if (dct_HPXML.get("geometry_unit_type") in ["apartment unit"]):
                        dct_HPXML[args] = 1
                    else:
                        dct_HPXML[args] = 1

        #geometry_rim_joist_height
        args = "geometry_rim_joist_height"
        if (args not in dct_HPXML.keys()):
            if (arg in dct_args.keys()):
                if (dct_HPXML.get("geometry_unit_type") in ["apartment unit"]):
                    if dct_args[arg] == "Sous sol 6 pied":
                        dct_HPXML[args] = 9.25
                    elif dct_args[arg] == "Vide sanitaire moins 6 pieds":
                        dct_HPXML[args] = 9.25
                    elif dct_args[arg] == "Aucun Sous-sol ou vide sanitaire":
                        dct_HPXML[args] = 0
                    elif dct_args[arg] == "Sous-sol et vide sanitaire":
                        dct_HPXML[args] = 9.25
                else:
                    if dct_args[arg] == "Sous sol 6 pied":
                        dct_HPXML[args] = 9.25
                    elif dct_args[arg] == "Vide sanitaire moins 6 pieds":
                        dct_HPXML[args] = 9.25
                    elif dct_args[arg] == "Aucun Sous-sol ou vide sanitaire":
                        dct_HPXML[args] = 0
                    elif dct_args[arg] == "Sous-sol et vide sanitaire":
                        dct_HPXML[args] = 9.25
            else:
                if self.HPXMLArg.arguments[args].get("Default Value", "Defaut_Not_Existing")!="Defaut_Not_Existing":
                    dct_HPXML[args] = self.HPXMLArg.arguments[args].get("Default Value")
                else:
                    if (dct_HPXML.get("geometry_unit_type") in ["apartment unit"]):
                        dct_HPXML[args] = 9.25
                    else:
                        dct_HPXML[args] = 9.25

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
        
        dct_Insulation_Wall["QC_WoodStud-R12.2"]={"wall_type":"WoodStud", "wall_assembly_r":10.9}
        dct_Insulation_Wall["QC_WoodStud-R12.6"]={"wall_type":"WoodStud", "wall_assembly_r":11.1}
        dct_Insulation_Wall["QC_WoodStud-R14"]={"wall_type":"WoodStud", "wall_assembly_r":11.7}
        dct_Insulation_Wall["QC_WoodStud-R14.5"]={"wall_type":"WoodStud", "wall_assembly_r":11.9}
        dct_Insulation_Wall["QC_WoodStud-R17.2"]={"wall_type":"WoodStud", "wall_assembly_r":13.915}
        dct_Insulation_Wall["QC_WoodStud-R18.9"]={"wall_type":"WoodStud", "wall_assembly_r":15.32}
        dct_Insulation_Wall["QC_WoodStud-R20.7"]={"wall_type":"WoodStud", "wall_assembly_r":16.09}
        dct_Insulation_Wall["QC_WoodStud-R24.5"]={"wall_type":"WoodStud", "wall_assembly_r":17.63}
        
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
       
        if (arg in dct_args.keys()):
            for args in dct_Insulation_Ceiling["None"]:
                if ((args not in dct_HPXML.keys()) & (dct_Insulation_Ceiling["None"][args]!="auto")):
                    dct_HPXML[args] = dct_Insulation_Ceiling["None"][args]

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
                                                                 "rim_joist_assembly_interior_r":8.32,#LLb a verifier *0.8
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
                                                                 "rim_joist_assembly_interior_r":9.6, #LLb a verifier *0.8
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
                                                                 "rim_joist_assembly_interior_r":11.52, #LLb a verifier *0.8
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
                                                                 "rim_joist_assembly_interior_r":13.68, #LLb a verifier *0.8
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
                                                                 "rim_joist_assembly_interior_r":13.6, #LLb a verifier *0.8
                                                                 "rim_joist_assembly_r":"auto"}
        
        #defaut
        arg = "Insulation Foundation Wall"
        if (arg in dct_args.keys()):
            for args in dct_Insulation_Foundation_Wall["None"]:
                if ((args not in dct_HPXML.keys()) & (dct_Insulation_Foundation_Wall["None"][args]!="auto")):
                    dct_HPXML[args] = dct_Insulation_Foundation_Wall["None"][args]

        arg = "Insulation Foundation Wall"
        if (arg in dct_args.keys()):
            for args in dct_Insulation_Foundation_Wall[dct_args[arg]]:
                if ((args not in dct_HPXML.keys()) & (dct_Insulation_Foundation_Wall[dct_args[arg]][args]!="auto")):
                    dct_HPXML[args] = dct_Insulation_Foundation_Wall[dct_args[arg]][args]


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

        #defaut
        arg = "Geometry Wall Exterior Finish"
        if (arg in dct_args.keys()):
            for args in dct_Geometry_Wall_Exterior_Finish["None"]:
                if ((args not in dct_HPXML.keys()) & (dct_Geometry_Wall_Exterior_Finish["None"][args]!="auto")):
                    dct_HPXML[args] = dct_Geometry_Wall_Exterior_Finish["None"][args]
        arg = "Geometry Wall Exterior Finish"
        if (arg in dct_args.keys()):
            for args in dct_Geometry_Wall_Exterior_Finish[dct_args[arg]]:
                if ((args not in dct_HPXML.keys()) & (dct_Geometry_Wall_Exterior_Finish[dct_args[arg]][args]!="auto")):
                    dct_HPXML[args] = dct_Geometry_Wall_Exterior_Finish[dct_args[arg]][args]
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
        if (arg in dct_args.keys()):
            for args in dct_Geometry_Attic_Type["None"]:
                if ((args not in dct_HPXML.keys()) & (dct_Geometry_Attic_Type["None"][args]!="auto")):
                    dct_HPXML[args] = dct_Geometry_Attic_Type["None"][args]
        arg = "geometry attic type"
        if (arg in dct_args.keys()):
            for args in dct_Geometry_Attic_Type[dct_args[arg]]:
                if ((args not in dct_HPXML.keys()) & (dct_Geometry_Attic_Type[dct_args[arg]][args]!="auto")):
                    dct_HPXML[args] = dct_Geometry_Attic_Type[dct_args[arg]][args]

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
                if dct_args[arg] == ["1 ACH50","2 ACH50","3 ACH50","4 ACH50","5 ACH50","6 ACH50","7 ACH50","8 ACH50","10 ACH50","15 ACH50","20 ACH50","25 ACH50","30 ACH50","40 ACH50","50 ACH50"]:
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
            
            if horiz_location == 'Left':
                dct_HPXML["geometry_unit_right_wall_is_adiabatic"] = True
            elif horiz_location == 'Middle':
                dct_HPXML["geometry_unit_left_wall_is_adiabatic"]  = True
                dct_HPXML["geometry_unit_right_wall_is_adiabatic"] = True
            elif horiz_location == 'Right':
                dct_HPXML["geometry_unit_left_wall_is_adiabatic"]  = True
            
        
        # Infiltration adjustment for SFA/MF units
        # Calculate exposed wall area ratio for the unit (unit exposed wall area
        # divided by average unit exposed wall area)

        ##A FAIRE

 

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
        dct_HVAC_Heating["MSHP, SEER 29.3, 14 HSPF, Ducted"] = {"heating_system_type": "none", "heating_system_heating_efficiency": 0.0, "heating_system_heating_capacity": "auto", "heating_system_heating_autosizing_limit": "auto", "heating_system_fraction_heat_load_served": 1.0, "heating_system_has_flue_or_chimney": "auto", "heat_pump_type": "mini-split", "heat_pump_heating_efficiency_type": "HSPF", "heat_pump_heating_efficiency": 14.0, "heat_pump_cooling_efficiency_type": "SEER", "heat_pump_cooling_efficiency": 29.3, "heat_pump_sizing_methodology": "ACCA", "heat_pump_sizing_is_duct_limited": "false", "heat_pump_backup_sizing_methodology": "auto", "heat_pump_heating_capacity": "auto", "heat_pump_heating_autosizing_limit": "auto", "heat_pump_fraction_heat_load_served": 1.0, "heat_pump_cooling_capacity": "auto", "heat_pump_cooling_autosizing_limit": "auto", "heat_pump_fraction_cool_load_served": 1.0, "heat_pump_backup_use_existing_system": "false", "heat_pump_backup_type": "integrated", "heat_pump_backup_fuel": "electricity", "heat_pump_backup_heating_efficiency": 1.0, "heat_pump_backup_heating_capacity": "auto", "heat_pump_backup_heating_autosizing_limit": "auto", "heat_pump_heating_capacity_retention_fraction": 0.5, "heat_pump_heating_capacity_retention_temp": -15.0, "heat_pump_is_ducted": "true", "heat_pump_backup_heating_lockout_temp": "auto", "heat_pump_compressor_lockout_temp": "auto", "heat_pump_cooling_compressor_type": "variable speed", "heat_pump_cooling_sensible_heat_fraction": "auto", "heat_pump_crankcase_heater_watts": "auto", "geothermal_loop_configuration": "none", "geothermal_loop_borefield_configuration": "auto", "geothermal_loop_loop_flow": "auto", "geothermal_loop_boreholes_count": "auto", "geothermal_loop_boreholes_length": "auto", "geothermal_loop_boreholes_spacing": "auto", "geothermal_loop_boreholes_diameter": "auto", "geothermal_loop_grout_type": "auto", "geothermal_loop_pipe_type": "auto", "geothermal_loop_pipe_diameter": "auto"}
        dct_HVAC_Heating["MSHP, SEER 33, 13.3 HSPF"] = {"heating_system_type": "none", "heating_system_heating_efficiency": 0.0, "heating_system_heating_capacity": "auto", "heating_system_heating_autosizing_limit": "auto", "heating_system_fraction_heat_load_served": 1.0, "heating_system_has_flue_or_chimney": "auto", "heat_pump_type": "mini-split", "heat_pump_heating_efficiency_type": "HSPF", "heat_pump_heating_efficiency": 13.3, "heat_pump_cooling_efficiency_type": "SEER", "heat_pump_cooling_efficiency": 33.0, "heat_pump_sizing_methodology": "ACCA", "heat_pump_sizing_is_duct_limited": "false", "heat_pump_backup_sizing_methodology": "auto", "heat_pump_heating_capacity": "auto", "heat_pump_heating_autosizing_limit": "auto", "heat_pump_fraction_heat_load_served": 1.0, "heat_pump_cooling_capacity": "auto", "heat_pump_cooling_autosizing_limit": "auto", "heat_pump_fraction_cool_load_served": 1.0, "heat_pump_backup_use_existing_system": "false", "heat_pump_backup_type": "integrated", "heat_pump_backup_fuel": "electricity", "heat_pump_backup_heating_efficiency": 1.0, "heat_pump_backup_heating_capacity": "auto", "heat_pump_backup_heating_autosizing_limit": "auto", "heat_pump_heating_capacity_retention_fraction": 0.5, "heat_pump_heating_capacity_retention_temp": -15.0, "heat_pump_is_ducted": "false", "heat_pump_backup_heating_lockout_temp": "auto", "heat_pump_compressor_lockout_temp": "auto", "heat_pump_cooling_compressor_type": "variable speed", "heat_pump_cooling_sensible_heat_fraction": "auto", "heat_pump_crankcase_heater_watts": "auto", "geothermal_loop_configuration": "none", "geothermal_loop_borefield_configuration": "auto", "geothermal_loop_loop_flow": "auto", "geothermal_loop_boreholes_count": "auto", "geothermal_loop_boreholes_length": "auto", "geothermal_loop_boreholes_spacing": "auto", "geothermal_loop_boreholes_diameter": "auto", "geothermal_loop_grout_type": "auto", "geothermal_loop_pipe_type": "auto", "geothermal_loop_pipe_diameter": "auto"}
        dct_HVAC_Heating["MSHP, SEER 33, 13.3 HSPF, Ducted"] = {"heating_system_type": "none", "heating_system_heating_efficiency": 0.0, "heating_system_heating_capacity": "auto", "heating_system_heating_autosizing_limit": "auto", "heating_system_fraction_heat_load_served": 1.0, "heating_system_has_flue_or_chimney": "auto", "heat_pump_type": "mini-split", "heat_pump_heating_efficiency_type": "HSPF", "heat_pump_heating_efficiency": 13.3, "heat_pump_cooling_efficiency_type": "SEER", "heat_pump_cooling_efficiency": 33.0, "heat_pump_sizing_methodology": "ACCA", "heat_pump_sizing_is_duct_limited": "false", "heat_pump_backup_sizing_methodology": "auto", "heat_pump_heating_capacity": "auto", "heat_pump_heating_autosizing_limit": "auto", "heat_pump_fraction_heat_load_served": 1.0, "heat_pump_cooling_capacity": "auto", "heat_pump_cooling_autosizing_limit": "auto", "heat_pump_fraction_cool_load_served": 1.0, "heat_pump_backup_use_existing_system": "false", "heat_pump_backup_type": "integrated", "heat_pump_backup_fuel": "electricity", "heat_pump_backup_heating_efficiency": 1.0, "heat_pump_backup_heating_capacity": "auto", "heat_pump_backup_heating_autosizing_limit": "auto", "heat_pump_heating_capacity_retention_fraction": 0.5, "heat_pump_heating_capacity_retention_temp": -15.0, "heat_pump_is_ducted": "true", "heat_pump_backup_heating_lockout_temp": "auto", "heat_pump_compressor_lockout_temp": "auto", "heat_pump_cooling_compressor_type": "variable speed", "heat_pump_cooling_sensible_heat_fraction": "auto", "heat_pump_crankcase_heater_watts": "auto", "geothermal_loop_configuration": "none", "geothermal_loop_borefield_configuration": "auto", "geothermal_loop_loop_flow": "auto", "geothermal_loop_boreholes_count": "auto", "geothermal_loop_boreholes_length": "auto", "geothermal_loop_boreholes_spacing": "auto", "geothermal_loop_boreholes_diameter": "auto", "geothermal_loop_grout_type": "auto", "geothermal_loop_pipe_type": "auto", "geothermal_loop_pipe_diameter": "auto"}
        dct_HVAC_Heating["MSHP, SEER2 22.7, 10.3 HSPF2, Typical Cold Climate"] = {"heating_system_type": "none", "heating_system_heating_efficiency": 0.0, "heating_system_heating_capacity": "auto", "heating_system_heating_autosizing_limit": "auto", "heating_system_fraction_heat_load_served": 1.0, "heating_system_has_flue_or_chimney": "auto", "heat_pump_type": "mini-split", "heat_pump_heating_efficiency_type": "HSPF2", "heat_pump_heating_efficiency": 10.3, "heat_pump_cooling_efficiency_type": "SEER2", "heat_pump_cooling_efficiency": 22.7, "heat_pump_sizing_methodology": "ACCA", "heat_pump_sizing_is_duct_limited": "false", "heat_pump_backup_sizing_methodology": "auto", "heat_pump_heating_capacity": "auto", "heat_pump_heating_autosizing_limit": "auto", "heat_pump_fraction_heat_load_served": 1.0, "heat_pump_cooling_capacity": "auto", "heat_pump_cooling_autosizing_limit": "auto", "heat_pump_fraction_cool_load_served": 1.0, "heat_pump_backup_use_existing_system": "false", "heat_pump_backup_type": "integrated", "heat_pump_backup_fuel": "electricity", "heat_pump_backup_heating_efficiency": 1.0, "heat_pump_backup_heating_capacity": "auto", "heat_pump_backup_heating_autosizing_limit": "auto", "heat_pump_heating_capacity_retention_fraction": "auto", "heat_pump_heating_capacity_retention_temp": "auto", "heat_pump_is_ducted": "false", "heat_pump_backup_heating_lockout_temp": "auto", "heat_pump_compressor_lockout_temp": -15.0, "heat_pump_cooling_compressor_type": "variable speed", "heat_pump_cooling_sensible_heat_fraction": "auto", "heat_pump_crankcase_heater_watts": "auto", "geothermal_loop_configuration": "none", "geothermal_loop_borefield_configuration": "auto", "geothermal_loop_loop_flow": "auto", "geothermal_loop_boreholes_count": "auto", "geothermal_loop_boreholes_length": "auto", "geothermal_loop_boreholes_spacing": "auto", "geothermal_loop_boreholes_diameter": "auto", "geothermal_loop_grout_type": "auto", "geothermal_loop_pipe_type": "auto", "geothermal_loop_pipe_diameter": "auto"}
        dct_HVAC_Heating["None"] = {"heating_system_type": "none", "heating_system_heating_efficiency": 0.0, "heating_system_heating_capacity": "auto", "heating_system_heating_autosizing_limit": "auto", "heating_system_fraction_heat_load_served": 1.0, "heating_system_has_flue_or_chimney": "auto", "heat_pump_type": "none", "heat_pump_heating_efficiency_type": "HSPF", "heat_pump_heating_efficiency": 6.2, "heat_pump_cooling_efficiency_type": "SEER", "heat_pump_cooling_efficiency": 10.0, "heat_pump_sizing_methodology": "ACCA", "heat_pump_sizing_is_duct_limited": "false", "heat_pump_backup_sizing_methodology": "auto", "heat_pump_heating_capacity": "auto", "heat_pump_heating_autosizing_limit": "auto", "heat_pump_fraction_heat_load_served": 1.0, "heat_pump_cooling_capacity": "auto", "heat_pump_cooling_autosizing_limit": "auto", "heat_pump_fraction_cool_load_served": 1.0, "heat_pump_backup_use_existing_system": "false", "heat_pump_backup_type": "none", "heat_pump_backup_fuel": "electricity", "heat_pump_backup_heating_efficiency": 1.0, "heat_pump_backup_heating_capacity": "auto", "heat_pump_backup_heating_autosizing_limit": "auto", "geothermal_loop_configuration": "none", "geothermal_loop_borefield_configuration": "auto", "geothermal_loop_loop_flow": "auto", "geothermal_loop_boreholes_count": "auto", "geothermal_loop_boreholes_length": "auto", "geothermal_loop_boreholes_spacing": "auto", "geothermal_loop_boreholes_diameter": "auto", "geothermal_loop_grout_type": "auto", "geothermal_loop_pipe_type": "auto", "geothermal_loop_pipe_diameter": "auto"}
        dct_HVAC_Heating["Shared Heating"] = {}
        dct_HVAC_Heating["Void"] = {}
        #bois  #TODO: ajouter les autres types de chauffage
        dct_HVAC_Heating["Fuel Boiler, 72% AFUE & Electric Baseboard, 100% Efficiency"] = dct_HVAC_Heating["Fuel Boiler, 72% AFUE"].copy()
        dct_HVAC_Heating["Fuel Boiler, 72% AFUE & Electric Wall Furnace, 100% AFUE"] = dct_HVAC_Heating["Fuel Boiler, 72% AFUE"].copy()
        dct_HVAC_Heating["Fuel Boiler, 72% AFUE & ASHP, SEER 15, 8.5 HSPF"] = dct_HVAC_Heating["Fuel Boiler, 72% AFUE"].copy()
        dct_HVAC_Heating["Fuel Boiler, 72% AFUE & Electric Furnace, 100% AFUE"] = dct_HVAC_Heating["Fuel Boiler, 72% AFUE"].copy()
        dct_HVAC_Heating["Fuel Boiler, 72% AFUE & Electric Boiler, 100% AFUE"] = dct_HVAC_Heating["Fuel Boiler, 72% AFUE"].copy()
        dct_HVAC_Heating["Fuel Boiler, 72% AFUE & Electric Wall Furnace, 100% AFUE.1"] = dct_HVAC_Heating["Fuel Boiler, 72% AFUE"].copy()
        dct_HVAC_Heating["Fuel Boiler, 72% AFUE & Fuel Furnace, 80% AFUE"] = dct_HVAC_Heating["Fuel Boiler, 72% AFUE"].copy()
        dct_HVAC_Heating["Fuel Boiler, 72% AFUE & Fuel Boiler, 80% AFUE"] = dct_HVAC_Heating["Fuel Boiler, 72% AFUE"].copy()

        # bienergie PAC + Gz ou mazout app
        dct_HVAC_Heating["Fuel Furnace, 80% AFUE & ASHP, SEER 15, 8.5 HSPF"] = dct_HVAC_Heating["ASHP, SEER 15, 8.5 HSPF"].copy()
        dct_HVAC_Heating["Fuel Furnace, 80% AFUE & ASHP, SEER 15, 8.5 HSPF"]["heat_pump_type"] = "air-to-air"
        dct_HVAC_Heating["Fuel Furnace, 80% AFUE & ASHP, SEER 15, 8.5 HSPF"]["heat_pump_compressor_lockout_temp"] = 10.4 #F =-12C
        dct_HVAC_Heating["Fuel Furnace, 80% AFUE & ASHP, SEER 15, 8.5 HSPF"]["heat_pump_backup_type"] = "integrated"
        dct_HVAC_Heating["Fuel Furnace, 80% AFUE & ASHP, SEER 15, 8.5 HSPF"]["heat_pump_backup_fuel"] = "fuel oil"
        dct_HVAC_Heating["Fuel Furnace, 80% AFUE & ASHP, SEER 15, 8.5 HSPF"]["heat_pump_backup_heating_efficiency"] = 0.8
        dct_HVAC_Heating["Fuel Furnace, 80% AFUE & ASHP, SEER 15, 8.5 HSPF"]["heat_pump_backup_heating_capacity"] = "auto"

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
    path = PROJECT_DIR+"/data/BayesianNetwork/BN_EUEMr.XDSL"
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