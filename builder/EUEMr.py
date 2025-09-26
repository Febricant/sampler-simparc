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
import time
import pickle
import numpy as np
import pandas as pd
import random
from datetime import datetime
from datetime import timedelta
import matplotlib.pyplot as plt
from utils.Master_genereBN import Master_genereBN

import pyagrum as gum

#import json

import warnings
warnings.filterwarnings('ignore', category=UserWarning, module='openpyxl')

FILE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(FILE_DIR+ "/../")  # répertoire supérieur
#PACKAGE_DIR = os.path.abspath(PROJECT_DIR+ "/../")
#sys.path.append(os.path.join(PACKAGE_DIR))


class Attribut_EUEMr(object):

    # Attributs de l'enquête EUEMr

    # QA1 : Quel est votre lien avec ce logement ? En êtes-vous...
    QA1 = {}
    QA1["Label"] = ["Le propriétaire / Co-propriétaire",
                     "Le locataire / Co-locataire"]
    QA1["IdLabel"] = ["0", "1"]
    QA1["Description"] = "Quel est votre lien avec ce logement ? En êtes-vous..."
    QA1["Type"] = "discrete"

    # QA4 : De quel genre d'habitation s'agit-il ?
    QA4 = {}
    QA4["Label"] = ['Immeuble de 4 à 8 appartements',
                    'Immeuble de 9 à 19 appartements',
                    'Immeuble de 20 à 49 appartements',
                    'Immeuble de 50 appartements ou plus',
                    'Immeuble à appartement (sans précision)', # trop peu
                    'Maison mobile/roulotte',
                    'Maison individuelle détachée/unifamiliale',
                    'Maison individuelle en rangée attachée des 2 côtés',
                    'Maison individuelle en rangée (sans précisions)', # trop peu
                    'Maison jumelée/bout de rangée attachée 1 côté/semi-détaché',
                    'Duplex détaché',
                    'Duplex en milieu de rangée attaché 2 côtés',
                    'Duplex jumelé/en bout de rangée attaché 1 seul côté',
                    'Duplex (sans précision)', # trop peu
                    'Triplex milieu de rangée attaché 2 côtés',
                    'Triplex jumelé/en bout de rangée attaché 1 seul côté',
                    'Triplex (sans précision)', # trop peu
                    'Triplex détaché']
    QA4["IdLabel"] = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13"]#, "14", "15", "16", "17"]
    QA4["Description"] = "De quel genre d'habitation s'agit-il?"
    QA4["Type"] = "discrete"

    # QC1R : Principale source d'énergie utilisée pour le chauffage du domicile
    QC1R = {}
    QC1R["Label"] = ['Électricité',
                        'Bois seul ou en combinaison',
                        'Bi-énergie',
                        'Gaz naturel',
                        'Mazout']
    QC1R["IdLabel"] = ["0", "1", "2", "3", "4"]
    QC1R["Description"] = "Principale source d'énergie utilisée pour le chauffage du domicile"
    QC1R["Type"] = "discrete"

    # CONS_AN : Consommation annuelle d'électricité en kWh
    CONS_AN = {}
    CONS_AN["Label"] = None
    CONS_AN["IdLabel"] = None
    CONS_AN["Description"] = "Consommation annuelle d'électricité en kWh"
    CONS_AN["Type"] = "Double"

    # QA6M : Année de construction de l'habitation
    QA6M = {}
    QA6M["Label"] = None
    QA6M["IdLabel"] = None
    QA6M["Description"] = "Année de construction de l'habitation"
    QA6M["Type"] = "Entier"

    # TERR_HQ : Territoire de l'habitation
    TERR_HQ = {}
    TERR_HQ["Label"] = ["Est et nord du Québec",
                        "Laurentides",
                        "Montmorency",
                        "Montréal",
                        "Richelieu"]
    TERR_HQ["IdLabel"] = ["0", "1", "2", "3", "4"]
    TERR_HQ["Description"] = "Territoire HQ"
    TERR_HQ["Type"] = "discrete"

    ZONE = {}
    ZONE["Label"] = ["Outaouais rural",
                     "Milles-Îles",
                     "IDM Est",
                     "IDM Nord",
                     "CUQ",
                     "CUO",
                     "St-Maurice",
                     "Côte-Nord",
                     "Le Noroit",
                     "IDM Ouest",
                     "Chateauguay-Vaudreuil",
                     "Des Cantons",
                     "Sorel-Victoriaville",
                     "Drummonville",
                     "Lévis",
                     "IDM Sud",
                     "Laval",
                     "Montmorency-nord",
                     "Saguenay",
                     "Le Haut St-Laurent",
                     "Bas St-Laurent",
                     "Gaspésie",
                     "Appalaches",
                     "Antoine-Labelle",
                     "Des Seigneuries",
                     "Lanaudière",
                     "Ozias-Leduc"]
    ZONE["IdLabel"] = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10",
                        "11", "12", "13", "14", "15", "16", "17", "18", "19", "20",
                          "21", "22", "23", "24", "25", "26"]
    ZONE["Description"] = "Zone du Québec"
    ZONE["Type"] = "discrete"

    # QA4R : Type d'habitation (code : Multi, Uni, Plex)
    QA4R = {}
    QA4R["Label"] = ["Uni", "Plex", "Multi"]
    QA4R["IdLabel"] = ["0", "1", "2"]
    QA4R["Description"] = "Type d'habitation"
    QA4R["Type"] = "discrete"

    # QA4M : Nombre de logements dans l'immeuble
    QA4M = {}
    QA4M["Label"] = None
    QA4M["IdLabel"] = None
    QA4M["Description"] = "Nombre de logements dans l'immeuble"
    QA4M["Type"] = "Entier"

    # QA6RR : Décennie de construction de l'habitation
    QA6RR = {}
    QA6RR["Label"] = ["Avant 1900",
                        "Entre 1900 et 1950",
                        "Dans les années 50",
                        "Dans les années 60",
                        "Dans les années 70",
                        "Dans les années 80",
                        "Dans les années 90",
                        "Entre 2000 et 2009",
                        "Entre 2010 et 2013",
                        "Entre 2014 et 2017",
                        "Entre 2018 et aujourd'hui"]
    QA6RR["IdLabel"] = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
    QA6RR["Description"] = "Décennie de construction de l'habitation"
    QA6RR["Type"] = "discrete"

    # QA2 : Résidence principale ou secondaire
    QA2 = {}
    QA2["Label"] = ["Résidence principale",
                    "Résidence secondaire"]
    QA2["IdLabel"] = ["0", "1"]
    QA2["Description"] = "est-ce votre résidence principale ou secondaire?"
    QA2["Type"] = "discrete"

    # QH1 : Nombre de pièces dans la résidence (incluant les pièces du sous-sol et le garage, excluant les salles de bain et les couloirs)
    QH1 = {}
    QH1["Label"] = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"] 
    QH1["IdLabel"] = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11"]
    QH1["Description"] = "Nombre de pièces dans la résidence (incluant les pièces du sous-sol et le garage, excluant les salles de bain et les couloirs)"
    QH1["Type"] = "discrete"

    # QH2 : Nombre d'étages habitables dans la résidence (incluant le sous-sol et le garage)
    QH2 = {}
    QH2["Label"] = ["Un étage",
                    "1½ étages",
                    "Deux étages",
                    "2 ½étages",
                    "Trois étages",
                    "3½ étages",
                    "Quatre étages",
                    "4½ étages",
                    "5 étages"]
    QH2["IdLabel"] = ["0", "1", "2", "3", "4", "5", "6", "7", "8"]
    QH2["Description"] = "Nombre d'étages habitables dans la résidence (incluant le sous-sol et le garage)"
    QH2["Type"] = "discrete"

    # ETAGE : Nombre d'étages habitables dans la résidence (incluant le sous-sol et le garage) (MÉTRIQUE)
    ETAGE = {}
    ETAGE["Label"] = ["1.0", "1.5", "2.0", "2.5", "3.0", "3.5", "4.0", "4.5", "5.0"]
    ETAGE["IdLabel"] = ["0", "1", "2", "3", "4", "5", "6", "7", "8"]
    ETAGE["Description"] = "Nombre d'étages habitables dans la résidence (incluant le sous-sol et le garage) (MÉTRIQUE)"
    ETAGE["Type"] = "discrete"

    # SUPERTOT : Superficie totale de la résidence incluant le sous-sol et le garage
    SUPERTOT = {}
    SUPERTOT["Label"] = None,
    SUPERTOT["IdLabel"] = None
    SUPERTOT["Description"] = "Quelle est la superficie TOTALE habitable de votre résidence incluant le sous-sol et le garage?"
    SUPERTOT["Type"] = "Double"

    # QH4 : Présence d'un sous-sol ou vide sanitaire dans la résidence
    QH4 = {}
    QH4["Label"] = ["Un sous-sol d'une hauteur de 6 ou 7 pied",
                    "Un vide sanitaire d'une hauteur inférieure à 6 pieds",
                    "Ne comporte ni sous-sol, ni vide sanitaire",
                    "Un sous-sol et un vide sanitaire"]
    QH4["IdLabel"] = ["0", "1", "2", "3"]
    QH4["Description"] = "Votre résidence comporte-elle un sous-sol ou vide sanitaire?"
    QH4["Type"] = "discrete"

    # QM1A : Présence d'un garage dans la résidence #Question seulement pour les propriétaire
    QM1A = {}
    QM1A["Label"] = ["Oui", "Non"]
    QM1A["IdLabel"] = ["0", "1"]
    QM1A["Description"] = "Avez-vous un garage?"
    QM1A["Type"] = "discrete"

    # QM1AA : Garage chauffé (Oui/Non)
    QM1AA = {}
    QM1AA["Label"] = ["Oui", "Non"]
    QM1AA["IdLabel"] = ["0", "1"]
    QM1AA["Description"] = "Est-ce que votre garage est chauffé?"
    QM1AA["Type"] = "discrete"

    # QM1B : Garage chauffé à l'électricité (Oui/Non)
    QM1B = {}
    QM1B["Label"] = ["Oui", "Non"]
    QM1B["IdLabel"] = ["0", "1"]
    QM1B["Description"] = "Est-ce que votre garage est chauffé à l'électricité?"
    QM1B["Type"] = "discrete"

    # QL1 : Nombre de personnes habitant le logement (incluant l'interviewé)
    QL1 = {}
    QL1["Label"] = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "15", "25"]
    QL1["IdLabel"] = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13"]
    QL1["Description"] = "En vous incluant, combien de personnes habitent ce logement?"
    QL1["Type"] = "discrete"

    # QL3A : Catégorie d'âge de l'interviewé
    QL3A = {}
    QL3A["Label"] = ["18-24 ans", "25-34 ans", "35-44 ans", "45-54 ans", "55-64 ans", "65 ans et plus"]
    QL3A["IdLabel"] = ["0", "1", "2", "3", "4", "5"]
    QL3A["Description"] = "Quel est votre âge?"
    QL3A["Type"] = "discrete"

    # QL4A : Dernier niveau de scolarité complété par l'interviewé
    QL4A = {}
    QL4A["Label"] = ["Primaire (0 à 7 ans)", "Secondaire (8 à 12 ans)", "CEGEP/techniques (13 à 15 ans)", "Université (16 ans et plus)"]
    QL4A["IdLabel"] = ["0", "1", "2", "3"]
    QL4A["Description"] = "Quel est le dernier niveau de scolarité que vous avez complété?"
    QL4A["Type"] = "discrete"

    # QL5A : Valeur approximative de la résidence incluant le terrain
    QL5A = {}
    QL5A["Label"] = ["Moins de 100  000 $",
                     "100 000 à 199 999 $", 
                     "200 000 $ à 299 999 $",
                     "300 000 $ à 399 999 $",
                     "400 000 $ à 499 999 $",
                     "500 000 $ à 599 999 $",
                     "600 000 $ à 699 999 $",
                     "700 000 $ à 799 999 $",
                     "800 000 $ à 899 999 $",
                     "900 000 $ à 999 999 $",
                     "1 million $ ou plus"]
    QL5A["IdLabel"] = ["0", "1", "2", "3", "4", "5", "6", "7", "8"]
    QL5A["Description"] = "Quelle est la valeur approximative de votre résidence incluant le terrain?"
    QL5A["Type"] = "discrete"

    # QL5BA : Revenu total du ménage (avant impôts incluant les revenus de toutes provenances et de tous les membres du ménage)
    QL5BA = {}
    QL5BA["Label"] = ["Moins de 20 000 $",
                        "20 000 $ à 39 999 $", 
                        "40 000 $ à 59 999 $",
                        "60 000 $ à 79 999 $",
                        "80 000 $ à 99 999 $",
                        "100 000 $ à 119 999 $",
                        "120 000 $ à 199 999 $",
                        "200 000 $ à 299 999 $",
                        "300 000 $ ou plus"]
    QL5BA["IdLabel"] = ["0", "1", "2", "3", "4", "5", "6", "7", "8"]
    QL5BA["Description"] = "Quel est le revenu total de votre ménage (avant impôts incluant les revenus de toutes provenances et de tous les membres du ménage)?"
    QL5BA["Type"] = "discrete"

    # QB2I1 : Nombre de réfrigérateurs dans la résidence
    QB2I1 = {}
    QB2I1["Label"] = ["0", "1", "2", "3", "4", "5",
                      "7"]
    QB2I1["IdLabel"] = ["0", "1", "2", "3", "4", "5", "6"]
    QB2I1["Description"] = "Combien de réfrigérateurs avez-vous dans votre résidence?"
    QB2I1["Type"] = "discrete"

    # QB2I2 : Âge du réfrigérateur principal
    QB2I2 = {}
    QB2I2["Label"] = ["Moins de 1 an",
                        "1 à 5 ans",
                        "6 à 10 ans",
                        "11 à 15 ans",
                        "16 à 20 ans",
                        "21 à 25 ans",
                        "Plus de 25 ans"]
    QB2I2["IdLabel"] = ["0", "1", "2", "3", "4", "5", "6"]
    QB2I2["Description"] = "Quel est l'âge de votre réfrigérateur principal?"
    QB2I2["Type"] = "discrete"

    # QBM1 : Présence de congélateurs distincts (Oui/Non)
    QBM1 = {}
    QBM1["Label"] = ["Oui", "Non"]
    QBM1["IdLabel"] = ["0", "1"]
    QBM1["Description"] = "Avez-vous un congélateur distinct de votre réfrigérateur?"
    QBM1["Type"] = "discrete"
    
    # QB2M2R : Nombre de congélateurs distinct dans la résidence
    QB2M2R = {}
    QB2M2R["Label"] = ["Aucun", "1", "2", "3", "4", "5", "6"]
    QB2M2R["IdLabel"] = ["0", "1", "2", "3", "4", "5", "6"]
    QB2M2R["Description"] = "Combien de congélateurs distincts avez-vous dans votre résidence?"
    QB2M2R["Type"] = "discrete"

    # QB1A1 : Présence de cuisinières (Oui/Non)
    QB1A1 = {}
    QB1A1["Label"] = ["Oui", "Non"]
    QB1A1["IdLabel"] = ["0", "1"]
    QB1A1["Description"] = "Avez-vous une cuisinière?"
    QB1A1["Type"] = "discrete"

    # QB1RR : Nombre d'appareils de cuisson dans la résidence
    QB1RR = {}
    QB1RR["Label"] = ["Aucun", "1", "2", "3"]
    QB1RR["IdLabel"] = ["0", "1", "2", "3"]
    QB1RR["Description"] = "Combien d'appareils de cuisson avez-vous dans votre résidence?"
    QB1RR["Type"] = "discrete"

    # QB1A3 : Source d'énergie de la cuisinière
    QB1A3 = {}
    QB1A3["Label"] = ["Électricité",
                      "Gaz propane ou gaz naturel",
                      "Autre"]
    QB1A3["IdLabel"] = ["0", "1", "2"]
    QB1A3["Description"] = "Quelle est la source d'énergie de votre cuisinière?"
    QB1A3["Type"] = "discrete"

    # QB1C1 : Présence de four encastré électrique (Oui/Non)
    QB1C1 = {}
    QB1C1["Label"] = ["Oui", "Non"]
    QB1C1["IdLabel"] = ["0", "1"]
    QB1C1["Description"] = "Possédez-vous un four encastré électrique?"
    QB1C1["Type"] = "discrete"

    # QB1D1 : Présence de plaque avec des ronds de cuisson indépendante de la cuisinière (de type Jen Air) (Oui/Non)
    QB1D1 = {}
    QB1D1["Label"] = ["Oui", "Non"]
    QB1D1["IdLabel"] = ["0", "1"]
    QB1D1["Description"] = "Avez-vous une plaque de cuisson avec des ronds de cuisson indépendante de la cuisinière (de type Jen Air)?"
    QB1D1["Type"] = "discrete"

    # QB1D2 : Source d'énergie de la plaque de cuisson
    QB1D2 = {}
    QB1D2["Label"] = ["Électricité",
                        "Gaz propane ou gaz naturel"]
    QB1D2["IdLabel"] = ["0", "1"]
    QB1D2["Description"] = "Quelle est la source d'énergie de votre plaque de cuisson?"
    QB1D2["Type"] = "discrete"

    # QB1E1 : Présence de hotte ou ventilateur de cuisine (Oui/Non)
    QB1E1 = {}
    QB1E1["Label"] = ["Oui", "Non"]
    QB1E1["IdLabel"] = ["0", "1"]
    QB1E1["Description"] = "Avez-vous une hotte ou un ventilateur de cuisine?"
    QB1E1["Type"] = "discrete"
    
    # QB1F : Présence de micro-ondes (Oui/Non)
    QB1F = {}
    QB1F["Label"] = ["Oui", "Non"]
    QB1F["IdLabel"] = ["0", "1"]
    QB1F["Description"] = "Avez-vous un micro-ondes?"
    QB1F["Type"] = "discrete"

    # QB1G : Présence de lave-vaisselle (Oui/Non)
    QB1G = {}
    QB1G["Label"] = ["Oui", "Non"]
    QB1G["IdLabel"] = ["0", "1"]
    QB1G["Description"] = "Avez-vous un lave-vaisselle?"
    QB1G["Type"] = "discrete"
    
    # QB1H : Présence de sécheuse à linge électrique (Oui/Non)
    QB1H = {}
    QB1H["Label"] = ["Oui", "Non"]
    QB1H["IdLabel"] = ["0", "1"]
    QB1H["Description"] = "Avez-vous une sécheuse à linge électrique?"
    QB1H["Type"] = "discrete"
    
    # QB1I : Présence de machine à laver le linge (Oui/Non)
    QB1I = {}
    QB1I["Label"] = ["Oui", "Non"]
    QB1I["IdLabel"] = ["0", "1"]
    QB1I["Description"] = "Avez-vous une machine à laver le linge?"
    QB1I["Type"] = "discrete"

    # QB1I1 : S'agit-il d'une machine à chargement frontal (Oui/Non)
    QB1I1 = {}
    QB1I1["Label"] = ["Oui", "Non"]
    QB1I1["IdLabel"] = ["0", "1"]
    QB1I1["Description"] = "Votre machine à laver le linge est-elle à chargement frontal?"
    QB1I1["Type"] = "discrete"

    #QB1I1R : Type de machines à laver (Base totale)
    QB1I1R = {}
    QB1I1R["Label"] = ["N'a pas de machine à laver le linge",
                       "Machine traditionnelle",
                       "Machine à chargement frontal"]
    QB1I1R["IdLabel"] = ["0", "1", "2"]
    QB1I1R["Description"] = "Quel type de machine à laver le linge avez-vous?"
    QB1I1R["Type"] = "discrete"

    # QB1S : Présence de cellier avec système de réfrigération (Oui/Non)
    QB1S = {}
    QB1S["Label"] = ["Oui", "Non"]
    QB1S["IdLabel"] = ["0", "1"]
    QB1S["Description"] = "Avez-vous un cellier avec système de réfrigération?"
    QB1S["Type"] = "discrete"

    # QB1N : Présence de sauna (Oui/Non)
    QB1N = {}
    QB1N["Label"] = ["Oui", "Non"]
    QB1N["IdLabel"] = ["0", "1"]
    QB1N["Description"] = "Avez-vous un sauna?"
    QB1N["Type"] = "discrete"

    # QB2 : Nombre de téléviseurs dans la résidence

    QB2 = {}
    QB2["Label"] = ["0", "1", "2", "3", "4", "5", "6", "7", "8",
                    "10"]
    QB2["IdLabel"] = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
    QB2["Description"] = "Combien de téléviseurs avez-vous dans votre résidence?"
    QB2["Type"] = "discrete"

    # B2A3 : Type du téléviseur principal
    B2A3 = {}
    B2A3["Label"] = ["Conventionnel",
                     "Écran 3D ACL",
                    "Écran 3D DEL",
                    "Écran 3D sans précision",
                    "Écran DEL",
                    "Écran DLP",
                    "Écran OLED",
                    "Écran plat ACL",
                    "Écran plat plasma",
                    "Écran plat sans précision (plasma /ACL)",
                    "Projecteur",
                    "Télévision 4K, 8K ou 16k (Utra HD)"]
    B2A3["IdLabel"] = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
    B2A3["Description"] = "Quel est le type de votre téléviseur principal?"
    B2A3["Type"] = "discrete"

    # B3A2R : Taille du téléviseur principal (Base possède un téléviseur) [catégorie de taille]
    B3A2R = {}
    B3A2R["Label"] = ["Moins de 30 pouces",
                        "De 30 à 45 pouces",
                        "De 46 à 65 pouces",
                        "Plus de 65 pouces"]
    B3A2R["IdLabel"] = ["0", "1", "2", "3"]
    B3A2R["Description"] = "Quelle est la taille de votre téléviseur principal?"
    B3A2R["Type"] = "discrete"

    # B2A4 : Type du 2nd téléviseur

    # QB2C1 : Présence d'ordinateur (Oui/Non)
    QB2C1 = {}
    QB2C1["Label"] = ["Oui", "Non"]
    QB2C1["IdLabel"] = ["0", "1"]
    QB2C1["Description"] = "Avez-vous un ordinateur?"
    QB2C1["Type"] = "discrete"

    # B2C2R : Nombre d'ordinateur total
    B2C2R = {}
    B2C2R["Label"] = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11"]
    B2C2R["IdLabel"] = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
    B2C2R["Description"] = "Combien d'ordinateurs avez-vous dans votre résidence?"
    B2C2R["Type"] = "discrete"

    # B2C2BR : Nombre d'ordinateur portable (Base possède un ordinateur)
    B2C2BR = {}
    B2C2BR["Label"] = ["0", "1", "2", "3", "4", "5", "6", "7", "8"]
    B2C2BR["IdLabel"] = ["0", "1", "2", "3", "4", "5", "6", "7", "8"]
    B2C2BR["Description"] = "Combien d'ordinateurs portables avez-vous dans votre résidence?"
    B2C2BR["Type"] = "discrete"

    # B2C2AR : Nombre d'ordinateur de bureau
    B2C2AR = {}
    B2C2AR["Label"] = ["0", "1", "2", "3", "4", "5", "6"]
    B2C2AR["IdLabel"] = ["0", "1", "2", "3", "4", "5", "6"]
    B2C2AR["Description"] = "Combien d'ordinateurs de bureau avez-vous dans votre résidence?"
    B2C2AR["Type"] = "discrete"

    # QB2D1 : Accès à Internet (Oui/Non)
    QB2D1 = {}
    QB2D1["Label"] = ["Oui", "Non"]
    QB2D1["IdLabel"] = ["0", "1"]
    QB2D1["Description"] = "Avez-vous accès à Internet?"
    QB2D1["Type"] = "discrete"

    # QB2D1R : Accès à internet avec un ordinateur (Oui/Non)
    QB2D1R = {}
    QB2D1R["Label"] = ["Oui", "Non"]
    QB2D1R["IdLabel"] = ["0", "1"]
    QB2D1R["Description"] = "Avez-vous accès à Internet avec un ordinateur?"
    QB2D1R["Type"] = "discrete"

    # QB2X6 : Présence d'éclairage à LED (Oui/Non)
    QB2X6 = {}
    QB2X6["Label"] = ["Oui", "Non"]
    QB2X6["IdLabel"] = ["0", "1"]
    QB2X6["Description"] = "Avez-vous de l'éclairage à DEL dans votre résidence?"
    QB2X6["Type"] = "discrete"

    # QB2X8R : Pourcentage d'éclairage à LED (Base possède de l'éclairage à LED)
    QB2X8R = {}
    QB2X8R["Label"] = ["0%",
                        "1 à 24 %",
                        "25 à 50 %",
                        "Plus de 50 %"]
    QB2X8R["IdLabel"] = ["0", "1", "2", "3"]
    QB2X8R["Description"] = "Quel pourcentage de votre éclairage est à DEL?"
    QB2X8R["Type"] = "discrete"

    # SOURC : Principale source d'énergie utilisée pour le chauffage de l'habitation - détail
    SOURC = {}
    SOURC["Label"] = ["L'électricité",
                      "Le gaz naturel",
                      "Le propane",
                      "Le mazout (huile)",
                      "Le bois (ou granule)",
                      "L'électricité et le gaz naturel",
                    "L'électricité et le propane",
                    "L'électricité et le mazout",
                    "Le bois (ou granules) ET électricité",
                    "Le bois ET mazout (huile)",
                    "Bi-énergie (sans précision)"]
    SOURC["IdLabel"] = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
    SOURC["Description"] = "Principale source d'énergie utilisée pour le chauffage de l'habitation - détail"
    SOURC["Type"] = "discrete"

    # QC1R : Principale source d'énergie utilisée pour le chauffage de l'habitation
    QC1R = {}
    QC1R["Label"] = ["Électricité",
                     "Gaz naturel",
                     "Mazout",
                     "Bois seul ou en combinaison",
                     "Bi-énergie",
                     "Autres"]
    QC1R["IdLabel"] = ["0", "1", "2", "3", "4", "5"]
    QC1R["Description"] = "Principale source d'énergie utilisée pour le chauffage de l'habitation"
    QC1R["Type"] = "discrete"

    # CENTRAL2 : Possède un système central
    CENTRAL2 = {}
    CENTRAL2["Label"] = ["Oui", "Non"]
    CENTRAL2["IdLabel"] = ["0", "1"]
    CENTRAL2["Description"] = "Possédez-vous un système central?"
    CENTRAL2["Type"] = "discrete"

    # SYSTEM1 : Système principal de chauffage - détail

    # SYSTEM1R : Système principal de chauffage
    SYSTEM1R = {}
    SYSTEM1R["Label"] = ["Plinthes électriques",
                        "Unités convecteurs, plancher ou plafond radiant",
                        "Thermopompe",
                        "Autres",
                        "Système central à air chaud",
                        "Système central à eau chaude",
                        "Fournaise ou poêle à bois",
                        "Fournaise murale ou de plancher"]
    SYSTEM1R["IdLabel"] = ["0", "1", "2", "3", "4", "5", "6", "7"]
    SYSTEM1R["Description"] = "Système principal de chauffage"
    SYSTEM1R["Type"] = "discrete"

    # SYSTEM2 : Système principal de chauffage en combinaison - détail
    SYSTEM2 = {}
    SYSTEM2["Label"] = ["Thermopompe (pompe à chaleur) murale",
                        "Plinthes électriques",
                        "Fournaise centrale (système central à air chaud)",
                        "Unités convecteurs",
                        "Fournaise murale ou de plancher",
                        "Chaudière centrale (système central à eau chaude)",
                        "Système radiant à rayonnement dans le plancher",
                        "Poêle au mazout",
                        "Système radiant à rayonnement dans le plafond"]
    SYSTEM2["IdLabel"] = ["0", "1", "2", "3", "4", "5", "6", "7", "8"]
    SYSTEM2["Description"] = "Système principal de chauffage en combinaison"
    SYSTEM2["Type"] = "discrete"

    # SYSTEM2R : Système principal de chauffage en combinaison
    SYSTEM2R = {}
    SYSTEM2["Label"] = ["Thermopompe",
                "Plinthes électriques",
                "Système central à air chaud",
                "Unités convecteurs, plancher ou plafond radiant",
                "Fournaise murale ou de plancher",
                "Système central à eau chaude"]
    SYSTEM2R["IdLabel"] = ["0", "1", "2", "3", "4", "5"]
    SYSTEM2R["Description"] = "Système principal de chauffage en combinaison"
    SYSTEM2R["Type"] = "discrete"

    # QC9A : Avec quel autre système votre thermopompe (pompe à chaleur) est-elle combinée?
    QC9A = {}
    QC9A["Label"] = ["Plinthes",
                     "Convecteurs",
                    "Plinthes et convecteurs",
                    "Radiants de plancher",
                    "Bouilloire électrique",
                    "Fournaise électrique à air chaud",
                    "Fournaise au gaz naturel à air chaud",
                    "Fournaise au propane à air chaud",
                    "Fournaise au mazout à air chaud",
                    "Pas de système de relève"]
    QC9A["IdLabel"] = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
    QC9A["Description"] = "Avec quel autre système votre thermopompe (pompe à chaleur) est-elle combinée?"
    QC9A["Type"] = "discrete"

    # QC7A : Votre thermopompe est-elle de type « climat froid » ou « basse température »?
    QC7A = {}
    QC7A["Label"] = ["Oui", "Non"]
    QC7A["IdLabel"] = ["0", "1"]
    QC7A["Description"] = "Votre thermopompe est-elle de type « climat froid » ou « basse température »?"
    QC7A["Type"] = "discrete"

    # QC21A : Année installation thermopompe
    QC21A = {}
    QC21A["Label"] = None
    QC21A["IdLabel"] = None
    QC21A["Description"] = "En quelle année votre thermopompe a-t-elle été installée?"
    QC21A["Type"] = "Entier"

    # APPOINT : Nombre de systèmes d'appoint possédés
    APPOINT = {}
    APPOINT["Label"] = ["0", "1", "2", "3", "4", "5", "6"]
    APPOINT["IdLabel"] = ["0", "1", "2", "3", "4", "5", "6"]
    APPOINT["Description"] = "Combien de systèmes d'appoint possédez-vous?"
    APPOINT["Type"] = "discrete"

    # QD1A : Utilisez-vous comme chauffage d'appoint des chaufferettes (radiateurs électriques portatifs)?
    QD1A = {}
    QD1A["Label"] = ["Oui", "Non"]
    QD1A["IdLabel"] = ["0", "1"]
    QD1A["Description"] = "Utilisez-vous comme chauffage d'appoint des chaufferettes (radiateurs électriques portatifs)?"
    QD1A["Type"] = "discrete"

    # QD1B : Utilisez-vous comme chauffage d'appoint des plinthes électriques fixes?
    QD1B = {}
    QD1B["Label"] = ["Oui", "Non"]
    QD1B["IdLabel"] = ["0", "1"]
    QD1B["Description"] = "Utilisez-vous comme chauffage d'appoint des plinthes électriques fixes?"
    QD1B["Type"] = "discrete"

    # QD1C : Utilisez-vous comme chauffage d'appoint des unités convecteurs?
    QD1C = {}
    QD1C["Label"] = ["Oui", "Non"]
    QD1C["IdLabel"] = ["0", "1"]
    QD1C["Description"] = "Utilisez-vous comme chauffage d'appoint des unités convecteurs?"
    QD1C["Type"] = "discrete"

    # QD1D : Utilisez-vous comme chauffage d'appoint un poêle à combustion lente (hermétique)?
    QD1D = {}
    QD1D["Label"] = ["Oui", "Non"]
    QD1D["IdLabel"] = ["0", "1"]
    QD1D["Description"] = "Utilisez-vous comme chauffage d'appoint un poêle à combustion lente (hermétique)?"
    QD1D["Type"] = "discrete"

    # QD1E : Utilisez-vous un poêle à bois à combustion lente ou conventionnel comme chauffage d'appoint (Base totale)
    QD1E = {}
    QD1E["Label"] = ["Oui", "Non"]
    QD1E["IdLabel"] = ["0", "1"]
    QD1E["Description"] = "Utilisez-vous un poêle à bois à combustion lente ou conventionnel comme chauffage d'appoint?"
    QD1E["Type"] = "discrete"

    # QD1F : Utilisez-vous comme chauffage d'appoint un foyer?
    QD1F = {}
    QD1F["Label"] = ["Oui", "Non"]
    QD1F["IdLabel"] = ["0", "1"]
    QD1F["Description"] = "Utilisez-vous comme chauffage d'appoint un foyer?"
    QD1F["Type"] = "discrete"
    #   QD2F2 : Quelle source d'énergie utilisez-vous pour ce foyer?
    QD2F2 = {}
    QD2F2["Label"] = ["Électricité",
                        "Gaz naturel",
                        "Gaz propane",
                        "Mazout",
                        "Bois"]
    QD2F2["IdLabel"] = ["0", "1", "2", "3", "4"]   
    QD2F2["Description"] = "Quelle source d'énergie utilisez-vous pour ce foyer?"
    QD2F2["Type"] = "discrete"

    # QD1J : Utilisez-vous comme chauffage d'appoint un système radiant à rayonnement dans le plancher ou le plafond?
    QD1J = {}           
    QD1J["Label"] = ["Oui", "Non"]
    QD1J["IdLabel"] = ["0", "1"]
    QD1J["Description"] = "Utilisez-vous comme chauffage d'appoint un système radiant à rayonnement dans le plancher ou le plafond?"
    QD1J["Type"] = "discrete"

    # QD1G : Utilisez-vous comme chauffage d'appoint une fournaise individuelle murale ou de plancher?
    QD1G = {}
    QD1G["Label"] = ["Oui", "Non"]
    QD1G["IdLabel"] = ["0", "1"]
    QD1G["Description"] = "Utilisez-vous comme chauffage d'appoint une fournaise individuelle murale ou de plancher?"
    QD1G["Type"] = "discrete"
    
    #   QD2G : Quelle source d'énergie utilisez-vous pour cette fournaise?
    QD2G = {}
    QD2G["Label"] = ["Électricité",
                    "Gaz naturel",
                    "Gaz propane",
                    "Mazout",
                    "Bois"]
    QD2G["IdLabel"] = ["0", "1", "2", "3"]
    QD2G["Description"] = "Quelle source d'énergie utilisez-vous pour cette fournaise?"
    QD2G["Type"] = "discrete"

    # QD1H : Utilisez-vous comme chauffage d'appoint une fournaise centrale à air chaud (avec bouches de chaleur)?
    QD1H = {}
    QD1H["Label"] = ["Oui", "Non"]
    QD1H["IdLabel"] = ["0", "1"]
    QD1H["Description"] = "Utilisez-vous comme chauffage d'appoint une fournaise centrale à air chaud (avec bouches de chaleur)?"
    QD1H["Type"] = "discrete"
    #   QD2H : Quelle source d'énergie utilisez-vous pour cette fournaise?
    QD2H = {}
    QD2H["Label"] = ["Électricité",
                    "Gaz naturel",
                    "Gaz propane",
                    "Mazout",
                    "Bois"]
    QD2H["IdLabel"] = ["0", "1", "2", "3"]
    QD2H["Description"] = "Quelle source d'énergie utilisez-vous pour cette fournaise?"
    QD2H["Type"] = "discrete"

    # QD1I : Utilisez-vous comme chauffage d'appoint une chaudière centrale à eau chaude (avec calorifères)?
    QD1I = {}
    QD1I["Label"] = ["Oui", "Non"]
    QD1I["IdLabel"] = ["0", "1"]
    QD1I["Description"] = "Utilisez-vous comme chauffage d'appoint une chaudière centrale à eau chaude (avec calorifères)?"
    QD1I["Type"] = "discrete"
    #   QD2I : Quelle source d'énergie utilisez-vous pour cette chaudière?
    QD2I = {}
    QD2I["Label"] = ["Électricité",
                    "Gaz naturel",
                    "Gaz propane",
                    "Mazout",
                    "Bois"]
    QD2I["IdLabel"] = ["0", "1", "2", "3"]
    QD2I["Description"] = "Quelle source d'énergie utilisez-vous pour cette chaudière?"
    QD2I["Type"] = "discrete"

    # QD4A : Utilisez-vous un thermostat central, c'est-à-dire celui de votre système central qui contrôle la température de plusieurs pièces en même temps?
    QD4A = {}
    QD4A["Label"] = ["Oui", "Non"]
    QD4A["IdLabel"] = ["0", "1"]
    QD4A["Description"] = "Utilisez-vous un thermostat central, c'est-à-dire celui de votre système central qui contrôle la température de plusieurs pièces en même temps?"
    QD4A["Type"] = "discrete"

    # QD4C : Votre thermostat central est-il programmable, c'est-à-dire qui vous permet de programmer à l'avance des hausses et des baisses automatiques de la température à heures fixes sans autre intervention de votre part?
    QD4C = {}
    QD4C["Label"] = ["Oui", "Non"]
    QD4C["IdLabel"] = ["0", "1"]
    QD4C["Description"] = "Votre thermostat central est-il programmable, c'est-à-dire qui vous permet de programmer à l'avance des hausses et des baisses automatiques de la température à heures fixes sans autre intervention de votre part?"
    QD4C["Type"] = "discrete"

    # QD4C1 : Habituellement, programmez-vous à l'avance des hausses et des baisses automatiques de la température à heures fixes à l'aide de votre thermostat central programmable?
    QD4C1 = {}
    QD4C1["Label"] = ["Oui", "Non"]
    QD4C1["IdLabel"] = ["0", "1"]
    QD4C1["Description"] = "Habituellement, programmez-vous à l'avance des hausses et des baisses automatiques de la température à heures fixes à l'aide de votre thermostat central programmable?"
    QD4C1["Type"] = "discrete"

    # Plus de détails disponible dans le sondage sur les thermostats

    # QD6A : Utilisez-vous un ou des thermostat(s) placé(s) sur le mur et qui contrôle(nt) le chauffage d'une seule ou plusieurs pièces à la fois? (thermostats muraux)
    QD6A = {}
    QD6A["Label"] = ["Oui", "Non"]
    QD6A["IdLabel"] = ["0", "1"]
    QD6A["Description"] = "Utilisez-vous un ou des thermostat(s) placé(s) sur le mur et qui contrôle(nt) le chauffage d'une seule ou plusieurs pièces à la fois? (thermostats muraux)"
    QD6A["Type"] = "discrete"
    # QD6 : Combien avez-vous de thermostats muraux? (thermostats placé(s) sur le mur et qui contrôle(nt) le chauffage d'une seule pièce à la fois)
    QD6 = {}
    QD6["Label"] = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18"]
    QD6["IdLabel"] = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17"]
    QD6["Description"] = "Combien avez-vous de thermostats muraux? (thermostats placé(s) sur le mur et qui contrôle(nt) le chauffage d'une seule pièce à la fois)"
    QD6["Type"] = "discrete"
    # QD6B : En avez-vous qui sont électroniques, c est-à-dire qu il y a un écran qui affiche la température?
    QD6B = {}
    QD6B["Label"] = ["Oui", "Non"]
    QD6B["IdLabel"] = ["0", "1"]
    QD6B["Description"] = "En avez-vous qui sont électroniques, c est-à-dire qu il y a un écran qui affiche la température?"
    QD6B["Type"] = "discrete"

    # QD6C : Combien avez-vous de thermostats électroniques programmables, c'est-à-dire qui vous permet de programmer à l'avance des hausses et des baisses automatiques de la température à heures fixes sans autre intervention de votre part?
    QD6C = {}
    QD6C["Label"] = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18"]
    QD6C["IdLabel"] = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17"]
    QD6C["Description"] = "Combien avez-vous de thermostats électroniques programmables, c'est-à-dire qui vous permet de programmer à l'avance des hausses et des baisses automatiques de la température à heures fixes sans autre intervention de votre part?"
    QD6C["Type"] = "discrete"

    # QD6C1 : Habituellement, programmez-vous à l'avance des hausses et des baisses automatiques de la température à heures fixes à l'aide de votre ou vos thermostats muraux programmables?
    QD6C1 = {}
    QD6C1["Label"] = ["Oui", "Non"]
    QD6C1["IdLabel"] = ["0", "1"]
    QD6C1["Description"] = "Habituellement, programmez-vous à l'avance des hausses et des baisses automatiques de la température à heures fixes à l'aide de votre ou vos thermostats muraux programmables?"
    QD6C1["Type"] = "discrete"

    # QD11A : Climatisez-vous votre habitation, que ce soit une seule pièce ou l'ensemble des pièces?
    QD11A = {}
    QD11A["Label"] = ["Oui", "Non"]
    QD11A["IdLabel"] = ["0", "1"]
    QD11A["Description"] = "Climatisez-vous votre habitation, que ce soit une seule pièce ou l'ensemble des pièces?"
    QD11A["Type"] = "discrete"

    # QD11BM1 : Parmi les appareils suivants, lesquels utilisez-vous pour climatiser votre habitation? (Ensemble des mentions)
    QD11BM1 = {}
    QD11BM1["Label"] = ["Climatiseur central autre qu'une thermopompe",
                        "Climatiseur de fenêtre",
                        "Climatiseur mobile / portable",
                        "Climatiseur mural ou bibloc (mini-split)",
                        "Thermopompe murale",
                        "Thermopompe centrale",
                        "Thermopompe géothermique"]
    QD11BM1["IdLabel"] = ["0", "1", "2", "3", "4", "5", "6"]
    QD11BM1["Description"] = "Parmi les appareils suivants, lesquels utilisez-vous pour climatiser votre habitation? (Ensemble des mentions)"
    QD11BM1["Type"] = "discrete"

    # QD11BM1R : Parmi les appareils suivants, lesquels utilisez-vous pour climatiser votre habitation? (Ensemble des mentions) (Base totale)
    QD11BM1R = {}
    QD11BM1R["Label"] = ["Central autre que thermopompe",
                        "Climatiseur de fenêtre",
                        "Climatiseur mobile",
                        "Climatiseur mural ou bibloc",
                        "Thermopompe murale",
                        "Thermopompe centrale",
                        "Thermopompe géothermique"]
    QD11BM1R["IdLabel"] = ["0", "1", "2", "3", "4", "5", "6"]
    QD11BM1R["Description"] = "Parmi les appareils suivants, lesquels utilisez-vous pour climatiser votre habitation? (Ensemble des mentions) (Base totale)"
    QD11BM1R["Type"] = "discrete"

    # D11B8 : En quelle année votre climatiseur a-t-il été installé?
    D11B8 = {}
    D11B8["Label"] = None
    D11B8["IdLabel"] = None
    D11B8["Description"] = "En quelle année votre climatiseur a-t-il été installé?"
    D11B8["Type"] = "Entier"

    # QD7F1 : Utilisez-vous un échangeur d'air?
    QD7F1 = {}
    QD7F1["Label"] = ["Oui", "Non"]
    QD7F1["IdLabel"] = ["0", "1"]
    QD7F1["Description"] = "Utilisez-vous un échangeur d'air?"
    QD7F1["Type"] = "discrete"

    # QD7G1 : S'agit-il d'un échangeur d'air avec ou sans récupérateur de chaleur?
    QD7G1 = {}
    QD7G1["Label"] = ["Avec récupérateur de chaleur",
                        "Sans récupérateur de chaleur"]
    QD7G1["IdLabel"] = ["0", "1"]
    QD7G1["Description"] = "S'agit-il d'un échangeur d'air avec ou sans récupérateur de chaleur?"
    QD7G1["Type"] = "discrete"

    # QD7H3 : Arrêtez-vous votre échangeur d'air en période de grands froids (-20 et plus froid)?
    QD7H3 = {}
    QD7H3["Label"] = ["Oui", "Non"]
    QD7H3["IdLabel"] = ["0", "1"]
    QD7H3["Description"] = "Arrêtez-vous votre échangeur d'air en période de grands froids (-20 et plus froid)?"
    QD7H3["Type"] = "discrete"
    
    # QF1 : À quelle source d'énergie votre chauffe-eau fonctionne-t-il?
    QF1 = {}
    QF1["Label"] = ["À l'électricité",
                    "Au gaz naturel",
                    "À l'huile/au mazout",
                    "Au propane",
                    "Au bois",
                    "Pas de chauffe-eau"]
    QF1["IdLabel"] = ["0", "1", "2", "3", "4", "5"]
    QF1["Description"] = "À quelle source d'énergie votre chauffe-eau fonctionne-t-il?"
    QF1["Type"] = "discrete"

    # QF2 : Est-ce que votre chauffe-eau est central, c'est-à-dire commun à deux ou plusieurs logements ou est-ce un chauffe-eau uniquement pour votre résidence?
    QF2 = {}
    QF2["Label"] = ["Central, soit pour plusieurs logements",
                    "Uniquement pour la résidence"]
    QF2["IdLabel"] = ["0", "1"]
    QF2["Description"] = "Est-ce que votre chauffe-eau est central, c'est-à-dire commun à deux ou plusieurs logements ou est-ce un chauffe-eau uniquement pour votre résidence?"
    QF2["Type"] = "discrete"

    # QF2R : Le chauffe-eau est central ou uniquement pour le lieu de résidence (Base totale)
    QF2R = {}
    QF2R["Label"] = ["Central, soit pour plusieurs logements",
                    "Uniquement pour la résidence",
                    "Pas de chauffe-eau"]
    QF2R["IdLabel"] = ["0", "1", "2"]
    QF2R["Description"] = "Le chauffe-eau est central ou uniquement pour le lieu de résidence (Base totale)"
    QF2R["Type"] = "discrete"


    # QF3 : Quelle est la capacité du chauffe-eau?
    QF3 = {}
    QF3["Label"] = ["Chauffe-eau sans réservoir",
                    "Moins de 22 gallons (97 litres)",
                    "22 gallons (97 litres)", 
                    "Entre 23 et 39 gallons (100 et 172 litres)",
                    "40 gallons (176 litres)",
                    "41 à 59 gallons (180 à 260 litres)",
                    "60 gallons (264 litres)",
                    "Plus de 60 gallons (264 litres)"]
    QF3["IdLabel"] = ["0", "1", "2", "3", "4", "5", "6", "7"]
    QF3["Description"] = "Quelle est la capacité du chauffe-eau?"
    QF3["Type"] = "discrete"

    # QG1 : Avez-vous une piscine installée en permanence, qu'elle soit creusée ou hors-terre?
    QG1 = {}
    QG1["Label"] = ["Oui", "Non"]
    QG1["IdLabel"] = ["0", "1"]
    QG1["Description"] = "Avez-vous une piscine installée en permanence, qu'elle soit creusée ou hors-terre?"
    QG1["Type"] = "discrete"

    # QG1A : Avez-vous une piscine gonflable?
    QG1A = {}
    QG1A["Label"] = ["Oui", "Non"]
    QG1A["IdLabel"] = ["0", "1"]
    QG1A["Description"] = "Avez-vous une piscine gonflable?"
    QG1A["Type"] = "discrete"
    # QG2 : De quel type de piscine s'agit-il?
    QG2 = {}
    QG2["Label"] = ["Une piscine hors-terre / semi-creusée",
                    "Une piscine creusée extérieure",
                    "Une piscine creusée intérieure",
                    "Une piscine hors-terre gonflable"]
    QG2["IdLabel"] = ["0", "1", "2", "3"]
    QG2["Description"] = "De quel type de piscine s'agit-il?"
    QG2["Type"] = "discrete"

    # QG2R : Type de piscine (Base possède une piscine)

    # QG3 : Votre filtreur est-il équipé d'une minuterie?
    QG3 = {}
    QG3["Label"] = ["Oui", "Non"]
    QG3["IdLabel"] = ["0", "1"]
    QG3["Description"] = "Votre filtreur est-il équipé d'une minuterie?"
    QG3["Type"] = "discrete"

    # QG5 : Possédez-vous une toile solaire?
    QG5 = {}
    QG5["Label"] = ["Oui", "Non"]
    QG5["IdLabel"] = ["0", "1"]
    QG5["Description"] = "Possédez-vous une toile solaire?"
    QG5["Type"] = "discrete"
    
    # QG7 : Votre piscine est-elle chauffée (autrement que par une toile solaire)?
    QG7 = {}
    QG7["Label"] = ["Oui", "Non"]
    QG7["IdLabel"] = ["0", "1"]
    QG7["Description"] = "Votre piscine est-elle chauffée (autrement que par une toile solaire)?"
    QG7["Type"] = "discrete"

    # QG8M1 : De quelle façon est-elle chauffée? (Ensemble des mentions)
    QG8M1 = {}
    QG8M1["Label"] = ["Une thermopompe de piscine",
                    "Un chauffe-piscine électrique (qui n’est pas une thermopompe)",
                    "Un capteur solaire",
                    "Un chauffe-piscine au propane",
                    "Un chauffe-piscine au gaz naturel",
                    "Un chauffe-piscine au bois",
                    "Un chauffe-piscine à l’huile/mazout"]
    QG8M1["IdLabel"] = ["0", "1", "2", "3", "4", "5", "6"]
    QG8M1["Description"] = "De quelle façon est-elle chauffée? (Ensemble des mentions)"
    QG8M1["Type"] = "discrete"

    # QB1M : Avez-vous un spa à votre résidence?
    QB1M = {}
    QB1M["Label"] = ["Oui", "Non"]
    QB1M["IdLabel"] = ["0", "1"]
    QB1M["Description"] = "Avez-vous un spa à votre résidence?"
    QB1M["Type"] = "discrete"
    # QB1M3 : Le spa est-il à l'intérieur ou à l'extérieur de la résidence?
    QB1M3 = {}
    QB1M3["Label"] = ["Intérieur",
                    "Extérieur"]
    QB1M3["IdLabel"] = ["0", "1"]
    QB1M3["Description"] = "Le spa est-il à l'intérieur ou à l'extérieur de la résidence?"
    QB1M3["Type"] = "discrete"
    # QS1 : Au cours des 12 derniers mois, avez-vous utilisé votre spa…?
    QS1 = {}
    QS1["Label"] = ["Oui", "Non"]
    QS1["IdLabel"] = ["0", "1"]
    QS1["Description"] = "Au cours des 12 derniers mois, avez-vous utilisé votre spa…?"
    QS1["Type"] = "discrete"
    #   QS2M1R : avez-vous utilisé votre spa…?
    QS2M1R = {}
    QS2M1R["Label"] = ["Le printemps",
                    "L'été",
                    "L'automne",
                    "L'hiver",
                    "Pas utilisé"]
    QS2M1R["IdLabel"] = ["0", "1", "2", "3", "4"]
    QS2M1R["Description"] = "Avez-vous utilisé votre spa…? (Printemps, été, automne, hiver, pas utilisé)"
    QS2M1R["Type"] = "discrete"
    #   QS2M2R : avez-vous utilisé votre spa…?
    QS2M2R = {}
    QS2M2R["Label"] = ["Le printemps",
                    "L'été",
                    "L'automne",
                    "L'hiver"]
    QS2M2R["IdLabel"] = ["0", "1", "2", "3"]
    QS2M2R["Description"] = "Avez-vous utilisé votre spa…? (Printemps, été, automne, hiver)"
    QS2M2R["Type"] = "discrete"
    #   QS2M3R : avez-vous utilisé votre spa…?
    QS2M3R = {}
    QS2M3R["Label"] = ["Le printemps",
                    "L'été",
                    "L'automne",
                    "L'hiver"]
    QS2M3R["IdLabel"] = ["0", "1", "2", "3"]
    QS2M3R["Description"] = "Avez-vous utilisé votre spa…? (Printemps, été, automne, hiver)"
    QS2M3R["Type"] = "discrete"

    #   QS2M4R : avez-vous utilisé votre spa…?
    QS2M4R = {}
    QS2M4R["Label"] = ["Le printemps",
                    "L'été",
                    "L'automne",
                    "L'hiver"]
    QS2M4R["IdLabel"] = ["0", "1", "2", "3"]
    QS2M4R["Description"] = "Avez-vous utilisé votre spa…? (Printemps, été, automne, hiver)"
    QS2M4R["Type"] = "discrete"
   
    # QS3AA : Lequel des deux énoncés suivants correspond le mieux à vos habitudes durant les mois froids de la dernière année?
    QS3AA = {}
    QS3AA["Label"] = ["Je maintenais la température de mon spa constante",
                    "J’augmentais la température pour les périodes de baignade"]
    QS3AA["IdLabel"] = ["0", "1"]
    QS3AA["Description"] = "Lequel des deux énoncés suivants correspond le mieux à vos habitudes durant les mois froids de la dernière année?"
    QS3AA["Type"] = "discrete"

    # QS3BB : Lequel des deux énoncés suivants correspond le mieux à vos habitudes durant les mois chauds de la dernière année?
    QS3BB = {}
    QS3BB["Label"] = ["Je maintenais la température de mon spa constante",
                    "J’augmentais la température pour les périodes de baignade"]
    QS3BB["IdLabel"] = ["0", "1"]
    QS3BB["Description"] = "Lequel des deux énoncés suivants correspond le mieux à vos habitudes durant les mois chauds de la dernière année?"
    QS3BB["Type"] = "discrete"

    # QT1 : Utilisez-vous une ou des voiture(s) électrique(s) rechargeable(s), qu'elle soit 100 % électrique ou hybride rechargeable, qu'elle soit achetée ou louée?
    QT1 = {}
    QT1["Label"] = ["Oui", "Non"]
    QT1["IdLabel"] = ["0", "1"]
    QT1["Description"] = "Utilisez-vous une ou des voiture(s) électrique(s) rechargeable(s), qu'elle soit 100 % électrique ou hybride rechargeable, qu'elle soit achetée ou louée?"
    QT1["Type"] = "discrete"
    # QT2 : Combien avez-vous de voiture(s) 100 % électrique?
    QT2 = {}
    QT2["Label"] = ["Aucune",
                    "Une",
                    "Deux",
                    "Trois"]
    QT2["IdLabel"] = ["0", "1", "2", "3"]
    QT2["Description"] = "Combien avez-vous de voiture(s) 100 % électrique?"
    QT2["Type"] = "discrete"

    # QT2R : Combien avez-vous de voiture(s) 100 % électrique? (Base totale)
    QT2R = {}
    QT2R["Label"] = ["Aucune",
                    "Une",
                    "Deux",
                    "Trois"]
    QT2R["IdLabel"] = ["0", "1", "2", "3"]
    QT2R["Description"] = "Combien avez-vous de voiture(s) 100 % électrique? (Base totale)"
    QT2R["Type"] = "discrete"

    # QT3 : Combien avez-vous de voiture(s) électrique(s) hybride rechargeable?
    QT3 = {}
    QT3["Label"] = ["Aucune",
                    "Une",
                    "Deux"]
    QT3["IdLabel"] = ["0", "1", "2"]
    QT3["Description"] = "Combien avez-vous de voiture(s) électrique(s) hybride rechargeable?"
    QT3["Type"] = "discrete"

    # QT3R : Combien avez-vous de voiture(s) électrique(s) hybride rechargeable? (Base totale)
    QT3R = {}
    QT3R["Label"] = ["Aucune",
                    "Une",
                    "Deux"]
    QT3R["IdLabel"] = ["0", "1", "2"]
    QT3R["Description"] = "Combien avez-vous de voiture(s) électrique(s) hybride rechargeable? (Base totale)"
    QT3R["Type"] = "discrete"

    # QT2T3 : Voiture(s) électrique? (Base totale)
    QT2T3 = {}
    QT2T3["Label"] = ["Ne possède aucune voiture électrique",
                    "Possède une ou plusieurs voitures 100 % électriques",
                    "Possède une ou plusieurs voitures électriques hybrides",
                    "Possède les deux types de voitures"]
    QT2T3["IdLabel"] = ["0", "1", "2", "3"]
    QT2T3["Description"] = "Voiture(s) électrique? (Base totale)"
    QT2T3["Type"] = "discrete"

    # QT4 : Disposez-vous d'une borne de recharge reliée à votre compteur d'électricité?
    QT4 = {}
    QT4["Label"] = ["Oui", "Non"]
    QT4["IdLabel"] = ["0", "1"]
    QT4["Description"] = "Disposez-vous d'une borne de recharge reliée à votre compteur d'électricité?"
    QT4["Type"] = "discrete"


