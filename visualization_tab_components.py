# This file contains definitions of dash components and callbacks used in the "data" tab of the app.

from dash import html, dcc
import dash_bootstrap_components as dbc
from params import POINT_SIZE, OPACITY  # default values

point_size_widget = [
    dbc.Col(html.Div("Velikost bodů: "), width=5),
    dbc.Col(dbc.Input(
        value=f"{POINT_SIZE}",
        id="point-size-input",
        type="number",
        min=1,
        max=50
    ), width=7)
]

point_color_widget = [
    dbc.Col(html.Div("Barevná škála: "), width=5),
    dbc.Col(dcc.Dropdown(
        options={'rgb': 'rudo-zeleno-modrá', 'rb': 'rudo-modrá', 'yr': 'žluto-rudá'},
        value='rgb',
        clearable=False,
        id='point-color-dropdown'
    ), width=7)
]

point_opacity_widget = [
    dbc.Col(html.Div("Průhlednost bodů: "), width=5),
    dbc.Col(dbc.Input(
        value=f"{OPACITY}",
        id="point-opacity-input",
        type="number",
        min=0,
        max=1,
        step=0.1
    ), width=7)
]

visualization_tab = [
    dbc.Row(dbc.Placeholder(color="white")),
    dbc.Row(html.Div("Zobrazení vrstev:")),
    dbc.Row(dcc.Checklist(
            options=[{'label': ' záběr z kamery', 'value': 'pic'}],
            value=['pic'],
            id='camera-picture-checkbox'
        )
    ),
    dbc.Row(dcc.Checklist(
            options=[{'label': ' mračno bodů', 'value': 'pcl'}],
            value=['pcl'],
            id='point-cloud-checkbox'
        )
    ),
    dbc.Row(dcc.Checklist(
            options=[{'label': ' vektorová data', 'value': 'vec'}],
            value=['vec'],
            id='vector-data-checkbox'
        )
    ),
    dbc.Placeholder(color="black", size="xs"),
    dbc.Row(point_size_widget),
    dbc.Placeholder(color="black", size="xs"),
    dbc.Row(point_color_widget),
    dbc.Placeholder(color="black", size="xs"),
    dbc.Row(point_opacity_widget)
]