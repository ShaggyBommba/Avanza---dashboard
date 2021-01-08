# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.


# Utility functions
from pandas.core.indexes import multi
import Model
from Data.DataManager import DataManager 
import numpy as np
import pandas as pd

# Dash and plotly 
import dash
import plotly.express as px
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go


### Variables ###
dm = DataManager()
options = [{'label' : stock, 'value' : stock, 'disabled' : not available} for (stock,available) in 
                            zip(dm.retrieveInformation(columns="Kortnamn"),dm.priceAvailable())]
d = dm.getOptionsAvailable()
stock_info = dm.retrieveInformation()


app = dash.Dash(__name__, external_stylesheets=["Datascience\Projects\Effective frontier\Assets\Layout.css"])
app.layout = html.Div( children=[
   
    ### Top part ###
    html.Div(children = [
        html.H1("Stocks",  
            style={
                'textAlign': 'center',
                'color':"#ffffff"
            }
        ), 
        html.Div(children = [
            html.Div(
                html.Div(children = [
                    # Construct a filter dropdown menu responsible for the feature selection
                    html.Div( 
                        dcc.Dropdown(
                            id = "filter_feature",
                            options=[{ "label" : key, "value" : key} for key,value in d.items()]), 
                        className= "six columns"),
                    # Construct a filter dropdown menu responsible for the lable selection
                    html.Div(
                        dcc.Dropdown(
                            id = "filter_lable"),
                        className="six columns")           
                ],className="row"), className="six columns"),
                    
            html.Div(
                html.Div(children=[
                    # Construct the drop down menu responsible for the ording selection 
                    html.Div(
                        dcc.Dropdown(id = "order",
                                options= [{ "label" : key, "value" : key} for key,value in d.items()]), 
                        className ="ten columns"),
                    # Construct the button to uppdate data 
                    html.Div([
                        dcc.ConfirmDialogProvider(
                            children=html.Button('Uppdate',style={"background-color" : "white"}),
                            id='uppdate',
                            message='"Uppdating"'
                        ),
                        html.Div(id='output-provider')
                    ],className ="two columns")
                ],className="row"), className="six columns"
            )
        ], className="row", style= { "padding-bottom" : 20}),


        # Table that show the available stocks. 
        html.Div([
            dcc.Graph(id = "information_stocks",
                figure= go.Figure(data=[go.Table(
                    header=dict(values=["Namn", "Bransch", "Kurs/eget kapital", "Omsättning/aktie SEK", "P/E-tal", "P/S-tal"], align='left'),
                    cells= dict(values=[stock_info.index, 
                                    stock_info["Bransch"], 
                                    stock_info["Kurs/eget kapital"],
                                    stock_info["Omsättning/aktie SEK"],
                                    stock_info["P/E-tal"],
                                    stock_info["P/S-tal"]],
                                    align='left')
                    )
                ], layout = go.Layout(
                    margin=dict(l=0,r=0,t=0,b=0)
                    )
                ))
        ])], style= {"background" : "#040308", "paddingTop" : 20, "padding-right" : 20, "padding-left" : 20}
    ),
    # Stock information
    html.Div(children = [
        html.H1("Stock information",  
            style={
                'textAlign': 'center',
                'color':"#ffffff"
            }),
        # Consists of a figure, a table, and a dropdown box.
        html.Div(children=[
            # Show a candlestick figure for the selected stock. 
            html.Div(children=[
                dcc.Graph(
                    id = "candlestick",     
                )], className="eight columns"),
            # Show a dropdown menu depicting the available stock. 
            html.Div(children=[
                dcc.Dropdown(
                    id = "select_stock",
                    options = options,
                    multi=False,
                    style = {"padding-bottom" : 10}),
                # Show the table with the information of the selected stock.
                dcc.Graph(
                    id = "information_stock",
                    figure= go.Figure(data=[
                        go.Table(
                            header=dict(values=["Attribute","Values"], align="left")                 
                        )
                    ]))
            ], className="four columns")], className="row")],  
        style= {"background" : "#332763", "paddingTop" : 20, "padding-right" : 20, "padding-left" : 20}
    ),
    ## Fronties
    html.Div(children = [
        html.H1("Efficient-frontier-optimization",  
            style={
                'textAlign': 'center',
                'color':"#ffffff"
            }),
        # Multi-Select Dropdown 
        html.Div(children=[
            html.Label('Multi-Select Dropdown'),
            dcc.Dropdown(
                id='select_stocks',
                options= options,
                multi = True)]),
        
        # Graph - frontier
        html.Div(children=[
            dcc.Graph(
                id = "frontier"                
            )])
    ],style= {"background" : "#543fa6", "paddingTop" : 20, "padding-right" : 20, "padding-left" : 20}
    )
])
  

@app.callback(  
    Output(component_id='filter_lable', component_property='options'),
    [Input(component_id='filter_feature', component_property='value')])

