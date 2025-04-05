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
    dbc.Col(dbc.Select(
        options={'bgr': 'modro-zeleno-rudá', 'yp': 'žluto-fialová'},
        value='bgr',
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
                'xaxis': {'showticklabels': False, 'showgrid': False},
                'yaxis': {'showticklabels': False, 'showgrid': False},
                'bargap': 0.6,
                'plot_bgcolor': '#rgba(0,0,0,0)',
                'paper_bgcolor': '#rgba(0,0,0,0)'
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

camera_position_x_widget = [
    dbc.Col(html.Div("Posunutí po osi x: "), width=4),
    dbc.Col(dcc.Input(
        value=0,
        id="camera-x-slider-input",
        type="range",
        min=-2,
        max=2,
        style={"margin": "10px", "width": "95%"}
    ), width=7)
]
camera_position_y_widget = [
    dbc.Col(html.Div("Posunutí po osi y: "), width=4),
    dbc.Col(dcc.Input(
        value=0,
        id="camera-y-slider-input",
        type="range",
        min=-1,
        max=1,
        style={"margin": "10px", "width": "95%"}
    ), width=7)
]
camera_position_z_widget = [
    dbc.Col(html.Div("Posunutí po osi z: "), width=4),
    dbc.Col(dcc.Input(
        value=0,
        id="camera-z-slider-input",
        type="range",
        min=-1,
        max=1,
        style={"margin": "10px", "width": "95%"}
    ), width=7)
]
camera_position_yaw_widget = [
    dbc.Col(html.Div("Otočení doleva/doprava: "), width=4),
    dbc.Col(dcc.Input(
        value=0,
        id="camera-yaw-slider-input",
        type="range",
        min=-4,
        max=4,
        style={"margin": "10px", "width": "95%"}
    ), width=7)
]
camera_position_pitch_widget = [
    dbc.Col(html.Div("Otočení nahoru/dolů: "), width=4),
    dbc.Col(dcc.Input(
        value=0,
        id="camera-pitch-slider-input",
        type="range",
        min=-4,
        max=4,
        style={"margin": "10px", "width": "95%"}
    ), width=7)
]

back_to_default_button = [
    dbc.Col(html.Div(""), width=7),
    dbc.Col(dbc.Button("Vrátit původní", id="back-to-default-button", style={"width": "100%"}), width=4)
]


visualization_tab = [
    dbc.Row(html.Div("Zobrazení vrstev:"), style={'marginTop': '15px'}),
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
    dbc.Row(html.Hr(), style={'marginTop': '15px'}),
    
    dbc.Row(html.Div("Mračno bodů", style={"fontWeight": "bold", "textAlign": "center", "paddingBottom": "0.5em",})),
    dbc.Row(point_size_widget),
    dbc.Row(color_scale_widget, style={'marginTop': '15px'}),
    dbc.Row(color_scale_graph, justify="center", style={'marginTop': '15px'}),
    dbc.Row(color_scale_interval_widget, justify="center", style={'marginTop': '15px'}),
    dbc.Row(point_opacity_widget, style={'marginTop': '15px'}),
    dbc.Row(html.Hr(), style={'marginTop': '15px'}),
    
    dbc.Row(html.Div("Vektorová data", style={"fontWeight": "bold", "textAlign": "center", "paddingBottom": "0.5em",})),
    dbc.Row(line_width_widget),
    dbc.Row(line_color_widget, style={'marginTop': '15px'}),
    dbc.Row(html.Hr(), style={'marginTop': '15px'}),
    
    dbc.Row(html.Div("Dopřesnění polohy virtuální kamery", style={"fontWeight": "bold", "textAlign": "center", "paddingBottom": "0.5em",})),
    dbc.Row(camera_position_x_widget),
    dbc.Row(camera_position_y_widget),
    dbc.Row(camera_position_z_widget),
    dbc.Row(camera_position_yaw_widget),
    dbc.Row(camera_position_pitch_widget),
    dbc.Row(back_to_default_button),
    dbc.Row(html.Hr(), style={"marginTop": "15px"}),
    
    dbc.Row(dbc.Button("Zkreslení", id="distortion-button"), style={"width":"10em", "marginLeft": "1px"})
]