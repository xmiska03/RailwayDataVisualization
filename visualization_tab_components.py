# This file contains definitions of dash components and callbacks used in the "data" tab of the app.

from dash import html, dcc
import dash_bootstrap_components as dbc
from params import POINT_SIZE, OPACITY, LINE_WIDTH  # default values

point_size_widget = [
    dbc.Col(html.Div("Velikost bodů: "), width=5),
    dbc.Col(dbc.Input(
        value=f"{POINT_SIZE}",
        id="point-size-input",
        type="number",
        min=1,
        max=50
    ), width=6)
]

point_color_widget = [
    dbc.Col(html.Div("Barevná škála: "), width=5),
    dbc.Col(dcc.Dropdown(
        options={'rgb': 'rudo-zeleno-modrá', 'rb': 'rudo-modrá', 'yr': 'žluto-rudá'},
        value='rgb',
        clearable=False,
        id='point-color-dropdown'
    ), width=6)
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
    ), width=6)
]

line_width_widget = [
    dbc.Col(html.Div("Tloušťka čar: "), width=5),
    dbc.Col(dbc.Input(
        value=f"{LINE_WIDTH}",
        id="line-width-input",
        type="number",
        min=10,
        max=150,
        step=5
    ), width=6)
]

line_color_widget = [
    dbc.Col(html.Div("Barva čar: "), width=5),
    dbc.Col(dbc.Input(
        type="color",
        id="line-color-picker",
        value="#fa650f",
    ), width=6)
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
    dbc.Row(html.Hr()),
    dbc.Row(html.Div("Mračno bodů", style={"fontWeight": "bold", "textAlign": "center", "paddingBottom": "0.5em",})),
    dbc.Row(point_size_widget),
    dbc.Placeholder(color="black", size="xs"),
    dbc.Row(point_color_widget),
    dbc.Placeholder(color="black", size="xs"),
    dbc.Row(point_opacity_widget),
    dbc.Placeholder(color="black", size="xs"),
    dbc.Row(html.Hr()),
    dbc.Row(html.Div("Vektorová data", style={"fontWeight": "bold", "textAlign": "center", "paddingBottom": "0.5em",})),
    dbc.Row(line_width_widget),
    dbc.Placeholder(color="black", size="xs"),
    dbc.Row(line_color_widget),
    dbc.Placeholder(color="black", size="xs"),
    dbc.Row(html.Hr()),
    dbc.Row(dbc.Button("Zkreslení", id="distortion-button"), style={"width":"10em", "margin": "1px"}),  
]