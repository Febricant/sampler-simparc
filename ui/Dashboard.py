# -*- coding: utf-8 -*-
"""
Dashboard.py
============

This module provides a Streamlit-based dashboard for exploring and downloading HPXML data.
It allows users to:
1. View the HPXML data in a table format.
2. Download the processed results as a CSV file.

Usage:
------
To run the dashboard, execute the following command in the terminal:
    python -m streamlit run "ui/Dashboard.py"

Dependencies:
-------------
- pandas
- streamlit

Author:
-------
[cv1751 - Brice Le Lostec]

version:
-------------
1.0

python version:
-------------
python 3.11

Usage:
-------------
python -m streamlit run "ui/Dashboard.py"

"""
import os
import sys
import time
import numpy as np
import pandas as pd
import pyagrum as gum
#import pyagrum.lib.ipython as gnb
import pyagrum.lib.notebook as gnb
#import dtale
#from dtale.views import startup
#from dtale.app import get_instance
import streamlit as st
import streamlit.components.v1 as components

FILE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(FILE_DIR+ "/../")  # répertoire supérieur
sys.path.append(os.path.join(PROJECT_DIR))
from src.utils.sampler.Sampler import Sampler,  BuildstockBatchArguments, MapHPXML

import warnings
warnings.filterwarnings('ignore', category=UserWarning, module='openpyxl')


# Cache the sampler instance (heavy object)
@st.cache_resource
def load_sampler(path):
    ins = Sampler()
    ins.Load_BN(path)
    return ins

# Cache SVG generation (depends on BN, evidence and size)
@st.cache_data(hash_funcs={gum.BayesNet: lambda b: id(b)})
def bn_svg(bn, evs=None, Inference=True, size=15):
    if Inference:
        # use pyagrum helpers once; cached result avoids recompute on every rerun
        svgtxt = gum.lib.image.dot_as_svg_string(
            gum.lib._colors.prepareDot(gum.lib.image.prepareShowInference(bn, evs=evs)),
            size=size
        )
    else:
        fig = gum.lib.bn2graph.BN2dot(bn)
        svgtxt = gum.lib.image.dot_as_svg_string(gum.lib._colors.prepareDot(fig), size=size)
    return svgtxt

def Page_Echantilloneur():
    """
    Main function to render the Streamlit dashboard.

    This function performs the following steps:
    1. Displays the HPXML data in a table format.
    2. Provides a download button for exporting the data as a CSV file.

    Returns:
    --------
    None
    """

    st.markdown("""
            # ResStock-QC - Tableau de bord utilisant un réseau bayesien construit sur l'EUEMr de 2022
            
            """)

    #InsClsSampler = Sampler()
    #path = PROJECT_DIR+"/data/processed/bayesian_network/BN_EUEMr.XDSL"
    #InsClsSampler.Load_BN(path)
    # use cached loader instead of creating a new Sampler each run
    path = PROJECT_DIR + "/data/processed/bayesian_network/BN_EUEMr.XDSL"
    InsClsSampler = load_sampler(path)

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
            dfAll = pd.concat([dfargs, dfHPXML], axis=1)

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
			data=dfAll.to_csv(index=False).encode('utf-8'),
			file_name='resultats.csv',
			mime='text/csv'
		)
