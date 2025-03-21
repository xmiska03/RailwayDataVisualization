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

color_scale_widget = [
    dbc.Col(html.Div("Barevná škála: "), width=5),
    dbc.Col(dcc.Dropdown(
        options={'bgr': 'modro-zeleno-rudá', 'yp': 'žluto-fialová'},
        value='bgr',
        clearable=False,
        id='color-scale-dropdown'
    ), width=6)
]

color_scale_graph = [
    dbc.Col(dcc.Graph(
        id='color-scale-graph',
        figure={
            'data': [{
                'y': [1 for _ in range(43)],
                'type': 'bar',
                'marker': {'color': ['#FFFFFF' for _ in range(43)]}
            }],
            'layout': {
                'height': 100,
                'margin': {'l': 0, 'r': 0, 't': 0, 'b': 0},
                'xaxis': {'showticklabels': False},
                'yaxis': {'showticklabels': False},
                'bargap': 0.6
            }
        },
        config={'displayModeBar': False},
        style={'height': '100px'}
    ), width=7),
    dcc.Store(
        id='visualization-data-aggregation'  # needed for the graph
    ),
    dcc.Store(
        id='scale-boundaries-store'
    ),
    dcc.Store(
        id='scale-colors-store',  # needed for the graph
        data='bgr'
    )
]

color_scale_interval_widget = [
    dbc.Col(html.Div("Od: "), width=1),
    dbc.Col(dbc.Input(
        value=0,
        id="scale-from-input",
        type="number",
        min=0,
        max=43,
        step=1
    ), width=3),
    dbc.Col(html.Div("Do: "), width=1),
    dbc.Col(dbc.Input(
        value=18,
        id="scale-to-input",
        type="number",
        min=0,
        max=43,
        step=1
    ), width=3)
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
        min=1,
        max=15,
        step=1
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
    dbc.Row(color_scale_widget),
    dbc.Placeholder(color="black", size="xs"),
    dbc.Row(color_scale_graph, justify="center"),
    dbc.Placeholder(color="black", size="xs"),
    dbc.Row(color_scale_interval_widget, justify="center"),
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