# Import required libraries
import os
import pickle
import copy
import datetime as dt
import math
import sys

sys.path.append('/usr/local/lib/python3.7/site-packages')
import requests
import time as timee
import pandas as pd
import dash
import dash_ui as dui
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from plotly import graph_objs as go
from plotly.graph_objs import *
from plotly.subplots import make_subplots
from datetime import datetime as dt
from datetime import timedelta
from dateutil.relativedelta import relativedelta
import calendar
from collections import OrderedDict
import copy
# from flask import Flask
# import requests
from controls import CITIES, TIMES

#########################
# Basic stuff
#########################
app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = 'Baywheels KPI Dashboard'

app.config['suppress_callback_exceptions'] = True

app.css.append_css({
    "external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"
})

baywheels_logo = "https://upload.wikimedia.org/wikipedia/en/thumb/9/95/Bay_Wheels_logo.png/200px-Bay_Wheels_logo.png"

#########################
# Dashboard Layout / View
#########################

app.layout = \
    html.Div([
        dcc.Store(id='aggregate_data'),
        html.Div([
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
                style={
                    'display': 'inline-block'
                }
            ),
            html.Div(
                dcc.Dropdown(
                    id='time-dropdown',
                    options=[
                        {'label': 'Monthly', 'value': 'MTH'},
                        {'label': 'Quarterly', 'value': 'QTR'},
                    ], multi=False),
                style={
                    # 'height': '100%',
                    'width': '20%',
                    'font-size': "100%",
                    'min-height': '1px',
                    "lineHeight": "100%",
                    'display': 'inline-block',
                }
            ),
            html.Div(
                dcc.Dropdown(
                    id='city-dropdown',
                    options=[
                        {'label': 'San Francisco', 'value': 'San Francisco'},
                        {'label': 'San Jose', 'value': 'San Jose'},
                        {'label': 'Palo Alto', 'value': 'Palo Alto'},
                        {'label': 'Redwood City', 'value': 'Redwood City'},
                        {'label': 'Mountain View', 'value': 'Mountain View'},
                        {'label': 'All Cities', 'value': 'All Cities'},
                    ], multi=False),
                style={
                    # 'height': '100%',
                    'width': '20%',
                    'font-size': "100%",
                    'min-height': '1px',
                    "lineHeight": "100%",
                    'display': 'inline-block',
                }
            ),
            html.Div(
                dbc.NavLink("Switch to Operational Dashboard", href="/operations_dashboard", id="page-1-link"),
                style={
                    'width': '30%',
                    'display': 'inline-block',
                    'fontsize': '5px'
                }
            )
        ], className='row',
        ),

        html.Div([
            html.Div(
                children=[
                    html.Div(
                        [
                            html.H5(
                                id="completed-trips",
                                className="info_text",
                            ),
                            html.H6("Completed Trips"),
                            html.P(id="last-time-period1"),
                        ],
                        className="pretty_container"
                    ),
                    html.Div(
                        [
                            html.H5(
                                id="avg-min-bike",
                                className="info_text"
                            ),
                            html.H6("Avg daily mins per bike"),
                            html.P(id="last-time-period2"),
                        ],
                        className="pretty_container"
                    ),
                    html.Div(
                        [
                            html.H5(
                                id="revenue",
                                className="info_text"
                            ),
                            html.H6("Revenue"),
                            html.P(id="last-time-period3"),
                        ],
                        className="pretty_container"
                    ),
                    html.Div(
                        [
                            html.H5(
                                id="revenue-per-trip",
                                className="info_text"
                            ),
                            html.H6("Revenue per trip"),
                            html.P(id="last-time-period4"),
                        ],
                        className="pretty_container"
                    ),
                    html.Div(
                        [
                            html.H5(
                                id="co2-saved",
                                className="info_text"
                            ),
                            html.H6("CO2 emissions saved"),
                            html.P(id="last-time-period5"),
                        ],
                        className="pretty_container"
                    ),
                ],
                id="fourContainer"
            ),
        ]),
        # Trips and Station graphs
        html.Div(
            [
                # Trips graph
                html.Div([
                    dcc.Graph(id='trips-by-subs-graph'),
                ], className='pretty_container2 six columns'
                ),
                # Revenue
                html.Div([
                    dcc.Graph(id='stations-by-city-pie')
                ], className='pretty_container2 six columns'
                )
            ], className='row'
        ),
        html.Div(
            [
                # Distribution of Trips by City pie chart
                html.Div([
                    dcc.Graph(id='revenue-line-graph')
                ], className='pretty_container2 six columns'
                ),
                # Bottlenecks graph
                html.Div([
                    # dcc.Graph(id='bottlenecks-by-city-graph')
                    dcc.Graph(
                        id='example-graph',
                        figure={
                            'data': [
                                {'x': ['San Francisco', 'San Jose', 'Mountain View', 'Palo Alto', 'Redwood City'],
                                 'y': [90, 68, 60, 22, 11],
                                 'marker': ['#1D668D', '#24859C', '#51A298', '#58AEDC', '#92CFEF'],
                                 # no difference in colors tho
                                 'type': 'bar',
                                 }
                            ],
                            'layout': {
                                'title': '% of Stations with Bottlenecks by City'
                            }
                        }
                    )
                ], className='pretty_container2 six columns'
                )
            ], className='row'
        ),
    ]
    )