def BaysianNetwork():

    st.markdown("""
            # ResStock-QC - Réseau bayesien construit sur l'EUEMr de 2022
            
            """)
    #créer des tabs pour afficher la description des données et le réseau bayesien
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Description des données", "Réseau bayesien", "liste de noeuds",  "Tables conditionnelles", "Inférence"])

    InsClsSampler = Sampler()
    path = PROJECT_DIR+"/data/processed/bayesian_network/BN_EUEMr.XDSL"
    InsClsSampler.Load_BN(path)

    #save inference graph
    #gum.lib.image.exportInference(InsClsSampler.bn, PROJECT_DIR + "ui/output_inference.png", evs={}, size='30')
    #inspiré de pyagrum.lib.image
    
    # List of node names and their values
    lst_NOEUD = InsClsSampler.lst_NOEUD
    LIST_Dict = InsClsSampler.LIST_Dict

    # data description
    pdfDataDescription = pd.read_csv(PROJECT_DIR+"/data/processed/Data_description.csv", index_col=0)

    
    #add dropdown to view data description
    with tab1:
        # Widget to select multiple parameters
        #st.markdown("## Visualisation du réseau bayesien")
        st.dataframe(pdfDataDescription)

    #add expander to view the bayesian network
    with tab2:
        check_stats = st.checkbox("Afficher les statistiques du réseau bayesien")
        selected_size = st.slider("Sélectionnez la taille du graphique:",
                                                min_value=5, max_value=50, value=15, step=1)
        if st.button("Afficher le réseau bayesien"):
            #st.image(PROJECT_DIR + "ui/output_inference.png", caption='Inférence du réseau bayesien', use_column_width=True)
            #svgtxt = gum.lib.image.dot_as_svg_string(gum.lib._colors.prepareDot(gum.lib.image.prepareShowInference(InsClsSampler.bn)), size=30)
            
            #svgtxt = gum.lib.image.dot_as_svg_string(gum.lib._colors.prepareDot(gum.lib.image.prepareShowInference(InsClsSampler.bn)), size=selected_size)
            # fetch cached SVG (recomputed only when bn, evs or size change)
            svgtxt = bn_svg(InsClsSampler.bn, evs=None,Inference=check_stats, size=selected_size)
            #svg = gum.lib._colors.prepareDot(gum.lib.image.prepareShowInference(InsClsSampler.bn)).create_svg(encoding="utf-8").decode("utf-8")

            components.html(svgtxt, height=900, scrolling=True)

            #st.graphviz_chart(gum.lib.bn2graph.BNinference2dot(InsClsSampler.bn,evs={},size = '30').to_string())

    #add expander to view the list of nodes and their values
    with tab3:
        for node in lst_NOEUD:
            st.markdown(f"**{node}**: {', '.join(LIST_Dict[node].values())}")
    
    #add expander to view the conditional probability tables
    with tab4:
        #select node to view its CPT
        selected_node = st.selectbox("Sélectionnez un noeud pour voir sa table de probabilité conditionnelle:", lst_NOEUD)
        cpt = InsClsSampler.bn.cpt(selected_node)
        
        #afficher la CPT sous forme de dataframe
        st.dataframe(cpt.topandas().style.background_gradient(axis=None, low=0.0, high=1.0))
    
    #add expander to view the inference example
    with tab5:
        st.markdown("### Exemple d'inférence")
        st.markdown("Dans cet exemple, nous allons effectuer une inférence en fixant certaines variables et en observant les effets sur d'autres variables.")
        st.markdown("#### Étape 1 - Sélection des variables imposées")
        
        settings = {}
        Noeuds_contraints = st.multiselect("Sélection des variables imposées:", lst_NOEUD)

        for input in Noeuds_contraints:
            st.markdown(f"**{input}**")
            settings[input] = st.selectbox(
                f"Choisissez la valeur d'intérêt pour {input} (scénario de référence)",
                options=LIST_Dict[input].values())
            pass
        
        st.markdown("#### Étape 2 - Résultats de l'inférence")
        selected_size2 = st.slider("Sélectionnez la taille du graphique (inférence):",
                                            min_value=5, max_value=50, value=15, step=1)

        if st.button("Effectuer l'inférence"):
            
            #svgtxt_inf = gum.lib.image.dot_as_svg_string(gum.lib._colors.prepareDot(gum.lib.image.prepareShowInference(InsClsSampler.bn, evs = settings)), size=selected_size2)
            # fetch cached SVG (recomputed only when bn, evs or size change)
            #svgtxt = bn_svg(InsClsSampler.bn, evs=None, size=selected_size)
            svgtxt_inf = bn_svg(InsClsSampler.bn, evs=settings, Inference = True, size=selected_size2)
            components.html(svgtxt_inf, height=900, scrolling=True)

if __name__ == "__main__":
    st.set_page_config(page_title="Navigation Example", layout="wide")
    pages = {"Echantilloneur": [st.Page(Page_Echantilloneur, title="Echantilloneur"), st.Page(BaysianNetwork, title="Réseau bayesien")]}
    pg = st.navigation(pages)
    pg.run()
