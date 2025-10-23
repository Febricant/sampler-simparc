# -*- coding: utf-8 -*-
"""
Dashboard.py
============

Enhanced Streamlit dashboard for exploring and downloading HPXML data with advanced features.

Features:
---------
- Theme customization (dark/light mode)
- Advanced data filtering and visualization
- Interactive Bayesian Network exploration
- Export options (CSV, JSON, Excel)
- Data validation and statistics
- Session state management
- Performance monitoring

Usage:
------
python -m streamlit run "ui/Dashboard_v2.py"

Author: cv1751 - Brice Le Lostec
Version: 2.0
Python: 3.11
"""

import os
import sys
import time
import json
import numpy as np
import pandas as pd
import pyagrum as gum
import pyagrum.lib.notebook as gnb
import streamlit as st
import streamlit.components.v1 as components
from io import BytesIO
import plotly.express as px
import plotly.graph_objects as go

FILE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(FILE_DIR + "/../")
sys.path.append(os.path.join(PROJECT_DIR))
from src.utils.sampler.Sampler import Sampler, BuildstockBatchArguments, MapHPXML

import warnings
warnings.filterwarnings('ignore', category=UserWarning, module='openpyxl')

# ==================== CONFIGURATION ====================

st.set_page_config(
    page_title="ResStock-QC Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/yourusername/LTE-Sampler-Residential',
        'Report a bug': "https://github.com/yourusername/LTE-Sampler-Residential/issues",
        'About': "# ResStock-QC Dashboard v2.0\nBayesian Network sampling tool for residential buildings."
    }
)

# Custom CSS for enhanced styling
#.block-container {max-width: 1400px; padding-top: 0.5rem;}
#    /* Prevent horizontal overflow */
#    body, .block-container {overflow-x: hidden;}
#    /* Make embedded SVGs scale */
#    .bn-wrapper svg {max-width:100%; height:auto;}
#    /* Reduce padding in dataframes (compact mode toggle will add class) */
#    .compact .stDataFrame div[data-testid="stGrid"] {font-size:0.78rem;}
st.markdown("""
<style>
    .main {
        padding: 0rem 1rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 0px 24px;
        background-color: #f0f2f6;
        border-radius: 8px 8px 0px 0px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ff4b4b;
        color: white;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #ff4b4b;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .warning-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
    }
    .error-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
    }
</style>
""", unsafe_allow_html=True)

# ==================== SESSION STATE INITIALIZATION ====================

if 'simulation_history' not in st.session_state:
    st.session_state.simulation_history = []
if 'settings' not in st.session_state:
    st.session_state.settings = {}
if 'last_simulation' not in st.session_state:
    st.session_state.last_simulation = None

# ==================== CACHING FUNCTIONS ====================

@st.cache_resource
def load_sampler(path):
    """Load and cache the Bayesian Network sampler."""
    ins = Sampler()
    ins.Load_BN(path)
    return ins

@st.cache_data(hash_funcs={gum.BayesNet: lambda b: id(b)})
def bn_svg(bn, evs=None, Inference=True, size=15):
    """Generate and cache SVG visualization of Bayesian Network."""
    if Inference:
        svgtxt = gum.lib.image.dot_as_svg_string(
            gum.lib._colors.prepareDot(gum.lib.image.prepareShowInference(bn, evs=evs)),
            size=size
        )
    else:
        fig = gum.lib.bn2graph.BN2dot(bn)
        svgtxt = gum.lib.image.dot_as_svg_string(gum.lib._colors.prepareDot(fig), size=size)
    return svgtxt

@st.cache_data
def load_data_description():
    """Load and cache data description."""
    return pd.read_csv(PROJECT_DIR + "/data/processed/Data_description.csv", index_col=0)

# ==================== UTILITY FUNCTIONS ====================

def export_to_excel(dataframes_dict):
    """Export multiple dataframes to Excel with multiple sheets."""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        for sheet_name, df in dataframes_dict.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    return output.getvalue()

def create_distribution_plot(df, column):
    """Create interactive distribution plot."""
    if df[column].dtype in ['int64', 'float64']:
        fig = px.histogram(df, x=column, title=f'Distribution de {column}',
                          color_discrete_sequence=['#ff4b4b'])
    else:
        value_counts = df[column].value_counts()
        fig = px.bar(x=value_counts.index, y=value_counts.values,
                    title=f'Distribution de {column}',
                    labels={'x': column, 'y': 'Fréquence'},
                    color_discrete_sequence=['#ff4b4b'])
    fig.update_layout(showlegend=False)
    return fig

