Module LTE-Sampler-Residential.ui.Dashboard_v2
==============================================
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

Functions
---------

`BaysianNetwork()`
:   Enhanced Bayesian Network visualization and exploration page.

`Page_Echantilloneur()`
:   Enhanced sampling page with advanced features.

`bn_posterior(bn, evidence: dict, varname: str)`
:   Return posterior distribution (dict state->prob) for varname given evidence.
    Uses bn.variable(...) to get labels instead of post.var().

`bn_svg(bn, evs=None, Inference=True, size=15)`
:   Generate and cache SVG visualization of Bayesian Network.

`create_correlation_heatmap(df)`
:   Create correlation heatmap for numerical columns.

`create_distribution_plot(df, column)`
:   Create interactive distribution plot.

`export_to_excel(dataframes_dict)`
:   Export multiple dataframes to Excel with multiple sheets.

`load_data_description()`
:   Load and cache data description.

`load_sampler(path)`
:   Load and cache the Bayesian Network sampler.

`main()`
:   Main application entry point.

`render_sidebar()`
:   Render enhanced sidebar with settings and controls.

`style_dataframe(df)`
:   Apply styling to dataframe for better visualization.