#############################################
# Interaction Between Components / Controller
#############################################
df = pd.read_csv('data/trip_data.csv')
df = df.iloc[:, 1:]

# HELPER FUNCTIONS
# Time
now = dt.now()
new_date = now - relativedelta(years=5)  # if we change current time to 5 years ago
new_date_1month = new_date - relativedelta(days=30)  # month
new_date_2month = new_date - relativedelta(days=60)  # previous month
new_date_1qtr = new_date - relativedelta(months=3)  # quarter
new_date_2qtr = new_date - relativedelta(months=6)  # previous quarter
new_date_1year_start = str(new_date.year - 1) + '-' + '0' + str(now.month) + '-01'  # previous year
# calculate cut off date for yearly
temp_date = new_date - relativedelta(months=1)
last_day_of_month = calendar.monthrange(temp_date.year, temp_date.month)[1]
new_date_1year_end = str(temp_date.year) + '-' + '0' + str(temp_date.month) + '-' + str(last_day_of_month)

mdf = df.copy()  # MOTHER DF


## FILTER
def filter_by_city(city):
    '''
    Filters the mother df based on city filter selected
    '''
    print(city)
    if city == 'All Cities':  # for 'All Cities'
        new_df = mdf
    elif city == 'San Francisco':
        new_df = mdf[mdf['start_city'] == 'San Francisco']
    elif city == 'San Jose':
        new_df = mdf[mdf['start_city'] == 'San Jose']
    elif city == 'Palo Alto':
        new_df = mdf[mdf['start_city'] == 'Palo Alto']
    elif city == 'Mountain View':
        new_df = mdf[mdf['start_city'] == 'Mountain View']
    elif city == 'Redwood City':
        new_df = mdf[mdf['start_city'] == 'Redwood City']
    else:
        new_df = mdf
    return new_df


def filter_by_time(df, time):
    '''
    Input: df refers to the df that has city filter applied to it.
           time refers to the time period (either 'Monthly' or 'Quarterly')
    Output: final filtered df by time
    '''
    lst = []
    print("filter_by_time" + str(time))

    if time == 'MTH':
        new_df = df[(df['converted_start_datetime'] > str(new_date_1month).split(' ')[0]) & (
                df['converted_start_datetime'] < str(new_date).split(' ')[0])]
        new_df1 = df[(df['converted_start_datetime'] > str(new_date_2month).split(' ')[0]) & (
                df['converted_start_datetime'] < str(new_date_1month).split(' ')[0])]

    elif time == 'QTR':
        new_df = df[(df['converted_start_datetime'] > str(new_date_1qtr).split(' ')[0]) & (
                df['converted_start_datetime'] < str(new_date).split(' ')[0])]
        new_df1 = df[(df['converted_start_datetime'] > str(new_date_2qtr).split(' ')[0]) & (
                df['converted_start_datetime'] < str(new_date_1qtr).split(' ')[0])]
    else:
        new_df = df[(df['converted_start_datetime'] > str(new_date_1month).split(' ')[0]) & (
                df['converted_start_datetime'] < str(new_date).split(' ')[0])]
        new_df1 = df[(df['converted_start_datetime'] > str(new_date_2month).split(' ')[0]) & (
                df['converted_start_datetime'] < str(new_date_1month).split(' ')[0])]

    # Get the yearly data to plot the graphs on the left of the dashboard
    df_year = df[(df['converted_start_datetime'] > str(new_date_1year_start).split(' ')[0]) & (
            df['converted_start_datetime'] < str(new_date_1year_end).split(' ')[0])]
    lst.append(new_df)
    lst.append(new_df1)
    lst.append(df_year)

    return lst


