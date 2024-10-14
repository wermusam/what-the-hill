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

    def create_layout(self):
        dropdown_options = self.dropdown_name_options()
        self._app.layout = dbc.Container([

            # Data Table
            html.H1("What The Hill Locations and Descriptions", style={"textAlign": "center"}),
            self.generate_hill_table(),
            
            # Divider
            html.Hr(),

             # Submission Form
            html.H2("Hill Submission Form", style={"textAlign": "center"}),    
            self.layout_submission_form(),

            # Output Container For Results
            html.Div(id="output-container", className="mt-4"),

        ], fluid=True)

    def dropdown_name_options(self, data=None):
        """Returns the dropdown options from the json data"""
        data = self.load_json()
        return [{'label': item["name"], 'value': item['name']} for item in data]

    def generate_hill_table(self, data=None):
        """Data Table that reads the json file and displays info on the website"""
        data = self.load_json()
        return dbc.Table(
            # Table header
            [html.Thead(html.Tr([html.Th('Name'), html.Th('Description'), html.Th('Length (Miles)'), html.Th('Vertical (Feet)'), html.Th('Strava Link')])),
                html.Tbody([
                    html.Tr([
                        html.Td(item.get('name', 'N/A')),
                        html.Td(item.get('description', 'N/A')),
                        html.Td(item.get('length', 'N/A')),
                        html.Td(item.get('vertical', 'N/A')),
                        html.Td(html.A(item.get('strava_link', '#'), href=item.get('strava_link', '#'), target="_blank"))
                ]) for item in data
                ])
            ],
            bordered=True, striped=True, hover=True, responsive=True, className="table-class"
        )

    def layout_hill_data_table(self):
        """layout for hill data table"""
        return dbc.Container([
            html.H2("What The Hill Data Table", style={"textAlign": "center"}),
            self.generate_hill_table(),
        ], fluid=True)

    def layout_submission_form(self):
        """layout for the submission form"""
        dropdown_options = self.dropdown_name_options()
        return dbc.Row([
                dbc.Col([
                    dbc.Form([

                        # Name Input
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Name"),
                                dbc.Input(id="name", type="text", placeholder="Enter your name", required=True),
                            ])
                        ], className="mb-3"), # adds margin-bottom for spacing

                        # Email Input
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Email"),
                                dbc.Input(id="email", type="email", placeholder="Enter your e-mail", required=True),  
                            ])
                        ], className="mb-3"),

                        # Dropdown for Hill Name Selection
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Select Item"),
                                dcc.Dropdown(id="item-dropdown", options=dropdown_options, placeholder="Select an item"),
                                ])
                        ], className="mb-3"),

                        # Number of Repetitions Input
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Number of Repetitions"),
                                dbc.Input(id="num-repetitions", type="number", min=1, placeholder="Enter number of repetitions", required=True),
                            ])
                        ], className="mb-3"),

                        # Optional Link Input
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Optional Strava Link"),
                                dbc.Input(id='optional-link', type="url", placeholder="Enter optional strava link"),
                            ])
                        ], className="mb-3"),

                        # Submit Button
                        dbc.Row([
                            dbc.Col([
                                dbc.Button("Submit", id="submit-button", color="primary", className="mt-3"),
                            ])
                        ])
                ], id="input-form"),
            ], xs=12, sm=10, md=8, lg=6, xl=6, className="mx-auto") # Set the width and use "mx-auto" for centering
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

