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

        arg = "Presence_Garage"
        argHPXML = "geometry_garage_width"
        if (argHPXML not in dct_HPXML.keys()):
            if (arg in dct_args.keys()):
                if (dct_args[arg] in ["Garage non chauffé",
                                      "Garage chauffé à électricité",
                                      "Garage chauffé à autre source"]):
                    if (dct_HPXML.get("geometry_unit_type") in ["single-family detached", "single-family attached"]):
                        dct_HPXML[argHPXML] = 24 #12 / 24 / 36 taille du garage
                    else:
                        dct_HPXML[argHPXML] = 0 #Pas de garage pour les plex/appartemnt
                else:
                    dct_HPXML[argHPXML] = 0
            else:
                if self.HPXMLArg.arguments[argHPXML].get("Default Value", "Defaut_Not_Existing")!="Defaut_Not_Existing":
                    dct_HPXML[argHPXML] = self.HPXMLArg.arguments[argHPXML].get("Default Value")
                else:
                    dct_HPXML[argHPXML] = 0 #No garage

        #geometry_garage_depth
        dct_HPXML["geometry_garage_depth"] = 24
        
        #geometry_garage_position
        dct_HPXML["geometry_garage_position"] = "Right"

        #_____________________________________________________________
        #geometry_unit_num_floors_above_grade
        
        #The number of floors above grade in the unit. 
        # Attic type ConditionedAttic is included. 
        # Assumed to be 1 for apartment units.
        arg = "Nombre_Etages"
        argHPXML = "geometry_unit_num_floors_above_grade"
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

#corridor_position

 #FAIRE Les murs adiabatiques

                #"Territoire_HQ",
                #FAIT "Type_Logement",
                #FAIT "Nombre_Pieces",
                #FAIT "Nombre_Etages",
                #FAIT # "Superficie_Totale",
                # "Presence_SousSol",
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





        # ajout des Valeurs par défaut du HPXML si cle n'existe pas
        k_missing = list(set(self.HPXMLArg.arguments.keys()) - set(dct_HPXML.keys()))
        dct_HPXML_missing = {k: self.HPXMLArg.arguments[k].get("Default Value", None) for k in k_missing if self.HPXMLArg.arguments[k].get("Default Value", "Defaut_Not_Existing")!="Defaut_Not_Existing"} 

        dct_HPXML = {**dct_HPXML, **dct_HPXML_missing}
        # ne pas traiter les variables exclues (cf. MapHPXML.py)    
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

    Nombre_de_Samples = 10
    Evidence = {"Type_Logement": "Collective",
                "Nombre_Pieces": "1"}#{"Mode_Occupation": "Proprietaire"}

    # Fait un échantillonage - Avant enregistrement
    df1 = InsClsSampler.do_Sampling(Nombre_de_Samples, evs = Evidence)
    lst_dct_args = df1.to_dict(orient='records')
    # Affiche les échantillons - Avant enregistrement
    
    #s.getBNStructure()
    #print(s.lst_NOEUD, s.LIST_Dict)

    MapSample = MapHPXML()
    lst_dct_HPXML = MapSample.run(lst_dct_args)
    
    print("Nombre d'attributs HPXML: ", len(lst_dct_HPXML[0].keys()))
    pd.DataFrame(lst_dct_HPXML)
