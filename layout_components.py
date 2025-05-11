from dash import  html, dcc
import dash_bootstrap_components as dbc

import data_tab_components
import visualization_tab_components
import profile_tab_components
import animation_control_components

# a part of the Dash app which visualizes the data
visualization = html.Div(
    [
        html.Video(
            src="/assets/video_long_compatible.mp4",
            id="background-video",
            style={
                'height': '100%',
                'display': 'block'
            }
        ),
        html.Canvas(
            id='visualization-canvas',
            style={
                'position': 'absolute',
                'top': 0,
                'left': 0
            }
        ),
        html.Canvas(
            id='distorted-visualization-canvas',
            style={
                'position': 'absolute',
                'top': 0,
                'left': 0
            }
        )
    ],
    style = {
        'height': '100%',
        'aspectRatio': '2048/1536',
        'overflow': 'hidden',
        'position': 'absolute',
        'left': '50%',
        'transform': 'translateX(-50%)'
    }
)

# the right side of the screen with tabs
tabs = dbc.Tabs(
    [
        dbc.Tab(
            dcc.Loading(        # display a circle over the data tab when the app is loading something
                type="circle",
                overlay_style={"visibility": "visible"},
                style={
                    "position": "fixed",         # put it into the middle of the data tab
                    "left": "230px",
                    "top": "calc(50% - 30px)",
                    "transform": "scale(1.4)"
                },
                children=data_tab_components.data_tab
            ),
            tab_id="data", 
            label="Data", 
            label_style={"padding": "10px"},
            style={"height": "calc(100vh - 100px)", "overflowY": "auto", "overflowX":"hidden"}
        ),
        dbc.Tab(
            visualization_tab_components.visualization_tab,
            tab_id="vis",
            label="Zobrazení",
            label_style={"padding": "10px"},
            style={"height": "calc(100vh - 100px)", "overflowY": "auto", "overflowX":"hidden"}
        ),
        dbc.Tab(
            profile_tab_components.profile_tab, 
            tab_id="profile", 
            label="Průjezdný profil", 
            label_style={"padding": "10px"},
            style={"overflowX":"hidden"}
        )
    ],
    active_tab="data"
)

# the right margin of the page, almost empty, contains only a color mode switch
color_mode_switch = html.Div(
    [
        html.I(className="bi bi-moon"),
        dbc.Switch(
            id="color-mode-switch",
            value=False,
            className="d-inline-block ms-1",
            persistence=True,
            style={"marginRight": "-3px"}),
        html.I(className="bi bi-sun")
    ],
    id = 'color-mode-div',
    style={
        'position': 'fixed', 
        'top': 0, 
        'right': 0,
        'backgroundColor': '#212529',
        'opacity': 0.95,
        'borderRadius': 30,
        'padding': '10px 15px',
        'fontSize': '1.1rem'
    }
)

main_part = [    # visualization + animation controls, takes full screen
    visualization,
    color_mode_switch,
    animation_control_components.bottom_panel,
]

side_panel = [ 
    html.Div(
        html.Div(
            tabs,
            style={
                'boxSizing': 'border-box',
                'padding': '10px 10px 20px 10px',
                'height': '100vh',
            }
        ),
        style={'overflow': 'hidden'}
    ),
    dbc.Button(
        html.I(className="bi bi-chevron-left"),
        id="roll-out-button",
        style={
            'position': 'absolute', 
            'top': 0, 
            'left': '100%',
            'backgroundColor': '#212529',
            'opacity': 0.95,
            'borderRadius': 30,
            'border': '1px solid white',
            'fontSize': '1.8rem',
            'padding': '2px 12px'
        }
    )
]

app_layout = [
    html.Div(
        side_panel,
        id='side-panel-div', 
        style={
            'width': '500px',    # open at the beginning
            'boxSizing': 'border-box',
            'transition': 'width 0.5s',
            'height': '100vh',
            'position': 'relative',
            'zIndex': 1,
            'flexShrink': 0
        }
    ),
    html.Div(main_part, style={'height': '100vh', 'flexGrow': 1, 'position': 'relative', 'overflow': 'hidden'}),
]