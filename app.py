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
import pandas as pd
import pymongo
from dash import dcc, html
from dash.dash_table import DataTable
from dash.dependencies import Input, Output, State

# visualizaton imports
import plotly.graph_objs as go 


# other scripts import
import robo_adam


class Application:

    def __init__(self):
        # initial dash app
        self.hill_data_loader = self.load_json()
        self.db = robo_adam.RoboAdam()
        self._app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

    def create_layout(self):
        dropdown_options = self.dropdown_name_options()
        self._app.layout = dbc.Container([

            # Header and Subtitle
            dbc.Row(dbc.Col(html.H1("Hill Yeah Hillvember!!!"), width={"size": 8, "offset": 2})),
            dbc.Row(dbc.Col(html.H2("November Project's Hill, Steps, and Steep Street Exploration Challenge Across LA"), width={"size": 8, "offset": 2})),

            # Divider
            html.Hr(),

            # Rules
            dbc.Row(
                dbc.Col(
                        self.paragraph_rules(), width={"size": 8, "offset": 2}
                       )
                    ),

            # Divider
            html.Hr(),

            # Data Table
            dbc.Row(
                dbc.Col(
                    [
                        html.H1("What The Hill Locations and Descriptions", style={"textAlign": "center"}),
                        self.generate_hill_table(),
                    ],
                    width={"size": 8, "offset": 2}
                )
            ),

            # Divider
            html.Hr(),

            # Map of Locations
            dbc.Row(
                dbc.Col(
                    [
                        html.H2("Map of All Hill Locations", className='text-center mt-4'),
                        html.P("This map shows all of the locations for the challenge", className='text-center'),
                        self.create_map(),
                    ],
                    width={"size": 8, "offset":2}
                )
            ),

            # Divider
            html.Hr(),

             # Submission Form
            dbc.Row(
                dbc.Col(
                    [                    
                        html.H3("Hill Submission Form", style={"textAlign": "center"}),    
                        self.layout_submission_form(),
                    ],
                    width={"size": 8, "offset":2}
                )
            ),

            # Output Container For Results
            html.Div(id="output-container", className="mt-4"),

        ], fluid=True)

        # Form Submission Response
        self.submission_form_response()

    def create_map(self, locations=None):
        """Filter hill data json and create a map"""
        locations = [{'name': item['name'], 'lat': item['lat'], 'lon': item['lon']} for item in self.hill_data_loader]
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
        ],style={'width': '100%', 'height': '500px'})

    def dropdown_name_options(self, data=None):
        """Returns the dropdown options from the json data"""
        return [{'label': item["name"], 'value': item['name']} for item in self.hill_data_loader]

    def generate_hill_table(self):
        """Data Table that reads the json file and displays info on the website"""
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
                ]) for item in self.hill_data_loader
                ])
            ],
            bordered=True, striped=True, hover=True, responsive=True, className="table-class"
        )

    def get_vertical_value(self, name=""):
        """Calculates the vertical feet by multiplying reps and feet"""
        for item in self.hill_data_loader:
            if item["name"] == name:
                return item["vertical"]

    def image_placer(self):
        """Used for image in assets dir"""
        return html.Img(
            src = "/assets/hill_yeah_img.jpg",
            style={"width": "100%", "max-width": "300px"}
        )

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
                                dbc.Label("Select Location"),
                                dcc.Dropdown(id="location-dropdown", options=dropdown_options, placeholder="Select Location"),
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
                            ], width={"size": 6, "offset": 3}, className="text-center")
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

    def paragraph_rules(self):
        # Paragraph explaining the rules
        return [
            # Introductory Paragraph
            html.P("Welcome to November Project's Hill Yeah Challenge! From November 1-November 24, your goals are for you and your team to:"),
            
            # Row with two columns: one for the image, one for bullet points
            dbc.Row([

                # Column for the image
                dbc.Col(
                    self.image_placer(), width=4
                ),
                # Column for the bullet poitns
                dbc.Col(
                    [
                        # Unordered list of Rules:
                        html.Ul([
                        html.Li("Go to as many of the 40 listed locations as you can."),
                        html.Li("Get as many repetitions for each location as you can."),
                        html.Li("Get the most vertical feet you can for you and your team."),
                        ]),

                    ],
                    width=8 # width ratio for the bullet points colum
                )
            ]),
            
            # Additional paragraph of rules
            html.P(
                "This challenge is inspired by November Project San Francisco's Hill Climb Challenge in 2021." 
                "Below is a table of all 40 locations showing their names, descriptions, lenght, vertical feet, and a link to their strava segments." 
                "There is also a map where clicking on the pins will take you to google maps so you know where each location starts."
                "At the bottom of the page is a form where you will submit your name, e-mail, select the location you did, enter number of reps, and an optional strava link as proof that you completed the route."
                "When you hit submit, 'RoboAdam' will calculate and keep track of your score for you and the team you are on. You can find that data in the Hill Data Portal."
            ),

            # Unordered List
            html.Ul([
                html.Li("Locations you've completed"),
                html.Li("Repetitions of each location"),
                html.Li("Your total vertical feet"),
            ]),

            # Additional Paragraph
            html.P(
                "When you submit your first score, you will be randomly assigned to a team of up to 6 people. If you'd like to be on a team with other people, please let leadership know when you submit and we will try to accomodate you." 
                "This is an honor system. We trust you. Please don't break that trust." 
                "If there any issues with the form or data, please contact Adam Wermus at amwermus@gmail.com"
            ),

            # Unordered List
                html.Ul([
                html.Li("Use the map to strategize how to best go to each location"),
                html.Li("Use the Hill Data Portal by 'RoboAdam'"),
                html.Li("Support your team. This is fun. Use e-mail, Marco Polo, Whatsapp, anything to support each other to win."),
            ]),

            # Let's go
                html.P(
                    "LET'S GOOOOOOO"
            )
        ]

    def submission_form_response(self):
        """Handles submission form response, updating data, and visualization"""
        @self._app.callback(
            Output("output-container","children"),
           [Input("submit-button", "n_clicks")],
            [State("name", "value"),
            State("email", "value"),
            State("location-dropdown", "value"),
            State("num-repetitions", "value"),
            State("optional-link", "value")],
            prevent_initial_call=True
        )
        def handle_submission_form(n_clicks, name, email, location, num_repetitions, optional_link):
            
            # Check each field individually
            if not name:
                return html.Div("Please enter a name!", style={"color": "red", 'textAlign': 'center'})
            if not email:
                return html.Div("Please enter a valid e-mail!", style={"color": "red", 'textAlign': 'center'})
            if not location:
                return html.Div("Please select a location!", style={"color": "red", 'textAlign': 'center'})
            if not num_repetitions:
                return html.Div("Please enter number of repetitions!", style={"color": "red", 'textAlign': 'center'})
            
            # Check if any fields were missed (might be redundant)
            if not (name and email and location and num_repetitions):
                return html.Div("Please fill out all required fields.", style={"color": "red"})

            # Validate number of repetitions
            if not isinstance(num_repetitions, int) or num_repetitions <= 0:
                return html.Div("Number of repetitions must be a positive integer.", style={"color": "red"})

            # Get the vertical value from the selected location and date
            vertical_value = self.get_vertical_value(location)
            total_submitted_feet = num_repetitions * vertical_value

            # Date
            date = pd.Timestamp.now().strftime("%Y-%m-%d")

            # Handle optional link
            link_text = optional_link if optional_link else "No link provided"

            # submission data to insert to database
            submission_data = {
                "name": name,
                "email": email,
                "location": location,
                "repetitions": num_repetitions,
                "vertical_gain": vertical_value,
                "strava_link": link_text,
                "date": date,
            }

            # insert the submission data into MongoDB
            self.db.insert_submitted_data(submission_data)

            result = html.Div(
                [
                    html.H4("Form Submission Results"),
                    html.P(f"Name: {submission_data['name']}"),
                    html.P(f"Email: {submission_data['email']}"),
                    html.P(f"Location: {submission_data['location']}"),
                    html.P(f"Number of Repetitions:  {submission_data['repetitions']}"),
                    html.P(f"Vertical Value: {vertical_value}"),
                    html.P(f"Total Feet: {total_submitted_feet}"),
                    html.P(f"Optional Link: {submission_data['strava_link']}"),
                
                ],
                style={
                    "display": 'flex',
                    'flexDirection': 'column',
                    'justifyContent': 'center',
                    'alignItems': 'center',
                    'textAlign': 'center',

                }
            )
            return result



    def run(self):
        """Runs the application"""
        self._app.run(debug=True)
    


# Run the app
if __name__ == "__main__":
    run_app = Application()
    run_app.create_layout()
    run_app.run()