def updateSelection(filter_feature):
    if (filter_feature != None):
        return [{"value" : val, "label" : val} for val in d[filter_feature]]
    else:
        return []



@app.callback( 
    Output(component_id='output-provider', component_property='children'),
    [Input(component_id='uppdate', component_property='submit_n_clicks')])

def downloadData(submit_n_clicks):
    if not submit_n_clicks:
        return ''
    else:
        dm.uppdate(save=False)
    return """Uppdating"""



@app.callback(  
    Output(component_id="information_stocks", component_property='figure'),
    [Input(component_id="order", component_property='value')],
    [State(component_id='filter_lable', component_property='value'),
    State(component_id='filter_feature', component_property='value')])

def uppdateTable(order, filter_lable, filter_feature):
    stocks = stock_info

    if(filter_lable != None and filter_feature != None):
        # Creating masks 
        if(isinstance(filter_lable, float) or isinstance(filter_lable, int)):
            values = d[filter_feature]
            pos = np.where(values == filter_lable)[0]
            stocks = stock_info.loc[(stock_info[filter_feature] != '-') , :]
            stock = stocks[filter_feature].astype("float")
            if( pos == 0):
                mask = (stock < values[pos][0]) 
            elif(pos == (len(values)-1)):
                mask = (stock > values[pos][0])
            else:
                mask = ( (stock > values[pos-1][0])&(stock < values[pos+1][0]) )
        else:
            mask = (stock_info[filter_feature] == filter_lable)
        stocks = stocks.loc[mask,:]

    if ( order != None):
        # Ordering the data. 
        mask = (stocks[order] == '-')
        upper = stocks.loc[mask,:]
        try: 
            lower = stocks.loc[~mask,:].astype({order : "float"})
        except ValueError:
            lower = stocks.loc[~mask,:].astype({order : "str"})
        lower = lower.sort_values(by=[order])
        stocks = pd.concat([upper, lower])

    figure= go.Figure(data=[go.Table(
                    header=dict(values=["Namn","Bransch", "Kurs/eget kapital", "Omsättning/aktie SEK", "P/E-tal", "P/S-tal"], align='left'),
                    cells= dict(values=[stocks.index, 
                                    stocks["Bransch"], 
                                    stocks["Kurs/eget kapital"],
                                    stocks["Omsättning/aktie SEK"],
                                    stocks["P/E-tal"],
                                    stocks["P/S-tal"]],
                                    align='left')
                    )
                ], layout = go.Layout(
                    margin=dict(l=0,r=0,t=0,b=0)
                    )
                )
    return figure



@app.callback(
    [Output(component_id='candlestick', component_property='figure'),
     Output(component_id="information_stock", component_property='figure')],
    [Input(component_id="select_stock", component_property='value')] 
    )

def uppdateStock(select_stock):
    if(select_stock != None):
        # Candelstick for the selected stock
        df_candlestick = dm.retrievePrices([select_stock], drop=True)
        candlestick = go.Figure(data=[go.Candlestick(x=df_candlestick.index,
                                    open=df_candlestick['Open'],
                                    high=df_candlestick['High'],
                                    low=df_candlestick['Low'],
                                    close=df_candlestick['Close'])],
                                    layout = go.Layout(
                                        height=500,
                                        margin = dict(l=0,r=0,t=0,b=0)
                                        )
                                    )
                                    
        # Table for the selected stock 
        df_information_stock = dm.retrieveInformation(select_stock)
        information_stock = go.Figure(data=[
                                    go.Table(
                                    header = dict(values=["Attribute","Values"], align="left"),
                                    cells = dict(values = [df_information_stock.index, df_information_stock.values], align="left")
                                    )],
                                     layout = go.Layout(
                                        height=450, 
                                        margin = dict(l=0,r=0,t=0,b=0)
                                    ))    
    
    else: 
        candlestick = go.Figure(data=go.Scatter())
        information_stock = go.Figure(data=go.Scatter())
   

    
    return (candlestick, information_stock)
    


@app.callback(  
    Output('frontier', 'figure'),
    [Input('select_stocks', 'value')])

def updateFrontier(select_stocks):
    # The Figure that depicts the frontier.
    frontier= go.Figure(data=go.Scatter())
    if(select_stocks != None):
        if(len(select_stocks) > 1):
            df_frontier = dm.retrievePrices(stock=select_stocks, columns=["Close"], drop=True)
            returns, risks, sharpe, wheights = Model.buildFrontier(df_frontier)
            frontier = go.Figure(data=go.Scattergl(
                x = risks,
                y = returns,
                mode='markers',
                text=wheights,
                marker=dict(
                    color=sharpe,
                    colorscale='Viridis',
                    line_width=1,
                    showscale=True
                    )
                ),
                layout = go.Layout(
                    height=700,
                    margin = dict(l=0,r=0,b=0,t=0)
                ))
    return frontier



if __name__ == '__main__':
    app.run_server(debug=True)


