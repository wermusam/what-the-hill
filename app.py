"""
Author: Adam Wermus
Date: September 30, 2024

Initial web app using dash
"""
# Initial import
import json
import os
import sys
from pathlib import Path

# Dash imports
import dash
import dash_bootstrap_components as dbc
import dash_leaflet as dl
import pymongo
from dash import dcc, html
from dash.dash_table import DataTable
from dash.dependencies import Input, Output, State

# visualizaton imports
import plotly.graph_objs as go 


# other scripts import
import mongo_setup


class Application:

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

            # Map of Locations
            html.H2("Map of All Hill Locations", className='text-center mt-4'),
            html.P("This map shows all of the locations for the challenge", className='text-center'),
            self.create_map(),

            # Divider
            html.Hr(),

             # Submission Form
            html.H3("Hill Submission Form", style={"textAlign": "center"}),    
            self.layout_submission_form(),

            # Output Container For Results
            html.Div(id="output-container", className="mt-4"),

        ], fluid=True)

        # Form Submission Response
        self.submission_form_response()

    def create_map(self, locations=None):
        """Filter hill data json and create a map"""
        data = self.load_json()
        locations = [{'name': item['name'], 'lat': item['lat'], 'lon': item['lon']} for item in data]
        markers = [dl.Marker(position=[loc["lat"], loc["lon"]],
                             children=[
                                dl.Tooltip(loc["name"]),
                                dl.Popup(html.A(
                                    "Open in Google Maps",
                                    href=f"https://www.google.com/maps?q={loc['lat']}, {loc['lon']}",
                                    target="_blank",
                                    style={"color": "blue", "text-decoration": "underline"}
                                )) 
                             ]
                             ) for loc in locations
                ]

        return dl.Map(center=[34.0522, -118.2437], zoom=10, children=[
            dl.TileLayer(), # Base map layer
            *markers
        ], style={'width': '100%', 'height': '500px'})
        


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

    def get_vertical_value(self, name=""):
        """Calculates the vertical feet by multiplying reps and feet"""
        data = self.load_json()
        for item in data:
            if item["name"] == name:
                return item["vertical"]
        return 0

    def submission_form_response(self):
        """Handles submission form response"""
        @self._app.callback(
            Output("output-container","children"),
            Input("submit-button", "n_clicks"),
            State("name", "value"),
            State("email", "value"),
            State("item-dropdown", "value"),
            State("num-repetitions", "value"),
            State("optional-link", "value"),
            prevent_initial_call=True
        )
        def handle_submission_form(n_clicks, name, email, selected_item, num_repetitions, optional_link):
            # Check if all required fields are filled
            if not (name and email and selected_item and num_repetitions):
                return html.Div("Please fill out all required fields.", style={"color": "red"})

            # Validate number of repetitions
            if not isinstance(num_repetitions, int) or num_repetitions <= 0:
                return html.Div("Number of repetitions must be a positive integer.", style={"color": "red"})
            
            # Get the vertical value from the selected item
            vertical_value = self.get_vertical_value(selected_item)

            # Calculate the results
            total_submitted_feet = num_repetitions * vertical_value

            # Optional link handling
            link_text = optional_link if optional_link else "No link provided"

            result = html.Div([
                html.H4("Form Submission Results"),
                html.P(f"Name: {name}"),
                html.P(f"Email: {email}"),
                html.P(f"Selected Item: {selected_item}"),
                html.P(f"Number of Repetitions:  {num_repetitions}"),
                html.P(f"Vertical Value: {vertical_value}"),
                html.P(f"Total Feet: {total_submitted_feet}"),
                html.P(f"Optional Link: {link_text}")
            ])
            return result

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
    run_app = Application()
    run_app.create_layout()
    run_app.run()

