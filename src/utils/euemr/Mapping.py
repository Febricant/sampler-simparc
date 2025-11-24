# -*- coding: utf-8 -*-
"""
Created on 26-06-2025

@author: cv1751 - Brice Le Lostec
@description: Class for generating Bayesian Networks (BN) using pyAgrum.
@note: This class provides methods to save, load, plot Bayesian Networks and load CSV files.
@version: 1.0
python 3.11

"""

import pandas as pd
from src.utils.euemr.EUEMR_attributs import Attributs_EUEMr
from pathlib import Path

import warnings
warnings.filterwarnings('ignore', category=UserWarning, module='openpyxl')

class EUEMR_formatage:
    """
    Classe pour transformet les données EUEMr en données pour le BN.
    """
    def __init__(self):
        self.set_Mapping()
    def set_Mapping(self):
        """
        Définit le mapping direct pour les colonnes du DataFrame EUEMr.
        """
        self.Mapping = {}
        self.Mapping["Type_Logement"] = {
                                "ColSrc" : "QA4",
                                "typeMapping" : "list",
                                "Mapping" : {"Collective" :["Immeuble de 4 à 8 appartements",
                                                            "Immeuble de 9 à 19 appartements",
                                                            "Immeuble de 50 appartements ou plus",
                                                            "Immeuble de 20 à 49 appartements",
                                                            "Immeuble à appartement (sans précision)"],
                                            "Triplex" : ["Triplex détaché", 
                                                        "Triplex jumelé/en bout de rangée attaché 1 seul côté",
                                                        "Triplex (sans précision)",
                                                        "Triplex milieu de rangée attaché 2 côtés"],
                                            "Duplex" : ["Duplex jumelé/en bout de rangée attaché 1 seul côté",
                                                        "Duplex (sans précision)",
                                                        "Duplex détaché",
                                                        "Duplex en milieu de rangée attaché 2 côtés"],
                                            "Maison en rangee" : ["Maison individuelle en rangée attachée des 2 côtés",
                                                                  "Maison individuelle en rangée (sans précisions)"],
                                            "Maison individuelle" : ['Maison individuelle détachée/unifamiliale',
                                                                    "Maison jumelée/bout de rangée attachée 1 côté/semi-détaché",
                                                                    "Maison mobile/roulotte"]}}
        
        self.Mapping["Type_Batiment"] = {
                                "ColSrc" : "Type_Logement",
                                "typeMapping" : "list",
                                "Mapping" : {"Collective" :["Collective"],
                                            "Plex" : ["Triplex", "Duplex"],
                                            "Maison" : ["Maison en rangee", "Maison individuelle"]}}
        
        self.Mapping["Mode_Occupation"] = {
                                "ColSrc" : "QA1",
                                "typeMapping" : "list",
                                "Mapping" : {"Locataire" :["Le locataire / Co-locataire"],
                                            "Proprietaire" : ["Le propriétaire / Co-propriétaire"]}}
        
        ConsoElecAn_kmax = 45000
        ConsoElecAn_kstep = 5000
        ConsoElecAn_kmin = 0
        ConsoElecAn_bins = [ConsoElecAn_kmin-50000]+[i for i in range(ConsoElecAn_kmin,ConsoElecAn_kmax+ConsoElecAn_kstep, ConsoElecAn_kstep)]+[ConsoElecAn_kmax+ConsoElecAn_kstep+50000]
        ConsoElecAn_labels = ['< '+str(ConsoElecAn_kstep)] + [f"[{ConsoElecAn_bins[i+1]} - {ConsoElecAn_bins[i+2]})" for i in range(len(ConsoElecAn_bins)-3)] + ['>= '+str(ConsoElecAn_kmax)]
        self.Mapping["Consommation_Elec_An"] = {
                                "ColSrc" : "CONS_AN",
                                "typeMapping" : "bin",
                                "Mapping" : {"labels" : ConsoElecAn_labels,
                                              "bins" : ConsoElecAn_bins}}
        
        AnConstruction_kmax = 2020
        AnConstruction_kstep = 10
        AnConstruction_kmin = 1950
        AnConstruction_bins = [AnConstruction_kmin-1000]+[i for i in range(AnConstruction_kmin,AnConstruction_kmax+AnConstruction_kstep, AnConstruction_kstep)]+[AnConstruction_kmax+AnConstruction_kstep+1000]
        AnConstruction_labels = ['< '+str(AnConstruction_kmin)] + [f"[{AnConstruction_bins[i+1]} - {AnConstruction_bins[i+2]})" for i in range(len(AnConstruction_bins)-3)] + ['>= '+str(AnConstruction_kmax)]
        self.Mapping["An_Construction"] = {
                                "ColSrc" : "QA6M",
                                "typeMapping" : "bin",
                                "Mapping" : {"labels" : AnConstruction_labels,
                                            "bins" : AnConstruction_bins}}

        AnConstructionCode_bins = [1946-1000, 1946, 1971, 1986, 2013, 2013+1000]
        AnConstructionCode_labels = ["< 1946", "[1946 - 1971)", "[1971 - 1986)", "[1986 - 2013)", ">= 2013"]
        self.Mapping["An_ConstructionCode"] = {
                                "ColSrc" : "QA6M",
                                "typeMapping" : "bin",
                                "Mapping" : {"labels" : AnConstructionCode_labels,
                                            "bins" : AnConstructionCode_bins}}
        AnConstruction_bins = [1946 - 1000]+[1960, 1983, 2011]+[2011+1000]; 

        self.Mapping["Source_Energie_Chauf"] = {
                                "ColSrc" : "QC1R",
                                "typeMapping" : "list",
                                "Mapping" : {"Electricite" :["Électricité"],
                                            "Mazout" : ["Mazout"],
                                            "Gaz naturel" : ["Gaz naturel"],
                                            "Bi-energie" : ["Bi-énergie"],
                                            "Bois" : ["Bois seul ou en combinaison"]}}
        
        self.Mapping["Territoire_HQ"] = {}
        self.Mapping["Territoire_HQ"]["ColSrc"] = "TERR_HQ"
        self.Mapping["Territoire_HQ"]["typeMapping"] = "list"
        self.Mapping["Territoire_HQ"]["Mapping"] = {"Est et Nord du Québec" : ["Est et nord du Québec"],
                                                     "Laurentides": ["Laurentides"],
                                                     "Montmorency": ["Montmorency"],
                                                     "Montréal": ["Montréal"],
                                                     "Richelieu": ["Richelieu"]}
        self.Mapping["Region_Administrative"] = {}
        self.Mapping["Region_Administrative"]["ColSrc"] = "ZONE"
        self.Mapping["Region_Administrative"]["typeMapping"] = "custom"
        self.Mapping["Region_Administrative"]["Mapping"] = {"Bas-Saint-Laurent":None,
                                                            "Capitale-Nationale":None,
                                                            "Centre-du-Québec":None,
                                                            "Chaudière-Appalaches":None,
                                                            "Côte-Nord":None,
                                                            "Estrie":None,
                                                            "Gaspésie-Îles-de-la-Madeleine":None,
                                                            "Lanaudière":None,
                                                            "Laurentides":None,
                                                            "Laval":None,
                                                            "Mauricie":None,
                                                            "Montérégie":None,
                                                            "Montréal":None,
                                                            "Outaouais":None,
                                                            "Saguenay-Lac-Saint-Jean":None}
        #"Abitibi-Témiscamingue":None,
        #Nord-du-Québec":None,

        self.Mapping["Nombre_Pieces"] = {}
        self.Mapping["Nombre_Pieces"]["ColSrc"] = "QH1"
        self.Mapping["Nombre_Pieces"]["typeMapping"] = "list"
        self.Mapping["Nombre_Pieces"]["Mapping"] = {str(i): [i] for i in range(1,14+1)}
        self.Mapping["Nombre_Pieces"]["Mapping"]["15 et plus"] = [str(i) for i in range(15,20+1)]

        self.Mapping["Nombre_Etages"] = {}
        self.Mapping["Nombre_Etages"]["ColSrc"] = "QH2"
        self.Mapping["Nombre_Etages"]["typeMapping"] = "list"
        self.Mapping["Nombre_Etages"]["Mapping"] = {"Un étage": ["Un étage", "1.5 étages"],#trop peu de "1.5 étages"
                                                     "Deux étages": ["Deux étages", "2 ½étages"],#trop peu de "2 ½étages"
                                                        "Trois étages et plus": ["Trois étages", "3½ étages", "Quatre étages", "4½ étages", "5 étages"]}

        Superficie_Totale_kmax = 5000
        Superficie_Totale_kstep = 500
        Superficie_Totale_kmin = 0
        Superficie_Totale_bins = [1 if i==0 else i for i in range(Superficie_Totale_kmin,Superficie_Totale_kmax+Superficie_Totale_kstep, Superficie_Totale_kstep)]+[Superficie_Totale_kmax+Superficie_Totale_kstep+10000]
        Superficie_Totale_labels = [f"[{Superficie_Totale_bins[i]} - {Superficie_Totale_bins[i+1]})" for i in range(len(Superficie_Totale_bins)-2)] + ['>= '+str(Superficie_Totale_kmax)]
        self.Mapping["Superficie_Totale"] = {}
        self.Mapping["Superficie_Totale"]["ColSrc"] = "SUPERTOT"
        self.Mapping["Superficie_Totale"]["typeMapping"] = "bin"
        self.Mapping["Superficie_Totale"]["Mapping"] = {"labels" : Superficie_Totale_labels,
                                    "bins" : Superficie_Totale_bins}


        self.Mapping["Presence_SousSol"] = {}
        self.Mapping["Presence_SousSol"]["ColSrc"] = "QH4"
        self.Mapping["Presence_SousSol"]["typeMapping"] = "list"# ne s'applique qu'au maison
        self.Mapping["Presence_SousSol"]["Mapping"] = {"Sous sol 6 pied":["Un sous-sol d'une hauteur de 6 ou 7 pieds avec murs & planchers en béton (inclus les demis sous-sol)"],
                                                        "Vide sanitaire moins 6 pieds" :["Un vide sanitaire d'une hauteur inférieure à 7 pieds avec plancher en terre"],
                                                        "Aucun Sous-sol ou vide sanitaire" :[".", "Ne comporte ni sous-sol, ni vide sanitaire"],
                                                        "Sous-sol et vide sanitaire" :["Un sous-sol et un vide sanitaire"]}
        
        self.Mapping["Nombre_Personnes"] = {}
        self.Mapping["Nombre_Personnes"]["ColSrc"] = "QL1"
        self.Mapping["Nombre_Personnes"]["typeMapping"] = "list"
        self.Mapping["Nombre_Personnes"]["Mapping"] = {"1":[1],
                                                        "2" :[2],
                                                        "3" :[3],
                                                        "4" :[4],
                                                        "5 et plus" :[5, 6, 7, 8, 9, 10, 11, 12, 15, 25]}


        #presence garage et chauffé et type chauffage
        self.Mapping["Presence_Garage"] = {}
        self.Mapping["Presence_Garage"]["ColSrc"] = "QM1A" # seulement pour la méthode get_Mettadata
        self.Mapping["Presence_Garage"]["typeMapping"] = "custom"
        self.Mapping["Presence_Garage"]["Mapping"] = {"Pas de Garage":None,
                                                        "Garage non chauffé":None,
                                                        "Garage chauffé à électricité":None,
                                                        "Garage chauffé à autre source":None}
                                        
        #Type de chauffage
        self.Mapping["Chauffage_Logement"] = {}
        self.Mapping["Chauffage_Logement"]["ColSrc"] = "SYSTEM1R" # seulement pour la méthode get_Mettadata
        self.Mapping["Chauffage_Logement"]["typeMapping"] = "custom"
        self.Mapping["Chauffage_Logement"]["Mapping"] = {"Plinthes électriques":None,
                                                        "Unités convecteurs, plancher ou plafond radiant":None,
                                                        "Thermopompe et Système central à air chaud":None,
                                                        "Thermopompe et Système central à eau chaude": None,
                                                        "Thermopompe géothermique seule": None,
                                                        "Thermopompe géothermique et Plinthes électriques": None,
                                                        "Thermopompe géothermique et Fournaise": None,
                                                        "Thermopompe murale" : None,
                                                        "Thermopompe murale et Plinthes électriques": None,
                                                        "Thermopompe murale et Fournaise": None,
                                                        "Système central à air chaud":None,
                                                        "Système central à eau chaude":None,
                                                        "Fournaise ou poêle à bois":None,
                                                        "Fournaise murale ou de plancher":None,
                                                        "Fournaise ou poêle à bois et Plinthes électriques":None,
                                                        "Fournaise ou poêle à bois et Unités convecteurs, plancher ou plafond radiant":None,
                                                        "Fournaise ou poêle à bois et Thermopompe murale":None,
                                                        "Fournaise ou poêle à bois et Système central à air chaud":None,
                                                        "Fournaise ou poêle à bois et Système central à eau chaude":None,
                                                        "Fournaise ou poêle à bois et Fournaise murale ou de plancher":None}#,
                                                        #"Autres":None,
                                                        #"Pas de système principal (chalet)":None,}

        # QB2I1 : Nombre de réfrigérateurs dans la résidence
        self.Mapping["Nombre_Refrigerateur"] = {}
        self.Mapping["Nombre_Refrigerateur"]["ColSrc"] = "QB2I1"
        self.Mapping["Nombre_Refrigerateur"]["typeMapping"] = "list"
        self.Mapping["Nombre_Refrigerateur"]["Mapping"] = {"1":[1],
                                                        "2" :[2],
                                                        "3 et plus" :[3, 4, 5,
                                                                       7]}

        # no MAPPING ; fOR CSV STATS
        self.Mapping["Nombre_Logement"] = {}
        self.Mapping["Nombre_Logement"]["ColSrc"] = "QA4M"
        self.Mapping["Nombre_Logement"]["typeMapping"] = "no"
        self.Mapping["Nombre_Logement"]["Mapping"] = {}

        #QD11BM1 type de climatisation
        #Ne sait pas/Ne répond pas ; Aucune de ces réponses

        self.Mapping["Climatisation"] = {}
        self.Mapping["Climatisation"]["ColSrc"] = "QD11BM1"
        self.Mapping["Climatisation"]["typeMapping"] = "list"
        self.Mapping["Climatisation"]["Mapping"] = {"Aucune": ["."],
                                                     "Fenêtre, mobile, portable": ["Climatiseur de fenêtre",
                                                                                   "Climatiseur mobile / portable"],
                                                     "Murale": ["Climatiseur mural ou bibloc (mini-split)","Thermopompe murale"],
                                                     "Centrale": ["Thermopompe centrale", "Thermopompe géothermique","Climatiseur central autre qu'une thermopompe"]}

        #presence spa
        # spa (oui, non, oui+type)
        # spa utilisation (saison)
        # spa utilisation (habitude Temperature)
        self.Mapping["Spa_Presence"] = {}
        self.Mapping["Spa_Presence"]["ColSrc"] = "QB1M"
        self.Mapping["Spa_Presence"]["typeMapping"] = "list"
        self.Mapping["Spa_Presence"]["Mapping"] = {"Oui":["Oui"],
                                                   "Non":["Non", "Ne sait pas/Ne répond pas"]}

        self.Mapping["Spa_Logement"] = {}
        self.Mapping["Spa_Logement"]["ColSrc"] = "QB1M3"
        self.Mapping["Spa_Logement"]["typeMapping"] = "list"
        self.Mapping["Spa_Logement"]["Mapping"] = {"Aucun": ["."],
                                                    "Exterieur":["Extérieur", "Ne sait pas/Ne répond pas"],
                                                   "Interieur":["Intérieur"]}

                #Spa_Saison
        self.Mapping["Spa_Saison"] = {}
        self.Mapping["Spa_Saison"]["ColSrc"] = "QS2M1R" # seulement pour la méthode get_Mettadata
        self.Mapping["Spa_Saison"]["typeMapping"] = "custom"
        self.Mapping["Spa_Saison"]["Mapping"] = {"Aucun": None,
                                                 "Pas utilisé":None,
                                                 "Ne sait pas": None,
                                                 "Toute_Saison": None,
                                                 "Printemps": None,
                                                 "Ete": None,
                                                 "Automne": None,
                                                 "Hiver": None,
                                                 "Printemps_Ete": None,
                                                 "Printemps_Automne": None,
                                                 "Printemps_Hiver":None,
                                                 "Ete_Automne":None,
                                                 "Ete_Hiver":None,
                                                "Automne_Hiver":None,
                                                "Printemps_Ete_Automne":None,
                                                #"Printemps_Ete_Hiver":None,
                                                "Printemps_Automne_Hiver":None,
                                                "Ete_Automne_Hiver":None,
                                                    }
        self.Mapping["Spa_Utilisation_SaisonChaude"] = {}
        self.Mapping["Spa_Utilisation_SaisonChaude"]["ColSrc"] = "QS3BB"
        self.Mapping["Spa_Utilisation_SaisonChaude"]["typeMapping"] = "list"
        self.Mapping["Spa_Utilisation_SaisonChaude"]["Mapping"] = {"Aucun": ["."],
                                                            "Ne sais pas":["Ne sait pas/Ne répond pas"],
                                                    "Constant":["Je maintenais la température de mon spa constante"],
                                                   "Augmentation":["J’augmentais la température pour les périodes de baignade"]}
        
        self.Mapping["Spa_Utilisation_SaisonFroide"] = {}
        self.Mapping["Spa_Utilisation_SaisonFroide"]["ColSrc"] = "QS3AA"
        self.Mapping["Spa_Utilisation_SaisonFroide"]["typeMapping"] = "list"
        self.Mapping["Spa_Utilisation_SaisonFroide"]["Mapping"] = {"Aucun": ["."],
                                                            "Ne sais pas":["Ne sait pas/Ne répond pas"],
                                                    "Constant":["Je maintenais la température de mon spa constante"],
                                                   "Augmentation":["J’augmentais la température pour les périodes de baignade"]}


        # piscine
        self.Mapping["Piscine_Presence"] = {}
        self.Mapping["Piscine_Presence"]["ColSrc"] = "QG1"
        self.Mapping["Piscine_Presence"]["typeMapping"] = "list"
        self.Mapping["Piscine_Presence"]["Mapping"] = {"Oui":["Oui"],
                                                       "Non":["Non", "Ne sait pas/Ne répond pas"]}
        self.Mapping["Piscine_Type"] = {}
        self.Mapping["Piscine_Type"]["ColSrc"] = "QG2"
        self.Mapping["Piscine_Type"]["typeMapping"] = "list"
        self.Mapping["Piscine_Type"]["Mapping"] = {"Aucun":["."],
                                                    "Hors_Terre":["Une piscine hors-terre / semi-creusée",
                                                                  "Une piscine hors-terre gonflable"],
                                                    "Creusee_Exterieur":["Une piscine creusée extérieure"],
                                                    "Creusee_Interieur":["Une piscine creusée intérieure"]}
        
        self.Mapping["Piscine_Minuterie"] = {}
        self.Mapping["Piscine_Minuterie"]["ColSrc"] = "QG3"
        self.Mapping["Piscine_Minuterie"]["typeMapping"] = "list"
        self.Mapping["Piscine_Minuterie"]["Mapping"] = {"Aucun": ["."],
                                                        "Oui":["Oui"],
                                                       "Non":["Non", "Ne sait pas/Ne répond pas"]}
        
        self.Mapping["Piscine_Toile"] = {}
        self.Mapping["Piscine_Toile"]["ColSrc"] = "QG5"
        self.Mapping["Piscine_Toile"]["typeMapping"] = "list"
        self.Mapping["Piscine_Toile"]["Mapping"] = {"Aucun": ["."],
                                                    "Oui":["Oui"],
                                                       "Non":["Non", "Ne sait pas/Ne répond pas"]}

        self.Mapping["Piscine_Chauffee"] = {}
        self.Mapping["Piscine_Chauffee"]["ColSrc"] = "QG7"
        self.Mapping["Piscine_Chauffee"]["typeMapping"] = "list"
        self.Mapping["Piscine_Chauffee"]["Mapping"] = {"Aucun": ["."],
                                                       "Oui":["Oui"],
                                                       "Non":["Non", "Ne sait pas/Ne répond pas"]}
        
        self.Mapping["Piscine_ChaufType"] = {}
        self.Mapping["Piscine_ChaufType"]["ColSrc"] = "QG8M1"
        self.Mapping["Piscine_ChaufType"]["typeMapping"] = "list"
        self.Mapping["Piscine_ChaufType"]["Mapping"] = {"Aucun":["."],
                                                       "Ne sait pas":["Ne sait pas/Ne répond pas"],
                                                       "Thermopompe": ["Une thermopompe de piscine"],
                                                       "Electrique": ["Un chauffe-piscine électrique (qui n’est pas une thermopompe)"],
                                                       "Capteur Solaire": ["Un capteur solaire"],
                                                       "Propane": ["Un chauffe-piscine au propane"],
                                                        "Gaz Naturel": ["Un chauffe-piscine au gaz naturel"],
                                                        "Bois": ["Un chauffe-piscine au bois"],
                                                        "Mazout": ["Un chauffe-piscine à l’huile/mazout"]}
    
        #Nombre de VE et Hybride en 1 variable
        self.Mapping["Vehicule_Presence"] = {}
        self.Mapping["Vehicule_Presence"]["ColSrc"] = "QT2T3" # seulement pour la méthode get_Mettadata
        self.Mapping["Vehicule_Presence"]["typeMapping"] = "custom"
        self.Mapping["Vehicule_Presence"]["Mapping"] = {"Aucune_VE_Aucune_VHR": None,
                                                 "Une_VE_Aucune_VHR":None,
                                                 "Aucune_VE_Une_VHR":None,
                                                "Deux_VE_Aucune_VHR":None,
                                                "Une_VE_Une_VHR":None,
                                                "Deux_VE_Une_VHR":None,
                                                "Trois_VE_Aucune_VHR":None,
                                                "Deux_VE_Deux_VHR":None,
                                                "Aucune_VE_Deux_VHR":None,
                                                    }
        
        self.Mapping["Vehicule_BornePresence"] = {}
        self.Mapping["Vehicule_BornePresence"]["ColSrc"] = "QT4"
        self.Mapping["Vehicule_BornePresence"]["typeMapping"] = "list"
        self.Mapping["Vehicule_BornePresence"]["Mapping"] = {"Aucun": ["."],
                                                       "Oui":["Oui"],
                                                       "Non":["Non", "Ne sait pas/Ne répond pas"]}
        

        # Chauffe eau
        self.Mapping["ChaufEau_Presence"] = {}
        self.Mapping["ChaufEau_Presence"]["ColSrc"] = "QF2R"
        self.Mapping["ChaufEau_Presence"]["typeMapping"] = "list"
        self.Mapping["ChaufEau_Presence"]["Mapping"] = {"Aucun":["Pas de chauffe-eau"],
                                                       "Logement":["Uniquement pour la résidence", "NSP/NRP"],
                                                       "Central": ["Central, soit pour plusieurs logements"]}

                # Chauffe eau
        self.Mapping["ChaufEau_ChaufType"] = {}
        self.Mapping["ChaufEau_ChaufType"]["ColSrc"] = "QF1"
        self.Mapping["ChaufEau_ChaufType"]["typeMapping"] = "list"
        self.Mapping["ChaufEau_ChaufType"]["Mapping"] = {"Aucun":["Pas de chauffe-eau"],
                                                       "Ne sait pas":["Ne sait pas/Ne répond pas"],
                                                       "Electrique": ["À l'électricité"],
                                                        "Propane": ["Au propane"],
                                                        "Gaz Naturel": ["Au gaz naturel"],
                                                        "Bois": ["Au bois"],
                                                        "Mazout": ["À l'huile/au mazout"]}
        # Chauffe eau
        self.Mapping["ChaufEau_Type"] = {}
        self.Mapping["ChaufEau_Type"]["ColSrc"] = "QF3"
        self.Mapping["ChaufEau_Type"]["typeMapping"] = "list"
        self.Mapping["ChaufEau_Type"]["Mapping"] = {"Non definit":["."],
                                                       "Ne sait pas":["Ne sait pas/Ne répond pas"],
                                                       "Chauffe-eau sans réservoir": ["Chauffe-eau sans réservoir"],
                                                       "Moins de 22 gallons": ["Moins de 22 gallons (97 litres)"],
                                                       "22 gallons" : ["22 gallons (97 litres)"],
                                                       "23-40 gallons": ["Entre 23 et 39 gallons (100 et 172 litres)"],
                                                       "40 gallons": ["40 gallons (176 litres)"],
                                                       "41-59 gallons": ["41 à 59 gallons (180 à 260 litres)"],
                                                       "60 gallons": ["60 gallons (264 litres)"],
                                                       "60 et plus gallons": ["Plus de 60 gallons (264 litres)"]}

        # QB2M2R : Nombre de congélateurs distinct dans la résidence
        self.Mapping["Congelateur_Nombre"] = {}
        self.Mapping["Congelateur_Nombre"]["ColSrc"] = "QB2M2R"
        self.Mapping["Congelateur_Nombre"]["typeMapping"] = "list"
        self.Mapping["Congelateur_Nombre"]["Mapping"] = {"Aucun":["Aucun", "NSP/NRP"],
                                                       "1":[1],
                                                       "2": [2],
                                                       "3": [3],
                                                       "4": [4],
                                                       "5": [5],
                                                       "6": [6]}

        # QB2I1 : Nombre de réfrigérateurs dans la résidence
        self.Mapping["Refrigerateur_Nombre"] = {}
        self.Mapping["Refrigerateur_Nombre"]["ColSrc"] = "QB2I1"
        self.Mapping["Refrigerateur_Nombre"]["typeMapping"] = "list"
        self.Mapping["Refrigerateur_Nombre"]["Mapping"] = {"Aucun":["Aucun", "NSP/NRP"],
                                                         "1":[1],
                                                         "2": [2],
                                                         "3": [3],
                                                         "4 et plus": [4,5,6,7]}

        #QB1I : Presence machine a laver
        self.Mapping["LaveLinge_Type"] = {}
        self.Mapping["LaveLinge_Type"]["ColSrc"] = "QB1I1R"
        self.Mapping["LaveLinge_Type"]["typeMapping"] = "list"
        self.Mapping["LaveLinge_Type"]["Mapping"] = {"Aucun":["N'a pas de machine à laver le linge", "NSP/NRP"],
                                                      "Frontale":["Machine à chargement frontal"],
                                                      "Traditionnelle": ["Machine traditionnelle"]}

        #QB1H : Type de machines à laver (Base totale)
        self.Mapping["SecheLinge_Presence"] = {}
        self.Mapping["SecheLinge_Presence"]["ColSrc"] = "QB1H"
        self.Mapping["SecheLinge_Presence"]["typeMapping"] = "list"
        self.Mapping["SecheLinge_Presence"]["Mapping"] = {"Oui":["Oui"],
                                                            "Non":["Non", "Ne sait pas/Ne répond pas"]}

        #QB1G : Type de lave-vaisselle (Base totale)
        self.Mapping["LaveVaisselle_Presence"] = {}
        self.Mapping["LaveVaisselle_Presence"]["ColSrc"] = "QB1G"
        self.Mapping["LaveVaisselle_Presence"]["typeMapping"] = "list"
        self.Mapping["LaveVaisselle_Presence"]["Mapping"] = {"Oui":["Oui"],
                                                            "Non":["Non"]}
        
        #QB1A1 : Présence de cuisinières (Oui/Non)
        self.Mapping["Cuisiniere_Presence"] = {}
        self.Mapping["Cuisiniere_Presence"]["ColSrc"] = "QB1A1"
        self.Mapping["Cuisiniere_Presence"]["typeMapping"] = "list"
        self.Mapping["Cuisiniere_Presence"]["Mapping"] = {"Oui":["Oui"],
                                                            "Non":["Non", "Ne sait pas/Ne répond pas"]}
        #QB1A3 : Source d'énergie de la cuisinière
        self.Mapping["Cuisiniere_Energie"] = {}
        self.Mapping["Cuisiniere_Energie"]["ColSrc"] = "QB1A3"
        self.Mapping["Cuisiniere_Energie"]["typeMapping"] = "list"
        self.Mapping["Cuisiniere_Energie"]["Mapping"] = {"Aucun":["."],
                                                        "Ne sait pas":["Ne sait pas/Ne répond pas"],
                                                        "Electrique": ["Électricité"],
                                                        "Gaz": ["Gaz propane ou gaz naturel"],
                                                        "Autre": ["Autre"]}        

        #QB2X8R : % d'éclairage à LED
        self.Mapping["Eclairage_LED"] = {}
        self.Mapping["Eclairage_LED"]["ColSrc"] = "QB2X8R"
        self.Mapping["Eclairage_LED"]["typeMapping"] = "list"
        self.Mapping["Eclairage_LED"]["Mapping"] = {"Ne sait pas":["Ne sait pas"],
                                                    "0%": [0],
                                                    "1 à 24 %": ["1 à 24 %"],
                                                    "25 à 50 %":["25 à 50 %"],
                                                    "Plus de 50 %":["Plus de 50 %"]}

        #_____________________________________________________
        # Mapping pour la pondération
        # NE PAS UTILISER LES CLEFS self.Mapping - sinon revoir la ligne {**self.Mapping, **self.Pond_Mapping}
        self.Pond_Mapping = {}
        
        #Vintage
        self.Pond_Mapping["Vintage"] = {}
        self.Pond_Mapping["Vintage"]["ColSrc"] = "QA6M" # seulement pour la méthode get_Mettadata
        self.Pond_Mapping["Vintage"]["typeMapping"] = "custom"
        self.Pond_Mapping["Vintage"]["Mapping"] = {"1946-70":None,
                                                    "1986-2012": None,
                                                    "pre-1945": None,
                                                    "1971-85": None,
                                                    "post-2012": None}

        self.Pond_Mapping["Territoire"] = {}
        self.Pond_Mapping["Territoire"]["ColSrc"] = "TERR_HQ" # seulement pour la méthode get_Mettadata
        self.Pond_Mapping["Territoire"]["typeMapping"] = "list"
        self.Pond_Mapping["Territoire"]["Mapping"] = {"0_Montreal": ["Montréal"],
                                                        "1_Laurentides": ["Laurentides"],
                                                        "2_Montmorency": ["Montmorency"],
                                                        "3_Nord-Est": ["Est et nord du Québec"],
                                                        "4_Richelieu": ["Richelieu"]}
        
        self.Pond_Mapping["Typo"] = {}
        self.Pond_Mapping["Typo"]["ColSrc"] = "Type_Logement" # seulement pour la méthode get_Mettadata
        self.Pond_Mapping["Typo"]["typeMapping"] = "list"
        self.Pond_Mapping["Typo"]["Mapping"] = {"individuelle" :["Maison individuelle"],
                                    "en rangee": ["Maison en rangee"], 
                                     "duplex": ["Duplex"],
                                     "triplex": ["Triplex"],
                                     "immeuble": ["Collective"]}

        self.Pond_Mapping["Source"] = {}
        self.Pond_Mapping["Source"]["ColSrc"] = "QC1R" # seulement pour la méthode get_Mettadata
        self.Pond_Mapping["Source"]["typeMapping"] = "list"
        self.Pond_Mapping["Source"]["Mapping"] = {"elec": ["Électricité"],
                                        "combustible": ["Gaz naturel", "Mazout", "Bois seul ou en combinaison"],
                                        "bi-energie": ["Bi-énergie"]}

        #______________________________________________________
        # QB1A1 : Présence de cuisinières (Oui/Non)
        # QB1A3 : Source d'énergie de la cuisinière
        # Faire 1 Variable : 1 = Non ; 2+=Oui+source

        # QB1F : Présence de micro-ondes (Oui/Non)

        # QB1G : Présence de lave-vaisselle (Oui/Non)

        # QB1H : Présence de sécheuse à linge électrique (Oui/Non)

        # QB1I : Présence de machine à laver le linge (Oui/Non)
        # QB1I1 : S'agit-il d'une machine à chargement frontal (Oui/Non)
        #   Faire 2 variable : Non ; Oui Frontale ; Oui Autre

        # QB1S : Présence de cellier avec système de réfrigération (Oui/Non)
    
        # QB1N : Présence de sauna (Oui/Non)

        # QB2 : Nombre de téléviseurs dans la résidence

        # B2C2R : Nombre d'ordinateur total

        # QB2X6 : Présence d'éclairage à LED (Oui/Non)
        # QB2X8R : Pourcentage d'éclairage à LED (Base possède de l'éclairage à LED)
        # Faire 2 variable : 1 = Non ; 2+=Oui+pourcentage

        #chauffage

        #chauffageappoint

        #thermostat setback


        #clim  (non, oui+system)

        # QD7F1 : Utilisez-vous un échangeur d'air?
        # QD7G1 : S'agit-il d'un échangeur d'air avec ou sans récupérateur de chaleur?
        # Faire une variable

        ## QF1 : À quelle source d'énergie votre chauffe-eau fonctionne-t-il?
        ## a voir si pertinent # # QF3 : Quelle est la capacité du chauffe-eau?

    def get_Mapping_Colsrc(self, colName):
        if colName in Attributs_EUEMr.__dict__.keys():
            return colName
        elif colName in self.Mapping.keys():
            return self.get_Mapping_Colsrc(self.Mapping[colName]["ColSrc"])#recursif

    def get_Mettadata(self):
        Metadata = {}
        for keyMap, dictMap in self.Mapping.items():
            try:
                ColSrc = self.get_Mapping_Colsrc(dictMap["ColSrc"])
                if dictMap["typeMapping"] == "list":
                    Metadata[keyMap] = {"Label": list(dictMap["Mapping"].keys()),
                                        "IdLabel": [str(i) for i in range(len(dictMap["Mapping"]))],
                                        "Description": Attributs_EUEMr.__dict__[ColSrc]["Description"],
                                        "Type": "discrete"}
                elif dictMap["typeMapping"] == "bin":
                    Metadata[keyMap] = {"Label": dictMap["Mapping"]["labels"],
                                        "IdLabel": [str(i) for i in range(len(dictMap["Mapping"]["labels"]))],
                                        "Description": Attributs_EUEMr.__dict__[ColSrc]["Description"],
                                        "Type": "discrete"}
                elif dictMap["typeMapping"] == "custom":
                    Metadata[keyMap] = {"Label": dictMap["Mapping"].keys(),
                                        "IdLabel": [str(i) for i in range(len(dictMap["Mapping"]))],
                                        "Description": Attributs_EUEMr.__dict__[ColSrc]["Description"],
                                        "Type": "discrete"}
                elif dictMap["typeMapping"] == "no":
                    Metadata[keyMap] = {"Label": [],
                                        "IdLabel": [],
                                        "Description": Attributs_EUEMr.__dict__[ColSrc]["Description"],
                                        "Type": ""}
            except KeyError as e:
                print(f"Error processing mapping for key: {keyMap} : {e}")
                
            #Metadata[keyMap] = {"Label": list(dictMap["Mapping"].keys()),
            #                    "IdLabel": [str(i) for i in range(len(dictMap["Mapping"]))],
            #                    "Description": Attributs_EUEMr.__dict__[dictMap["ColSrc"]]["Description"],
            #                   "Type": "discrete"}
        return Metadata

    def Load_excel(self, stFileName, sheet_name=None):
        self.dfEUEMrSrc = pd.read_excel(stFileName, sheet_name=sheet_name)
        
        for col in ["POND1", "POND2x", "POND1_POP", "POND2x_POP", "CONS_AN", "QA6M", 
                "LIVRE_202012_202111", "LIVRE_202012", "LIVRE_202101", "LIVRE_202102",
                "LIVRE_202103", "LIVRE_202104", "LIVRE_202105", "LIVRE_202106", "LIVRE_202107", "LIVRE_202108", "LIVRE_202109", "LIVRE_202110", "LIVRE_202111"]:
            self.dfEUEMrSrc[col] = pd.to_numeric(self.dfEUEMrSrc[col], errors='coerce')  # Convert to numeric, coercing errors to NaN

    def SaveToCSV(self, dfEUEMr, stFileName):
        """ Sauvegarde le DataFrame formaté en CSV.
        """
        dfEUEMr.to_csv(stFileName, index=False)
        print(f"DataFrame saved to {stFileName}.")

    def DoMapping(self, ColName):
        """
        Retourne le mapping pour la colonne donnée.
        """
        try:
            dct_map_concat = {**self.Mapping, **self.Pond_Mapping}
            if ColName in dct_map_concat:
                if dct_map_concat[ColName]["ColSrc"] in self.dfEUEMrSrc.columns:
                    dfEUEMrSrc_ColName = self.dfEUEMrSrc
                elif dct_map_concat[ColName]["ColSrc"] in  self.dfEUEMr_new.columns:
                    dfEUEMrSrc_ColName = self.dfEUEMr_new
                else:
                    raise ValueError(f"Unknown mapping source for column '{ColName}'.")
                
                if dct_map_concat[ColName]["typeMapping"] == "no":
                    return dfEUEMrSrc_ColName[dct_map_concat[ColName]["ColSrc"]].rename(ColName)
                
                elif dct_map_concat[ColName]["typeMapping"] == "list":
                    dct_replace = {}
                    for k, v in dct_map_concat[ColName]["Mapping"].items():
                        for val in v:
                            dct_replace[val] = k
                    tempoSeries = dfEUEMrSrc_ColName[dct_map_concat[ColName]["ColSrc"]].replace(dct_replace).rename(ColName)
                    tempoSeries[~tempoSeries.isin(list(set(dct_replace.values())))] = None
                    return tempoSeries

                elif dct_map_concat[ColName]["typeMapping"] == "bin":

                    return pd.cut(dfEUEMrSrc_ColName[dct_map_concat[ColName]["ColSrc"]],
                                bins=dct_map_concat[ColName]["Mapping"]["bins"],
                                labels=dct_map_concat[ColName]["Mapping"]["labels"],
                                right=False).rename(ColName)             
                
                elif dct_map_concat[ColName]["typeMapping"] == "custom":#type de Mapping (plus complexe)
                    if ColName == "Presence_Garage":
                        return dfEUEMrSrc_ColName.apply(lambda row: "Pas de Garage" if row["QM1A"] in ["Non", "."]\
                                                                 else ("Garage non chauffé" if row["QM1AA"]=="Non" \
                                                                 else ("Garage chauffé à électricité" if row["QM1B"]=="Oui"\
                                                                 else ("Garage chauffé à autre source" if row["QM1A"]=="Oui" else ""))), axis=1).rename(ColName)
                    
                    elif ColName == "Chauffage_Logement":
                        return dfEUEMrSrc_ColName.apply(lambda row: "Plinthes électriques" if row["SYSTEM1R"] in ["Plinthes électriques"]\
                                                                else ("Fournaise ou poêle à bois et Plinthes électriques" if (((row["SYSTEM1R"] in ["Fournaise ou poêle à bois"]) or (row["SYSTEM1"] in ["Chaudière à eau chaude chauffée au bois"])) and (row["SYSTEM2R"] in ["Plinthes électriques"]))\
                                                                else ("Fournaise ou poêle à bois et Unités convecteurs, plancher ou plafond radiant" if (((row["SYSTEM1R"] in ["Fournaise ou poêle à bois"])or (row["SYSTEM1"] in ["Chaudière à eau chaude chauffée au bois"])) and (row["SYSTEM2R"] in ["Unités convecteurs, plancher ou plafond radiant"]))\
                                                                else ("Fournaise ou poêle à bois et Thermopompe murale" if (((row["SYSTEM1R"] in ["Fournaise ou poêle à bois"]) or (row["SYSTEM1"] in ["Chaudière à eau chaude chauffée au bois", "Foyer"])) and (row["SYSTEM2R"] in ["Thermopompe"]))\
                                                                else ("Fournaise ou poêle à bois et Système central à air chaud" if (((row["SYSTEM1R"] in ["Fournaise ou poêle à bois"]) or (row["SYSTEM1"] in ["Chaudière à eau chaude chauffée au bois"])) and (row["SYSTEM2R"] in ["Système central à air chaud"]))\
                                                                else ("Fournaise ou poêle à bois et Système central à eau chaude" if (((row["SYSTEM1R"] in ["Fournaise ou poêle à bois"]) or (row["SYSTEM1"] in ["Chaudière à eau chaude chauffée au bois"])) and (row["SYSTEM2R"] in ["Système central à eau chaude"]))\
                                                                else ("Fournaise ou poêle à bois et Fournaise murale ou de plancher" if (((row["SYSTEM1R"] in ["Fournaise ou poêle à bois"]) or (row["SYSTEM1"] in ["Chaudière à eau chaude chauffée au bois"])) and (row["SYSTEM2R"] in ["Fournaise murale ou de plancher"]))\
                                                                else ("Fournaise ou poêle à bois" if ((row["SYSTEM1R"] in ["Fournaise ou poêle à bois"]) or (row["SYSTEM1"] in ["Chaudière à eau chaude chauffée au bois"]))\
                                                                else ("Unités convecteurs, plancher ou plafond radiant" if row["SYSTEM1R"] in ["Unités convecteurs, plancher ou plafond radiant"]\
                                                                else ("Thermopompe et Système central à air chaud" if row["SYSTEM1"] in ["Thermopompe (pompe à chaleur) et fournaise"]\
                                                                else ("Thermopompe et Système central à eau chaude" if row["SYSTEM1"] in ["Thermopompe et chaudière"]\
                                                                else ("Thermopompe géothermique seule" if ((row["SYSTEM1"] in ["Thermopompe géothermique"]) and (row["QC9A"] in ["Pas de système de relève"]))\
                                                                else ("Thermopompe géothermique et Plinthes électriques" if ((row["SYSTEM1"] in ["Thermopompe géothermique"]) and (row["QC9A"] in ["Ne sait pas/Ne répond pas", "Convecteurs", "Plinthes", "Plinthes et convecteurs", "Radiants de plancher"]))\
                                                                else ("Thermopompe géothermique et Fournaise" if ((row["SYSTEM1"] in ["Thermopompe géothermique"]) and (row["QC9A"] in ["Bouilloire électrique", "Fournaise au gaz naturel à air chaud", "Fournaise au mazout à air chaud","Fournaise au propane à air chaud", "Fournaise électrique à air chaud"]))\
                                                                else ("Thermopompe murale" if ((row["SYSTEM1"] in ["Thermopompe (pompe à chaleur) murale"]) and (row["QC9A"] in ["Pas de système de relève"]))\
                                                                else ("Thermopompe murale et Plinthes électriques" if ((row["SYSTEM1"] in ["Thermopompe (pompe à chaleur) murale"]) and (row["QC9A"] in ["Ne sait pas/Ne répond pas", "Convecteurs", "Plinthes", "Plinthes et convecteurs", "Radiants de plancher"]))\
                                                                else ("Thermopompe murale et Fournaise" if ((row["SYSTEM1"] in ["Thermopompe (pompe à chaleur) murale"]) and (row["QC9A"] in ["Bouilloire électrique", "Fournaise au gaz naturel à air chaud", "Fournaise au mazout à air chaud","Fournaise au propane à air chaud", "Fournaise électrique à air chaud"]))\
                                                                else ("Système central à air chaud" if row["SYSTEM1R"] in ["Système central à air chaud"]\
                                                                else ("Système central à eau chaude" if row["SYSTEM1R"] in ["Système central à eau chaude"]\
                                                                else ("Fournaise murale ou de plancher" if row["SYSTEM1R"] in ["Fournaise murale ou de plancher"]\
                                                                else None))))))))))))))))))), axis=1).rename(ColName)
                    elif ColName == "Spa_Saison":
                        return dfEUEMrSrc_ColName.apply(lambda row: "Aucun" if row["QB1M"] in ["Non"]\
                                                                else ("Pas utilisé" if row["QS1"] in ["Pas du tout"]\
                                                                else ("Ne sait pas" if row["QS2M1R"] in ["Ne sait pas"]\
                                                                else ("Toute_Saison" if row["QS1"] in ["Toute l’année"]\
                                                                else ("Printemps" if sorted([row["QS2M1R"], row["QS2M2R"], row["QS2M3R"], row["QS2M4R"]])== sorted(["Le printemps",".",".", "."])\
                                                                else ("Ete" if sorted([row["QS2M1R"], row["QS2M2R"], row["QS2M3R"], row["QS2M4R"]])== sorted(["L'été",".",".", "."])\
                                                                else ("Automne" if sorted([row["QS2M1R"], row["QS2M2R"], row["QS2M3R"], row["QS2M4R"]])== sorted(["L'automne",".",".", "."])\
                                                                else ("Hiver" if sorted([row["QS2M1R"], row["QS2M2R"], row["QS2M3R"], row["QS2M4R"]])== sorted(["L'hiver",".",".", "."])\
                                                                else ("Printemps_Ete" if sorted([row["QS2M1R"], row["QS2M2R"], row["QS2M3R"], row["QS2M4R"]])== sorted(["Le printemps","L'été",".", "."])\
                                                                else ("Printemps_Automne" if sorted([row["QS2M1R"], row["QS2M2R"], row["QS2M3R"], row["QS2M4R"]])== sorted(["Le printemps","L'automne",".", "."])\
                                                                else ("Printemps_Hiver" if sorted([row["QS2M1R"], row["QS2M2R"], row["QS2M3R"], row["QS2M4R"]])== sorted(["Le printemps","L'hiver",".", "."])\
                                                                else ("Ete_Automne" if sorted([row["QS2M1R"], row["QS2M2R"], row["QS2M3R"], row["QS2M4R"]])== sorted(["L'été","L'automne",".", "."])\
                                                                else ("Ete_Hiver" if sorted([row["QS2M1R"], row["QS2M2R"], row["QS2M3R"], row["QS2M4R"]])== sorted(["L'été","L'hiver",".", "."])\
                                                                else ("Automne_Hiver" if sorted([row["QS2M1R"], row["QS2M2R"], row["QS2M3R"], row["QS2M4R"]])== sorted(["L'automne","L'hiver",".", "."])\
                                                                else ("Printemps_Ete_Automne" if sorted([row["QS2M1R"], row["QS2M2R"], row["QS2M3R"], row["QS2M4R"]])== sorted(["Le printemps","L'été","L'automne", "."])\
                                                                else ("Printemps_Automne_Hiver" if sorted([row["QS2M1R"], row["QS2M2R"], row["QS2M3R"], row["QS2M4R"]])== sorted(["Le printemps","L'automne","L'hiver", "."])\
                                                                else ("Ete_Automne_Hiver" if sorted([row["QS2M1R"], row["QS2M2R"], row["QS2M3R"], row["QS2M4R"]])== sorted(["L'été","L'automne","L'hiver", "."])\
                                                                else None)))))))))))))))), axis=1).rename(ColName)

                    elif ColName == "Vehicule_Presence":
                        return dfEUEMrSrc_ColName.apply(lambda row: "Aucune_VE_Aucune_VHR" if ((row["QT2R"] in ["Aucune"]) and (row["QT3R"] in ["Aucune"]))\
                                                                else ("Une_VE_Aucune_VHR" if ((row["QT2R"] in ["Une"]) and (row["QT3R"] in ["Aucune"]))\
                                                                else ("Deux_VE_Aucune_VHR" if ((row["QT2R"] in ["Deux"]) and (row["QT3R"] in ["Aucune"]))\
                                                                else ("Trois_VE_Aucune_VHR" if ((row["QT2R"] in ["Trois"]) and (row["QT3R"] in ["Aucune"]))\
                                                                else ("Aucune_VE_Une_VHR" if ((row["QT2R"] in ["Aucune"]) and (row["QT3R"] in ["Une"]))\
                                                                else ("Une_VE_Une_VHR" if ((row["QT2R"] in ["Une"]) and (row["QT3R"] in ["Une"]))\
                                                                else ("Deux_VE_Une_VHR" if ((row["QT2R"] in ["Deux"]) and (row["QT3R"] in ["Une"]))\
                                                                else ("Trois_VE_Une_VHR" if ((row["QT2R"] in ["Trois"]) and (row["QT3R"] in ["Une"]))\
                                                                else ("Aucune_VE_Deux_VHR" if ((row["QT2R"] in ["Aucune"]) and (row["QT3R"] in ["Deux"]))\
                                                                else ("Une_VE_Deux_VHR" if ((row["QT2R"] in ["Une"]) and (row["QT3R"] in ["Deux"]))\
                                                                else ("Deux_VE_Deux_VHR" if ((row["QT2R"] in ["Deux"]) and (row["QT3R"] in ["Deux"]))\
                                                                else ("Trois_VE_Deux_VHR" if ((row["QT2R"] in ["Trois"]) and (row["QT3R"] in ["Deux"]))\
                                                                else None))))))))))), axis=1).rename(ColName)
                    elif ColName == "Region_Administrative":
                        return dfEUEMrSrc_ColName.apply(lambda row: "Outaouais" if ((row["ZONE"] in ["Outaouais rural", "CUO"]))\
                                                                else("Laurentides" if ((row["ZONE"] in ["Milles-Îles", "Antoine-Labelle", "Le Noroit"]))\
                                                                else("Montréal" if ((row["ZONE"] in ["IDM Est", "IDM Nord", "IDM Ouest", "IDM Sud"]))\
                                                                else("Capitale-Nationale" if ((row["ZONE"] in ["CUQ", "Montmorency-nord", "Appalaches"]))\
                                                                else("Mauricie" if ((row["ZONE"] in ["St-Maurice"]))\
                                                                else("Côte-Nord" if ((row["ZONE"] in ["Côte-Nord"]))\
                                                                else("Chaudière-Appalaches" if ((row["ZONE"] in ["Lévis", "Appalaches"]))\
                                                                else("Montérégie" if ((row["ZONE"] in ["Chateauguay-Vaudreuil", "Le Haut St-Laurent", "Des Seigneuries", "Drummonville", "Ozias-Leduc"]) or ((row["ZONE"] in ["Sorel-Victoriaville"]) and (row["MONTREAL_RMR"] in ["Montréal RMR"])))\
                                                                else("Estrie" if ((row["ZONE"] in ["Des Cantons"]))\
                                                                else("Centre-du-Québec" if ((row["ZONE"] in ["Drummonville"]) or ((row["ZONE"] in ["Sorel-Victoriaville"]) and (row["MONTREAL_RMR"] in ["Pas Montréal RMR"])))\
                                                                else("Laval" if ((row["ZONE"] in ["Laval"]))\
                                                                else("Lanaudière" if ((row["ZONE"] in ["Lanaudière"]))\
                                                                else("Saguenay-Lac-Saint-Jean" if ((row["ZONE"] in ["Saguenay"]))\
                                                                else("Bas-Saint-Laurent" if ((row["ZONE"] in ["Bas St-Laurent"]))\
                                                                else("Gaspésie-Îles-de-la-Madeleine" if ((row["ZONE"] in ["Gaspésie"]))\
                                                                else None)))))))))))))), axis=1).rename(ColName)
                    
                    elif ColName == "Vintage":
                        return dfEUEMrSrc_ColName.apply(lambda row: "pre-1945" if row["QA6M"] in [i for i in range(1500, 1945+1)]\
                                                                else ("pre-1945" if ((row["QA6RR"] in ["Avant 1900", "Entre 1900 et 1950"]) and (pd.isnull(row["QA6M"])))\
                                                                else ("1946-70" if row["QA6M"] in [i for i in range(1946, 1970+1)]\
                                                                else ("1946-70" if ((row["QA6RR"] in ["Dans les années 50", "Dans les années 60"]) and (pd.isnull(row["QA6M"])))\
                                                                else ("1971-85" if row["QA6M"] in [i for i in range(1971, 1985+1)]\
                                                                else ("1971-85" if ((row["QA6RR"] in ["Dans les années 70", "Dans les années 80"]) and (pd.isnull(row["QA6M"])))\
                                                                else ("1986-2012" if row["QA6M"] in [i for i in range(1986, 2012+1)]\
                                                                else ("1986-2012" if ((row["QA6RR"] in ["Dans les années 90", "Entre 2000 et 2009", "Entre 2010 et 2013"]) and (pd.isnull(row["QA6M"])))\
                                                                else ("post-2012" if row["QA6M"] in [i for i in range(2013, 2050+1)]\
                                                                else ("post-2012" if ((row["QA6RR"] in ["Entre 2014 et 2017", "Entre 2018 et aujourd'hui"]) and (pd.isnull(row["QA6M"])))\
                                                                else None))))))))), axis=1).rename(ColName)
                else:
                    raise ValueError(f"Unknown mapping type for column '{ColName}'.")
            else:
                raise ValueError(f"Mapping for column '{ColName}' not found.")
        except Exception as e:
            print(f"Error in DoMapping for column '{ColName}': {e}")

    def DoAllMapping(self):
        """
        Applique tous les mappings définis dans la classe.
        """
        self.dfEUEMr_new = pd.DataFrame()
        for c in ["POND1","POND2x","POND1_POP","POND2x_POP"]:
            self.dfEUEMr_new[c] = self.dfEUEMrSrc[c]

        for ColName in {**self.Mapping, **self.Pond_Mapping}:
            self.dfEUEMr_new = pd.concat([self.dfEUEMr_new, self.DoMapping(ColName)], axis=1)
        
        return self.dfEUEMr_new

    def Create_Pond(self, df_toPond_src):
        
        df_toPond = df_toPond_src[~pd.isnull(df_toPond_src["POND1"])]
        
        dataStats = pd.read_csv(str(Path(__file__).parents[3] / "data/input/euemr/2022/raked_data.csv"))
        dataStats["Typo"] = dataStats["Typo-Source"].str.split("_").str[0]
        dataStats["Source"] = dataStats["Typo-Source"].str.split("_").str[1]

        df_toPond_grp = df_toPond[['Vintage', 'Territoire', "Typo", "Source"]].groupby(['Vintage', 'Territoire', "Typo", "Source"]).value_counts().reset_index(name='Nombre')

        df_Pond = pd.merge(df_toPond_grp,dataStats, on=['Vintage', 'Territoire', "Typo", "Source"], how='left')
        sum_df_Pond = df_Pond['Nombre'].sum()
        df_Pond["Nombre_rel"] = df_Pond["Nombre"]/sum_df_Pond
        df_Pond["PONDNew"] = df_Pond["count_pound_rel"]/df_Pond["Nombre_rel"]
        
        df_toPond_weight = df_toPond_src.merge(df_Pond[["Vintage","Territoire","Typo","Source", "PONDNew"]], on=['Vintage', 'Territoire', "Typo", "Source"], how='left')#["Weighted"].sum()
        df_toPond_weight.loc[pd.isnull(df_toPond_weight["POND1"]), "PONDNew"] = None#ne s'applique pas sur le sous-groupe des logements récents
        df_toPond_weight.insert(0, "PONDNew", df_toPond_weight.pop("PONDNew"))

        return df_toPond_weight

    def Main(self):
        """
        Fonction principale pour exécuter le formatage des données EUEMr.
        """
        stFileName = str(Path(__file__).parents[3] / "data/input/euemr/2022/sondage_residentiel_version_finale.xlsx")
        sheet_name = "Data"

        self.Load_excel(stFileName, sheet_name)
        #dfEUEMr_new = self.DoAllMapping()
        self.DoAllMapping()

        #add new ponderation column
        self.dfEUEMr_new = self.Create_Pond(self.dfEUEMr_new)

        output_file = str(Path(__file__).parents[3] / "data/processed/euemr/2022/sondage_residentiel_version_finale_formatted.csv")
        self.SaveToCSV(self.dfEUEMr_new, output_file)

if __name__ == "__main__":
    euemr = EUEMR_formatage()
    euemr.Main()
