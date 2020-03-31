# Import required libraries
import os
import pickle
import copy
import datetime as dt
import math
import sys
sys.path.append('/usr/local/lib/python3.7/site-packages')

import requests
import pandas as pd
#from flask import Flask
import dash
import dash_ui as dui
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from plotly import graph_objs as go
from plotly.graph_objs import *
import requests
from controls import CITIES, TIMES

#API Key
mapbox_access_token = 'pk.eyJ1IjoidmljdG9yaWF0ZW8iLCJhIjoiY2s3eXZwYnZuMDAwYzNtbXVjZmZrNWR5dyJ9.tNAzZh9QzslDrPb7azgi8Q'
#Data Set


app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = 'Baywheels KPI Dashboard'

app.css.append_css({
    "external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"
})


baywheels_logo = "https://upload.wikimedia.org/wikipedia/en/thumb/9/95/Bay_Wheels_logo.png/200px-Bay_Wheels_logo.png"


# Create controls
def onLoad_city_options():
    city_options = ([{'label': str(CITIES[city]), 'value': str(city)}
                  for city in CITIES])
    return city_options

def onLoad_time_options():
    time_options = ([{'label': str(TIMES[time]), 'value': str(time)}
                  for time in TIMES])
    return time_options

time_periods = [
    dbc.DropdownMenuItem("Monthly"),
    dbc.DropdownMenuItem(divider=True),
    dbc.DropdownMenuItem("Quarterly"),
]

cities = [
    dbc.DropdownMenuItem("Mountain View"),
    dbc.DropdownMenuItem(divider=True),
    dbc.DropdownMenuItem("Palo Alto"),
    dbc.DropdownMenuItem(divider=True),
    dbc.DropdownMenuItem("Red Wood City"),
    dbc.DropdownMenuItem(divider=True),
    dbc.DropdownMenuItem("San Francisco"),
    dbc.DropdownMenuItem(divider=True),
    dbc.DropdownMenuItem("San Jose"),
]

navbar = dbc.Navbar(
    [
        html.A(
            dbc.Row(
                [
                    dbc.Col(html.Img(src=baywheels_logo, height="60px")),
                    dbc.Col(dbc.NavbarBrand("KPI Dashboard", className="ml-2")),
                    ]
                ,

                align="center",
                no_gutters=True,
            ),
            href="http://127.0.0.1:5000/",
        ),

        html.A(
            dbc.Row(
                [
                    dbc.Col(dbc.DropdownMenu(label="Monthly", children=time_periods, className="mb-3")),
                    dbc.Col(dbc.DropdownMenu(label="All Cities", children=cities, className="mb-3")),
                ]
            )
        ),

        html.A(
            dbc.Row(
                dbc.Col(dbc.NavLink("Switch to Operational Dashboard", href="/operations_dashboard", id="page-1-link")),
                align="right",
            )
        ),
        #dbc.NavbarToggler(id="navbar-toggler")
    ],
    color="#F6F6F6", #light grey color
)

card_content = [
    dbc.CardBody(
        [
            html.H5("Card title", className="card-title"),
            html.H6(
                "Completed Trips",
                className="card-subtitle",
            ),
            html.P("last 30 days", className="card-text"),
        ]
    ),
]

cards = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(dbc.Card(card_content, color="light")),
                dbc.Col(dbc.Card(card_content, color="light")),
                dbc.Col(dbc.Card(card_content, color="light")),
                dbc.Col(dbc.Card(card_content, color="light")),
                dbc.Col(dbc.Card(card_content, color="light")),
            ],
            className="mb-4",
        ),
    ]
)
# graphRow1 = dbc.Row([dbc.Col(pie, md=6), dbc.Col(bar, md=6)])
# app.layout = html.Div([navbar,html.Br(),graphRow0, html.Br(), graphRow1], style={'backgroundColor':'black'})
bar = dcc.Graph(
    figure={
        'data': [{
            'x': [1, 2, 3],
            'y': [3, 1, 2],
            'type': 'bar'
        }],
        'layout': {
            'height': 400,
            'margin': {
                'l': 10, 'b': 20, 't': 0, 'r': 0
            }
        }
    }
)

# graphRow1 = dbc.Row([dbc.Col(bar, md=4), dbc.Col(bar, md=4), dbc.Col(bar,md=4)])
# graphRow2 = dbc.Row([dbc.Col(bar, md=4), dbc.Col(bar, md=4), dbc.Col(bar,md=4)])