def filter_dataframe(time, city):
    '''
    applies city filter, then time filter
    input: city and time
    Output: list of 3 dataframes
    '''

    df = filter_by_city(city)
    lst = filter_by_time(df, time)
    # print("Filter Dataframe function")
    # print('lst[0].head()')
    # print(lst[0].head())
    # print('lst[1].head()')
    # print(lst[1].head())
    return lst


## KEY STATS
def delta_change(value1, value2):
    '''
    Description: This function calculates the sign of the difference in value1 and value2
    Input: value1 is curr month, value2 is for the previous time period
    Output: color
    '''
    diff = value1 - value2
    pctg_change = diff / value2 * 100.0 if value2 != 0 else float("inf") * abs(
        current) / current if current != 0 else 0.0

    if diff > 0:  # positive difference represents growth
        return (str(round(pctg_change)) + '%', 'green')
    elif diff == 0:
        return (0, 'yellow')
    else:  # negative difference represents declines
        return (str(round(pctg_change)) + '%', 'red')


def num_trips(lst):
    '''
    Description: takes in a list of dfs and output the num of trips for each time period
    Input: list of dfs
    Output: a tuple contaning number of trips for 1st time period, number of trips for 2nd time \
    period and color of sign indicating whether there is a rise or fall in the values from this \
    time period and the prev time period.
    '''
    value1 = len(lst[0].drop_duplicates())
    value2 = len(lst[1].drop_duplicates())
    deltaChange = delta_change(value1, value2)

    return value1, value2, deltaChange


def avg_mins_per_bike(lst):
    '''
    Description: takes in a list of dfs and output the avg mins per bike for each time period\
    essentially we are calculating the average of average mins per bike for all bikes within each time period
    Input: list of dfs
    Output: a tuple contaning avg mins per bike for 1st time period, avg mins per bike for 2nd time \
    period and color of sign indicating whether there is a rise or fall in the values from this \
    time period and the prev time period.
    '''

    value1 = lst[0].groupby('bike_id')['duration'].mean().sum() / lst[0]['bike_id'].nunique()
    value2 = lst[1].groupby('bike_id')['duration'].mean().sum() / lst[1]['bike_id'].nunique()
    deltaChange = delta_change(value1, value2)

    return int(round(value1 / 60)), int(round(value2 / 60)), deltaChange


def calc_revenue_fn(lst):
    #     lst[0]['paid']= lst[0].apply(lambda row: calculate(row['duration_in_minutes'],row['subscription_type']),axis=1)
    #     lst[1]['paid']= lst[1].apply(lambda row: calculate(row['duration_in_minutes'],row['subscription_type']),axis=1)
    value1 = lst[0]['paid'].sum()
    value2 = lst[1]['paid'].sum()
    deltaChange = delta_change(value1, value2)
    return value1, value2, deltaChange


def calc_revenue_per_trip_fn(lst):
    # lst[0]['paid'] = lst[0].apply(lambda row: calculate(row['duration_in_minutes'], row['subscription_type']), axis=1)
    # lst[1]['paid'] = lst[1].apply(lambda row: calculate(row['duration_in_minutes'], row['subscription_type']), axis=1)
    value1 = lst[0]['paid'].sum() / len(lst[0])
    value2 = lst[1]['paid'].sum() / len(lst[1])
    deltaChange = delta_change(value1, value2)
    return round(value1, 2), round(value2, 2), deltaChange


