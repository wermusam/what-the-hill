"""
Author: Adam Wermus
Date: September 30, 2024

Initial web app using dash
"""
# Initial import
import json
import dash
import os
import sys
from dash import dcc, html
from dash.dash_table import DataTable
from pathlib import Path
import dash_bootstrap_components as dbc

class App():

    def __init__(self):
        # initial dash app
        self.load_json()
        self._app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

    def create_data_table(self):
        """Data Table that reads the json file and displays info on the website"""
        table = DataTable(
            data = self.load_json(),
            columns = [
                {"name": "Name", "id": "name"},
                {"name": "Description", "id": "description"},
                {"name": "Length", "id": "length"},
                {"name": "Vertical", "id": "vertical"},
                {"name": "Link", "id": "strava_link", "presentation": "markdown"},
            ],
            style_table={"width": '100%'},
            style_cell = {'textAlign': 'left', 'padding': '10px'},
            style_header={'backgroundColor': 'rgb(30,30,30)', 'color': 'white'},
        )
        return table

    def create_layout(self):
        self._app.layout = html.Div([
            html.H1("What The Hill Table"),
            self.create_data_table()
        ])

    def load_json(self, file_path=None):
        """Loads hill data json file

        Returns:
            hill data json file
        """
        file_directory = Path(os.path.dirname(os.path.realpath(__file__)))
        hill_data_file = file_directory / Path("_data/hill_data.json")
        with open(hill_data_file, "r") as _file:
            data = json.load(_file)
        return data


    def run(self):
        """Runs the application"""
        self._app.run(debug=True)
    


# Run the app
if __name__ == "__main__":
    app = App()
    app.create_layout()
    app.run()

