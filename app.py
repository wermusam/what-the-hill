"""
Author: Adam Wermus
Date: September 30, 2024

Initial web app using dash
"""
# Initial import
from dash import Dash, html, dash_table, dcc, callback, Output, Input
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc

# Initial Dash application
app = Dash()

# Run the app
if __name__ == "__main__":
    app.run(debug=True)

