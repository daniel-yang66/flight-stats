import requests
from dash import Dash, html, dcc
from dash.dependencies import Output, Input
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
            style = {'margin-bottom':12,'text-align':'center','font-weight':'bold','font-size':40, 'font-family':'sans-serif','margin-top':7}),
    dbc.Row(
    dcc.Link('Powered by WeatherAPI.com', target='_blank', href = "https://www.weatherapi.com/", style = {'font-weight':'bold','font-size':20, 'font-family':'sans-serif'}),
     style = {'text-align':'center'}),
        html.Br(),
    dbc.Row([
    dbc.Col([
        html.H5('Enter Location:' , style = {'margin-bottom':12}),
        dcc.Input(id='loc', type='text', value='San Francisco', placeholder='Location', 
                   style = {'height':30,'text-align':'center','border-radius': 10, 'margin-bottom':12, 'width':150}),
        html.H5('Metric to Visualize:', style = {'margin-bottom':12}),
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
    dbc.Row(
        dcc.Graph(id='bar')
    ),
    dbc.Row([
        dbc.Col(
    html.Footer("Copyright", style = {'margin-left':-30}), width = 1),
        dbc.Col(
    dcc.Link('Daniel Yang', target = '_blank', href= 'https://www.linkedin.com/in/daniel-yang-a17ab3229/', style = {'margin-left': -47}), 
            width = 11)], style = {'margin-bottom':10})])
@app.callback(
              Output('line','figure'), 
              Output('donut','figure'),
              Output('bar','figure'),
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
    wind_dir = []
    epoch = time()

    for day in fcast:
        hour_data = day['hour']
        hours = filter(lambda x: x['time_epoch'] > epoch, hour_data)
        for hour in hours:
            wind_dir.append(hour['wind_dir'])
            date.append(hour['time'])
            temp.append(hour['temp_f'])
            wind.append(hour['wind_mph'])
            clouds.append(hour['cloud'])
            humidity.append(hour['humidity'])
            condition.append(hour['condition']['text'])

    df = pd.DataFrame(list(zip(date,temp,condition,wind,clouds,humidity, wind_dir)), 
                      columns=['Time','Temp','Condition','Wind (mph)','Cloud Cover (%)','Humidity (%)','Wind Direction'])
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
    df2 = df2.rename(columns = {'Temp':'Count'})
    
    df3 = df.groupby('Wind Direction').count().reset_index().sort_values(by='Temp', ascending=False)
    df3 = df3.rename(columns = {'Temp':'Count'})
    
    line = px.line(df, x='Time',y=metric, title = f'{metric} Over Time').update_traces(line_color='green')
    donut = px.pie(df2, hole = 0.7, values = 'Count', names = 'conditions_new', title = 'Condition Outlook').update_layout(showlegend=False)
    bar = px.bar(df3, x='Wind Direction', y='Count', title = 'Wind Direction Frequency').update_traces(marker_color = 'green')
    
    return line, donut, bar


if __name__ == '__main__':
    app.run_server(debug=False)