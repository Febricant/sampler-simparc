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

#current_dir = os.getcwd()
#parent_dir = os.path.dirname(current_dir)
#sys.path.append(parent_dir)

FILE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(FILE_DIR+ "/../")  # répertoire supérieur
#PACKAGE_DIR = os.path.abspath(PROJECT_DIR)#+ "/../")
sys.path.append(os.path.join(PROJECT_DIR))

from utils.Sampler import Sampler, MapHPXML

import pyAgrum.lib.image as gimg
#try:
#    import pyAgrum.lib.ipython as gnb
#except:
#    import pyAgrum.lib.notebook as gnb

import pyAgrum as gum

import json

import streamlit as st

import plotly.graph_objects as go

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
    path = PROJECT_DIR+"/data/BayesianNetwork/BN_EUEMr.XDSL"
    InsClsSampler.Load_BN(path)

    # List of node names and their values
    lst_NOEUD = InsClsSampler.lst_NOEUD
    LIST_Dict = InsClsSampler.LIST_Dict

    # Widget to select multiple parameters
    st.markdown("## Étape 1 - Sélection des paramètres d'intérêt")

    #col1, col2, col3 = st.columns(3, border=True)
    #with col1:
    st.markdown("### Paramètre")
    #with col2:
    #    st.markdown("### Valeur pour le scénario de référence")
    #with col3:
    #    st.markdown("### Valeur pour le scénario alternatif")
    settings = {}
    #settings["Baseline"] = {}
    #settings["Alternative"] = {}

    Noeuds_contraints = st.multiselect("Selection des variables imposées:", lst_NOEUD)

    for input in Noeuds_contraints:
        #col1, col2, col3 = st.columns(3, border=True)
        #with col1:
        st.markdown(f"**{input}**")
        #with col2:
        settings[input] = st.selectbox(
            f"Choisissez la valeur d'intérêt pour {input} (scénario de référence)",
            options=LIST_Dict[input].values())
        pass
    
	# Create a dataframe from the settings dictionary
    #df = pd.DataFrame(settings)
    
	# Add a toggle to activate the simulations
    st.markdown("## Étape 2 - Simulation des résultats")
    Nombre_de_Samples = st.number_input("Nombre de simulations à réaliser:", min_value=1, max_value=10000, value=10, step=1)
    #on = st.toggle(label="Simuler", value=False)
    #ajouter d'un bouton push
    on = st.button("Simuler")
    
    if on:
        with st.status("Calcul en cours..."):
            st.write(settings)
            st.write("Calcul en utiisant le réseau bayesien...")
			# Add outputs estimated by the models to the dataframe

            #InsClsSampler = EUEMr()
            #InsClsSampler.Make_BN()
            df = InsClsSampler.do_Sampling(Nombre_de_Samples, evs = settings)

            lst_dct_args = df.to_dict(orient='records')
            MapSample = MapHPXML()
            lst_dct_HPXML = MapSample.run(lst_dct_args)
            df2 = pd.DataFrame(lst_dct_HPXML)
            #g=gum.BNDatabaseGenerator(InsClsSampler.bn)
            #g.setRandomVarOrder()
            ##g.setDiscretizedLabelModeRandom()
            #g.drawSamples(10, settings)
            #df = g.to_pandas()
            st.write("Calcul terminé.")  

        st.markdown("## Étape 3 - Résultats")   
        st.dataframe(df)   	
        st.dataframe(df2) 

        ## Perform inference
        #ie = gum.LazyPropagation(InsClsSampler.bn)
        #ie.setEvidence(settings)
        #ie.makeInference()
        ## Export inference as SVG
        #gimg.exportInference(ie, "inference_result.png", size="30")
        ## Display the inference result
        #st.markdown("### Résultats de l'inférence")
        #st.image("inference_result.png", use_column_width=True)
                
    ## Add a toggle to activate visualization
    #st.markdown("## Étape 3 - Résultats")
    #on2 = st.toggle(label="Visualiser", value=False)
    #if on2:
    #    st.dataframe(df)

if "__main__" == __name__:
    #python -m streamlit run "ui/Dashboard.py"
    DashBoard()
    