@app.callback(Output('aggregate_data', 'data'),
              [Input('time-dropdown', 'value'),
               Input('city-dropdown', 'value')])
def update_key_stats(time, city):
    dff = filter_dataframe(time, city)
    completedTrips = num_trips(dff)[0]
    avgMinBike = avg_mins_per_bike(dff)[0]
    revenue = '$' + str(calc_revenue_fn(dff)[0])
    revenuePerTrip = '$' + str(calc_revenue_per_trip_fn(dff)[0])
    co2saved = '250kg'
    return [completedTrips, avgMinBike, revenue, revenuePerTrip, co2saved]


@app.callback([
    Output('last-time-period1', 'children'),
    Output('last-time-period2', 'children'),
    Output('last-time-period3', 'children'),
    Output('last-time-period4', 'children'),
    Output('last-time-period5', 'children')
], [Input('time-dropdown', 'value')])
def update_time_period_text(time):
    if time == None or time == 'MTH':
        return 'Last 30 days', 'Last 30 days', 'Last 30 days', 'Last 30 days', 'Last 30 days'
    else:  # if time == 'QTR'
        return 'Last 3 months', 'Last 3 months', 'Last 3 months', 'Last 3 months', 'Last 3 months'


@app.callback(Output('completed-trips', 'children'),
              [Input('aggregate_data', 'data')])
def update_trips_text(data):
    return data[0]


@app.callback(Output('avg-min-bike', 'children'),
              [Input('aggregate_data', 'data')])
def update_avgMin_text(data):
    return data[1]


@app.callback(Output('revenue', 'children'),
              [Input('aggregate_data', 'data')])
def update_revenue_text(data):
    return data[2]


@app.callback(Output('revenue-per-trip', 'children'),
              [Input('aggregate_data', 'data')])
def update_rpt_text(data):
    return data[3]


@app.callback(Output('co2-saved', 'children'),
              [Input('aggregate_data', 'data')])
def update_co2_text(data):
    return data[4]


##### Graphs ######

layout = dict(
    autosize=True,
    automargin=True,
    margin=dict(
        l=30,
        r=30,
        b=20,
        t=40
    ),
    hovermode="closest",
    plot_bgcolor="#F9F9F9",
    paper_bgcolor="#F9F9F9",
    legend=dict(font=dict(size=10), orientation='h'),
    title='Satellite Overview',
)


# pie-graph
@app.callback(Output('stations-by-city-pie', 'figure'),
              [Input('time-dropdown', 'value'),
               Input('city-dropdown', 'value')])
def make_pie_figure(city, time):
    layout_pie = copy.deepcopy(layout)

    dff = filter_dataframe(city, time)

    vals = dff[0]['start_city'].value_counts().to_frame()  # this will always retrieve the stats for the time periods
    print(vals.head())
    labels = [vals.index[0], vals.index[1], vals.index[2], vals.index[3], vals.index[4]]
    # print(labels)

    values = [vals['start_city'][0], vals['start_city'][1], vals['start_city'][2], vals['start_city'][3],
              vals['start_city'][4]]
    # print(values)

    data = [
        dict(
            type='pie',
            labels=[vals.index[0], vals.index[1], vals.index[2], vals.index[3], vals.index[4]],
            values=[vals['start_city'][0], vals['start_city'][1], vals['start_city'][2], vals['start_city'][3],
                    vals['start_city'][4]],
            # name='Production Breakdown',
            text=['% of Trips in SF', '% of Trips in SJ', '% of Trips in MV', '% of Trips in PA', '% of Trips in RW'],
            hoverinfo="text+value+percent",
            textinfo="label+percent+name",
            # hole=0.5,
            marker=dict(
                colors=['#1D668D', '#24859C', '#51A298', '#58AEDC', '#92CFEF']
            ),
            domain={"x": [0, .45], 'y': [0.2, 0.8]},
        )
    ]
    layout_pie['title'] = 'Distribution of Trips by City'
    layout_pie['font'] = dict(color='#777777')
    layout_pie['legend'] = dict(
        font=dict(color='#CCCCCC', size='10'),
        orientation='h',
        bgcolor='rgba(0,0,0,0)'
    )

    figure = dict(data=data, layout=layout_pie)
    return figure