def create_correlation_heatmap(df):
    """Create correlation heatmap for numerical columns."""
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 1:
        corr = df[numeric_cols].corr()
        fig = px.imshow(corr, 
                       labels=dict(color="Corrélation"),
                       x=corr.columns,
                       y=corr.columns,
                       color_continuous_scale='RdBu_r',
                       aspect="auto")
        fig.update_layout(title="Matrice de corrélation")
        return fig
    return None

def style_dataframe(df):
    """Apply styling to dataframe for better visualization."""
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if numeric_cols:
        return df.style.background_gradient(subset=numeric_cols, cmap="RdYlGn").format("{:.3f}", subset=numeric_cols)
    return df

def bn_posterior(bn, evidence: dict, varname: str):
    """
    Return posterior distribution (dict state->prob) for varname given evidence.
    Uses bn.variable(...) to get labels instead of post.var().
    """
    if varname not in [bn.variable(i).name() for i in bn.nodes()]:
        return None
    ie = gum.LazyPropagation(bn)
    if evidence:
        ie.setEvidence(evidence)
    ie.makeInference()
    pot = ie.posterior(varname)
    var = bn.variable(bn.idFromName(varname))
    states = [var.label(i) for i in range(var.domainSize())]
    probs = [float(pot[i]) for i in range(var.domainSize())]
    return dict(zip(states, probs))
# ==================== SIDEBAR CONFIGURATION ====================

def render_sidebar():
    """Render enhanced sidebar with settings and controls."""
    with st.sidebar:
        st.image("https://via.placeholder.com/150x50/ff4b4b/ffffff?text=ResStock-QC", use_container_width=True)
                
        # Data folder selector
        st.subheader("📁 Dossiers de données")
        data_output_dir = os.path.join(PROJECT_DIR, "data", "output")
        
        if os.path.isdir(data_output_dir):
            csv_files = ["<Aucun>"] + sorted([f for f in os.listdir(data_output_dir) 
                                             if f.lower().endswith(".csv")])
            selected_file = st.selectbox("📊 Fichiers CSV disponibles", csv_files)
            
            if selected_file != "<Aucun>":
                file_path = os.path.join(data_output_dir, selected_file)
                try:
                    df_preview = pd.read_csv(file_path)
                    st.info(f"📋 {len(df_preview)} lignes × {len(df_preview.columns)} colonnes")
                    
                    if st.button("📥 Charger le fichier"):
                        st.session_state.loaded_file = df_preview
                        st.success("Fichier chargé avec succès!")
                except Exception as e:
                    st.error(f"Erreur: {e}")
        
        # Simulation history
        st.markdown("---")
        st.subheader("📜 Historique")
        if st.session_state.simulation_history:
            st.metric("Simulations effectuées", len(st.session_state.simulation_history))
            if st.button("🗑️ Effacer l'historique"):
                st.session_state.simulation_history = []
                st.rerun()
        else:
            st.info("Aucune simulation effectuée")
        
        # System info
        st.markdown("---")
        st.subheader("ℹ️ Informations système")
        st.text(f"Python: {sys.version.split()[0]}")
        st.text(f"Streamlit: {st.__version__}")
        st.text(f"PyAgrum: {gum.__version__}")

# ==================== PAGE: ECHANTILLONNEUR ====================