class FormatageEUEMr:
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
        if colName in Attribut_EUEMr.__dict__.keys():
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
                                        "Description": Attribut_EUEMr.__dict__[ColSrc]["Description"],
                                        "Type": "discrete"}
                elif dictMap["typeMapping"] == "bin":
                    Metadata[keyMap] = {"Label": dictMap["Mapping"]["labels"],
                                        "IdLabel": [str(i) for i in range(len(dictMap["Mapping"]["labels"]))],
                                        "Description": Attribut_EUEMr.__dict__[ColSrc]["Description"],
                                        "Type": "discrete"}
                elif dictMap["typeMapping"] == "custom":
                    Metadata[keyMap] = {"Label": dictMap["Mapping"].keys(),
                                        "IdLabel": [str(i) for i in range(len(dictMap["Mapping"]))],
                                        "Description": Attribut_EUEMr.__dict__[ColSrc]["Description"],
                                        "Type": "discrete"}
                elif dictMap["typeMapping"] == "no":
                    Metadata[keyMap] = {"Label": [],
                                        "IdLabel": [],
                                        "Description": Attribut_EUEMr.__dict__[ColSrc]["Description"],
                                        "Type": ""}
            except KeyError as e:
                print(f"Error processing mapping for key: {keyMap} : {e}")
                
            #Metadata[keyMap] = {"Label": list(dictMap["Mapping"].keys()),
            #                    "IdLabel": [str(i) for i in range(len(dictMap["Mapping"]))],
            #                    "Description": Attribut_EUEMr.__dict__[dictMap["ColSrc"]]["Description"],
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
            if ColName in self.Mapping:
                if self.Mapping[ColName]["ColSrc"] in self.dfEUEMrSrc.columns:
                    dfEUEMrSrc_ColName = self.dfEUEMrSrc
                elif self.Mapping[ColName]["ColSrc"] in  self.dfEUEMr_new.columns:
                    dfEUEMrSrc_ColName = self.dfEUEMr_new
                else:
                    raise ValueError(f"Unknown mapping source for column '{ColName}'.")
                
                if self.Mapping[ColName]["typeMapping"] == "no":
                    return dfEUEMrSrc_ColName[self.Mapping[ColName]["ColSrc"]].rename(ColName)
                
                elif self.Mapping[ColName]["typeMapping"] == "list":
                    dct_replace = {}
                    for k, v in self.Mapping[ColName]["Mapping"].items():
                        for val in v:
                            dct_replace[val] = k
                    tempoSeries = dfEUEMrSrc_ColName[self.Mapping[ColName]["ColSrc"]].replace(dct_replace).rename(ColName)
                    tempoSeries[~tempoSeries.isin(list(set(dct_replace.values())))] = None
                    return tempoSeries

                elif self.Mapping[ColName]["typeMapping"] == "bin":

                    return pd.cut(dfEUEMrSrc_ColName[self.Mapping[ColName]["ColSrc"]],
                                bins=self.Mapping[ColName]["Mapping"]["bins"],
                                labels=self.Mapping[ColName]["Mapping"]["labels"],
                                right=False).rename(ColName)                
                
                elif self.Mapping[ColName]["typeMapping"] == "custom":#type de Mapping (plus complexe)
                    if ColName == "Presence_Garage":
                        return dfEUEMrSrc_ColName.apply(lambda row: "Pas de Garage" if row["QM1A"] in ["Non", "."]\
                                                                 else ("Garage non chauffé" if row["QM1AA"]=="Non" \
                                                                 else ("Garage chauffé à électricité" if row["QM1B"]=="Oui"\
                                                                 else ("Garage chauffé à autre source" if row["QM1A"]=="Oui" else ""))), axis=1).rename(ColName)
                    
                    if ColName == "Chauffage_Logement":
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
                    if ColName == "Spa_Saison":
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
                        #else ("Printemps_Ete_Hiver" if sorted([row["QS2M1R"], row["QS2M2R"], row["QS2M3R"], row["QS2M4R"]])== sorted(["Le printemps","L'été","L'hiver", "."])\
                    if ColName == "Vehicule_Presence":
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
                    if ColName == "Region_Administrative":
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

        for ColName in self.Mapping:
            self.dfEUEMr_new = pd.concat([self.dfEUEMr_new, self.DoMapping(ColName)], axis=1)
        
        return self.dfEUEMr_new

    def Main(self):
        """
        Fonction principale pour exécuter le formatage des données EUEMr.
        """
        stFileName = PROJECT_DIR+"//data//EUEMr//2022//sondage_residentiel_version_finale.xlsx"
        sheet_name = "Data"

        self.Load_excel(stFileName, sheet_name)
        #dfEUEMr_new = self.DoAllMapping()
        self.DoAllMapping()

        output_file = PROJECT_DIR+"//data//EUEMr//2022//sondage_residentiel_version_finale_formatted.csv"
        self.SaveToCSV(self.dfEUEMr_new, output_file)