# helper function for chart below
def get_order_of_keys(period):
    '''
    :param period: a string, either 'MTH' or 'QTR' (monthly or quarterly)
    :return: order of keys
    '''
    print(dt.now().month)
    print(period)
    if dt.now().month == 3:
        if period == 'MTH' or period == None:
            order_of_keys = ['Mar 2014', 'Apr 2014', 'May 2014', 'Jun 2014', 'Jul 2014', 'Aug 2014', 'Sep 2014',
                                   'Oct 2014', 'Nov 2014', 'Dec 2014', 'Jan 2015', 'Feb 2015']
        elif period == 'QTR':
            order_of_keys = ['Mar 2014 - May 2014', 'Jun 2014 - Aug 2014', 'Sep 2014 - Nov 2014', 'Dec 2014 - Feb 2015']

        return order_of_keys

    elif dt.now().month == 4:
        if period == 'MTH' or period == None:
            order_of_keys = ['Apr 2014', 'May 2014', 'Jun 2014', 'Jul 2014', 'Aug 2014', 'Sep 2014',
                                   'Oct 2014', 'Nov 2014', 'Dec 2014', 'Jan 2015', 'Feb 2015', 'Mar 2015']
        elif period == 'QTR':
            order_of_keys = ['Apr 2014 - Jun 2014', 'Jul 2014 - Sep 2014', 'Oct 2014 - Dec 2014', 'Jan 2015 - Mar 2015']

        return order_of_keys

    else:
        print("Sorry this month is not supported...")

date_arr = [1,2,3,4,5,6,7,8,9,10,11,12]
minus1q = [date_arr[dt.now().month-2], date_arr[dt.now().month-3], date_arr[dt.now().month-4]]
minus2q = [date_arr[dt.now().month-5], date_arr[dt.now().month-6], date_arr[dt.now().month-7]]
minus3q = [date_arr[dt.now().month-8], date_arr[dt.now().month-9], date_arr[dt.now().month-10]]
minus4q = [date_arr[dt.now().month-11], date_arr[dt.now().month-12], date_arr[dt.now().month-13]]

def count_trips(df, time_dropdown):
    df = df[2]
    order_of_keys = get_order_of_keys(time_dropdown)
    if time_dropdown == 'MTH' or time_dropdown == None:
        trips_dict = df['monthYear'].value_counts().to_dict()
    elif time_dropdown == 'QTR':
        trips_dict = {}
        trips_dict[order_of_keys[0]] = len(df[df['start_date_month'].isin(minus4q)])
        trips_dict[order_of_keys[1]] = len(df[df['start_date_month'].isin(minus3q)])
        trips_dict[order_of_keys[2]] = len(df[df['start_date_month'].isin(minus2q)])
        trips_dict[order_of_keys[3]] = len(df[df['start_date_month'].isin(minus1q)])

    list_of_tuples = [(key, trips_dict[key]) for key in order_of_keys]
    trips_dict = OrderedDict(list_of_tuples)
    return trips_dict

def perc_trips_by_subs(df, time_dropdown):
    df = df[2]
    order_of_keys = get_order_of_keys(time_dropdown)
    if time_dropdown == None or time_dropdown == 'MTH':
        tbs = pd.crosstab(df['monthYear'], df['subscription_type'], normalize='index') * 100
        tbs_subs = tbs['Subscriber']
        tbs_dict = tbs_subs.to_dict()
        list_of_tuples1 = [(key, tbs_dict[key]) for key in order_of_keys]
        tbs_dict = OrderedDict(list_of_tuples1)
        for k, v in tbs_dict.items():
            tbs_dict[k] = round(v, 1)

    else: # time_dropdown == 'QTR'
        tbs_dict = {}
        quarters = [minus4q, minus3q, minus2q, minus1q]
        i = 0
        for q in quarters:
            dff = df[df['start_date_month'].isin(q)]
            temp = dff['subscription_type'].value_counts(normalize=True)*100
            subs_perc = temp['Subscriber'].round(1)
            tbs_dict[order_of_keys[i]] = subs_perc
            i+=1
    return tbs_dict

