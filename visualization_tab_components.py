## @file visualization_tab_components.py
# @author Zuzana Miškaňová
# @brief Contains definitions of Dash components used in the "visualization" tab.

from dash import html, dcc
import dash_bootstrap_components as dbc
from params import POINT_SIZE, OPACITY, LINE_WIDTH  # default values


## @brief A widget to choose between the postprocess and the real-time point cloud.
point_cloud_type_widget = [
    dbc.Col(html.Div("Typ: "), width=5),
    dbc.Col(dbc.Select(
        options={'united': 'postprocess', 'divided': 'real-time'},
        value='divided',
        id='point-cloud-type-dropdown',
    ), width=6)
]

## @brief An input to choose the size of the points in the point cloud.
point_size_widget = [
    dbc.Col(html.Div("Velikost bodů: "), width=5),
    dbc.Col(dbc.Input(
        value=f"{POINT_SIZE}",
        id="point-size-input",
        type="number",
        min=10,
        max=50,
        step=1
    ), width=6)
]

## @brief An input to select the type of the color scale.
color_scale_widget = [
    dbc.Col(html.Div("Barevná škála: "), width=5),
    dbc.Col(dbc.Select(
        options={'bgr': 'modro-zeleno-rudá', 'yp': 'žluto-fialová'},
        value='bgr',
        id='color-scale-dropdown'
    ), width=6)
]

## @brief The color scale graph.
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
                'height': 140,
                'margin': {'l': 5, 'r': 0, 't': 0, 'b': 20},
                'xaxis': {'showgrid': False, 'color': '#909090'},
                'yaxis': {'showticklabels': False, 'showgrid': False},
                'bargap': 0.6,
                'plot_bgcolor': '#rgba(0,0,0,0)',
                'paper_bgcolor': '#rgba(0,0,0,0)'
            }
        },
        config={'displayModeBar': False, 'staticPlot': True},
        style={'height': '100px'}
    ), width=7),
    dcc.Store(
        id='pc-data-aggregation'         # needed for the graph
    ),
    dcc.Store(
        id='united-pc-data-aggregation'  # needed for the graph
    ),
    dcc.Store(
        id='scale-boundaries-store'
    ),
    dcc.Store(
        id='scale-colors-store',         # needed for the graph
        data='bgr'
    )
]

## @brief A widget to choose the boundaries of the color scale.
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
        value=20,
        id="scale-to-input",
        type="number",
        min=0,
        max=43,
        step=1
    ), width=3)
]

## @brief An input to choose the opacity of the point cloud layer.
point_opacity_widget = [
    dbc.Col(html.Div("Průhlednost bodů: "), width=5),
    dbc.Col(dbc.Input(
        value=f"{OPACITY}",
        id="point-opacity-input",
        type="number",
        min=0,
        max=1,
        step=0.2
    ), width=6)
]

## @brief An input to choose the line width of the vector data.
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

## @brief A widget to choose the color of the vector data.
line_color_widget = [
    dbc.Col(html.Div("Barva čar: "), width=5),
    dbc.Col(dbc.Input(
        type="color",
        id="line-color-picker",
        value="#fa650f",
    ), width=6)
]

## @brief A slider to add offset to the position of the virtual camera - move it on the x axis.
camera_position_x_widget = [
    dbc.Col(html.Div("Posunutí po ose x: "), width=4),
    dbc.Col(dcc.Input(
        value=0,
        id="camera-x-slider-input",
        type="range",
        min=-4,
        max=4,
        style={"margin": "10px", "width": "95%"}
    ), width=7)
]
## @brief A slider to add offset to the position of the virtual camera - move it on the y axis.
camera_position_y_widget = [
    dbc.Col(html.Div("Posunutí po ose y: "), width=4),
    dbc.Col(dcc.Input(
        value=0,
        id="camera-y-slider-input",
        type="range",
        min=-1,
        max=1,
        style={"margin": "10px", "width": "95%"}
    ), width=7)
]
## @brief A slider to add offset to the position of the virtual camera - move it on the z axis.
camera_position_z_widget = [
    dbc.Col(html.Div("Posunutí po ose z: "), width=4),
    dbc.Col(dcc.Input(
        value=0,
        id="camera-z-slider-input",
        type="range",
        min=-1,
        max=1,
        style={"margin": "10px", "width": "95%"}
    ), width=7)
]
## @brief A slider to add offset to the orientation of the virtual camera - adjust the yaw angle.
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
## @brief A slider to add offset to the orientation of the virtual camera - adjust the pitch angle.
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
## @brief A slider to add offset to the orientation of the virtual camera - adjust the roll angle.
camera_position_roll_widget = [
    dbc.Col(html.Div("Naklonění doleva/doprava: "), width=4),
    dbc.Col(dcc.Input(
        value=0,
        id="camera-roll-slider-input",
        type="range",
        min=-4,
        max=4,
        style={"margin": "10px", "width": "95%"}
    ), width=7)
]

