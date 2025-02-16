# This file contains definitions of dash components and callbacks used in the "data" tab of the app.

from dash import html, dcc
import dash_bootstrap_components as dbc

down_panel_upper = [
    dbc.Col(dbc.Button(html.I(className="bi bi-play-fill"), id='play-button'), width=1),
    dbc.Col(html.Div("00:00", id="current-time-div"), width=1),
    dbc.Col(dcc.Input(
        value=0,
        id="camera-position-slider-input",
        type="range",
        min=0,
        max=499,
        style={'width': '100%'}
    ), width=9),
    dbc.Col(html.Div("00:19", id="total-time-div"), width=1),
]

down_panel_lower = [
    html.Div("Snímek:"),
    dbc.Input(
        value="0",
        id="camera-position-input",
        type="number",
        min=0,
        max=499,
        style={'width':'90px'}
    ),
    html.Div(
        "",
        className="ms-auto",   # works as a spacer
    ),
    html.Div("Rychlost:"),
    dcc.Dropdown(
        options={'2': '2×', '1': '1×', '0.5': '0.5×'},
        value='1',
        clearable=False,
        id='animation-speed-dropdown',
        style={'width':'80px'}
    )
]
