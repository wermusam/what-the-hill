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

    def generate_table(self, data=None):
        """Data Table that reads the json file and displays info on the website"""
        data = self.load_json()
        return dbc.Table(
            # Table header
            [html.Thead(html.Tr([html.Th('Name'), html.Th('Description'), html.Th('Length'), html.Th('Vertical'), html.Th('Strava Link')])),
                html.Tbody([
                    html.Tr([
                        html.Td(item.get('name', 'N/A')),
                        html.Td(item.get('description', 'N/A')),
                        html.Td(item.get('length', 'N/A')),
                        html.Td(item.get('vertical', 'N/A')),
                        # html.Td(html.A('Go to Page', href=item.get('strava_link', '#'), target="_blank"))
                        html.Td(html.A(item.get('strava_link', '#'), href=item.get('strava_link', '#'), target="_blank"))
                ]) for item in data
                ])
            ],
            bordered=True, striped=True, hover=True, responsive=True, className="table-class"
        )

    def create_layout(self):
        self._app.layout = dbc.Container([
            html.H1("What The Hill Data Table"),
            self.generate_table(),
        ], fluid=True)

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