## @brief A button to return the sliders back to default.
back_to_default_button = [
    dbc.Col(html.Div(""), width=7),
    dbc.Col(dbc.Button("Vrátit původní", id="back-to-default-button", style={"width": "100%"}), width=4),
    dbc.Col(dcc.Store(id="camera-offset-default-store", data=[0, 0, 0, 0, 0, 0]))
]

## @brief A button to export all the workspace settings.
export_workspace_widget = [
    dbc.Col(dbc.Button(
        "Exportovat nastavení zobrazení", 
        id="export-workspace-button",
        style={"width": "100%"}
    ), width=7),
    dcc.Download(id="workspace-download")  # not visible
]
## @brief A button to import workspace settings from a TOML file.
import_workspace_widget = [
    dbc.Col(dcc.Upload(
        dbc.Button("Importovat nastavení zobrazení", style={"width": "100%"}), 
        id="import-workspace-upload",
        style={"width": "100%"}
    ), width=7)
]

## @brief The whole content of the "visualization" tab.
visualization_tab = [
    dbc.Row(html.Div("Mračno bodů", style={"fontWeight": "bold", "textAlign": "center", "paddingBottom": "0.5em", 'marginTop': '15px'})),
    dbc.Row(dcc.Checklist(
            options=[{'label': ' zobrazovat mračno bodů', 'value': 'pcl'}],
            value=['pcl'],
            id='point-cloud-checkbox'
        )
    ),
    dbc.Row(point_cloud_type_widget, style={'marginTop': '15px'}),
    dbc.Row(point_size_widget, style={'marginTop': '15px'}),
    dbc.Row(color_scale_widget, style={'marginTop': '15px'}),
    dbc.Row(color_scale_graph, justify="center", style={'marginTop': '15px'}),
    dbc.Row(color_scale_interval_widget, justify="center", style={'marginTop': '15px'}),
    dbc.Row(point_opacity_widget, style={'marginTop': '15px'}),
    dbc.Row(html.Hr(), style={'marginTop': '15px'}),

    dbc.Row(html.Div("Video", style={"fontWeight": "bold", "textAlign": "center", "paddingBottom": "0.5em",})),
    dbc.Row(dcc.Checklist(
            options=[{'label': ' zobrazovat video', 'value': 'pic'}],
            value=['pic'],
            id='camera-picture-checkbox'
        )
    ),
    dbc.Row(html.Hr(), style={'marginTop': '15px'}),
    
    dbc.Row(html.Div("Vektorová data", style={"fontWeight": "bold", "textAlign": "center", "paddingBottom": "0.5em",})),
    dbc.Row(dcc.Checklist(
            options=[{'label': ' zobrazovat vektorová data', 'value': 'vec'}],
            value=['vec'],
            id='vector-data-checkbox'
        )
    ),
    dbc.Row(line_width_widget, style={'marginTop': '15px'}),
    dbc.Row(line_color_widget, style={'marginTop': '15px'}),
    dbc.Row(html.Hr(), style={'marginTop': '15px'}),
    
    dbc.Row(html.Div("Posunutí virtuální kamery", style={"fontWeight": "bold", "textAlign": "center", "paddingBottom": "0.5em",})),
    dbc.Row(camera_position_x_widget),
    dbc.Row(camera_position_y_widget),
    dbc.Row(camera_position_z_widget),
    dbc.Row(camera_position_yaw_widget),
    dbc.Row(camera_position_pitch_widget),
    dbc.Row(camera_position_roll_widget),
    dbc.Row(back_to_default_button),
    dbc.Row(html.Hr(), style={"marginTop": "15px"}),
    
    dbc.Row(html.Div("Zkreslení", style={"fontWeight": "bold", "textAlign": "center", "paddingBottom": "0.5em",})),
    dbc.Row(dcc.Checklist(
            options=[{'label': ' zobrazovat se zkreslením', 'value': 'dist'}],
            value=[],    # initially no distortion
            id='distortion-checkbox'
        )
    ),
    dbc.Row(html.Hr(), style={"marginTop": "15px"}),
    
    dbc.Row(export_workspace_widget),
    dbc.Row(import_workspace_widget, style={"marginTop": "15px"})
]   