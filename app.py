"""
Author: Adam Wermus
Date: September 30, 2024

Initial web app using dash
"""
# Initial import
import dash
from dash import html
import dash_bootstrap_components as dbc

class App():

    def __init__(self):
        # initial dash app
        self._app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

    def create_layout(self):
        self._app.layout = dbc.Container([dbc.Row(dbc.Col(html.H1('What The Hill',
        className='text-center'))),
        dbc.Row(dbc.Col(html.P('A Hill and Stair Exploration Adventure Across Los Angeles.', className='text-center'))),
        ])


    def run(self):
        """Runs the application"""
        self._app.run(debug=True)
    


# Run the app
if __name__ == "__main__":
    app = App()
    app.create_layout()
    app.run()

