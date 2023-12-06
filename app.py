import requests
from dash import Dash, html, dcc
from dash.dependencies import Output, Input
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template

import pandas as pd
import plotly.express as px
from datetime import datetime

app = Dash(__name__, external_stylesheets = [dbc.themes.SLATE])
server = app.server

load_figure_template('darkly')

app.layout = dbc.Container([
    html.H2(id='title', children="Real-Time Scheduled & Active Flight Stats", style = {'text-align':'center','font-weight':'bold','font-size':35, 'font-family':'sans-serif'}),
        dbc.Row(dcc.Link('Powered by aviationstack',href = 'https://aviationstack.com/'), style = {'text-align':'center','font-size':20}),
    dbc.Row([
        dbc.Col([
        
        html.H3('Origin Airport:', style={'margin-bottom':15, 'font-size':25, 'font-family':'sans-serif'}),
        dcc.Input(id='dep',type='text', placeholder='Departure Airport', style = {'text-align':'center','border-radius': 10})]),
        dbc.Col([
        html.H3('Destination Airport:', style={'margin-bottom':15,'font-size':25, 'font-family':'sans-serif'}),
        dcc.Input(id='arr', type='text', placeholder='Arrival Airport', style = {'text-align':'center','border-radius': 10})])], style = {'text-align':'center'}),
        html.Br(),
        dbc.Row(
        html.Button('View Stats', id='submit', style = {'margin-bottom':10,'width':300, 'margin-left':420,'border-radius':30,'background-color':'green','color':'white'}), style = {'text-align':'center'}),
        dbc.Row([
        dbc.Col([
            dcc.Graph(id='pie')
        ])])
        
    
])

@app.callback(Output("submit", "n_clicks"),Output('title','children'),Output('pie','figure'), Input('dep','value'), Input('arr','value'), Input('submit','n_clicks'))
def view_stats(dep, arr, clicks):
    if not clicks:
        raise PreventUpdate

    params = {
      'access_key': '349746e955fc67b11e41ece61dfad998',
        'dep_iata':dep,
        'arr_iata':arr,
        'flight_status':'scheduled'
    }
    params2 = {
      'access_key': '349746e955fc67b11e41ece61dfad998',
        'dep_iata':dep,
        'arr_iata':arr,
        'flight_status':'active'
    }

    response = requests.get('http://api.aviationstack.com/v1/flights', params)
    data = response.json()
    response2 = requests.get('http://api.aviationstack.com/v1/flights', params2)
    data2 = response2.json()
    
    data_all = data['data'] + data2['data']
    
    title = f"Flight Stats | {dep.upper()} - {arr.upper()}"
    
    airlines = []
    delayed = []
    iata = []
    unique_flights = []
    flights = filter(lambda x: x['flight_date'] == datetime.now().strftime('%Y-%m-%d'), data_all)
    for flight in flights:
        if flight['flight']['codeshared']!=None:
            if flight['flight']['codeshared']['flight_number'] not in unique_flights:
                unique_flights.append(flight['flight']['codeshared']['flight_number'])
                airline_lst = flight['flight']['codeshared']['airline_name'].split()
                new_lst = []
                for word in airline_lst:
                    new_word = word.title()
                    new_lst.append(new_word)
                airline = (' ').join(new_lst)
                
                delay = 0
                if flight['departure']['actual'] != None and flight['departure']['scheduled'] < flight['departure']['actual']:
                    delay += (datetime.strptime(flight['departure']['actual'][0:10] + ' '+ flight['departure']['actual'][11:19], '%Y-%m-%d %H:%M:%S') - datetime.strptime(flight['departure']['actual'][0:10] + ' '+ flight['departure']['actual'][11:19], '%Y-%m-%d %H:%M:%S')).total_seconds() / 60

                if delay >= 15:
                    delay_status = 'Delayed'
                else:
                    delay_status = 'On Time'
                    
                airlines.append(airline)
                delayed.append(delay_status)
                iata.append(flight['departure']['iata'])
        else:
            if flight['flight']['number'] not in unique_flights:
                
                unique_flights.append(flight['flight']['number'])
                airline = flight['airline']['name']
                
                delay = 0
                if flight['departure']['actual'] != None and flight['departure']['scheduled'] < flight['departure']['actual']:
                    delay += (datetime.strptime(flight['departure']['actual'][0:10] + ' '+ flight['departure']['actual'][11:19], '%Y-%m-%d %H:%M:%S') - datetime.strptime(flight['departure']['actual'][0:10] + ' '+ flight['departure']['actual'][11:19], '%Y-%m-%d %H:%M:%S')).total_seconds() / 60

                if delay >= 15:
                    delay_status = 'Delayed'
                else:
                    delay_status = 'On Time'
                airlines.append(airline)
                delayed.append(delay_status)
                iata.append(flight['departure']['iata'])
            
    

    df = pd.DataFrame(list(zip(airlines, delayed,iata)), columns=['Airline','Delay Status','Count'])
    figure = px.pie(df.groupby('Airline').count().reset_index(),values='Count',names='Airline', hole = 0.7, title='Airline Market Share')
    clicks = None
    return clicks,title, figure
    

if __name__ == '__main__':
    app.run_server(debug=False)

