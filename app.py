import requests
from dash import Dash, html, dcc
from dash.dependencies import Output, Input
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template

import pandas as pd
import plotly.express as px

app = Dash(__name__, external_stylesheets = [dbc.themes.SLATE])
server = app.server

load_figure_template('darkly')

app.layout = dbc.Container([
    html.H2(id='title', children="Weather Analytics", style = {'text-align':'center','font-weight':'bold','font-size':35, 'font-family':'sans-serif'}),
     dbc.Row([
         dcc.Input(id='loc', type='text', placeholder='Location'),
        dbc.Row(html.Button('View Stats', id='submit', style = {'margin-bottom':10,'width':300, 'margin-left':420,'border-radius':30,'background-color':'green','color':'white'})),

         dbc.Col([
        dbc.Row([
        dbc.Col([
            dcc.Graph(id='pie')
        ])
        
        ])
])
     ])
])

@app.callback(Output('submit','n_clicks'),Output('pie','figure'), Input('loc','value'), Input('submit','n_clicks'))

def draw(loc,clicks):
    if not clicks:
        raise PreventUpdate
    weather_requests = requests.get(
        f'https://api.weatherapi.com/v1/forecast.json?key=905b9d1765cd4e4abb5173151230411&q={loc}&days=2'
    )
    json_data = weather_requests.json()
    fcast = json_data['forecast']['forecastday'][0]['hour'] + json_data['forecast']['forecastday'][1]['hour']

    time = []
    temp = []

    for hour in fcast:
        time.append(hour['time'])
        temp.append(hour['temp_f'])
    df = pd.DataFrame(list(zip(time,temp)), columns=['time','temp'])
    figure = px.line(df, x='time',y='temp')
    clicks=None
    return clicks, figure


if __name__ == '__main__':
    app.run_server(debug=False)