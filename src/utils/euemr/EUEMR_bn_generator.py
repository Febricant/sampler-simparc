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
import numpy as np
import pandas as pd
import pyagrum as gum
from pathlib import Path

from src.utils.euemr.EUEMR_attributs import Attributs_EUEMr
from src.utils.euemr.Mapping import EUEMR_formatage
from src.utils.sampler.bayesian_network import bayesian_network


import warnings
warnings.filterwarnings('ignore', category=UserWarning, module='openpyxl')

class EUEMr(bayesian_network):
    '''
    Class qui permet de générer un réseau bayésien à partir des données EUEMr.

    Les données de consommation électrique annuelle sont ignorées (i.e. ConsoElecAn) pour éviter une référence circulaire.
    '''

    lst_NOEUD = ["Territoire_HQ",
                 "Region_Administrative",
                 "Type_Logement",
                 "Type_Batiment",
                 "Nombre_Etages",
                 "Nombre_Pieces",
                 "Superficie_Totale",
                 "Presence_SousSol",
                 "Nombre_Personnes",
                 "Presence_Garage",
                 "Mode_Occupation",
                 "An_Construction",
                 "An_ConstructionCode",
                 "Climatisation",
                 "Source_Energie_Chauf",
                 "Chauffage_Logement",
                 "Spa_Presence",
                 "Spa_Logement",
                 "Spa_Saison",
                 "Spa_Utilisation_SaisonChaude",
                 "Spa_Utilisation_SaisonFroide",
                 "Piscine_Presence",
                 "Piscine_Type",
                 "Piscine_Minuterie",
                 "Piscine_Toile",
                 "Piscine_Chauffee",
                 "Piscine_ChaufType",
                "Vehicule_Presence",
                "Vehicule_BornePresence",
                "ChaufEau_ChaufType",
                "ChaufEau_Type",
                "ChaufEau_Presence",
                "Congelateur_Nombre",
                "Refrigerateur_Nombre",
                "LaveLinge_Type",
                "SecheLinge_Presence",
                "LaveVaisselle_Presence",
                "Cuisiniere_Presence",
                "Cuisiniere_Energie",
                "Eclairage_LED"]

    # création des noeuds 
    # Nom_Noeud:description_Noeud

    MapEUEMr = EUEMR_formatage()
    dictMapEUEMr = MapEUEMr.get_Mettadata()
    NOEUD_EUEMr = {}
    for key in lst_NOEUD:
        if key in dictMapEUEMr.keys():
            NOEUD_EUEMr[key] = dictMapEUEMr[key]["Description"]
        else:
            NOEUD_EUEMr[key] = Attributs_EUEMr.__dict__[key]["Description"]

    # création des dictionnaires des noeuds
    # {Nom_Noeud: {IdLabel: Label}}

    LIST_Dict = {}
    for key in lst_NOEUD:
        if key in dictMapEUEMr.keys():
            LIST_Dict[key] = {idL:Lab for idL,Lab in zip(dictMapEUEMr[key]["IdLabel"],
                                                         dictMapEUEMr[key]["Label"])}

        else:
            LIST_Dict[key] = {idL:Lab for idL,Lab in zip(Attributs_EUEMr.__dict__[key]["IdLabel"],
                                                        Attributs_EUEMr.__dict__[key]["Label"])}

    fileEUEMr = str(Path(__file__).parents[3] / "/data/processed/euemr/2022/sondage_residentiel_version_finale_formatted.csv")

    def __init__(self):
        """
        Initialize the EUEMr class with an optional DataFrame.
        
        :param df: pandas DataFrame containing the data.
        """
        pass
    
    def Add_Node_Fromcsv(self, dct_housing_characteristics, listAttributs):
        
        for Attributs in listAttributs:
            #for csv file (ne charger qu'une fois) et creer une structure
            dct_dependancy = dct_housing_characteristics[Attributs]["Dependency"]
            dct_option = dct_housing_characteristics[Attributs]["Option"]
            df = dct_housing_characteristics[Attributs]["Table"]
            
            # remove option if only 0
            option_remove = []
            for option, option_name in dct_option.items():
                if df[option].sum() == 0:
                    option_remove.append(option)
            for k in option_remove:
                del dct_option[k]

            # add node
            Node_name = Attributs
            Node_value  = dct_option.keys()
            self.bn.add(gum.LabelizedVariable(Node_name, Node_name, [str(i.split("Option=")[-1]) for i in Node_value]))   # par key [1,2,99]

            # add dependency (i.e. add arcs)
            for dep in list(dct_dependancy.values())[::-1]:
                self.bn.addArc(dep, Node_name)
    
            for idx in df.index:
                filtered_df = df[df.index == idx]
                dep_values = {dep_name: str(filtered_df[dep].values[0]) for dep, dep_name in dct_dependancy.items()}
                option_values = [float(filtered_df[option].values[0]) for option, option_name in dct_option.items()]
                sumlst = sum(option_values)
                listProb = [k/sumlst for k in option_values]
                self.bn.cpt(Node_name)[dep_values] = listProb

    def Make_BN(self):

        Pond_col_Name = "POND1"
        absolute_path = self.fileEUEMr
        self.Load_csv(absolute_path)#self.dfcsv
        self.dfcsv = self.dfcsv[self.dfcsv[Pond_col_Name].notnull()]  # Filtrer les lignes où POND1 est supérieur à 0 (enleve logement spécifique aux nouvelle constructions)

        for col in ["PONDNew", "POND1", "POND2x", "POND1_POP", "POND2x_POP"]:
            self.dfcsv[col] = pd.to_numeric(self.dfcsv[col], errors='coerce')  # Convert to numeric, coercing errors to NaN

        # Assigner les information de la structure des variable
        diEUEMr = self.LIST_Dict
        # Création du réseau
        self.bn=gum.BayesNet('EUEMr_BN')
        
        # Ajout des Noeuds dans le réseau
        for k in diEUEMr :
            #self.bn.add(k, len(diEUEMr[k]))   # par id [0,1,2] 
            #self.bn.add(gum.LabelizedVariable(k,k,[str(i) for i in diEUEMr[k].keys()]))   # par key [1,2,99]
            #Description : self.NOEUD_EUEMr[k]
            self.bn.add(gum.LabelizedVariable(k,self.NOEUD_EUEMr[k],[str(i) for i in diEUEMr[k].values()]))   # par key [1,2,99]

        # Imposition des dépendances
        diDep = {ele : [] for ele in diEUEMr} # Par défaut, ne mettre aucune dépendance à toutes les variables => list vide
        diDep['Territoire_HQ'] = []
        diDep['Region_Administrative'] = ["Territoire_HQ"]
        diDep['Type_Logement'] = ["Region_Administrative"]
        diDep["Type_Batiment"] = ["Type_Logement"]
        diDep["Nombre_Etages"] = ["Type_Logement", "Region_Administrative"]
        diDep["Nombre_Pieces"] = ["Type_Logement", "Nombre_Etages"]
        diDep["Superficie_Totale"] = ["Nombre_Pieces"]
        diDep["Presence_SousSol"] = ["Type_Logement", "Nombre_Etages"]
        diDep["Presence_Garage"] = ["Type_Logement"]#, "Region_Administrative"]
        diDep["Nombre_Personnes"] = ["Nombre_Pieces"]#["Type_Logement", "Nombre_Pieces","Region_Administrative"]
        diDep["Mode_Occupation"] = ["Type_Logement"]
        diDep["An_Construction"] = ["Type_Logement"]
        diDep["An_ConstructionCode"] = ["An_Construction"]
        #diDep["Source_Energie_Chauf"] = ["Type_Logement","An_Construction"]
        diDep["Source_Energie_Chauf"] = ["Territoire_HQ","Type_Batiment" , "An_ConstructionCode"]
        diDep["Chauffage_Logement"] = ["Type_Logement", "Source_Energie_Chauf"]
        diDep["Climatisation"] = ["Type_Logement","Chauffage_Logement"]
        diDep["Spa_Presence"] = ["Region_Administrative","Type_Logement"]
        diDep["Spa_Logement"] = ["Spa_Presence", "Type_Logement"]
        diDep["Spa_Saison"] = ["Spa_Presence", "Spa_Logement"]
        diDep["Spa_Utilisation_SaisonChaude"] = ["Spa_Saison"]
        diDep["Spa_Utilisation_SaisonFroide"] = ["Spa_Saison"]
        diDep["Piscine_Presence"] = ["Region_Administrative","Type_Logement"]
        diDep["Piscine_Type"] = ["Piscine_Presence", "Type_Logement"]
        diDep["Piscine_Minuterie"] = ["Piscine_Type"]
        diDep["Piscine_Toile"] = ["Piscine_Type"]
        diDep["Piscine_Chauffee"] = ["Piscine_Type"]
        diDep["Piscine_ChaufType"] = ["Piscine_Chauffee"]
        diDep["Vehicule_Presence"] = ["Region_Administrative","Type_Logement"]
        diDep["Vehicule_BornePresence"] = ["Vehicule_Presence","Type_Logement"]
        diDep["ChaufEau_Presence"] = ["Type_Logement"]
        diDep["ChaufEau_Type"] = ["ChaufEau_Presence", "Type_Logement"]
        diDep["ChaufEau_ChaufType"] = ["ChaufEau_Presence","Source_Energie_Chauf"]
        diDep["Congelateur_Nombre"] = ["Type_Logement","Nombre_Personnes"]
        diDep["Refrigerateur_Nombre"] = ["Type_Logement","Nombre_Personnes"]
        diDep["LaveLinge_Type"] = ["Type_Logement","Nombre_Personnes"]
        diDep["SecheLinge_Presence"] = ["Type_Logement","Nombre_Personnes"]
        diDep["LaveVaisselle_Presence"] = ["Type_Logement","Nombre_Personnes"]
        diDep["Cuisiniere_Presence"] = ["Type_Logement","Nombre_Personnes"]
        diDep["Cuisiniere_Energie"] = ["Cuisiniere_Presence","Source_Energie_Chauf"]
        diDep["Eclairage_LED"] = ["Type_Logement","Mode_Occupation"]

        #diDep["ConsoElecAn"] = ["AnConstruction", "TypeLogement", "SourceEnerChauf"]

        # Ajout des Arcs
        for k in diDep :
            if diDep[k] != [] :
                for ele in diDep[k][::-1]:
                    self.bn.addArc(ele,k)  

        # Ajout des tables conditionnelles
        diCPT = {}
        for k in diDep :
            if len(diDep[k]) == 0 :  # Aucune dépendance
                ind = [0]
                liInd = [0]
            elif len(diDep[k]) == 1 :  # 1 dépendance
                ind = pd.Index(diEUEMr[diDep[k][0]].values(), name = diDep[k][0]) # # diEUEMr[k].keys()
                liInd = self.dfcsv[diDep[k][0]]
            else: 
                iterables = [diEUEMr[j].values() for j in diDep[k]] # # diEUEMr[k].keys()
                ind = pd.MultiIndex.from_product(iterables, names = diDep[k])
                liInd = [self.dfcsv[ele] for ele in diDep[k]]

            #Créer un fataframe vide avec tous les champs des dépendant   
            diCPT[k] = pd.DataFrame(index = ind, columns = diEUEMr[k].values()).astype(float).fillna(0)#.fillna(0) # diEUEMr[k].keys()
            
            # Updater le DataFrame avec l'occurance d'individu par dépendances

            diCPT[k].update(pd.crosstab(liInd,
                                        self.dfcsv[k],
                                    values=self.dfcsv[Pond_col_Name], # Pondération
                                    aggfunc="sum"))
            #diCPT[k] = diCPT[k].astype('double')#int64

    #    # Mettre les prob associées à la 1ère dépendance [diDEP[k][0]] si le nombre d'individu par Bin est =< à NbMaxBin 
            nbIndMin = -1 #   -1 bipass # 5
            maskIndMin = diCPT[k].sum(axis=1) <= nbIndMin
            if maskIndMin.sum() > 0 :
                liLevel0 = list(diCPT[k].loc[maskIndMin].index.get_level_values(0).unique())
                for i in liLevel0:
                    maskLevel0 = diCPT[k].index.get_level_values(0) == i
                    maskTot =  maskIndMin & maskLevel0
                    liOccSum = pd.crosstab(self.dfcsv[diDep[k][0]],
                                        self.dfcsv[k],
                                        values=self.dfcsv[Pond_col_Name], # Pondération
                                        aggfunc="sum").fillna(0).loc[i].tolist()
                    intNbCat = len(diCPT[k].loc[maskTot].index)
                    liOcc =[liOccSum for j in range(intNbCat)] 
                    diCPT[k].loc[maskTot,:] = liOcc
                     
            # Normaliser le DataFrame
            dfCPT = diCPT[k].apply(lambda x: (x/x.sum()), axis = 1).fillna(0)#(0.000000000001)        
            #dfCPT = diCPT[k].apply(lambda x: (x/x.sum()), axis = 1).fillna(0)

            # Définir la dimension de la table d'occurence   
            liShape = [len(diEUEMr[ele]) for ele in diDep[k]]
            liShape.append(len(diEUEMr[k]))  
            
            # Affecter le table d'occurence au réseau
            arPCT  = np.reshape(dfCPT.values,tuple(liShape))                
            self.bn.cpt(k)[:] = arPCT   
           
        #gnb.showBN(self.bn,size = '30')
    
    
    def Make_csv(self):
        Pond_col_Name = "POND1"
        absolute_path = self.fileEUEMr
        self.Load_csv(absolute_path)#self.dfcsv
        self.dfcsv = self.dfcsv[self.dfcsv[Pond_col_Name].notnull()]  # Filtrer les lignes où POND1 est supérieur à 0 (enleve logement spécifique aux nouvelle constructions)

        # Assigner les information de la structure des variable
        diEUEMr = self.LIST_Dict

        for col in ["PONDNew","POND1", "POND2x", "POND1_POP", "POND2x_POP"]:
            self.dfcsv[col] = pd.to_numeric(self.dfcsv[col], errors='coerce')  # Convert to numeric, coercing errors to NaN

        # QA4M : Nombre de logements dans l'immeuble
        dct_MetaStats = {"Nombre_Logement" : {"Csv_name": "Geometry Building Number Units.csv",
                                              "dropvalues" : [".", "NSP/NRP"],
                                              "Dependancy": ["Type_Logement"]}}

                # Ajout des tables conditionnelles
        for Name, dct_val in dct_MetaStats.items():
            csvName = str(Path(__file__).parents[3] / "/data/processed/housing_characteristics/"+dct_val["Csv_name"])
            lstDep = dct_val["Dependancy"]

            #for k in diDep :
            if len(lstDep) == 0 :  # Aucune dépendance
                ind = [0]
                liInd = [0]
            elif len(lstDep) == 1 :  # 1 dépendance
                ind = pd.Index(diEUEMr[lstDep[0]].values(), name = lstDep[0]) # # diEUEMr[k].keys()
                liInd = self.dfcsv[lstDep[0]]
            else: 
                iterables = [diEUEMr[j].values() for j in lstDep] # # diEUEMr[k].keys()
                ind = pd.MultiIndex.from_product(iterables, names = lstDep)
                liInd = [self.dfcsv[ele] for ele in lstDep]
            
            #Créer un fataframe vide avec tous les champs des dépendant  
            colval = self.dfcsv[Name].drop_duplicates()
            maskvalues = colval.isin(dct_val["dropvalues"]).values
            colVal_f = colval[~maskvalues].values
             
            diCPT = pd.DataFrame(index = ind, columns = colVal_f).astype(float).fillna(0)#.fillna(0) # diEUEMr[k].keys()

            # Updater le DataFrame avec l'occurance d'individu par dépendances

            diCPT.update(pd.crosstab(liInd,
                                    self.dfcsv[Name],
                                    values=self.dfcsv[Pond_col_Name], # Pondération
                                    aggfunc="sum"))


            #Correction manuelle pour certains cas
            #Nombre_Logement
            if Name == "Nombre_Logement":
                if "1" not in diCPT.columns:
                    diCPT["1"] = 0
                if "2" not in diCPT.columns:
                    diCPT["2"] = 0
                if "3" not in diCPT.columns:
                    diCPT["3"] = 0
                
                diCPT.loc["Triplex"] = 0
                diCPT.loc["Triplex", "3"] = 1
                diCPT.loc["Duplex"] = 0
                diCPT.loc["Duplex", "2"] = 1
                diCPT.loc["Maison en rangee"] = 0
                diCPT.loc["Maison en rangee", "1"] = 1
                diCPT.loc["Maison individuelle"] = 0
                diCPT.loc["Maison individuelle", "1"] = 1
            
            # Normaliser le DataFrame
            dfCPT = diCPT.apply(lambda x: (x/x.sum()), axis = 1).fillna(0) 
            #Changement des noms
            dfCPTf = dfCPT.reset_index()
            
            rename = {i: "Dependency="+str(i) for i in lstDep} | {col: "Option="+str(col) for col in dfCPTf.columns if col not in lstDep}
            dfCPTf = dfCPTf.rename(columns=rename)
            #Enregistrement des donnes
            dfCPTf.to_csv(csvName, index=False, header=True, sep=";")

