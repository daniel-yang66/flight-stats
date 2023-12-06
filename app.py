import requests
from dash import Dash, html, dcc
from dash.dependencies import Output, Input
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
from time import time

import pandas as pd
import plotly.express as px

app = Dash(__name__, external_stylesheets = [dbc.themes.SLATE])
server = app.server

load_figure_template('slate')

app.layout = dbc.Container([
    html.H2(id='title', children="MeteoAnalytics", 
            style = {'margin-bottom':12,'text-align':'center','font-weight':'bold','font-size':35, 'font-family':'sans-serif','margin-top':7}),
    dbc.Row(
    dcc.Link('Powered by WeatherAPI.com', target='_blank', href = "https://www.weatherapi.com/", style = {'font-weight':'bold','font-size':22, 'font-family':'sans-serif'}),
     style = {'text-align':'center'}),
        html.Br(),
    dbc.Row([
    dbc.Col([
        html.H3('Enter Location:' , style = {'margin-bottom':12}),
        dcc.Input(id='loc', type='text', value='San Francisco', placeholder='Location', 
                   style = {'height':30,'text-align':'center','border-radius': 10, 'margin-bottom':12, 'width':150}),
        html.H3('Metric to Visualize:', style = {'margin-bottom':12}),
            dcc.Dropdown(id='metric',options = ['Temp','Humidity (%)','Cloud Cover (%)','Wind (mph)'], value = 'Temp', style = {'width':150}),
        html.Br(),
        ], width = 2),
        dbc.Col(
            dbc.Row([
            dbc.Col(
            dcc.Graph(id='line'), width = 7),
            dbc.Col(
            dcc.Graph(id='donut'), width = 5)]), width = 10)
            
        
        

]),
    dbc.Row([
        dbc.Col(
    html.Footer("Copyright", style = {'margin-left':-25}), width = 1),
        dbc.Col(
    dcc.Link('Daniel Yang', target = '_blank', href= 'https://www.linkedin.com/in/daniel-yang-a17ab3229/', style = {'margin-left': -40}), 
            width = 11)])])
@app.callback(
              Output('line','figure'), 
              Output('donut','figure'),
              Input('loc','value'),
              Input('metric','value'))

def draw(loc,metric):

    resp = requests.get(
        f'https://api.weatherapi.com/v1/forecast.json?key=905b9d1765cd4e4abb5173151230411&q={loc}&days=3'
    )
    
    data = resp.json()
    
    fcast = data['forecast']['forecastday']
    
    date = []
    temp = []
    humidity = []
    clouds = []
    condition = []
    wind = []
    epoch = time()

    for day in fcast:
        hour_data = day['hour']
        hours = filter(lambda x: x['time_epoch'] > epoch, hour_data)
        for hour in hours:
            date.append(hour['time'])
            temp.append(hour['temp_f'])
            wind.append(hour['wind_mph'])
            clouds.append(hour['cloud'])
            humidity.append(hour['humidity'])
            condition.append(hour['condition']['text'])

    df = pd.DataFrame(list(zip(date,temp,condition,wind,clouds,humidity)), 
                      columns=['Time','Temp','Condition','Wind (mph)','Cloud Cover (%)','Humidity (%)'])
    conditions = df['Condition'].tolist()
    cond_list = []
    for c in conditions:
        if c=='Sunny':
            cond_list.append('Clear')
        elif 'rain' in c or 'drizzle' in c:
            cond_list.append('rain')
        elif c=='Overcast':
            cond_list.append('Cloudy')
        else:
            cond_list.append(c)
    df['conditions_new'] = cond_list

    df2 = df.groupby('conditions_new').count().reset_index()
    df2.columns = ['Condition','Temp','Time','Count','Wind','Cloud','Humidity']
    
    line = px.line(df, x='Time',y=metric, title = f'{metric} Over Time').update_traces(line_color='green')
    donut = px.pie(df2, hole = 0.7, values = 'Count', names = 'Condition', title = 'Condition Outlook').update_layout(showlegend=False)
    
    return line, donut


if __name__ == '__main__':
    app.run_server(debug=False)