# app.layout = html.Div(
# #     [
# #         dcc.Location(id="url"),
# #         navbar,
# #         html.Br(),
# #         cards,
# #         html.Div([
# #             html.Div([
# #                 html.H3('Column 1'),
# #                 dcc.Graph(id='g4', figure={'data': [{'y': [1, 2, 3,4]}]})
# #             ], className="six columns"),
# #
# #             html.Div([
# #                 html.H3('Column 2'),
# #                 dcc.Graph(id='g5', figure={'data': [{'y': [1, 2, 3,4]}]})
# #             ], className="six columns"),
# #
# #         ], className="row"),
# #
# #     ]
# # )

app.layout = html.Div(
    html.Div([
        html.Div(
            [
                navbar,
                html.Br(),
                cards,
                # html.H1(children='Hello World',
                #         className='nine columns'),
                # html.Img(
                #     src="http://test.fulcrumanalytics.com/wp-content/uploads/2015/10/Fulcrum-logo_840X144.png",
                #     className='three columns',
                #     style={
                #         'height': '9%',
                #         'width': '9%',
                #         'float': 'right',
                #         'position': 'relative',
                #         'margin-top': 10,
                #     },
                # ),
                # html.Div(children='''
                #         Dash: A web application framework for Python.
                #         ''',
                #         className='nine columns'
                # )
            ], className="row"
        ),

        html.Div(
            [
            html.Div([
                html.Div([
                dcc.Graph(
                    id='example-graph-2',
                    figure={
                        'data': [
                            {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'line', 'name': 'SF'},
                            {'x': [1, 2, 3], 'y': [2, 9, 8], 'type': 'line', 'name': u'Montréal'},
                        ],
                        'layout': {
                            'title': 'Graph 2'
                        }
                    }
                )
                ], className= 'row'
                )
            ], className="four columns"
        ),
        html.Div([
            dcc.Graph(
                id='example-graph-4',
                figure={
                    'data': [
                        {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'line', 'name': 'SF'},
                        {'x': [1, 2, 3], 'y': [2, 9, 8], 'type': 'line', 'name': u'Montréal'},
                    ],
                    'layout': {
                        'title': 'Graph 2'
                    }
                }
            )
        ], className='row'
        )
    ], className="four columns"
        ),
        html.Div([
            dcc.Graph(
                id='example-graph-3',
                figure={
                    'data': [
                        {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'line', 'name': 'SF'},
                        {'x': [1, 2, 3], 'y': [2, 9, 8], 'type': 'line', 'name': u'Montréal'},
                    ],
                    'layout': {
                        'title': 'Graph 2'
                    }
                }
            )
        ], className='row'
        )
    ], className="twelve columns"
    ),
)

# def create_card(title, content, period):
#     card = dbc.Card(
#         dbc.CardBody(
#             [
#                 html.Br(),
#                 html.Br(),
#                 html.H3(title, className="card-title"),
#                 html.Br(),
#                 html.H5(content, className="card-subtitle"),
#                 html.Br(),
#                 html.H6(period, className="card-text"),
#                 ]
#         ),
#         color="info", inverse=True
#     )
#     return(card)
#
# card1 = create_card("3400", "Completed Trips", "last 30 days")
# card2 = create_card("Number of Likes On Articles", "None Likes", "last 30 days")
# card3 = create_card("Number of Articles", "None Articles", "last 30 days")
# card4 = create_card("Number of Comment on Articles", "None Comments", "last 30 days")
# card5 = create_card("Number of Comment on Articles", "None Comments", "last 30 days")
#
# graphRow0 = dbc.Row([dbc.Col(id='card1', children=[card1], md=2.4), dbc.Col(id='card2', children=[card2], md=2.4), dbc.Col(id='card3', children=[card3], md=2.4), dbc.Col(id='card4', children=[card4], md=2.4), dbc.Col(id='card5', children=[card5], md=2.4)])


#
# # this callback uses the current pathname to set the active state of the
# # corresponding nav link to true, allowing users to tell see page they are on
# @app.callback(
#     [Output(f"page-{i}-link", "active") for i in range(1, 2)],
#     [Input("url", "pathname")],
# )
# def toggle_active_links(pathname):
#     if pathname == "/":
#         # Treat page 1 as the homepage / index
#         return True, False, False
#     return [pathname == f"/page-{i}" for i in range(1, 2)]
#
#
# @app.callback(Output("page-content", "children"), [Input("url", "pathname")])
# def render_page_content(pathname):
#     if pathname in ["/", "/operations_dashboard"]:
#         return html.P("This is the content of page 1!")
#     elif pathname == "/page-2":
#         return html.P("This is the content of page 2. Yay!")
#     # If the user tries to reach a different page, return a 404 message
#     return dbc.Jumbotron(
#         [
#             html.H1("404: Not found", className="text-danger"),
#             html.Hr(),
#             html.P(f"The pathname {pathname} was not recognised..."),
#         ]
#     )

###



# Main
if __name__ == '__main__':
    app.server.run(debug=True, threaded=True)