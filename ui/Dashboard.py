# -*- coding: utf-8 -*-
"""
Created on 26-06-2025

@author: cv1751 - Brice Le Lostec
@description: Class for generating Bayesian Networks (BN) using pyagrum.
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
#import dtale
#from dtale.views import startup
#from dtale.app import get_instance
import streamlit.components.v1 as components

FILE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(FILE_DIR+ "/../")  # répertoire supérieur
sys.path.append(os.path.join(PROJECT_DIR))

from src.utils.sampler.Sampler import Sampler,  BuildstockBatchArguments, MapHPXML

import pyagrum.lib.image as gimg
import pyagrum as gum

import json

import streamlit as st

import plotly.graph_objects as go
from dtale.views import startup
import warnings
warnings.filterwarnings('ignore', category=UserWarning, module='openpyxl')


def DashBoard():
    # Set the page configuration
    st.set_page_config(page_title="Echantillonneur ResStock-QC Dashboard",
                       page_icon="🏠",
                       layout="wide",
                       initial_sidebar_state="expanded")
    st.markdown("""
                # ResStock-QC - Tableau de bord utilisant un réseau bayesien construit sur l'EUEMr de 2022
                
                """)
    
    InsClsSampler = Sampler()
    path = PROJECT_DIR+"/data/processed/bayesian_network/BN_EUEMr.XDSL"
    InsClsSampler.Load_BN(path)

    # List of node names and their values
    lst_NOEUD = InsClsSampler.lst_NOEUD
    LIST_Dict = InsClsSampler.LIST_Dict

    # Widget to select multiple parameters
    st.markdown("## Étape 1 - Sélection des paramètres d'intérêt")

    st.markdown("### Paramètre")

    settings = {}


    Noeuds_contraints = st.multiselect("Selection des variables imposées:", lst_NOEUD)

    for input in Noeuds_contraints:

        st.markdown(f"**{input}**")

        settings[input] = st.selectbox(
            f"Choisissez la valeur d'intérêt pour {input} (scénario de référence)",
            options=LIST_Dict[input].values())
        pass
    
	# Add a toggle to activate the simulations
    st.markdown("## Étape 2 - Simulation des résultats")
    Nombre_de_Samples = st.number_input("Nombre de simulations à réaliser:", min_value=1, max_value=10000, value=10, step=1)

    #ajouter d'un bouton push
    on = st.button("Simuler")
    if on:
        with st.status("Calcul en cours..."):
            st.write(settings)
            st.write("Calcul en utiisant le réseau bayesien...")
			# Add outputs estimated by the models to the dataframe

            df = InsClsSampler.do_Sampling(Nombre_de_Samples, evs = settings)

            lst_dct_args = df.to_dict(orient='records')
            
            #Ajout de varaible hors BN
            Bba = BuildstockBatchArguments()
            lst_dct_args2 = Bba.sampling( lst_dct_args)

            lst_dct_args = [ d1 | d2 for d1, d2 in zip(lst_dct_args, lst_dct_args2)]

            MapSample = MapHPXML()
            lst_dct_HPXML = MapSample.run(lst_dct_args)
            dfargs = pd.DataFrame(lst_dct_args)
            dfHPXML = pd.DataFrame(lst_dct_HPXML)

            st.write("Calcul terminé.")  

        st.markdown("## Étape 3 - Résultats")   
       
        #instance1 = startup(data_id="1", data=dfargs)
        #instance2 = startup(data_id = "2", data=dfHPXML)

        #st.html("""<a href="/dtale/main/1" target="_blank">Exploration de l'échantillonnage</a>""")
        st.dataframe(dfargs)
        
        #st.html("""<a href="/dtale/main/2" target="_blank">Exploration du HPXML</a>""")
        st.dataframe(dfHPXML)

        st.markdown("## Étape 4 - Téléchargement des résultats")
        st.markdown("Les résultats sont disponibles au format CSV. " \
		"Attention: le fichier ne devrait pas être trop volumineux (< 100 Mo).")
        st.download_button(
			label="Télécharger les résultats",
			data=dfHPXML.to_csv(index=False).encode('utf-8'),
			file_name='resultats.csv',
			mime='text/csv'
		)

if "__main__" == __name__:
    #python -m streamlit run "ui/Dashboard.py"
    #dtale-streamlit run "ui/Dashboard.py"
    DashBoard()
    #documentation