class EUEMr(Master_genereBN):
    '''
    Class qui permet de générer un réseau bayésien à partir des données EUEMr.
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
                 ##"ConsoElecAn",
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
                    
        
#    ["QA4", # De quel genre d'habitation s'agit-il?
#                 "QA1", # Quel est votre lien avec ce logement ?
#                 "QC1R", # Principale source d'énergie utilisée pour le chauffage du domicile
#                 ]

    # création des noeuds 
    # Nom_Noeud:description_Noeud
    MapEUEMr = FormatageEUEMr()
    dictMapEUEMr = MapEUEMr.get_Mettadata()
    NOEUD_EUEMr = {}
    for key in lst_NOEUD:
        if key in dictMapEUEMr.keys():
            NOEUD_EUEMr[key] = dictMapEUEMr[key]["Description"]
        else:
            NOEUD_EUEMr[key] = Attribut_EUEMr.__dict__[key]["Description"]

    # création des dictionnaires des noeuds
    # {Nom_Noeud: {IdLabel: Label}}

    LIST_Dict = {}
    for key in lst_NOEUD:
        if key in dictMapEUEMr.keys():
            LIST_Dict[key] = {idL:Lab for idL,Lab in zip(dictMapEUEMr[key]["IdLabel"],
                                                         dictMapEUEMr[key]["Label"])}

        else:
            LIST_Dict[key] = {idL:Lab for idL,Lab in zip(Attribut_EUEMr.__dict__[key]["IdLabel"],
                                                        Attribut_EUEMr.__dict__[key]["Label"])}

    #TODO
    # Changer en relatif

    fileEUEMr = PROJECT_DIR+"//data//EUEMr//2022//sondage_residentiel_version_finale_formatted.csv"

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
            self.bn.add(gum.LabelizedVariable(Node_name, Node_name, [str(i) for i in Node_value]))   # par key [1,2,99]

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

        absolute_path = self.fileEUEMr
        self.Load_csv(absolute_path)#self.dfcsv
        self.dfcsv = self.dfcsv[self.dfcsv["POND1"].notnull()]  # Filtrer les lignes où POND1 est supérieur à 0 (enleve logement spécifique aux nouvelle constructions)

        for col in ["POND1", "POND2x", "POND1_POP", "POND2x_POP"]:
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
                                    values=self.dfcsv["POND1"], # Pondération
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
                                        values=self.dfcsv["POND1"], # Pondération
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
        
        absolute_path = self.fileEUEMr
        self.Load_csv(absolute_path)#self.dfcsv
        self.dfcsv = self.dfcsv[self.dfcsv["POND1"].notnull()]  # Filtrer les lignes où POND1 est supérieur à 0 (enleve logement spécifique aux nouvelle constructions)

        # Assigner les information de la structure des variable
        diEUEMr = self.LIST_Dict

        for col in ["POND1", "POND2x", "POND1_POP", "POND2x_POP"]:
            self.dfcsv[col] = pd.to_numeric(self.dfcsv[col], errors='coerce')  # Convert to numeric, coercing errors to NaN

        # QA4M : Nombre de logements dans l'immeuble
        dct_MetaStats = {"Nombre_Logement" : {"Csv_name": "Geometry Building Number Units.csv",
                                              "dropvalues" : [".", "NSP/NRP"],
                                              "Dependancy": ["Type_Logement"]}}

        #csvName = PROJECT_DIR+"//data//housing_characteristics//"+dct_MetaStats["Nombre_Logement"]["Csv_name"]
        
                # Ajout des tables conditionnelles
        for Name, dct_val in dct_MetaStats.items():
            csvName = PROJECT_DIR+"//data//housing_characteristics//"+dct_val["Csv_name"]
            lstDep = dct_val["Dependancy"]
            diCPT = {}
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
            #diCPT = diCPT.sort_index(axis=1) # sort column
            # Updater le DataFrame avec l'occurance d'individu par dépendances

            diCPT.update(pd.crosstab(liInd,
                                    self.dfcsv[Name],
                                    values=self.dfcsv["POND1"], # Pondération
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

