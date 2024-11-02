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
from dash import dcc, html, callback_context
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

        # Load data once during app initialization
        self.location_data = self.db.get_unique_location_counts().to_dict('records')
        self.reps_data = self.db.get_top_reps_per_location().to_dict('records')
        self.total_vertical_data = self.db.get_total_vertical_per_person().to_dict('records')
        top_10_df = self.db.get_total_vertical_per_person().nlargest(10, 'Total Vertical Feet')

        # Create figure for the bar graph
        self.bar_vert_graph = {
                'data': [
                    go.Bar(
                        x=top_10_df['Name'],
                        y=top_10_df['Total Vertical Feet'],
                        marker=dict(color='#FFA07A')
                    )
                ],
                'layout': go.Layout(
                    title="Top 10 Vert (Feet)",
                    xaxis=dict(title="", tickangle=-45, automargin=True),
                    yaxis=dict(title="Total Vert (Feet)", title_standoff=10),
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    margin=dict(l=60, r=20, t=40, b=120),
                )
            }


        self._app = dash.Dash(__name__, external_stylesheets=[
                                        dbc.themes.BOOTSTRAP,
                                        "https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&family=Merriweather:wght@300;400;700&family=Montserrat:wght@300;500;700&display=swap"
                                    ])

        # Create Layout
        self.create_layout()

    def create_layout(self):
        dropdown_options = self.dropdown_name_options()
        self._app.layout = dbc.Container([

            dcc.Location(id="url", refresh=False),

            # Navigation Bar with Rounded Corners
            dbc.NavbarSimple(
                children=[
                    dbc.NavItem(dbc.NavLink("Hill Yeah Locations and Descriptions", href="#locations")),
                    dbc.NavItem(dbc.NavLink("Map of All Hill Yeah Locations", href="#map")),
                    dbc.NavItem(dbc.NavLink("Robo-Adam Resource Portal", href="#scores")),
                    dbc.NavItem(dbc.NavLink("Hill Yeah Submission Form", href="#form")),
                ],
                brand="Hill Yeah",
                brand_href="#",
                color="primary",
                dark=True,
                style={
                    'borderRadius': '8px',  # Rounds the corners
                    'marginBottom': '10px'  # Adds some space below
                }
            ),

            # Updated "November Project's Exploration Elevation Challenge Across LA" Section
            dbc.Row(
                dbc.Col(
                    html.Div(
                         html.H2(
                            html.Span("HILL YEAH\nAn Exploration Elevation Challenge Across LA\n40 Hills\nNovember 1 - November 24\n LET'S GOOO!!!!", className="gradient-text"),
                            className="resource-portal-title mt-4"
                        ),
                        style={
                            'padding': '15px',  # Adds padding inside the box
                            'background-color': '#e6f2ff',
                            'borderRadius': '12px',  # Extra rounded corners for a softer look
                            'boxShadow': '0px 6px 12px rgba(0, 0, 0, 0.1)',  # Slightly stronger shadow for contrast
                            'marginBottom': '20px'  # Adds spacing below the entire div
                        }
                    ),
                    xs=12,  # Full width on extra small screens (e.g., iPhones)
                    sm=12,  # Full width on small screens
                    md={"size": 10, "offset": 1},  # Adjusted for medium screens
                    lg={"size": 8, "offset": 2}  # Standard size and offset for large screens
                ),
            ),

            # Divider
            html.Hr(),


            # Rules Section with Light Gray Background
            dbc.Row(
                dbc.Col(
                    html.Div(
                        children=self.paragraph_rules(),
                        style={
                            'backgroundColor': '#e8e8e8',  # Light gray background
                            'padding': '15px',  # Adds padding inside the box
                            'borderRadius': '8px',  # Rounds the corners
                            'marginBottom': '20px'  # Adds spacing below the section
                        }
                    ),
                    xs=12,  # Full width on extra small screens (e.g., iPhones)
                    sm=12,  # Full width on small screens
                    md={"size": 10, "offset": 1},  # Adjusted for medium screens
                    lg={"size": 8, "offset": 2}  # Standard size and offset for large screens
                ),
            ), 

            # Divider
            html.Hr(),

            # Data Table with Shadow and Rounded Corners
            dbc.Row(
                dbc.Col(
                    html.Div(
                        id="locations",
                        children=[
                            html.H1(
                                "Hill Yeah Locations and Descriptions",
                                style={'marginBottom': '20px'}
                            ),
                            self.generate_hill_table()
                        ],
                        style={
                            'marginTop': '100px',
                            'textAlign': 'center',
                            'boxShadow': '0px 4px 8px rgba(0, 0, 0, 0.1)',  # Soft shadow
                            'borderRadius': '8px',  # Rounded corners
                            'padding': '15px',  # Adds padding inside the box
                            'backgroundColor': '#fff'  # White background for contrast
                        }
                    ),
                    xs=12,  # Full width on extra small screens (e.g., iPhones)
                    sm=12,  # Full width on small screens
                    md={"size": 10, "offset": 1},  # Adjusted for medium screens
                    lg={"size": 8, "offset": 2}  # Standard size and offset for large screens
                ),
            ), 

            # Divider
            html.Hr(),

            # Map of Locations
            dbc.Row(
                dbc.Col(
                    [
                        html.Div(id="map"),
                        html.H2(
                            html.Span("Map of All Hill Yeah Locations", className="gradient-text"),
                            className="resource-portal-title mt-4"
                        ),
                        html.P("Double click a pin and google maps will give you directions to the starting location", 
                        className='text-center',
                        style=
                            {
                                "textAlign": "center", 
                                "whiteSpace": "pre-line",
                                "fontFamily": "'Montserrat', sans-serif",
                                "fontWeight": "700",
                                "fontSize": "15px",
                                "textShadow": "1px 1px 2px rgba(0, 0, 0, 0.2)",  # Add text shadow here
                                "color": "#007bff"  # Blue accent
                            }, 
                        
                        ),
                        self.create_map(),
                    ],
                    xs=12,  # Full width on extra small screens (e.g., iPhones)
                    sm=12,  # Full width on small screens
                    md={"size": 10, "offset": 1},  # Adjusted for medium screens
                    lg={"size": 8, "offset": 2}  # Standard size and offset for large screens
                )
            ),

            # Divider
            html.Hr(),

            # Robo Adam Resource Portal
            dbc.Row(
                dbc.Col(
                    [
                        html.Div(id="scores"),
                        html.H2(
                            html.Span("Robo-Adam Resource Portal", className="gradient-text"),
                            className="resource-portal-title mt-4"
                        ),
                        self.create_resource_portal_layout(),
                    ],
                    xs=12,  # Full width on extra small screens (e.g., iPhones)
                    sm=12,  # Full width on small screens
                    md={"size": 10, "offset": 1},  # Adjusted for medium screens
                    lg={"size": 8, "offset": 2}  # Standard size and offset for large screens
                )
            ),

            # Divider
            html.Hr(),

             # Submission Form
            dbc.Row(
                dbc.Col(
                    [
                        html.Div(id="form"),                    
                        html.H3(
                            html.Span("Hill Yeah Submission Form", className="gradient-text"),
                            className="resource-portal-title mt-4"
                        ),

                        self.layout_submission_form(),
                    ],
                    width={"size": 8, "offset":2}
                )
            ),

            # Output Container For Results
            html.Div(id="output-container", className="mt-4"),

            # Add a footer at the bottom
            dbc.Row(
                dbc.Col(
                    html.Div(
                        children=[
                            html.P(
                                "© 2024 Hill Yeah Challenge.",
                                style={'color': '#6c757d', 'margin': '0'}
                            ),
                            html.P(
                                "Developed by Adam Wermus",
                                style={'color': '#6c757d', 'margin': '0'}
                            ),
                        ],
                        style={
                            'background': 'linear-gradient(to right, #dcdcdc, #e8e8e8)',  # Light gradient
                            'padding': '10px',
                            'textAlign': 'center',
                            'borderTop': '1px solid #ccc',  # Light border on top
                            'marginTop': '20px'
                        }
                    ),
                    width={"size": 12}  # Full width of the container
                )
            )

        ],

        style={
            'background': 'linear-gradient(to bottom, #f0f0f0, #dcdcdc)',
            'padding': '20px',
            'fontFamily': 'Roboto, sans-serif'  # Apply the font family
        },
        fluid=True)

        # Form Submission Response and Page Refresh
        self.combined_callback()

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
        # Responsive style for all devices
        map_style = {
            'width': '100%',
            'height': '50vh',  # Adapts height based on viewport
            'max-height': '500px',  # Ensures it doesn’t grow too large on larger screens
            'margin': '10px auto',  # Centers and adds spacing for smaller screens
        }

        # Find the center for all locations
        latitudes = [loc['lat'] for loc in locations]
        longitudes = [loc['lon'] for loc in locations]
        # Calculate the center by averaging the latitude and longitude
        center_lat = sum(latitudes) / len(latitudes) if latitudes else 34.0522
        center_lon = sum(longitudes) / len(longitudes) if longitudes else -118.2437

        return dl.Map(center=[center_lat, center_lon], zoom=10, children=[
            dl.TileLayer(), # Base map layer
            *markers
        ],style=map_style)

    def create_resource_portal_layout(self):

        # Generate a DataTable of all hills
        total_hill_count = DataTable(
            id='location-table-portal',
            columns=[
            {"name": "Hills Yeah Leaderboard", "id": "Name"},
            {"name": "Hills Count", "id": "Locations Covered"}
            ],
            data= self.location_data,
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'left'},
            style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'}
        )

        # Generate a DataTable from the sample data
        wth_table = DataTable(
            id='total-vertical-table',
            columns=[
                {"name": "Name", "id": "Name"},
                {"name": "Total Vert (Feet)", "id": "Total Vertical Feet"}
            ],
            data=self.total_vertical_data,
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'left'},
            style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'}
        )

        # Generate a bar graph showing repetitions per location
        # Bar Graph component
        total_vertical_df = self.db.get_total_vertical_per_person()
        top_10_df = total_vertical_df.nlargest(10, 'Total Vertical Feet')
        bar_graph_wth = dcc.Graph(
            id='total-vertical-bar-graph',
            figure={
                'data': [
                    go.Bar(
                        x=top_10_df['Name'],
                        y=top_10_df['Total Vertical Feet'],
                        marker=dict(color='#FFA07A')  # Soft salmon color for the bars
                    )
                ],
                'layout': go.Layout(
                    title="Top 10 Vert (Feet)",
                    xaxis=dict(title="",tickangle=-45, automargin=True),
                    yaxis=dict(title="Total Vert (Feet)", title_standoff=10),
                    plot_bgcolor='rgba(0,0,0,0)',  # Transparent background
                    paper_bgcolor='rgba(0,0,0,0)',
                    margin=dict(l=60, r=20, t=40, b=120),  # Increase bottom margin for x-axis labels
                )
            },
            style={'width': '100%', 'padding': '10px'}
        )
        # Generate a DataTable with adjusted mobile-friendly styles
        reps_represent = DataTable(
            id='top-reps-table',
            columns=[
                {"name": "Location", "id": "Location"},
                {"name": "Reps", "id": "Reps"},
                {"name": "Name", "id": "Name"}
            ],
            data=self.reps_data,
            style_table={'overflowX': 'auto'},  # Keeps horizontal scroll but minimizes it
            style_cell={
                'textAlign': 'left',
                'padding': '5px',  # Smaller padding to reduce table width
            },
            style_cell_conditional=[
                {'if': {'column_id': 'Location'}, 'whiteSpace': 'normal', 'minWidth': '100px', 'maxWidth': '200px'},
                {'if': {'column_id': 'Reps'}, 'width': '50px'},
                {'if': {'column_id': 'Name'}, 'whiteSpace': 'normal', 'minWidth': '100px', 'maxWidth': '200px'},  # Wraps text in Name
            ],
            style_header={
                'backgroundColor': 'rgb(230, 230, 230)',
                'fontWeight': 'bold'
            }
        )

        # Return the Resource Portal layout with improved font styles
        return dbc.Container([
            html.H2("", className="text-center mt-4"),
            
            html.Div([
                html.H4(
                    "HILLS YEAH", 
                    className="mt-4", 
                    style={
                        "textAlign": "center", 
                        "whiteSpace": "pre-line",
                        "fontFamily": "'Montserrat', sans-serif",
                        "fontWeight": "700",
                        "fontSize": "24px",
                        "textShadow": "1px 1px 2px rgba(0, 0, 0, 0.2)",  # Add text shadow here
                        "color": "#007bff"  # Blue accent
                    }
                ),
                html.P("Total Number of Hills Leaderboard", 
                        className='text-center',
                        style={
                            "textAlign": "center", 
                            "whiteSpace": "pre-line",
                            "fontFamily": "'Montserrat', sans-serif",
                            "fontWeight": "700",
                            "fontSize": "15px",
                            "textShadow": "1px 1px 2px rgba(0, 0, 0, 0.2)",  # Add text shadow here
                            "color": "#007bff"  # Blue accent
                        }, 
                ),
                total_hill_count
            ], className="mb-4"),
            
            html.Div([
                html.H4(
                    "REPSertoire REPSresentative", 
                    className="mt-4", 
                    style={
                        "textAlign": "center", 
                        "whiteSpace": "pre-line",
                        "fontFamily": "'Montserrat', sans-serif",
                        "fontWeight": "700",
                        "fontSize": "24px",
                        "textShadow": "1px 1px 2px rgba(0, 0, 0, 0.2)",  # Add text shadow here
                        "color": "#007bff"  # Blue accent
                    }
                ),
                html.P("Top Number of Reps at Each Location", 
                    className='text-center',
                    style={
                        "textAlign": "center", 
                        "whiteSpace": "pre-line",
                        "fontFamily": "'Montserrat', sans-serif",
                        "fontWeight": "700",
                        "fontSize": "15px",
                        "textShadow": "1px 1px 2px rgba(0, 0, 0, 0.2)",  # Add text shadow here
                        "color": "#007bff"  # Blue accent
                    }, 
                ),
                
                reps_represent
            ], className="mb-4"),
            
            html.Div([
                html.H4(
                    "What The Hill", 
                    className="mt-4", 
                    style={
                        "textAlign": "center", 
                        "whiteSpace": "pre-line",
                        "fontFamily": "'Montserrat', sans-serif",
                        "fontWeight": "700",
                        "fontSize": "24px",
                        "textShadow": "1px 1px 2px rgba(0, 0, 0, 0.2)",  # Add text shadow here
                        "color": "#007bff"  # Blue accent
                    }
                ),
                html.P("Vertical Feet Leaderboard", 
                    className='text-center',
                    style={
                        "textAlign": "center", 
                        "whiteSpace": "pre-line",
                        "fontFamily": "'Montserrat', sans-serif",
                        "fontWeight": "700",
                        "fontSize": "15px",
                        "textShadow": "1px 1px 2px rgba(0, 0, 0, 0.2)",  # Add text shadow here
                        "color": "#007bff"  # Blue accent
                    }, 
                ),
                wth_table
            ], className="mb-4"),
            
            html.Div([
                html.H4(
                    "What The Hill Top 10", 
                    className="mt-4", 
                    style={
                        "textAlign": "center", 
                        "whiteSpace": "pre-line",
                        "fontFamily": "'Montserrat', sans-serif",
                        "fontWeight": "700",
                        "fontSize": "24px",
                        "textShadow": "1px 1px 2px rgba(0, 0, 0, 0.2)",  # Add text shadow here
                        "color": "#007bff"  # Blue accent
                    }
                ),
                bar_graph_wth
            ], className="mb-4"),
            
        ], fluid=True)

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

    def image_placer(self, image_path="/assets/hill_yeah_img.jpg"):
        """Used for placing images in assets directory"""
        return html.Img(
            src=image_path,
            style={"width": "100%", "max-width": "250px", "margin": "10px auto"}
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
                        dbc.Row(
                            dbc.Col(
                                dbc.Button(
                                    "Submit",
                                    id="submit-button",
                                    style={
                                        'background': 'linear-gradient(to right, #FF6F61, #007bff)',  # Gradient from orange to blue
                                        'color': 'white',
                                        'border': 'none',
                                        'padding': '10px 20px',
                                        'borderRadius': '8px'
                                    },
                                    className="mt-3"
                                ),
                                width={"size": 6, "offset": 3},
                                className="text-center"
                            ),
                        ),

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
            html.P(
                "Welcome to a collaboration between November Project and Saturday Stairs for the Hill Yeah Challenge! Inspired by November Project San Francisco's Hill Climb Challenge in 2021, "
                "this adventure will have you exploring 40 elevation-based locations across Santa Monica, West Hollywood, Culver City, Hollywood Bowl, Los Feliz, Griffith Park, Highland Park, Pasadena, Echo Park, and Silver Lake. "
                "The routes include staircases, steep streets, and hills, which you’ll conquer using only your own body power—no motorized assistance allowed. "
                "There are three categories to win:",
                className="intro-paragraph"
            ),

            # Row with three images and bullet points
            dbc.Row([
                # First Image
                dbc.Col(
                    self.image_placer("/assets/hill_yeah_img1.jpg"), 
                    width=4
                ),
                # Second Image
                dbc.Col(
                    self.image_placer("/assets/hill_yeah_img2.jpg"), 
                    width=4
                ),
                # Third Image
                dbc.Col(
                    self.image_placer("/assets/hill_yeah_img3.jpg"), 
                    width=4
                ),
            ], className="mb-3"),  # Adds margin-bottom for spacing

            # Row with bullet points
            dbc.Row([
                dbc.Col([
                    html.Ul([
                        html.Li([
                            html.B("HILLS YEAH: "), 
                            "Visit as many of the 40 listed locations as possible."
                        ]),
                        html.Li([
                            html.B("REPSertoire REPSresentative: "), 
                            "Complete as many repetitions as possible for each location."
                        ]),
                        html.Li([
                            html.B("WHAT THE HILL: "), 
                            "Achieve the most vertical feet."
                        ]),
                    ]),
                ], width=12)
            ]),

            # Additional Paragraph
            html.P(
                "The data table below lists all 40 locations, including their name, description, length, vertical feet, and a Strava link to the segment. "
                "Only repetitions completed between November 1 and November 24 count toward the challenge. We've pre-calculated the vertical feet for each location. "
                "You’ll also find a map with pins showing directions to the start of each location.",
                className="intro-paragraph"
            ),

            # Row with three images and bullet points
            dbc.Row([
                # First Image
                dbc.Col(
                    self.image_placer("/assets/hill_yeah_img4.jpg"), 
                    width=4
                ),
                # Second Image
                dbc.Col(
                    self.image_placer("/assets/hill_yeah_img5.jpg"), 
                    width=4
                ),
                # Third Image
                dbc.Col(
                    self.image_placer("/assets/hill_yeah_img6.jpg"), 
                    width=4
                ),
            ], className="mb-3"),  # Adds margin-bottom for spacing

                        # Additional Paragraph
            html.P(
                "After completing a location, submit your score using the form at the bottom, "
                "where you can enter your name, email, selected location, number of reps, and an optional Strava/tracking link. "
                "Once submitted, 'Robo-Adam' will track the locations you’ve completed, your repetitions per location, and your total vertical feet. "
                "You can view all of this information in the 'Robo-Adam Resource Portal.'",
                className="intro-paragraph"
            ),

                        # Row with three images and bullet points

            # Unordered List
            html.Ul([
                html.Li("Discover new parts of LA you’ve never explored before!"),
                html.Li("Connect with other running groups at these locations. Ex: MRC, NPLA, NPWLA, Struggle Bus, and DHRC."),
                html.Li("Got questions or need support? Reach out to leadership or email Adam at amwermus@gmail.com."),
                html.Li("Above all—have fun, push yourself, support each other, and aim to conquer the challenge!"),
            ]),


            # Row with three images and bullet points
            dbc.Row([
                # First Image
                dbc.Col(
                    self.image_placer("/assets/hill_yeah_img7.jpg"), 
                    width=4
                ),
                # Second Image
                dbc.Col(
                    self.image_placer("/assets/hill_yeah_img8.jpg"), 
                    width=4
                ),
                # Third Image
                dbc.Col(
                    self.image_placer("/assets/hill_yeah_img9.jpg"), 
                    width=4
                ),
            ], className="mb-3"),  # Adds margin-bottom for spacing

            # Let's Go
            html.H2(
                    html.Span("LET'S GOOOOOOO!!! HILL Yeah!!!!", className="gradient-text"),
                    className="resource-portal-title mt-4"
                    )
        ]

    def combined_callback(self):
        """Handles submission form response, updating data, and visualization and a page refresh"""
        @self._app.callback(
            [
                Output("output-container", "children"),
                Output("location-table-portal", "data"),
                Output("top-reps-table", "data"),
                Output("total-vertical-bar-graph", "figure"),
                Output("total-vertical-table", "data")
            ],
            [
                Input("submit-button", "n_clicks"),
                Input("url", "pathname")
            ],
            [
                State("name", "value"),
                State("email", "value"),
                State("location-dropdown", "value"),
                State("num-repetitions", "value"),
                State("optional-link", "value")
            ],
            prevent_initial_call=True
        )
        def handle_submission_form(n_clicks, pathname, name, email, location, num_repetitions, optional_link):
            trigger = callback_context.triggered[0]["prop_id"].split(".")[0]


            # Determine if this callback was triggered by the form submission or by the page load
            if trigger == "submit-button" and n_clicks:

                # Check each field individually
                if not name:
                    return (
                        html.Div("Please enter a name!", style={"color": "red", 'textAlign': 'center'}),
                        [],  # Placeholder for location-table-portal.data
                        [],  # Placeholder for top-reps-table.data
                        {},  # Placeholder for total-vertical-bar-graph.figure
                        []   # Placeholder for total-vertical-table.data
                    )
                if not email:
                    return (
                        html.Div("Please enter a valid e-mail!", style={"color": "red", 'textAlign': 'center'}),
                        [], [], {}, []
                    )
                if not location:
                    return (
                        html.Div("Please select a location!", style={"color": "red", 'textAlign': 'center'}),
                        [], [], {}, []
                    )
                if not num_repetitions:
                    return (
                        html.Div("Please enter number of repetitions!", style={"color": "red", 'textAlign': 'center'}),
                        [], [], {}, []
                    )
                
                # Check if any fields were missed (might be redundant)
                if not (name and email and location and num_repetitions):
                    return (
                        html.Div("Please fill out all required fields.", style={"color": "red"}),
                        [], [], {}, []
                    )


                # Validate number of repetitions
                if not isinstance(num_repetitions, int) or num_repetitions <= 0:
                    return html.Div("Number of repetitions must be a positive integer.", style={"color": "red"})

                # Get the vertical value from the selected location and date
                vertical_value = self.get_vertical_value(location)
                total_submitted_feet = num_repetitions * vertical_value

                # Date
                date = pd.Timestamp.now().strftime("%Y-%m-%d")
                date_time = date = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")

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
                    "date_time": date_time,
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
                ),

            else:
                result = None
            
            # Load data once during app initialization
            self.location_data = self.db.get_unique_location_counts().to_dict('records')
            self.reps_data = self.db.get_top_reps_per_location().to_dict('records')
            self.total_vertical_data = self.db.get_total_vertical_per_person().to_dict('records')

            # Update bar graph
            # Top 10 for the bar graph
            top_10_df = self.db.get_total_vertical_per_person().nlargest(10, 'Total Vertical Feet')
    
            # Create figure for the bar graph
            self.bar_vert_graph = {
                'data': [
                    go.Bar(
                        x=top_10_df['Name'],
                        y=top_10_df['Total Vertical Feet'],
                        marker=dict(color='#FFA07A')
                    )
                ],
                'layout': go.Layout(
                    title="Top 10 Vert<br>(Feet)",
                    xaxis=dict(title="", tickangle=-45, automargin=True),
                    yaxis=dict(title="Total Vert<br>(Feet)", title_standoff=10),
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    margin=dict(l=60, r=20, t=40, b=120),
                )
            }

            return result, self.location_data, self.reps_data, self.bar_vert_graph, self.total_vertical_data



    def run(self):
        """Runs the application"""
        self._app.run(debug=True)
    


# Initialize and configure the application
run_app = Application()

# Expose the server to Gunicorn
server = run_app._app.server


# Run the app
if __name__ == "__main__":
    run_app.run()