def Page_Echantilloneur():
    """Enhanced sampling page with advanced features."""
    st.title("🏠 ResStock-QC - Échantillonneur")
    st.markdown("Génération d'échantillons résidentiels basée sur un réseau bayésien (EUEMr 2022)")
    
    # Load sampler
    path = PROJECT_DIR + "/data/processed/bayesian_network/BN_EUEMr.XDSL"
    with st.spinner("🔄 Chargement du réseau bayésien..."):
        InsClsSampler = load_sampler(path)
    
    lst_NOEUD = InsClsSampler.lst_NOEUD
    LIST_Dict = InsClsSampler.LIST_Dict
    
    # ===== STEP 1: Parameter Selection =====
    st.header("📝 Étape 1 - Configuration des paramètres")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Variables imposées")
        
        # Quick preset selection
        presets = {
            "Aucun": {},
            "Maison unifamiliale": {"Type_Logement": "Maison individuelle"},
            "Appartement récent": {"Type_Logement": "Appartement", "An_Construction": "[2000 - 2010)"},
        }
        
        selected_preset = st.selectbox("🎯 Préréglages rapides", list(presets.keys()))
        
        if selected_preset != "Aucun":
            st.session_state.settings = presets[selected_preset]
        
        # Advanced parameter selection
        with st.expander("⚙️ Sélection avancée des variables", expanded=True):
            # Search filter
            search = st.text_input("🔍 Rechercher une variable", "")
            filtered_nodes = [n for n in lst_NOEUD if search.lower() in n.lower()]
            
            Noeuds_contraints = st.multiselect(
                "Sélectionner les variables à contraindre:",
                filtered_nodes if search else lst_NOEUD,
                default=list(st.session_state.settings.keys())
            )
            
            settings = {}
            for input_var in Noeuds_contraints:
                col_a, col_b = st.columns([1, 2])
                with col_a:
                    st.markdown(f"**{input_var}**")
                with col_b:
                    default_idx = 0
                    if input_var in st.session_state.settings:
                        try:
                            default_idx = list(LIST_Dict[input_var].values()).index(
                                st.session_state.settings[input_var]
                            )
                        except ValueError:
                            pass
                    
                    settings[input_var] = st.selectbox(
                        f"Valeur pour {input_var}",
                        options=list(LIST_Dict[input_var].values()),
                        index=default_idx,
                        key=f"select_{input_var}"
                    )
            
            st.session_state.settings = settings
    
    with col2:
        st.subheader("📊 Résumé de la configuration")
        if st.session_state.settings:
            for key, value in st.session_state.settings.items():
                st.markdown(f"**{key}:** `{value}`")
            
            # Save/Load configuration
            if st.button("💾 Sauvegarder la configuration"):
                config_json = json.dumps(st.session_state.settings, indent=2)
                st.download_button(
                    "📥 Télécharger config.json",
                    config_json,
                    "configuration.json",
                    "application/json"
                )
            
            uploaded_config = st.file_uploader("📤 Charger une configuration", type=['json'])
            if uploaded_config:
                try:
                    config = json.load(uploaded_config)
                    st.session_state.settings = config
                    st.success("Configuration chargée!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erreur lors du chargement: {e}")
        else:
            st.info("Aucune variable contrainte sélectionnée")
    
    st.markdown("---")
    
    # ===== STEP 2: Simulation =====
    st.header("🚀 Étape 2 - Simulation")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        Nombre_de_Samples = st.number_input(
            "Nombre d'échantillons:",
            min_value=1,
            max_value=10000,
            value=100,
            step=10
        )
    
    with col2:
        seed = st.number_input("🎲 Graine aléatoire (0 = aléatoire)", 
                              min_value=0, max_value=99999, value=0)
    
    with col3:
        export_format = st.multiselect(
            "📦 Formats d'export",
            ["CSV", "Excel", "JSON"],
            default=["CSV"]
        )
    
    # Advanced options
    with st.expander("⚙️ Options avancées"):
        col_a, col_b = st.columns(2)
        with col_a:
            add_statistics = st.checkbox("📈 Ajouter statistiques descriptives", value=True)
            add_visualizations = st.checkbox("📊 Générer visualisations", value=True)
        with col_b:
            validate_data = st.checkbox("✅ Valider les données", value=True)
            save_history = st.checkbox("💾 Sauvegarder dans l'historique", value=True)
    
    # Simulation button
    simulate_btn = st.button("▶️ Lancer la simulation", type="primary", use_container_width=True)
    
    if simulate_btn:
        start_time = time.time()
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Step 1: BN Sampling
            status_text.text("🔄 Échantillonnage du réseau bayésien...")
            progress_bar.progress(20)
            
            if seed > 0:
                np.random.seed(seed)
            
            df = InsClsSampler.do_Sampling(Nombre_de_Samples, evs=st.session_state.settings)
            lst_dct_args = df.to_dict(orient='records')
            
            # Step 2: Add external variables
            status_text.text("➕ Ajout de variables additionnelles...")
            progress_bar.progress(40)
            
            Bba = BuildstockBatchArguments()
            lst_dct_args2 = Bba.sampling(lst_dct_args)
            lst_dct_args = [d1 | d2 for d1, d2 in zip(lst_dct_args, lst_dct_args2)]
            
            # Step 3: HPXML Mapping
            status_text.text("🗺️ Mapping vers HPXML...")
            progress_bar.progress(60)
            
            MapSample = MapHPXML()
            lst_dct_HPXML = MapSample.run(lst_dct_args)
            
            # Step 4: Create DataFrames
            status_text.text("📊 Génération des tableaux...")
            progress_bar.progress(80)
            
            dfargs = pd.DataFrame(lst_dct_args)
            dfHPXML = pd.DataFrame(lst_dct_HPXML)
            dfAll = pd.concat([dfargs, dfHPXML], axis=1)
            
            # Data validation
            if validate_data:
                status_text.text("✅ Validation des données...")
                null_counts = dfAll.isnull().sum()
                if null_counts.sum() > 0:
                    st.warning(f"⚠️ {null_counts.sum()} valeurs manquantes détectées")
            
            progress_bar.progress(100)
            status_text.text("✅ Simulation terminée!")
            
            elapsed_time = time.time() - start_time
            
            # Save to session state
            st.session_state.last_simulation = {
                'dfargs': dfargs,
                'dfHPXML': dfHPXML,
                'dfAll': dfAll,
                'settings': st.session_state.settings.copy(),
                'n_samples': Nombre_de_Samples,
                'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
                'elapsed_time': elapsed_time
            }
            
            if save_history:
                st.session_state.simulation_history.append(st.session_state.last_simulation)
            
            st.markdown(f"""
            <div class="success-box">
                ✅ <strong>Simulation réussie!</strong><br>
                📊 {Nombre_de_Samples} échantillons générés en {elapsed_time:.2f} secondes<br>
                📈 Vitesse: {Nombre_de_Samples/elapsed_time:.1f} échantillons/seconde
            </div>
            """, unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"❌ Erreur lors de la simulation: {str(e)}")
            st.exception(e)
            return
    
    # ===== STEP 3: Results Display =====
    if st.session_state.last_simulation:
        st.markdown("---")
        st.header("📊 Étape 3 - Résultats")
        
        sim = st.session_state.last_simulation
        dfargs = sim['dfargs']
        dfHPXML = sim['dfHPXML']
        dfAll = sim['dfAll']
        
        # Initialize active tab in session state
        if 'active_results_tab' not in st.session_state:
            st.session_state.active_results_tab = 0
        
        # Results tabs
        tab_names = [
            "📋 Échantillons", 
            "🗺️ Mapping HPXML", 
            "📊 Statistiques", 
            "📈 Visualisations",
            "💾 Export"
        ]
        
        # Create tab selector that persists across reruns
        selected_tab_name = st.radio(
            "Sélectionner une section:",
            tab_names,
            index=st.session_state.active_results_tab,
            horizontal=True,
            key="results_tab_selector"
        )
        
        # Update session state
        st.session_state.active_results_tab = tab_names.index(selected_tab_name)
        
        st.markdown("---")
        
        # Tab 1: Échantillons
        if selected_tab_name == "📋 Échantillons":
            st.subheader("Données d'échantillonnage")
            
            # Filters
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                search_col = st.text_input("🔍 Rechercher dans les colonnes", "", key="search_col_tab1")
            with col_f2:
                display_mode = st.radio("Mode d'affichage", ["Aperçu (50 lignes)", "Complet"], horizontal=True, key="display_mode_tab1")
            
            # Filter columns
            if search_col:
                filtered_cols = [c for c in dfargs.columns if search_col.lower() in c.lower()]
                df_display = dfargs[filtered_cols]
            else:
                df_display = dfargs
            
            # Display
            if display_mode == "Aperçu (50 lignes)":
                st.dataframe(style_dataframe(df_display.head(50)), use_container_width=True)
            else:
                st.dataframe(style_dataframe(df_display), use_container_width=True)
        
        # Tab 2: Mapping HPXML
        elif selected_tab_name == "🗺️ Mapping HPXML":
            st.subheader("Mapping HPXML")
            st.dataframe(style_dataframe(dfHPXML), use_container_width=True)
        
        # Tab 3: Statistiques
        elif selected_tab_name == "📊 Statistiques":
            st.subheader("Statistiques descriptives")
            
            if add_statistics:
                # Numeric statistics
                numeric_cols = dfAll.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) > 0:
                    st.markdown("#### Variables numériques")
                    st.dataframe(dfAll[numeric_cols].describe().T, use_container_width=True)
                
                # Categorical statistics
                cat_cols = dfAll.select_dtypes(include=['object']).columns
                if len(cat_cols) > 0:
                    st.markdown("#### Variables catégorielles")
                    selected_cat = st.selectbox("Sélectionner une variable", cat_cols, key="selected_cat_tab3")
                    value_counts = dfAll[selected_cat].value_counts()
                    
                    col_stat1, col_stat2 = st.columns(2)
                    with col_stat1:
                        st.dataframe(value_counts.reset_index(name='Fréquence'), use_container_width=True)
                    with col_stat2:
                        fig = px.pie(values=value_counts.values, names=value_counts.index,
                                    title=f"Distribution de {selected_cat}")
                        st.plotly_chart(fig, use_container_width=True)
        
        # Tab 4: Visualisations
        elif selected_tab_name == "📈 Visualisations":
            if add_visualizations:
                st.subheader("Visualisations interactives")
                
                # Initialize viz_type in session state to prevent reset
                if 'viz_type' not in st.session_state:
                    st.session_state.viz_type = "Distribution"
                
                viz_type = st.selectbox(
                    "Type de visualisation", 
                    ["Distribution", "Corrélation", "Box Plot", "Comparaison BN vs Échantillon"],
                    index=["Distribution", "Corrélation", "Box Plot", "Comparaison BN vs Échantillon"].index(st.session_state.viz_type),
                    key="viz_type_selector"
                )
                
                # Update session state
                st.session_state.viz_type = viz_type
                   
                if viz_type == "Distribution":
                    selected_col = st.selectbox("Sélectionner une colonne", dfAll.columns, key="dist_col")
                    fig = create_distribution_plot(dfAll, selected_col)
                    st.plotly_chart(fig, use_container_width=True)
                
                elif viz_type == "Corrélation":
                    fig = create_correlation_heatmap(dfAll)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("Pas assez de colonnes numériques pour la corrélation")
                
                elif viz_type == "Box Plot":
                    numeric_cols = dfAll.select_dtypes(include=[np.number]).columns
                    if len(numeric_cols) > 0:
                        selected_col = st.selectbox("Sélectionner une variable", numeric_cols, key="box_col")
                        fig = px.box(dfAll, y=selected_col, title=f"Box Plot: {selected_col}")
                        st.plotly_chart(fig, use_container_width=True)

                elif viz_type == "Comparaison BN vs Échantillon":
                    st.markdown("Comparer la distribution théorique (posterior BN) avec la distribution empirique des échantillons.")
                    
                    bn_vars = [c for c in dfAll.columns if c in lst_NOEUD]
                    
                    if not bn_vars:
                        st.warning("Aucune variable du réseau bayésien trouvée dans les données.")
                    else:
                        compare_var = st.selectbox(
                            "Variable catégorielle du réseau bayésien",
                            bn_vars,
                            key="compare_var_selector"
                        )
                        
                        if compare_var:
                            # Théorique (posterior)
                            posterior_dict = bn_posterior(InsClsSampler.bn, st.session_state.settings, compare_var)
                            if posterior_dict is None:
                                st.warning("Variable non présente dans le BN.")
                            else:
                                # Empirique
                                emp_counts = dfAll[compare_var].value_counts(normalize=True)
                                states = list(posterior_dict.keys())
                                posterior_vals = [posterior_dict.get(s, 0) for s in states]
                                empirical_vals = [emp_counts.get(s, 0) for s in states]

                                df_compare = pd.DataFrame({
                                    "État": states,
                                    "Posterior_BN": posterior_vals,
                                    "Empirique_Échantillon": empirical_vals,
                                    "Diff": np.array(empirical_vals) - np.array(posterior_vals)
                                })

                                colc1, colc2 = st.columns([2.5,1.5])
                                with colc1:
                                    fig = go.Figure()
                                    fig.add_trace(go.Bar(name='Posterior BN', x=states, y=posterior_vals, marker_color="#1f77b4"))
                                    fig.add_trace(go.Bar(name='Empirique', x=states, y=empirical_vals, marker_color="#ff4b4b"))
                                    fig.update_layout(barmode='group', title=f"Distribution - {compare_var}")
                                    st.plotly_chart(fig, use_container_width=True)
                                with colc2:
                                    st.dataframe(df_compare, use_container_width=True)

                                show_diff = st.checkbox("Afficher graphique des différences (Empirique - BN)", key="show_diff_checkbox")
                                if show_diff:
                                    fig_diff = go.Figure()
                                    fig_diff.add_trace(go.Bar(name='Différence', x=states, y=df_compare["Diff"], marker_color="#ff9f0a"))
                                    fig_diff.update_layout(title=f"Différences Empirique - Posterior BN ({compare_var})")
                                    st.plotly_chart(fig_diff, use_container_width=True)
        
        # Tab 5: Export
        elif selected_tab_name == "💾 Export":
            st.subheader("Export des données")
            
            col_e1, col_e2, col_e3 = st.columns(3)
            
            with col_e1:
                if "CSV" in export_format:
                    st.download_button(
                        label="📥 Télécharger CSV",
                        data=dfAll.to_csv(index=False).encode('utf-8'),
                        file_name=f'resultats_{time.strftime("%Y%m%d_%H%M%S")}.csv',
                        mime='text/csv',
                        use_container_width=True
                    )
            
            with col_e2:
                if "Excel" in export_format:
                    excel_data = export_to_excel({
                        'Echantillons': dfargs,
                        'HPXML': dfHPXML,
                        'Complet': dfAll
                    })
                    st.download_button(
                        label="📥 Télécharger Excel",
                        data=excel_data,
                        file_name=f'resultats_{time.strftime("%Y%m%d_%H%M%S")}.xlsx',
                        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                        use_container_width=True
                    )
            
            with col_e3:
                if "JSON" in export_format:
                    json_data = dfAll.to_json(orient='records', indent=2)
                    st.download_button(
                        label="📥 Télécharger JSON",
                        data=json_data,
                        file_name=f'resultats_{time.strftime("%Y%m%d_%H%M%S")}.json',
                        mime='application/json',
                        use_container_width=True
                    )

