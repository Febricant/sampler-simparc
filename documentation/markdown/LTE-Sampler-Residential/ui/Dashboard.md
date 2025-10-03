Module LTE-Sampler-Residential.ui.Dashboard
===========================================
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

Functions
---------

`DashBoard()`
:   Main function to render the Streamlit dashboard.
    
    This function performs the following steps:
    1. Displays the HPXML data in a table format.
    2. Provides a download button for exporting the data as a CSV file.
    
    Returns:
    --------
    None