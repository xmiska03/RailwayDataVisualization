# This file contains definitions of dash components and callbacks used in the "data" tab of the app.

from dash import html, dcc
import dash_bootstrap_components as dbc

play_button = dbc.Button(
    html.I(className="bi bi-play-fill"),
    id='play-button',
    style={
        'background': 'none',
        'border': 'none',
        'fontSize': '1.5rem',
        'padding': '0'
    }
)
current_time_div = html.Div("00:00", id="current-time-div")
camera_position_slider = dcc.Input(        # TODO try dbc input here
    value=0,
    id="camera-position-slider-input",
    type="range",
    min=0,
    max=499,
    style={'width': '100%'}
)
total_time_div = html.Div("00:19", id="total-time-div")
animation_speed_select = html.Div(
    [
        html.Div("Rychlost:", style={
            'position': 'absolute',
            'bottom': '100%',
            'left': 0,
            'marginBottom': '6px'
        }),
        dbc.Select(
            options={'2': '2×', '1': '1×', '0.5': '0.5×'},
            value='1',
            id='animation-speed-dropdown',
            style={'width':'80px'}
        )
    ],
    style={'position': 'relative'}

)

play_controls = html.Div(
    [
        play_button,
        current_time_div,
        camera_position_slider,
        total_time_div,
        animation_speed_select
    ],
    id='play-controls-div',
    style={
        'flexGrow': 1,
        'display': 'grid',
        'gap': '15px',
        'gridTemplateColumns': 'fit-content(40px) fit-content(40px) 1fr fit-content(40px) fit-content(100px)',
        'alignItems': 'center',
        'backgroundColor': '#212529',
        'opacity': 0.95,
        'borderRadius': 30,
        'padding': '5px 20px'
    }
)

camera_position_input = html.Div(
    [
        html.Div("Snímek:", style={'paddingLeft': '15px'}),
        html.Div(
            dbc.Input(
                value="0",
                id="camera-position-input",
                type="number",
                min=0,
                max=499,
                style={'width':'90px'}
            ),
            id='camera-position-div',
            style={
                'backgroundColor': '#212529',
                'opacity': 0.95,
                'borderRadius': 30,
                'padding': '5px 15px'
            }
        )
    ],
    style={'width': 'fit-content'}
)

bottom_panel = html.Div(
    [
        play_controls,
        camera_position_input
    ],
    id='bottom-panel-div',
    style={
        'position': 'fixed',
        'bottom': 0,
        'right': 0,
        'width': 'calc(100% - 500px)',  # side panel is open at the beginning
        'transition': 'width 0.5s',
        'display': 'flex',
        'alignItems': 'flex-end',
        'gap': '7px'
    }
)