# ==================== PAGE: BAYESIAN NETWORK ====================

def BaysianNetwork():
    """Enhanced Bayesian Network visualization and exploration page."""
    st.title("🕸️ Réseau Bayésien - EUEMr 2022")
    st.markdown("Exploration et analyse du réseau bayésien")
    
    # Load sampler
    path = PROJECT_DIR + "/data/processed/bayesian_network/BN_EUEMr.XDSL"
    with st.spinner("🔄 Chargement du réseau bayésien..."):
        InsClsSampler = load_sampler(path)
    
    lst_NOEUD = InsClsSampler.lst_NOEUD
    LIST_Dict = InsClsSampler.LIST_Dict
    pdfDataDescription = load_data_description()
    
    # Enhanced tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Description",
        "🕸️ Réseau",
        "📋 Nœuds",
        "🎲 CPT",
        "🔍 Inférence",
        "📈 Analyse"
    ])
    
    with tab1:
        st.subheader("Description des données")
        
        # Search functionality
        search_desc = st.text_input("🔍 Rechercher dans les descriptions", "")
        if search_desc:
            mask = pdfDataDescription.apply(lambda row: row.astype(str).str.contains(search_desc, case=False).any(), axis=1)
            st.dataframe(pdfDataDescription[mask], use_container_width=True)
        else:
            st.dataframe(pdfDataDescription, use_container_width=True)
        
        # Summary statistics
        st.markdown("#### Statistiques du réseau")
        col_s1, col_s2, col_s3 = st.columns(3)
        col_s1.metric("Nombre de nœuds", len(lst_NOEUD))
        col_s2.metric("Nombre d'arcs", InsClsSampler.bn.sizeArcs())
        col_s3.metric("Complexité max", max([InsClsSampler.bn.variable(i).domainSize() for i in InsClsSampler.bn.nodes()]))
    
    with tab2:
        st.subheader("Visualisation du réseau")
        
        col_v1, col_v2, col_v3 = st.columns(3)
        with col_v1:
            check_stats = st.checkbox("📊 Afficher statistiques", value=False)
        with col_v2:
            selected_size = st.slider("📏 Taille", 5, 50, 15, 1)
        with col_v3:
            show_labels = st.checkbox("🏷️ Afficher étiquettes", value=True)
        
        if st.button("🎨 Générer la visualisation", type="primary"):
            with st.spinner("Génération en cours..."):
                svgtxt = bn_svg(InsClsSampler.bn, evs=None, Inference=check_stats, size=selected_size)
                components.html(svgtxt, height=900, scrolling=True)
    
    with tab3:
        st.subheader("Liste des nœuds et valeurs possibles")
        
        # Node search
        search_node = st.text_input("🔍 Rechercher un nœud", "")
        filtered_nodes = [n for n in lst_NOEUD if search_node.lower() in n.lower()]
        
        # Display as expandable cards
        for node in filtered_nodes:
            with st.expander(f"📌 {node} ({len(LIST_Dict[node])} valeurs possibles)"):
                values_list = list(LIST_Dict[node].values())
                
                # Display as columns for better readability
                n_cols = 3
                cols = st.columns(n_cols)
                for idx, val in enumerate(values_list):
                    cols[idx % n_cols].markdown(f"• {val}")
                
                # Node statistics
                node_id = InsClsSampler.bn.idFromName(node)
                n_parents = len(InsClsSampler.bn.parents(node_id))
                n_children = len(InsClsSampler.bn.children(node_id))
                
                st.markdown(f"**Parents:** {n_parents} | **Enfants:** {n_children}")
    
    with tab4:
        st.subheader("Tables de Probabilités Conditionnelles (CPT)")
        
        col_cpt1, col_cpt2 = st.columns([2, 1])
        
        with col_cpt1:
            selected_node = st.selectbox("🎯 Sélectionner un nœud", lst_NOEUD)
        
        with col_cpt2:
            cpt_display = st.radio("Format d'affichage", ["Tableau", "Heatmap"], horizontal=True)
        
        if selected_node:
            cpt = InsClsSampler.bn.cpt(selected_node)
            cpt_df = cpt.topandas()
            
            if cpt_display == "Heatmap":
                st.dataframe(
                    cpt_df.style.background_gradient(axis=None, cmap='RdYlGn', low=0.0, high=1.0),
                    use_container_width=True
                )
            else:
                st.dataframe(cpt_df, use_container_width=True)
            
            # Export CPT
            st.download_button(
                "📥 Exporter cette CPT (CSV)",
                cpt_df.to_csv(index=True).encode('utf-8'),
                f"cpt_{selected_node}.csv",
                "text/csv"
            )
    
    with tab5:
        st.subheader("Moteur d'inférence")
        
        st.markdown("""
        Configurez des observations (evidence) et observez l'impact sur les distributions conditionnelles.
        """)
        
        col_inf1, col_inf2 = st.columns([2, 1])
        
        with col_inf1:
            st.markdown("#### 🎯 Configuration des observations")
            
            settings = {}
            Noeuds_contraints = st.multiselect("Variables à observer:", lst_NOEUD)
            
            for input_var in Noeuds_contraints:
                settings[input_var] = st.selectbox(
                    f"Valeur observée pour **{input_var}**",
                    options=list(LIST_Dict[input_var].values()),
                    key=f"inf_{input_var}"
                )
        
        with col_inf2:
            st.markdown("#### ⚙️ Paramètres de visualisation")
            selected_size2 = st.slider("Taille du graphique", 5, 50, 15, 1, key="inf_size")
            show_probs = st.checkbox("Afficher probabilités", value=True)
            num_vars_to_show = st.slider("Nombre de variables à afficher", 1, min(20, len(lst_NOEUD)), 5, 1, key="num_vars_inference")
        
        if st.button("🔍 Effectuer l'inférence", type="primary"):
            with st.spinner("Calcul des inférences..."):
                svgtxt_inf = bn_svg(InsClsSampler.bn, evs=settings, Inference=True, size=selected_size2)
                components.html(svgtxt_inf, height=900, scrolling=True)
            
            # Show marginal distributions
            if show_probs and settings:
                st.markdown("#### 📊 Distributions marginales après observation")
                ie = gum.LazyPropagation(InsClsSampler.bn)
                ie.setEvidence(settings)  # Set all evidence at once
                ie.makeInference()
                
                # Convert to list and get subset
                all_nodes = list(lst_NOEUD)
                # Filter out observed nodes
                unobserved_nodes = [n for n in all_nodes if n not in settings]
                
                # Show selected number of variables
                nodes_to_display = unobserved_nodes[:num_vars_to_show]
                
                st.markdown(f"**Affichage des {len(nodes_to_display)} premières variables non observées:**")
                
                for node_name in nodes_to_display:
                    try:
                        posterior = ie.posterior(node_name)
                        posterior_df = posterior.topandas()
                        
                        with st.expander(f"📊 {node_name}", expanded=False):
                            col_p1, col_p2 = st.columns([2, 1])
                            with col_p1:
                                # FIX: Handle different posterior_df formats correctly
                                if isinstance(posterior_df, pd.Series):
                                    # Simple Series - direct access
                                    x_vals = [str(x) for x in posterior_df.index.tolist()]
                                    y_vals = posterior_df.values.tolist()
                                elif isinstance(posterior_df, pd.DataFrame):
                                    # DataFrame case - may have multi-index or single column
                                    if posterior_df.shape[1] == 1:
                                        # Single column DataFrame
                                        x_vals = [str(idx) for idx in posterior_df.index]
                                        y_vals = posterior_df.iloc[:, 0].values.tolist()
                                    else:
                                        # Multi-column DataFrame - flatten and use first column
                                        posterior_df = posterior_df.reset_index(drop=False)
                                        # Get the last column (probabilities)
                                        prob_col = posterior_df.columns[-1]
                                        # Create labels from all other columns
                                        label_cols = [c for c in posterior_df.columns if c != prob_col]
                                        if label_cols:
                                            x_vals = posterior_df[label_cols].astype(str).agg(' | '.join, axis=1).tolist()
                                        else:
                                            x_vals = [str(i) for i in range(len(posterior_df))]
                                        y_vals = posterior_df[prob_col].tolist()
                                else:
                                    # Fallback for unexpected types
                                    x_vals = [str(i) for i in range(len(posterior_df))]
                                    y_vals = list(posterior_df)
                                
                                # Ensure same length before plotting
                                if len(x_vals) != len(y_vals):
                                    st.warning(f"Incohérence de données pour {node_name}: {len(x_vals)} labels vs {len(y_vals)} valeurs")
                                    # Truncate to shortest
                                    min_len = min(len(x_vals), len(y_vals))
                                    x_vals = x_vals[:min_len]
                                    y_vals = y_vals[:min_len]
                                
                                # Create figure
                                fig = px.bar(
                                    x=x_vals,
                                    y=y_vals,
                                    labels={'x': 'État', 'y': 'Probabilité'},
                                    title=f"Distribution posterieure - {node_name}",
                                    color_discrete_sequence=['#ff4b4b']
                                )
                                fig.update_layout(
                                    xaxis_title="État",
                                    yaxis_title="Probabilité",
                                    showlegend=False,
                                    xaxis={'tickangle': -45} if len(x_vals) > 5 else {}
                                )
                                st.plotly_chart(fig, use_container_width=True)
                            with col_p2:
                                st.dataframe(posterior_df, use_container_width=True)
                    except Exception as e:
                        st.error(f"Erreur pour {node_name}: {e}")
                        import traceback
                        st.code(traceback.format_exc())
            elif show_probs and not settings:
                st.info("Configurez au moins une observation pour voir les distributions marginales.")
                
    with tab6:
        st.subheader("Analyse structurelle du réseau")
        
        # Network metrics
        st.markdown("#### Métriques du réseau")
        
        metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)
        
        metrics_col1.metric("🔢 Nœuds", InsClsSampler.bn.size())
        metrics_col2.metric("🔗 Arcs", InsClsSampler.bn.sizeArcs())
        metrics_col3.metric("📊 États totaux", sum([InsClsSampler.bn.variable(i).domainSize() for i in InsClsSampler.bn.nodes()]))
        metrics_col4.metric("🎯 Paramètres", InsClsSampler.bn.log10DomainSize())
        
        # Node degree distribution
        st.markdown("#### Distribution des degrés des nœuds")
        
        degrees = []
        for node_id in InsClsSampler.bn.nodes():
            in_degree = len(InsClsSampler.bn.parents(node_id))
            out_degree = len(InsClsSampler.bn.children(node_id))
            degrees.append({
                'Node': InsClsSampler.bn.variable(node_id).name(),
                'In-Degree': in_degree,
                'Out-Degree': out_degree,
                'Total': in_degree + out_degree
            })
        
        df_degrees = pd.DataFrame(degrees).sort_values('Total', ascending=False)
        
        col_deg1, col_deg2 = st.columns(2)
        
        with col_deg1:
            st.dataframe(df_degrees.head(10), use_container_width=True)
        
        with col_deg2:
            fig = px.histogram(df_degrees, x='Total', nbins=20,
                             title="Distribution des degrés totaux")
            st.plotly_chart(fig, use_container_width=True)

# ==================== MAIN ====================

def main():
    """Main application entry point."""
    
    # Render sidebar
    render_sidebar()
    
    # Page navigation
    pages = {
        "Échantillonneur": [
            st.Page(Page_Echantilloneur, title="Échantillonneur", icon="🏠"),
            st.Page(BaysianNetwork, title="Réseau Bayésien", icon="🕸️")
        ]
    }
    
    pg = st.navigation(pages)
    pg.run()

if __name__ == "__main__":
    main()