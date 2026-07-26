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
uv run streamlit run "ui/Dashboard.py"

Author: cv1751 - Brice Le Lostec
Version: 2.0
Python: 3.11
"""

import os
import sys
import time
import json
import shutil
import numpy as np
import pandas as pd
import pyagrum as gum
# Imported for their side effect of registering the submodule on `gum`; the code
# below reaches them as gum.lib.image / gum.lib._colors / gum.lib.bn2graph.
# pyagrum.lib.notebook is deliberately NOT imported: it is unused here and drags in
# matplotlib_inline, which is not needed to render the network.
import pyagrum.lib.image
import pyagrum.lib._colors
import pyagrum.lib.bn2graph
import streamlit as st
import streamlit.components.v1 as components
from io import BytesIO
import plotly.express as px
import plotly.graph_objects as go

FILE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(FILE_DIR + "/../")
sys.path.append(os.path.join(PROJECT_DIR))
from src.utils.sampler.Sampler import Sampler
from src.utils.sampler.Mapping import BuildstockBatchArguments, MapHPXML
from src.utils.hpxml.hpxml_columns import stabilize_export
# Same rule the calibration pipeline uses: the Calgary network once it has been
# built, the Quebec original otherwise. Imported rather than repeated so the two
# cannot drift apart.
from calgary_adaptation.apply_to_sampler import default_bn

import warnings
warnings.filterwarnings('ignore', category=UserWarning, module='openpyxl')

# ==================== CONFIGURATION ====================

st.set_page_config(
    page_title="ResStock-QC Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/yourusername/LTE-Sampler-Residential',
        #'Report a bug': "https://github.com/yourusername/LTE-Sampler-Residential/issues",
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
    ins = Sampler(path)
    return ins

def node_states(LIST_Dict, node):
    """States of `node` in the network's own order.

    Bn.yml keys states by stringified index and is written with sorted keys, so
    '10' sorts between '1' and '2'. Any node with more than ten states would
    otherwise be listed scrambled -- Superficie_Totale offers '>= 5000' third,
    between '[500 - 1000)' and '[1000 - 1500)'."""
    return [v for _, v in sorted(LIST_Dict[node].items(), key=lambda kv: int(kv[0]))]


def bn_banner(path):
    """Say which network the page is showing.

    Québec and Calgary differ on 12 of 41 nodes and are otherwise identical in the
    UI -- same node names, same state labels, same layout. Without this, falling
    back to the Québec network is invisible, and that is how someone ends up
    quoting Québec numbers as Calgary ones."""
    name = os.path.basename(path)
    if name == "BN_Calgary.XDSL":
        st.caption(f"Network: **{name}** - Calgary probabilities "
                   f"(12 of 41 nodes recalibrated from 73,927 audited homes).")
    else:
        st.warning(f"Network: **{name}** - these are QUÉBEC probabilities. Build the "
                   f"Calgary network with "
                   f"`uv run python calgary_adaptation/apply_to_sampler.py bn`.")


def graphviz_available():
    """Check that the Graphviz `dot` executable can be found on PATH."""
    return shutil.which("dot") is not None

GRAPHVIZ_MISSING_MSG = (
    "Graphviz is required to draw the network but `dot` was not found on PATH.\n\n"
    "Install it with `winget install --id Graphviz.Graphviz -e`, add "
    "`C:\\Program Files\\Graphviz\\bin` to PATH, then restart the terminal and this app."
)

def histogram_targets(bn):
    """Nodes worth drawing a posterior histogram for.

    Single-state variables (Territoire_HQ='Calgary', Region_Administrative='Alberta'
    after the Calgary collapse) carry no information, so they are drawn as plain
    boxes instead of a degenerate 100% bar.
    """
    return {n for n in bn.names() if bn.variable(n).domainSize() > 1}

class MarginalisingInference:
    """Inference engine wrapper that forces posteriors to be one-dimensional.

    pyAgrum does not marginalise out variables whose domain has a single state, so
    with Territoire_HQ='Calgary' in the network `posterior(name)` returns a joint
    tensor (e.g. shape (1, 4) for Piscine_Type). pyagrum.lib.proba_histogram then
    hands that nested list to matplotlib's barh, which raises
    "TypeError: float() argument must be ... not 'NoneType'". Summing the extra
    single-state dimensions out restores the expected marginal.
    """

    def __init__(self, bn, engine):
        self._bn = bn
        self._engine = engine

    def __getattr__(self, item):
        return getattr(self._engine, item)

    def posterior(self, target):
        p = self._engine.posterior(target)
        if p.nbrDim() > 1:
            keep = target if isinstance(target, str) else self._bn.variable(target).name()
            p = p.sumOut([p.variable(i).name() for i in range(p.nbrDim())
                          if p.variable(i).name() != keep])
        return p

@st.cache_data(hash_funcs={gum.BayesNet: lambda b: id(b)})
def bn_svg(bn, evs=None, Inference=True, size=15):
    """Generate and cache SVG visualization of Bayesian Network."""
    targets = histogram_targets(bn) if Inference else set()
    if Inference and targets:
        engine = MarginalisingInference(bn, gum.LazyPropagation(bn))
        svgtxt = gum.lib.image.dot_as_svg_string(
            gum.lib._colors.prepareDot(
                gum.lib.image.prepareShowInference(bn, engine=engine, evs=evs, targets=targets)
            ),
            size=size
        )
    else:
        # No renderable node (or statistics disabled): show the structure only.
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
        fig = px.histogram(df, x=column, title=f'Distribution of {column}',
                          color_discrete_sequence=['#ff4b4b'])
    else:
        value_counts = df[column].value_counts()
        fig = px.bar(x=value_counts.index, y=value_counts.values,
                    title=f'Distribution of {column}',
                    labels={'x': column, 'y': 'Frequency'},
                    color_discrete_sequence=['#ff4b4b'])
    fig.update_layout(showlegend=False)
    return fig

def create_correlation_heatmap(df):
    """Create correlation heatmap for numerical columns."""
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 1:
        corr = df[numeric_cols].corr()
        fig = px.imshow(corr, 
                   labels=dict(color="Correlation"),
                   x=corr.columns,
                   y=corr.columns,
                   color_continuous_scale='RdBu_r',
                   aspect="auto")
        fig.update_layout(title="Correlation Matrix")
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
        #st.image("https://via.placeholder.com/150x50/ff4b4b/ffffff?text=ResStock-QC", use_container_width=True)
                
        # Data folder selector
        st.subheader("📁 Data folders")
        data_output_dir = os.path.join(PROJECT_DIR, "data", "output")
        
        if os.path.isdir(data_output_dir):
            csv_files = ["<None>"] + sorted([f for f in os.listdir(data_output_dir) 
                                             if f.lower().endswith(".csv")])
            selected_file = st.selectbox("📊 Available CSV files", csv_files)
            
            if selected_file != "<None>":
                file_path = os.path.join(data_output_dir, selected_file)
                try:
                    df_preview = pd.read_csv(file_path)
                    st.info(f"📋 {len(df_preview)} rows × {len(df_preview.columns)} columns")
                    
                    if st.button("📥 Load file"):
                        st.session_state.loaded_file = df_preview
                        st.success("File loaded successfully!")
                except Exception as e:
                    st.error(f"Error: {e}")
        
        # Simulation history
        st.markdown("---")
        st.subheader("📜 History")
        if st.session_state.simulation_history:
            st.metric("Simulations run", len(st.session_state.simulation_history))
            if st.button("🗑️ Clear history"):
                st.session_state.simulation_history = []
                st.rerun()
        else:
            st.info("No simulations run")
        
        # System info
        st.markdown("---")
        st.subheader("ℹ️ System information")
        st.text(f"Python: {sys.version.split()[0]}")
        st.text(f"Streamlit: {st.__version__}")
        st.text(f"PyAgrum: {gum.__version__}")

# ==================== PAGE: ECHANTILLONNEUR ====================

def Page_Echantilloneur():
    """Enhanced sampling page with advanced features."""
    st.title("🏠 ResStock-QC - Sampler")
    st.markdown("Residential sample generation based on a Bayesian network")
    
    # Load sampler
    path = default_bn()
    with st.spinner("🔄 Loading Bayesian network..."):
        InsClsSampler = load_sampler(path)
    bn_banner(path)
    
    lst_NOEUD = InsClsSampler.lst_NOEUD
    LIST_Dict = InsClsSampler.LIST_Dict
    
    # ===== STEP 1: Parameter Selection =====
    st.header("📝 Step 1 - Parameter configuration")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Constrained variables")
        
        # Quick preset selection
        presets = {
            "None": {},
            "Single-family house": {"Type_Logement": "Maison individuelle"},
            "Recent apartment": {"Type_Logement": "Appartement", "An_Construction": "[2000 - 2010)"},
        }
        
        selected_preset = st.selectbox("🎯 Quick presets", list(presets.keys()))
        
        # Initialize last_preset tracker ONCE here
        if 'last_preset' not in st.session_state:
            st.session_state.last_preset = "None"
        
        # Initialize selected nodes in session state if not exists
        if 'selected_constraint_nodes' not in st.session_state:
            st.session_state.selected_constraint_nodes = []
        
        # If preset changed, update the constraint nodes and force rerun
        if selected_preset != st.session_state.last_preset:
            st.session_state.last_preset = selected_preset
            if selected_preset != "None":
                st.session_state.settings = presets[selected_preset]
                st.session_state.selected_constraint_nodes = list(presets[selected_preset].keys())
            else:
                st.session_state.settings = {}
                st.session_state.selected_constraint_nodes = []
            st.rerun()  # Force rerun to update multiselect
        
        # Update settings if preset selected (for non-preset-change case)
        if selected_preset != "None" and not st.session_state.selected_constraint_nodes:
            st.session_state.settings = presets[selected_preset]
        
        # Advanced parameter selection
        with st.expander("⚙️ Advanced variable selection", expanded=True):
            # Search filter
            search = st.text_input("🔍 Search variable", "")
            filtered_nodes = [n for n in lst_NOEUD if search.lower() in n.lower()]
            
        # Multiselect with default from session_state
        Noeuds_contraints = st.multiselect(
            "Select variables to constrain:",
            filtered_nodes if search else lst_NOEUD,
            default=st.session_state.selected_constraint_nodes,
            key="multiselect_constraints"
        )
        
        # Update session_state after user interaction
        #st.session_state.selected_constraint_nodes = Noeuds_contraints
        
        settings = {}
        for input_var in Noeuds_contraints:
            col_a, col_b = st.columns([1, 2])
            with col_a:
                st.markdown(f"**{input_var}**")
            with col_b:
                default_idx = 0
                if input_var in st.session_state.settings:
                    try:
                        default_idx = node_states(LIST_Dict, input_var).index(
                            st.session_state.settings[input_var]
                        )
                    except ValueError:
                        pass
                
                settings[input_var] = st.selectbox(
                    f"Value for {input_var}",
                    options=node_states(LIST_Dict, input_var),
                    index=default_idx,
                    key=f"select_{input_var}"
                )
        
        st.session_state.settings = settings
    
    with col2:
        st.subheader("📊 Configuration summary")
        if st.session_state.settings:
            for key, value in st.session_state.settings.items():
                st.markdown(f"**{key}:** `{value}`")
            
            # Save/Load configuration
            if st.button("💾 Save configuration"):
                config_json = json.dumps(st.session_state.settings, indent=2)
                st.download_button(
                    "📥 Download config.json",
                    config_json,
                    "configuration.json",
                    "application/json"
                )
            
            uploaded_config = st.file_uploader("📤 Upload configuration", type=['json'])
            if uploaded_config:
                try:
                    config = json.load(uploaded_config)
                    st.session_state.settings = config
                    st.success("Configuration loaded!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error loading configuration: {e}")
        else:
            st.info("No constrained variables selected")
    
    st.markdown("---")
    
    # ===== STEP 2: Simulation =====
    st.header("🚀 Step 2 - Simulation")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        Nombre_de_Samples = st.number_input(
            "Number of samples:",
            min_value=1,
            max_value=10000,
            value=100,
            step=10
        )
    
    with col2:
        seed = st.number_input("🎲 Random seed (0 = random)", 
                              min_value=0, max_value=99999, value=0)
    
    with col3:
        export_format = st.multiselect(
            "📦 Export formats",
            ["CSV", "Excel", "JSON"],
            default=["CSV"]
        )
    
    # Advanced options
    with st.expander("⚙️ Advanced options"):
        col_a, col_b = st.columns(2)
        with col_a:
            add_statistics = st.checkbox("📈 Add descriptive statistics", value=True)
            add_visualizations = st.checkbox("📊 Generate visualizations", value=True)
        with col_b:
            validate_data = st.checkbox("✅ Validate data", value=True)
            save_history = st.checkbox("💾 Save to history", value=True)
    
    # Simulation button
    simulate_btn = st.button("▶️ Run simulation", type="primary", use_container_width=True)
    
    if simulate_btn:
        start_time = time.time()
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Step 1: BN Sampling
            status_text.text("🔄 Sampling Bayesian network...")
            progress_bar.progress(20)
            
            if seed > 0:
                np.random.seed(seed)
            
            df = InsClsSampler.GUM_Sampling(Nombre_de_Samples, evs=st.session_state.settings)
            lst_dct_args = df.to_dict(orient='records')
            
            # Step 2: Add external variables
            status_text.text("➕ Adding additional variables...")
            progress_bar.progress(40)

            lst_dct_args2 = InsClsSampler.resstock_args_sampling(lst_dct_args)
            # BN values win, matching Sampler.run() (Sampler.py:185), which
            # merges `d2 | d1` and calls lst_dct_args "prioritaire". This page
            # merged the other way round. Today the two agree by luck: the CSV
            # sampler's attribute list and the BN's node list share no key, so
            # neither dict can shadow the other. That is a property of the
            # current configuration, not a guarantee -- Infiltration already
            # exists as both a BN node and a housing_characteristics table, and
            # the day it joins BuildstockBatchArguments.listAttributs the two
            # code paths would silently disagree about a calibrated value.
            lst_dct_args = [d2 | d1 for d1, d2 in zip(lst_dct_args, lst_dct_args2)]
            
            # Step 3: HPXML Mapping
            status_text.text("🗺️ Mapping to HPXML...")
            progress_bar.progress(60)
            
            MapSample = MapHPXML()
            lst_dct_HPXML = MapSample.run(lst_dct_args)
            
            # Step 4: Create DataFrames
            status_text.text("📊 Generating tables...")
            progress_bar.progress(80)
            
            dfargs = pd.DataFrame(lst_dct_args)
            dfHPXML = pd.DataFrame(lst_dct_HPXML)
            dfAll = stabilize_export(dfargs, dfHPXML)
            
            # Data validation
            if validate_data:
                status_text.text("✅ Validating data...")
                null_counts = dfAll.isnull().sum()
                if null_counts.sum() > 0:
                    st.warning(f"⚠️ {null_counts.sum()} missing values detected")
            
            progress_bar.progress(100)
            status_text.text("✅ Simulation completed!")
            
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
                ✅ <strong>Simulation successful!</strong><br>
                📊 {Nombre_de_Samples} samples generated in {elapsed_time:.2f} seconds<br>
                📈 Speed: {Nombre_de_Samples/elapsed_time:.1f} samples/second
            </div>
            """, unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"❌ Error during simulation: {str(e)}")
            st.exception(e)
            return
    
    # ===== STEP 3: Results Display =====
    if st.session_state.last_simulation:
        st.markdown("---")
        st.header("📊 Step 3 - Results")
        
        sim = st.session_state.last_simulation
        dfargs = sim['dfargs']
        dfHPXML = sim['dfHPXML']
        dfAll = sim['dfAll']
        
        # Initialize selected results tab in session state
        if 'selected_results_tab' not in st.session_state:
            st.session_state.selected_results_tab = "📋 Samples"
        
        # Results tab configuration
        results_tab_names = [
            "📋 Samples", 
            "🗺️ HPXML mapping", 
            "📊 Statistics", 
            "📈 Visualizations",
            "💾 Export"
        ]
        
        # Custom CSS for tab-like buttons (same as BaysianNetwork)
        st.markdown("""
        <style>
        div[data-testid="column"] button[kind="secondary"] {
            width: 100%;
            border-radius: 8px 8px 0px 0px;
            border: none;
            background-color: #f0f2f6;
            color: #31333F;
            padding: 12px 24px;
            font-size: 14px;
            font-weight: 400;
            height: 50px;
        }
        div[data-testid="column"] button[kind="secondary"]:hover {
            background-color: #e0e2e6;
            border-color: transparent;
            color: #31333F;
        }
        div[data-testid="column"] button[kind="primary"] {
            width: 100%;
            border-radius: 8px 8px 0px 0px;
            border: none;
            background-color: #ff4b4b !important;
            color: white !important;
            padding: 12px 24px;
            font-size: 14px;
            font-weight: 600;
            height: 50px;
        }
        div[data-testid="column"] button[kind="primary"]:hover {
            background-color: #ff3333 !important;
            border-color: transparent !important;
            color: white !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Create results tab buttons
        cols = st.columns(5)
        for idx, tab_name in enumerate(results_tab_names):
            with cols[idx]:
                is_selected = (st.session_state.selected_results_tab == tab_name)
                btn_type = "primary" if is_selected else "secondary"
                if st.button(tab_name, key=f"results_tab_{idx}", type=btn_type, use_container_width=True):
                    st.session_state.selected_results_tab = tab_name
                    st.rerun()
        
        st.markdown("---")
        
        selected_results_tab = st.session_state.selected_results_tab
        
        # Tab 1: Samples
        if selected_results_tab == "📋 Samples":
            st.subheader("Sampling data")
            
            # Filters
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                search_col = st.text_input("🔍 Search in columns", "", key="search_col_tab1")
            with col_f2:
                display_mode = st.radio("Display mode", ["Preview (50 rows)", "Full"], horizontal=True, key="display_mode_tab1")
            
            # Filter columns
            if search_col:
                filtered_cols = [c for c in dfargs.columns if search_col.lower() in c.lower()]
                df_display = dfargs[filtered_cols]
            else:
                df_display = dfargs
            
            # Display
            if display_mode == "Preview (50 rows)":
                st.dataframe(style_dataframe(df_display.head(50)), use_container_width=True)
            else:
                st.dataframe(style_dataframe(df_display), use_container_width=True)
        
        # Tab 2: HPXML mapping
        elif selected_results_tab == "🗺️ HPXML mapping":
            st.subheader("HPXML mapping")
            st.dataframe(style_dataframe(dfHPXML), use_container_width=True)
        
        # Tab 3: Statistics
        elif selected_results_tab == "📊 Statistics":
            st.subheader("Descriptive statistics")
            
            if add_statistics:
                # Numeric statistics
                numeric_cols = dfAll.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) > 0:
                    st.markdown("#### Numeric variables")
                    st.dataframe(dfAll[numeric_cols].describe().T, use_container_width=True)
                
                # Categorical statistics
                cat_cols = dfAll.select_dtypes(include=['object']).columns
                if len(cat_cols) > 0:
                    st.markdown("#### Categorical variables")
                    selected_cat = st.selectbox("Select a variable", cat_cols, key="selected_cat_tab3")
                    value_counts = dfAll[selected_cat].value_counts()
                    
                    col_stat1, col_stat2 = st.columns(2)
                    with col_stat1:
                        st.dataframe(value_counts.reset_index(name='Frequency'), use_container_width=True)
                    with col_stat2:
                        fig = px.pie(values=value_counts.values, names=value_counts.index,
                                    title=f"Distribution of {selected_cat}")
                        st.plotly_chart(fig, use_container_width=True)
        
        # Tab 4: Visualizations
        elif selected_results_tab == "📈 Visualizations":
            if add_visualizations:
                st.subheader("Interactive visualizations")
                
                # Initialize viz_type in session state to prevent reset
                if 'viz_type' not in st.session_state:
                    st.session_state.viz_type = "Distribution"
                
                viz_type = st.selectbox(
                    "Visualization type", 
                    ["Distribution", "Correlation", "Box Plot", "BN vs Sample comparison"],
                    index=["Distribution", "Correlation", "Box Plot", "BN vs Sample comparison"].index(st.session_state.viz_type),
                    key="viz_type_selector"
                )
                
                # Update session state
                st.session_state.viz_type = viz_type
                   
                if viz_type == "Distribution":
                    selected_col = st.selectbox("Select a column", dfAll.columns, key="dist_col")
                    fig = create_distribution_plot(dfAll, selected_col)
                    st.plotly_chart(fig, use_container_width=True)
                
                elif viz_type == "Correlation":
                    fig = create_correlation_heatmap(dfAll)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("Not enough numeric columns for correlation")
                
                elif viz_type == "Box Plot":
                    numeric_cols = dfAll.select_dtypes(include=[np.number]).columns
                    if len(numeric_cols) > 0:
                        selected_col = st.selectbox("Select a variable", numeric_cols, key="box_col")
                        fig = px.box(dfAll, y=selected_col, title=f"Box Plot: {selected_col}")
                        st.plotly_chart(fig, use_container_width=True)

                elif viz_type == "BN vs Sample comparison":
                    st.markdown("Compare the theoretical distribution (BN posterior) with the empirical sample distribution.")
                    
                    bn_vars = [c for c in dfAll.columns if c in lst_NOEUD]
                    
                    if not bn_vars:
                        st.warning("No Bayesian network variables found in data.")
                    else:
                        compare_var = st.selectbox(
                            "Categorical BN variable",
                            bn_vars,
                            key="compare_var_selector"
                        )
                        
                        if compare_var:
                            # Theoretical (posterior)
                            posterior_dict = bn_posterior(InsClsSampler.bn, st.session_state.settings, compare_var)
                            if posterior_dict is None:
                                st.warning("Variable not present in BN.")
                            else:
                                # Empirique
                                emp_counts = dfAll[compare_var].value_counts(normalize=True)
                                states = list(posterior_dict.keys())
                                posterior_vals = [posterior_dict.get(s, 0) for s in states]
                                empirical_vals = [emp_counts.get(s, 0) for s in states]

                                df_compare = pd.DataFrame({
                                    "State": states,
                                    "Posterior_BN": posterior_vals,
                                    "Empirical_Sample": empirical_vals,
                                    "Diff": np.array(empirical_vals) - np.array(posterior_vals)
                                })

                                colc1, colc2 = st.columns([2.5,1.5])
                                with colc1:
                                    fig = go.Figure()
                                    fig.add_trace(go.Bar(name='Posterior BN', x=states, y=posterior_vals, marker_color="#1f77b4"))
                                    fig.add_trace(go.Bar(name='Empirical', x=states, y=empirical_vals, marker_color="#ff4b4b"))
                                    fig.update_layout(barmode='group', title=f"Distribution - {compare_var}")
                                    st.plotly_chart(fig, use_container_width=True)
                                with colc2:
                                    st.dataframe(df_compare, use_container_width=True)

                                show_diff = st.checkbox("Show differences plot (Empirical - BN)", key="show_diff_checkbox")
                                if show_diff:
                                    fig_diff = go.Figure()
                                    fig_diff.add_trace(go.Bar(name='Difference', x=states, y=df_compare["Diff"], marker_color="#ff9f0a"))
                                    fig_diff.update_layout(title=f"Empirical - Posterior BN differences ({compare_var})")
                                    st.plotly_chart(fig_diff, use_container_width=True)
        
        # Tab 5: Export
        elif selected_results_tab == "💾 Export":
            st.subheader("Data export")
            
            col_e1, col_e2, col_e3 = st.columns(3)
            
            with col_e1:
                if "CSV" in export_format:
                    st.download_button(
                        label="📥 Download CSV",
                        data=dfAll.to_csv(index=False).encode('utf-8'),
                        file_name=f'results_{time.strftime("%Y%m%d_%H%M%S")}.csv',
                        mime='text/csv',
                        use_container_width=True
                    )
            
            with col_e2:
                if "Excel" in export_format:
                    excel_data = export_to_excel({
                        'Samples': dfargs,
                        'HPXML': dfHPXML,
                        'Complete': dfAll
                    })
                    st.download_button(
                        label="📥 Download Excel",
                        data=excel_data,
                        file_name=f'results_{time.strftime("%Y%m%d_%H%M%S")}.xlsx',
                        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                        use_container_width=True
                    )
            
            with col_e3:
                if "JSON" in export_format:
                    json_data = dfAll.to_json(orient='records', indent=2)
                    st.download_button(
                        label="📥 Download JSON",
                        data=json_data,
                        file_name=f'results_{time.strftime("%Y%m%d_%H%M%S")}.json',
                        mime='application/json',
                        use_container_width=True
                    )

# ==================== PAGE: BAYESIAN NETWORK ====================

def BaysianNetwork():
    """Enhanced Bayesian Network visualization and exploration page."""
    st.title("🕸️ Bayesian Network")
    st.markdown("Exploration and analysis of the Bayesian network")
    
    # Load sampler
    path = default_bn()
    with st.spinner("🔄 Loading Bayesian network..."):
        InsClsSampler = load_sampler(path)
    bn_banner(path)
    
    lst_NOEUD = InsClsSampler.lst_NOEUD
    LIST_Dict = InsClsSampler.LIST_Dict
    pdfDataDescription = load_data_description()
    
    # Initialize selected tab in session state
    if 'selected_bn_tab' not in st.session_state:
        st.session_state.selected_bn_tab = "📊 Description"
    
    # Tab configuration
    tab_names = [
        "📊 Description",
        "🕸️ Network",
        "📋 Nodes",
        "🎲 CPT",
        "🔍 Inference",
        "📈 Analysis"
    ]
    
    # Custom CSS for tab-like buttons
    st.markdown("""
    <style>
    div[data-testid="column"] button[kind="secondary"] {
        width: 100%;
        border-radius: 8px 8px 0px 0px;
        border: none;
        background-color: #f0f2f6;
        color: #31333F;
        padding: 12px 24px;
        font-size: 14px;
        font-weight: 400;
        height: 50px;
    }
    div[data-testid="column"] button[kind="secondary"]:hover {
        background-color: #e0e2e6;
        border-color: transparent;
        color: #31333F;
    }
    div[data-testid="column"] button[kind="primary"] {
        width: 100%;
        border-radius: 8px 8px 0px 0px;
        border: none;
        background-color: #ff4b4b !important;
        color: white !important;
        padding: 12px 24px;
        font-size: 14px;
        font-weight: 600;
        height: 50px;
    }
    div[data-testid="column"] button[kind="primary"]:hover {
        background-color: #ff3333 !important;
        border-color: transparent !important;
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Create tab buttons
    cols = st.columns(6)
    for idx, tab_name in enumerate(tab_names):
        with cols[idx]:
            is_selected = (st.session_state.selected_bn_tab == tab_name)
            btn_type = "primary" if is_selected else "secondary"
            if st.button(tab_name, key=f"bn_tab_{idx}", type=btn_type, use_container_width=True):
                st.session_state.selected_bn_tab = tab_name
                st.rerun()
    
    st.markdown("---")
    
    selected_tab = st.session_state.selected_bn_tab
    
    # Tab 1: Description
    if selected_tab == "📊 Description":
        st.subheader("Data description")
        
        # Search functionality
        search_desc = st.text_input("🔍 Search in descriptions", "")
        if search_desc:
            mask = pdfDataDescription.apply(lambda row: row.astype(str).str.contains(search_desc, case=False).any(), axis=1)
            st.dataframe(pdfDataDescription[mask], use_container_width=True)
        else:
            st.dataframe(pdfDataDescription, use_container_width=True)
        
        # Summary statistics
        st.markdown("#### Network statistics")
        col_s1, col_s2, col_s3 = st.columns(3)
        col_s1.metric("Number of nodes", len(lst_NOEUD))
        col_s2.metric("Number of arcs", InsClsSampler.bn.sizeArcs())
        col_s3.metric("Max complexity", max([InsClsSampler.bn.variable(i).domainSize() for i in InsClsSampler.bn.nodes()]))
    
    # Tab 2: Network
    elif selected_tab == "🕸️ Network":
        st.subheader("Network visualization")
        
        col_v1, col_v2 = st.columns(2)
        with col_v1:
            check_stats = st.checkbox("📊 Show statistics", value=False)
        with col_v2:
            selected_size = st.slider("📏 Size", 5, 50, 15, 1)

        if st.button("🎨 Generate visualization", type="primary"):
            if not graphviz_available():
                st.error(GRAPHVIZ_MISSING_MSG)
            else:
                with st.spinner("Generating..."):
                    try:
                        svgtxt = bn_svg(InsClsSampler.bn, evs=None, Inference=check_stats, size=selected_size)
                    except Exception as exc:
                        st.error(f"Could not render the network: {exc}")
                    else:
                        components.html(svgtxt, height=900, scrolling=True)
    
    # Tab 3: Nodes
    elif selected_tab == "📋 Nodes":
        st.subheader("List of nodes and possible values")
        
        # Node search
        search_node = st.text_input("🔍 Search for a node", "")
        filtered_nodes = [n for n in lst_NOEUD if search_node.lower() in n.lower()]
        
        # Display as expandable cards
        for node in filtered_nodes:
            with st.expander(f"📌 {node} ({len(LIST_Dict[node])} possible values)"):
                values_list = node_states(LIST_Dict, node)
                
                # Display as columns for better readability
                n_cols = 3
                cols_node = st.columns(n_cols)
                for idx, val in enumerate(values_list):
                    cols_node[idx % n_cols].markdown(f"• {val}")
                
                # Node statistics
                node_id = InsClsSampler.bn.idFromName(node)
                n_parents = len(InsClsSampler.bn.parents(node_id))
                n_children = len(InsClsSampler.bn.children(node_id))
                
                st.markdown(f"**Parents:** {n_parents} | **Children:** {n_children}")
    
    # Tab 4: CPT
    elif selected_tab == "🎲 CPT":
        st.subheader("Conditional Probability Tables (CPT)")
        
        col_cpt1, col_cpt2 = st.columns([2, 1])
        
        with col_cpt1:
            selected_node = st.selectbox("🎯 Select a node", lst_NOEUD)
        
        with col_cpt2:
            cpt_display = st.radio("Display format", ["Table", "Heatmap"], horizontal=True)
        
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
                "📥 Export this CPT (CSV)",
                cpt_df.to_csv(index=True).encode('utf-8'),
                f"cpt_{selected_node}.csv",
                "text/csv"
            )
    
    # Tab 5: Inference
    elif selected_tab == "🔍 Inference":
        st.subheader("Inference engine")
        
        st.markdown("""
        Configurez des observations (evidence) et observez l'impact sur les distributions conditionnelles.
        """)
        
        col_inf1, col_inf2 = st.columns([2, 1])
        
        with col_inf1:
            st.markdown("#### 🎯 Observation configuration")
            
            # Initialize inference constraint nodes in session state
            if 'inference_constraint_nodes' not in st.session_state:
                st.session_state.inference_constraint_nodes = []
            
            settings = {}
            Noeuds_contraints = st.multiselect(
                "Variables to observe:", 
                lst_NOEUD,
                #default=st.session_state.inference_constraint_nodes,
                key="inference_multiselect"
            )
            
            # Update session state
            st.session_state.inference_constraint_nodes = Noeuds_contraints
            
            for input_var in Noeuds_contraints:
                settings[input_var] = st.selectbox(
                    f"Observed value for **{input_var}**",
                    options=node_states(LIST_Dict, input_var),
                    key=f"inf_{input_var}"
                )
        
        with col_inf2:
            st.markdown("#### ⚙️ Visualization parameters")
            selected_size2 = st.slider("Graph size", 5, 50, 15, 1, key="inf_size")
            show_probs = st.checkbox("Show probabilities", value=True)
            num_vars_to_show = st.slider("Number of variables to show", 1, min(20, len(lst_NOEUD)), 5, 1, key="num_vars_inference")
        
        if st.button("🔍 Run inference", type="primary"):
            if not graphviz_available():
                st.error(GRAPHVIZ_MISSING_MSG)
            else:
                with st.spinner("Computing inferences..."):
                    try:
                        svgtxt_inf = bn_svg(InsClsSampler.bn, evs=settings, Inference=True, size=selected_size2)
                    except Exception as exc:
                        st.error(f"Could not render the network: {exc}")
                    else:
                        components.html(svgtxt_inf, height=900, scrolling=True)

            # Show marginal distributions
            if show_probs and settings:
                st.markdown("#### 📊 Marginal distributions after observation")
                ie = gum.LazyPropagation(InsClsSampler.bn)
                ie.setEvidence(settings)
                ie.makeInference()
                
                all_nodes = list(lst_NOEUD)
                unobserved_nodes = [n for n in all_nodes if n not in settings]
                nodes_to_display = unobserved_nodes[:num_vars_to_show]
                
                st.markdown(f"**Showing the first {len(nodes_to_display)} unobserved variables:**")
                
                for node_name in nodes_to_display:
                    try:
                        posterior = ie.posterior(node_name)
                        posterior_df = posterior.topandas()
                        
                        with st.expander(f"📊 {node_name}", expanded=False):
                            col_p1, col_p2 = st.columns([2, 1])
                            with col_p1:
                                if isinstance(posterior_df, pd.Series):
                                    x_vals = [str(x) for x in posterior_df.index.tolist()]
                                    y_vals = posterior_df.values.tolist()
                                elif isinstance(posterior_df, pd.DataFrame):
                                    if posterior_df.shape[1] == 1:
                                        x_vals = [str(idx) for idx in posterior_df.index]
                                        y_vals = posterior_df.iloc[:, 0].values.tolist()
                                    else:
                                        posterior_df = posterior_df.reset_index(drop=False)
                                        prob_col = posterior_df.columns[-1]
                                        label_cols = [c for c in posterior_df.columns if c != prob_col]
                                        if label_cols:
                                            x_vals = posterior_df[label_cols].astype(str).agg(' | '.join, axis=1).tolist()
                                        else:
                                            x_vals = [str(i) for i in range(len(posterior_df))]
                                        y_vals = posterior_df[prob_col].tolist()
                                else:
                                    x_vals = [str(i) for i in range(len(posterior_df))]
                                    y_vals = list(posterior_df)
                                
                                if len(x_vals) != len(y_vals):
                                    st.warning(f"Data inconsistency for {node_name}: {len(x_vals)} labels vs {len(y_vals)} values")
                                    min_len = min(len(x_vals), len(y_vals))
                                    x_vals = x_vals[:min_len]
                                    y_vals = y_vals[:min_len]
                                
                                fig = px.bar(
                                    x=x_vals,
                                    y=y_vals,
                                    labels={'x': 'State', 'y': 'Probability'},
                                    title=f"Posterior distribution - {node_name}",
                                    color_discrete_sequence=['#ff4b4b']
                                )
                                fig.update_layout(
                                    xaxis_title="State",
                                    yaxis_title="Probability",
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
                st.info("Set at least one observation to see marginal distributions.")
    
    # Tab 6: Analyse
    elif selected_tab == "📈 Analysis":
        st.subheader("Structural analysis of the network")
        
        # Network metrics
        st.markdown("#### Network metrics")
        
        metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)
        
        metrics_col1.metric("🔢 Nodes", InsClsSampler.bn.size())
        metrics_col2.metric("🔗 Arcs", InsClsSampler.bn.sizeArcs())
        metrics_col3.metric("📊 Total states", sum([InsClsSampler.bn.variable(i).domainSize() for i in InsClsSampler.bn.nodes()]))
        metrics_col4.metric("🎯 Parameters", InsClsSampler.bn.log10DomainSize())
        
        # Node degree distribution
        st.markdown("#### Node degree distribution")
        
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
                             title="Total degree distribution")
            st.plotly_chart(fig, use_container_width=True)

# ==================== MAIN ====================

def main():
    """Main application entry point."""
    
    # Render sidebar
    render_sidebar()
    
    # Page navigation
    pages = {
        "Sampler": [
            st.Page(Page_Echantilloneur, title="Sampler", icon="🏠"),
            st.Page(BaysianNetwork, title="Bayesian Network", icon="🕸️")
        ]
    }
    
    pg = st.navigation(pages)
    pg.run()

if __name__ == "__main__":
    main()