# bar-line-graph (num trips as bar chart and % of subscribers as line chart)
@app.callback(Output('trips-by-subs-graph', 'figure'),
              [Input('time-dropdown', 'value'),
               Input('city-dropdown', 'value')])

def make_bar_line_chart(time, city):

    layout1 = copy.deepcopy(layout)
    dff = filter_dataframe(time,city)
    ## Prepare the data for:
    # 1. number of trips as bar chart
    trips_dict = count_trips(dff, time)
    # print("Trips Dict")
    # print(trips_dict)

    # 2. % of trips by subscribers as line chart
    tbs_dict = perc_trips_by_subs(dff, time)
    # print("Tbs Dict")
    # print(tbs_dict)

    ## State colors
    colors = ['#1C668D',]*12

    ## Now put in the data
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Bar(x=list(trips_dict.keys()), y=list(trips_dict.values()), marker_color=colors, name='Number of Trips in the past year'),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(x=list(tbs_dict.keys()), y=list(tbs_dict.values()), name='% of Trips by Subscribers'),
        secondary_y=True,
    )

    # Add figure title
    fig.update_layout(
        autosize=True,
        margin=dict(
            l=30,
            r=30,
            b=20,
            t=40
        ),
        hovermode="closest",
        plot_bgcolor="#F9F9F9",
        paper_bgcolor="#F9F9F9",
        legend=dict(font=dict(size=10), orientation='h'),
        title_text="Trips by All Customers",
        title_x=0.5,
        xaxis=dict(automargin=True, tickfont={"size": 9.5},),
        yaxis=dict(automargin=True, title_text="Number of Trips"),
        yaxis2=dict(automargin=True, title_text="% of Trips by Subscribers")
    )
    return fig


def count_revenue(df, time_dropdown):
    order_of_keys = get_order_of_keys(time_dropdown)
    if time_dropdown == 'MTH':
        rev_dict = df[2].groupby('monthYear')['paid'].sum().to_dict()
    elif time_dropdown == 'QTR':
        rev_dict = {}
        rev_dict[order_of_keys[0]] = df[2][df[2]['start_date_month'].isin(minus4q)].paid.sum()
        rev_dict[order_of_keys[1]] = df[2][df[2]['start_date_month'].isin(minus3q)].paid.sum()
        rev_dict[order_of_keys[2]] = df[2][df[2]['start_date_month'].isin(minus2q)].paid.sum()
        rev_dict[order_of_keys[3]] = df[2][df[2]['start_date_month'].isin(minus1q)].paid.sum()

    else:
        rev_dict = df[2].groupby('monthYear')['paid'].sum().to_dict()

    list_of_tuples2 = [(key, rev_dict[key]) for key in order_of_keys]
    rev_dict = OrderedDict(list_of_tuples2)

    return rev_dict


# line-graph (revenue)
@app.callback(Output('revenue-line-graph', 'figure'),
              [Input('time-dropdown', 'value'),
               Input('city-dropdown', 'value')])
def make_line_graph(time, city):
    layout_line = copy.deepcopy(layout)
    dff = filter_dataframe(time, city)
    revenue_per_month = count_revenue(dff, time)

    data = [
        dict(
            type='scatter',
            mode='lines+markers',
            name='Revenue ($)',
            x=list(revenue_per_month.keys()),
            y=list(revenue_per_month.values()),
            line=dict(
                shape="spline",
                smoothing=2,
                width=1,
            ),
            marker=dict(symbol='diamond-open')
        )
    ]
    layout_line['title'] = 'Total Revenue'
    layout_line['xaxis'] = dict(automargin=True, tickfont={"size": 9.5})
    figure = dict(data=data, layout=layout_line)

    return figure


##### Main
if __name__ == '__main__':
    app.server.run(debug=True, threaded=True)
